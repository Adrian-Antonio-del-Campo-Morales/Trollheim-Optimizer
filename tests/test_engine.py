import queue
import time

import numpy as np

import trollheim_simulator.engine as engine
from trollheim_simulator.engine import (
    ENEMY_VARIANTS_PER_PROFILE,
    _build_enemy_variants,
    _generate_shared_enemy_selection,
    _random_enemy_config,
    _random_candidate_charges,
    effective_fighter_key,
    run_single_task_optimized,
)
from trollheim_simulator.enemies import ENEMY_PROFILES
from trollheim_simulator.rules import (
    NORMAL_ENEMIES_DATABASE, TWO_HANDED_WEAPONS, WEAPON_UNARMED,
)
from trollheim_simulator.ui import DEFAULT_COMBO_SIMULATIONS, TrollheimApp


FIGHTER = {
    "HA": 4,
    "F": 3,
    "R": 3,
    "H": 1,
    "I": 4,
    "A": 1,
    "skills": [],
    "main_weapon": "Espada",
    "off_hand": "Ninguna",
    "has_helmet": False,
    "has_luck_amulet": False,
    "armor": "Sin Armadura",
}


def test_shared_enemy_selection_is_reproducible_and_valid():
    names = ["Guerrero humano", "Guerrero enano", "Orco"]
    first = _generate_shared_enemy_selection(names, 1_000, 1234)
    second = _generate_shared_enemy_selection(names, 1_000, 1234)
    assert np.array_equal(first, second)
    assert first.min() >= 0
    assert first.max() < len(names)


def test_first_turn_charge_is_drawn_per_duel_and_is_balanced():
    first = _random_candidate_charges(np.random.default_rng(2026), 100_000)
    second = _random_candidate_charges(np.random.default_rng(2026), 100_000)
    assert np.array_equal(first, second)
    assert first.dtype == np.bool_
    assert 0.49 < first.mean() < 0.51
    assert first.any() and (~first).any()


def test_worker_runs_a_small_custom_matchup():
    total = 100
    progress = queue.Queue()
    args = (
        "Single",
        "prueba",
        FIGHTER,
        "custom",
        NORMAL_ENEMIES_DATABASE["Humano"] | {
            "skills": [],
            "main_weapon": "Espada",
            "off_hand": "Ninguna",
            "has_helmet": False,
            "has_luck_amulet": False,
            "armor": "Sin Armadura",
        },
        [],
        np.zeros(total, dtype=np.int64),
        total,
        42,
        True,
        progress,
        0,
    )
    mode, label, win_rate, is_base = run_single_task_optimized(args)
    assert (mode, label, is_base) == ("Single", "prueba", True)
    assert 0.0 <= win_rate <= 100.0
    assert progress.get_nowait() == ("chunk", 0, total)


def test_worker_accepts_multiple_manual_enemies_with_shared_selection():
    total = 200
    enemies = [
        FIGHTER | {"enemy_name": "Espadachín"},
        FIGHTER | {"enemy_name": "Bruto", "F": 4, "main_weapon": "Maza"},
    ]
    indices = np.tile(np.array([0, 1], dtype=np.int64), total // 2)
    args = (
        "Single", "varios", FIGHTER, "custom", enemies, [], indices,
        total, 77, True, None, 0, 0,
    )
    mode, label, win_rate, is_base = run_single_task_optimized(args)
    assert (mode, label, is_base) == ("Single", "varios", True)
    assert 0.0 <= win_rate <= 100.0


def test_random_enemy_equipment_is_legal_and_levels_are_applied():
    rng = np.random.default_rng(9)
    config = _random_enemy_config("Guerrero humano", 4, rng)
    legal = ENEMY_PROFILES["Guerrero humano"]["equipment"]
    assert config["main_weapon"] in {name for name, *_ in legal["main"]}
    assert config["off_hand"] in {name for name, *_ in legal["off"]}
    assert config["armor"] in {name for name, *_ in legal["armor"]}
    assert sum(config[attr] - ENEMY_PROFILES["Guerrero humano"][attr]
               for attr in ("HA", "F", "R", "H", "I", "A")) + len(config["skills"]) == 4
    if config["main_weapon"] in TWO_HANDED_WEAPONS:
        assert config["off_hand"] in {"Ninguna", "Escudo", "Daga", "Maza", "Hacha", "Espada"}


def test_enemy_variants_have_expected_shape():
    enemies, owners = _build_enemy_variants(["Zombi", "Vampiro"], 2, 123, 5)
    assert enemies.shape == (10, 22)
    assert owners.tolist() == [0] * 5 + [1] * 5


def test_vectorized_engine_has_no_compilation_pause():
    total = 10_000
    names = ["Guerrero humano", "Orco"]
    indices = _generate_shared_enemy_selection(
        names, total, 77, ENEMY_VARIANTS_PER_PROFILE
    )
    args = (
        "Single", "rendimiento", FIGHTER, "sample", None, names, indices,
        total, 77, True, None, 0, 0,
    )
    started = time.perf_counter()
    result = run_single_task_optimized(args)
    elapsed = time.perf_counter() - started
    assert 0.0 <= result[2] <= 100.0
    assert elapsed < 3.0


def test_simulation_batch_is_split_into_small_chunks(monkeypatch):
    candidate = engine._make_fighter(FIGHTER)
    enemies = np.asarray([engine._make_fighter(FIGHTER | {"main_weapon": "Maza"})])
    sizes = []

    def fake_kernel(_candidate, _enemy, amount, _seed):
        sizes.append(amount)
        return amount, amount

    monkeypatch.setattr(engine, "_simulate_simple_native", fake_kernel)
    total = 250_000
    wins, resolved = engine._simulate_batch(
        candidate, enemies, np.zeros(total, dtype=np.int8), total, 42
    )
    assert sizes == [100_000, 100_000, 50_000]
    assert (wins, resolved) == (total, total)


def test_native_route_only_accepts_simple_fighters(monkeypatch):
    monkeypatch.setattr(engine, "_simulate_simple_native", lambda *_args: (0, 0))
    simple = engine._make_fighter(FIGHTER)
    assert engine._can_use_native_kernel(simple, simple)

    skilled = engine._make_fighter(FIGHTER | {"skills": ["Fortachón"]})
    poisoned = engine._make_fighter(FIGHTER | {"main_poison": "Loto Negro"})
    special = engine._make_fighter(FIGHTER | {"main_weapon": "Látigo de Acero"})
    assert not engine._can_use_native_kernel(skilled, simple)
    assert not engine._can_use_native_kernel(poisoned, simple)
    assert not engine._can_use_native_kernel(special, simple)


def test_effective_key_ignores_equipment_specific_skills_when_inert():
    base = FIGHTER | {"skills": []}
    inert = FIGHTER | {"skills": ["Maestro del Hacha", "Golpe con el Escudo"]}
    assert effective_fighter_key(base) == effective_fighter_key(inert)


def test_effective_key_keeps_equipment_specific_skills_when_active():
    axe = FIGHTER | {"main_weapon": "Hacha", "skills": []}
    axe_master = axe | {"skills": ["Maestro del Hacha"]}
    shield = FIGHTER | {"off_hand": "Escudo", "skills": []}
    shield_strike = shield | {"skills": ["Golpe con el Escudo"]}
    assert effective_fighter_key(axe) != effective_fighter_key(axe_master)
    assert effective_fighter_key(shield) != effective_fighter_key(shield_strike)


def test_effective_key_never_drops_general_combat_skills():
    for skill in ("Combatiente Experto", "Golpe Poderoso", "Curtido"):
        upgraded = FIGHTER | {"skills": [skill]}
        assert effective_fighter_key(FIGHTER) != effective_fighter_key(upgraded)


def test_task_deduplication_preserves_aliases_for_inert_skills():
    base_task = ("Single", "base", FIGHTER, None, None, None, None, 100, 1, True)
    inert_task = (
        "Single", "maestro sin hacha", FIGHTER | {"skills": ["Maestro del Hacha"]},
        None, None, None, None, 100, 2, False,
    )
    unique, aliases = TrollheimApp._deduplicate_tasks([base_task, inert_task])
    assert len(unique) == 1
    assert aliases[("Single", "base")] == [
        ("base", True),
        ("maestro sin hacha", False),
    ]


def test_task_deduplication_keeps_active_skills_separate():
    base_task = ("Single", "base", FIGHTER, None, None, None, None, 100, 1, True)
    active_task = (
        "Single", "esgrima", FIGHTER | {"skills": ["Experto en Esgrima"]},
        None, None, None, None, 100, 2, False,
    )
    unique, _aliases = TrollheimApp._deduplicate_tasks([base_task, active_task])
    assert len(unique) == 2


def test_tree_sort_keys_never_mix_incompatible_types():
    values = ["Espada + Escudo", "★ 62.40% (+3.20%)", "", "+1 HA", "−2.5%"]
    sorted(values, key=TrollheimApp._tree_sort_key)


def test_analysis_default_is_one_hundred_thousand():
    assert DEFAULT_COMBO_SIMULATIONS == 100_000


def test_luck_amulet_is_not_an_upgrade_anymore():
    upgrades = TrollheimApp._build_upgrade_list(object(), FIGHTER)
    assert all("Amuleto" not in label for label, _upgrade in upgrades)


def test_equipment_catalog_contains_armour_objects_and_consumables():
    options = TrollheimApp._equipment_options()
    labels = {label for label, _kind, _value in options}
    assert {"Armadura Ligera", "Casco", "Amuleto de la suerte"} <= labels
    assert {"Sombra Carmesí", "Loto Negro", "Saliva de Araña"} <= labels
    assert {"Hongos Sombrero Loco", "Hongos Pirakabezas"} <= labels


def test_equipment_loadout_starts_without_optional_equipment():
    candidate = FIGHTER | {
        "armor": "Armadura Pesada",
        "has_helmet": True,
        "has_luck_amulet": True,
    }
    equipped = TrollheimApp._apply_equipment_items(candidate, (
        ("Armadura Ligera", "armor", "Armadura Ligera"),
        ("Amuleto de la suerte", "amulet", True),
    ))
    assert equipped["armor"] == "Armadura Ligera"
    assert not equipped["has_helmet"]
    assert equipped["has_luck_amulet"]


def test_owned_equipment_is_deducted_once_from_combination_cost():
    candidate = FIGHTER | {
        "armor": "Armadura Ligera", "has_helmet": True,
        "main_poison": "Loto Negro", "offhand_poison": "Sin veneno",
    }
    costs = {"Armadura Ligera": 20.0, "Casco": 10.0, "Loto Negro": 13.5}
    assert TrollheimApp._equipment_acquisition_costs(
        ("Casco", "Armadura Ligera", "Loto Negro"), candidate, costs
    ) == (0.0, 0.0, 0.0)
    assert TrollheimApp._equipment_acquisition_costs(
        ("Loto Negro", "Loto Negro"), candidate, costs
    ) == (0.0, 13.5)
    display, total = TrollheimApp._equipment_cost_display((0.0, 13.5))
    assert display == "0 + 13.5 = 13.5 co"
    assert total == 13.5


def test_only_poison_can_be_selected_twice():
    armor = ("Armadura Ligera", "armor", "Armadura Ligera")
    amulet = ("Amuleto de la suerte", "amulet", True)
    poison = ("Loto Negro", "poison", "Loto Negro")
    legal = TrollheimApp._equipment_combination_is_legal
    assert not legal((armor, armor))
    assert not legal((amulet, amulet))
    assert legal((poison, poison))


def test_equipment_loadouts_can_include_legal_triples():
    armor = ("Armadura Ligera", "armor", "Armadura Ligera")
    helmet = ("Casco", "helmet", True)
    poison = ("Loto Negro", "poison", "Loto Negro")
    loadouts = TrollheimApp._equipment_loadouts([armor, helmet, poison], 3)
    item_sets = {items for _labels, items in loadouts}
    assert (armor, helmet, poison) in item_sets
    assert (poison, poison, poison) not in item_sets
    assert all(1 <= len(items) <= 3 for _labels, items in loadouts)


def test_equipment_maximum_one_only_generates_individual_items():
    options = TrollheimApp._equipment_options()[:3]
    loadouts = TrollheimApp._equipment_loadouts(options, 1)
    assert len(loadouts) == len(options)
    assert all(len(items) == 1 for _labels, items in loadouts)


def test_weapon_loadouts_cover_the_four_hand_configurations():
    loadouts = TrollheimApp._weapon_loadouts(
        ["Espada", "Maza", "Arma 2H", "Bagh Nakh"]
    )
    assert ("Single", "Espada", "Ninguna") in loadouts
    assert ("Shield", "Espada", "Escudo") in loadouts
    assert ("Dual", "Espada", "Maza") in loadouts
    assert ("Dual", "Maza", "Espada") in loadouts
    assert ("TwoHand", "Arma 2H", "Ninguna") in loadouts
    assert ("TwoHand", "Bagh Nakh", "Ninguna") in loadouts
    assert ("Single", "Ninguna", "Ninguna") in loadouts


def test_two_handed_weapons_are_not_generated_as_dual_combinations():
    loadouts = TrollheimApp._weapon_loadouts(["Espada", "Arma 2H"])
    assert all(
        main != "Arma 2H" or mode == "TwoHand"
        for mode, main, _off in loadouts
    )


def test_weapons_that_demand_attention_do_not_get_a_second_weapon():
    loadouts = TrollheimApp._weapon_loadouts(
        ["Lanza", "Mangual", "Rebanadora", "Pinchagarrapatos", "Daga"]
    )
    assert not any(
        mode == "Dual" and main in {"Lanza", "Mangual", "Rebanadora", "Pinchagarrapatos"}
        for mode, main, _off in loadouts
    )


def test_spiked_gauntlet_is_the_exception_for_difficult_weapons():
    loadouts = TrollheimApp._weapon_loadouts(
        ["Rebanadora", "Pinchagarrapatos", "Guantelete con Pincho"]
    )
    assert ("Dual", "Rebanadora", "Guantelete con Pincho") in loadouts
    assert ("Dual", "Pinchagarrapatos", "Guantelete con Pincho") in loadouts


def test_sun_gauntlet_is_only_generated_in_the_off_hand():
    loadouts = TrollheimApp._weapon_loadouts(["Espada", "Guantelete Solar"])
    assert not any(main == "Guantelete Solar" for _mode, main, _off in loadouts)
    assert ("Dual", "Espada", "Guantelete Solar") in loadouts


def test_weapon_loadouts_use_selected_defenses_and_respect_exceptions():
    loadouts = TrollheimApp._weapon_loadouts(
        ["Espada", "Lanza", "Mangual", "Rebanadora"],
        ("Escudo", "Rodela"),
    )
    assert ("Shield", "Espada", "Escudo") in loadouts
    assert ("Shield", "Espada", "Rodela") in loadouts
    assert ("Shield", "Lanza", "Rodela") in loadouts
    assert ("Shield", "Rebanadora", "Escudo") in loadouts
    assert ("Shield", "Rebanadora", "Rodela") not in loadouts
    assert not any(mode == "Shield" and main == "Mangual" for mode, main, _off in loadouts)


def test_materialized_weapon_loadouts_assign_material_to_each_weapon_only():
    loadouts = TrollheimApp._materialized_weapon_loadouts(
        ["Espada", "Daga"], ("Sin material", "Gromril"), ("Rodela",)
    )
    assert ("Shield", "Espada", "Rodela", "Gromril", "Sin material") in loadouts
    assert ("Dual", "Espada", "Daga", "Gromril", "Sin material") in loadouts
    assert ("Dual", "Espada", "Daga", "Sin material", "Gromril") in loadouts
    assert all(
        off_material == "Sin material"
        for _mode, _main, off, _main_material, off_material in loadouts
        if off in {"Ninguna", "Escudo", "Rodela"}
    )


def test_weapon_cost_uses_material_multiplier_and_formats_total():
    costs = {"Espada": 10.0, "Rodela": 5.0}
    main = TrollheimApp._weapon_cost("Espada", "Gromril", costs)
    off = TrollheimApp._weapon_cost("Rodela", "Sin material", costs)
    display, total = TrollheimApp._weapon_cost_display(main, off)
    assert main == 40.0
    assert total == 45.0
    assert display == "40 + 5 = 45 co"


def test_owned_weapons_are_deducted_once_regardless_of_hand():
    candidate = {
        "main_weapon": "Espada", "main_weapon_material": "Gromril",
        "off_hand": "Daga", "offhand_material": "Sin material",
    }
    costs = {"Espada": 10.0, "Daga": 2.0}
    assert TrollheimApp._weapon_acquisition_costs(
        "Daga", "Espada", "Sin material", "Gromril", candidate, costs,
    ) == (0.0, 0.0)
    assert TrollheimApp._weapon_acquisition_costs(
        "Espada", "Espada", "Gromril", "Gromril", candidate, costs,
    ) == (0.0, 40.0)


def test_every_warrior_owns_exactly_one_free_normal_dagger():
    costs = {"Daga": 2.0}
    assert TrollheimApp._weapon_acquisition_costs(
        "Daga", "Ninguna", "Sin material", "Sin material", {}, costs,
    ) == (0.0, 0.0)
    assert TrollheimApp._weapon_acquisition_costs(
        "Daga", "Daga", "Sin material", "Sin material", {}, costs,
    ) == (0.0, 2.0)
    assert TrollheimApp._weapon_acquisition_costs(
        "Daga", "Ninguna", "Gromril", "Sin material", {}, costs,
    ) == (8.0, 0.0)


def test_empty_hands_have_zero_acquisition_cost_and_a_clear_label():
    assert TrollheimApp._weapon_acquisition_costs(
        "Ninguna", "Ninguna", "Sin material", "Sin material", {}, {}
    ) == (0.0, 0.0)
    assert TrollheimApp._weapon_loadout_label(
        "Ninguna", "Ninguna", "Sin material", "Sin material"
    ) == "Sin armas || Ninguna"
    assert engine._make_fighter(FIGHTER | {"main_weapon": "Ninguna"})[6] == WEAPON_UNARMED


def test_weapon_export_includes_total_cost_and_motta_index():
    table_data = (
        {
            "Single": [40.0, [["Espada || Ninguna", 50.0, 10.0]]],
            "Shield": [40.0, []], "Dual": [40.0, []], "TwoHand": [40.0, []],
        },
        {"Single": "Espada"},
        {"Espada || Ninguna": (10.0, 0.0)},
    )
    headers, rows = TrollheimApp._result_export_rows("weapons", table_data)
    row = next(value for value in rows if value[0] == "Espada")
    assert "Coste" in headers
    assert "Índice MOTTA" in headers
    assert row[headers.index("Coste")] == 10.0
    assert np.isclose(
        row[headers.index("Índice MOTTA")],
        10.0 / np.hypot(10.0, 0.01) * 507.4,
    )


def test_regularized_motta_is_large_at_zero_cost_linear_and_symmetric():
    positive = TrollheimApp._motta_index(2.0, 0.0)
    negative = TrollheimApp._motta_index(-2.0, 0.0)
    assert np.isclose(positive, 101_480.0)
    assert negative == -positive
    assert TrollheimApp._motta_index(0.0, 0.0) == 0.0
    assert np.isclose(
        TrollheimApp._motta_index(2.0, 10.0),
        2.0 / np.hypot(10.0, 0.01) * 507.4,
    )


def test_two_poisons_are_applied_one_to_each_hand():
    equipped = TrollheimApp._apply_equipment_items(FIGHTER, (
        ("Loto Negro", "poison", "Loto Negro"),
        ("Veneno Negro", "poison", "Veneno Negro"),
    ))
    assert equipped["main_poison"] == "Loto Negro"
    assert equipped["offhand_poison"] == "Veneno Negro"


def test_optimal_view_only_uses_visible_equipment_modes():
    values = {
        "Single": (55.0, 1.0),
        "Shield": (70.0, 2.0),
        "Dual": (65.0, 3.0),
        "TwoHand": (60.0, 4.0),
    }
    assert TrollheimApp._best_visible_mode(values, {"Single", "Shield", "Dual"}) == "Shield"
    assert TrollheimApp._best_visible_mode(values, {"Single", "Dual"}) == "Dual"


def test_optimal_view_handles_sparse_weapon_modes():
    values = {"Shield": (61.0, 2.0)}
    assert TrollheimApp._best_visible_mode(values, {"Single", "Shield"}) == "Shield"
    assert TrollheimApp._best_visible_mode(values, {"Single", "Dual"}) is None


def test_combo_parts_keep_one_canonical_order():
    parts = TrollheimApp._combo_parts("+1 A + Fortachón")
    assert parts == ("+1 A", "Fortachón")


def test_combo_search_ignores_case_accents_and_component_order():
    parts = TrollheimApp._combo_parts("+1 A + Fortachón")
    assert TrollheimApp._combo_matches(parts, "FORTACHON")
    assert TrollheimApp._combo_matches(parts, "+1 a")
    assert not TrollheimApp._combo_matches(parts, "Curtido")
