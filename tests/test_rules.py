import numpy as np

from trollheim_simulator.engine import (
    _armor_base_save,
    _armour_strength,
    _attack_strength,
    _weapon_attacks_first,
    _combat_initiative,
    _extra_armour_penalty,
    _house_rule_hit_penalty,
    _strength_armour_penalty,
    _make_fighter,
    _nb_armour_save,
    _nb_to_hit,
    _nb_to_wound,
    _poison_for_attack,
    _parry_profile,
    _phase_attack_plan,
    _phase_attack_count,
    _phase_weapon_for_attack,
    _weapon_for_attack,
)
from trollheim_simulator.rules import (
    OFF_NONE,
    OFF_SHIELD,
    OFF_BUCKLER,
    WEAPON_2H,
    WEAPON_MACE,
    WEAPON_DAGGER,
    WEAPON_FLAIL,
    WEAPON_RAPIER,
    WEAPON_SWORD,
    WEAPON_WAR_MAUL,
    WEAPON_CHOPPA,
    WEAPON_ESHIN_CLAWS,
    WEAPON_SIGMARITE_HAMMER,
    WEAPON_SPIKED_GAUNTLET,
    WEAPON_WITCH_BLADE,
    WEAPON_PIRATE_SCOURGE,
    WEAPON_PISTOL,
    WEAPON_DUELING_PISTOL,
    WEAPON_POISONED_DAGGERS,
    WEAPON_SUN_GAUNTLET,
    WEAPON_DRAICH,
    WEAPON_DEATH_KNIFE,
    WEAPON_LONG_HOOK,
    WEAPON_TRIDENT,
    WEAPON_SERPENT_WHIP,
    WEAPON_WEEPING_BLADES,
    WEAPON_BALL_AND_CHAIN,
    WEAPONS_EXCLUSIVE,
    WEAPONS_GENERAL,
    WEAPONS_ALL,
    WEAPONS_MAIN,
    OFF_HAND_OPTIONS,
    OFFHAND_RESTRICTED_WEAPONS,
    WEAPON_CODES,
    OFFHAND_CODES,
    ARMORS,
    ARMOR_CODES,
    POISON_BLACK_VENOM,
    POISON_REPTILE,
    POISON_BLACK_LOTUS,
    PREPARATION_CRIMSON_SHADE,
    PREPARATION_MANDRAKE_ROOT,
    PREPARATION_MAD_CAP,
    PREPARATION_HEAD_SPLITTER,
    SKILL_FENCER,
)


BASE_FIGHTER = {
    "HA": 4,
    "F": 3,
    "R": 3,
    "H": 1,
    "I": 4,
    "A": 1,
    "skills": [],
    "main_weapon": "Espada",
    "off_hand": "Ninguna",
    "armor": "Sin Armadura",
}


def test_hit_table():
    assert _nb_to_hit(4, 0) == 2
    assert _nb_to_hit(4, 3) == 3
    assert _nb_to_hit(4, 4) == 4
    assert _nb_to_hit(2, 5) == 5


def test_complete_hit_table_matches_manual():
    for attacker in range(1, 11):
        for defender in range(1, 11):
            expected = 3 if attacker > defender else 5 if defender > 2 * attacker else 4
            assert _nb_to_hit(attacker, defender) == expected


def test_wound_table():
    expected = [2, 3, 4, 5, 6, 6, 7]
    assert [_nb_to_wound(4, resistance) for resistance in range(2, 9)] == expected


def test_armour_values():
    assert _armor_base_save("Sin Armadura") == 7
    assert _armor_base_save("Armadura Ligera") == 6
    assert _armor_base_save("Armadura Pesada") == 5
    assert _armor_base_save("Armadura de Gromril") == 4


def test_dagger_grants_a_six_plus_save_without_armour():
    assert _nb_armour_save(7, WEAPON_DAGGER) == 6


def test_two_handed_weapon_disables_offhand_and_initiative():
    config = BASE_FIGHTER | {
        "main_weapon": "Arma 2H",
        "off_hand": "Espada",
    }
    fighter = _make_fighter(config)
    assert fighter.dtype == np.int64
    assert fighter[6] == WEAPON_2H
    assert fighter[7] == OFF_NONE
    assert fighter[4] == BASE_FIGHTER["I"]


def test_powerful_blow_increases_strength():
    fighter = _make_fighter(BASE_FIGHTER | {"skills": ["Golpe Poderoso"]})
    assert fighter[1] == BASE_FIGHTER["F"]
    assert _attack_strength(fighter, WEAPON_SWORD, False) == BASE_FIGHTER["F"] + 1
    assert _armour_strength(fighter, WEAPON_SWORD) == BASE_FIGHTER["F"] + 1


def test_offhand_codes_are_translated_to_weapon_codes():
    sword = _make_fighter(BASE_FIGHTER | {"off_hand": "Espada"})
    mace = _make_fighter(BASE_FIGHTER | {"off_hand": "Maza"})
    assert _weapon_for_attack(sword, BASE_FIGHTER["A"]) == WEAPON_SWORD
    assert _weapon_for_attack(mace, BASE_FIGHTER["A"]) == WEAPON_MACE


def test_house_rules_apply_the_expected_hit_penalties():
    offhand_only = _make_fighter(
        BASE_FIGHTER | {
            "off_hand": "Daga",
            "house_rule_offhand_penalty": True,
        }
    )
    both_hands = _make_fighter(
        BASE_FIGHTER | {
            "off_hand": "Daga",
            "house_rule_dual_penalty": True,
        }
    )
    both_rules = _make_fighter(
        BASE_FIGHTER | {
            "off_hand": "Daga",
            "house_rule_offhand_penalty": True,
            "house_rule_dual_penalty": True,
        }
    )
    assert _house_rule_hit_penalty(offhand_only, 0) == 0
    assert _house_rule_hit_penalty(offhand_only, BASE_FIGHTER["A"]) == 1
    assert _house_rule_hit_penalty(both_hands, 0) == 1
    assert _house_rule_hit_penalty(both_hands, BASE_FIGHTER["A"]) == 1
    assert _house_rule_hit_penalty(both_rules, BASE_FIGHTER["A"]) == 2


def test_better_armour_and_useful_shields_improve_the_save():
    light = _make_fighter(BASE_FIGHTER | {"armor": "Armadura Ligera"})
    better = _make_fighter(BASE_FIGHTER | {
        "armor": "Armadura Ligera", "house_rule_better_armour": True,
    })
    shield = _make_fighter(BASE_FIGHTER | {"off_hand": "Escudo"})
    useful = _make_fighter(BASE_FIGHTER | {
        "off_hand": "Escudo", "house_rule_useful_shields": True,
    })
    assert better[8] == light[8] - 1
    assert useful[8] == shield[8] - 1


def test_sea_dragon_cloak_is_equipment_with_its_own_save():
    cloak = _make_fighter(BASE_FIGHTER | {"has_sea_dragon_cloak": True})
    combined = _make_fighter(BASE_FIGHTER | {
        "armor": "Armadura Ligera", "has_sea_dragon_cloak": True,
    })
    better_cloak = _make_fighter(BASE_FIGHTER | {
        "has_sea_dragon_cloak": True, "house_rule_better_armour": True,
    })
    assert cloak[8] == 5
    assert combined[8] == 5
    assert better_cloak[8] == cloak[8]


def test_hard_armour_delays_strength_penetration_until_strength_five():
    normal = _make_fighter(BASE_FIGHTER)
    hard = _make_fighter(BASE_FIGHTER | {"house_rule_hard_armour": True})
    assert _strength_armour_penalty(normal, 4) == 1
    assert _strength_armour_penalty(hard, 4) == 0
    assert _strength_armour_penalty(hard, 5) == 1


def test_fencing_expertise_uses_the_current_canonical_name():
    sword_expert = _make_fighter(
        BASE_FIGHTER | {"skills": ["Experto en Esgrima"]}
    )
    assert sword_expert[9] & SKILL_FENCER


def test_new_weapon_profiles_are_encoded():
    assert _make_fighter(BASE_FIGHTER | {"main_weapon": "Mayal"})[6] == WEAPON_FLAIL
    assert _make_fighter(BASE_FIGHTER | {"main_weapon": "Estoque"})[6] == WEAPON_RAPIER
    assert _make_fighter(BASE_FIGHTER | {"main_weapon": "Mazo de Guerra"})[6] == WEAPON_WAR_MAUL


def test_weapon_catalog_is_split_without_duplicates():
    assert "Espada" in WEAPONS_GENERAL
    assert "Martillo Sigmarita" in WEAPONS_EXCLUSIVE
    assert set(WEAPONS_GENERAL).isdisjoint(WEAPONS_EXCLUSIVE)
    assert set(WEAPONS_GENERAL + WEAPONS_EXCLUSIVE) == set(WEAPON_CODES)
    assert set(WEAPONS_ALL) == set(WEAPON_CODES)
    assert set(WEAPONS_MAIN) == set(WEAPON_CODES) - {"Guantelete Solar"}
    assert set(OFF_HAND_OPTIONS) == set(OFFHAND_CODES)
    assert set(ARMORS) == set(ARMOR_CODES)


def test_all_one_handed_weapons_are_available_in_the_off_hand():
    expected = set(WEAPONS_GENERAL + WEAPONS_EXCLUSIVE) - OFFHAND_RESTRICTED_WEAPONS
    assert expected == set(OFF_HAND_OPTIONS) - {"Ninguna", "Escudo", "Rodela"}
    assert "Látigo de Acero" in OFFHAND_CODES
    assert "Mangual" not in OFFHAND_CODES
    assert "Báculo de Serpiente" not in OFFHAND_CODES


def test_band_weapons_apply_their_core_mechanics():
    hammer = _make_fighter(BASE_FIGHTER | {"main_weapon": "Martillo Sigmarita"})
    choppa = _make_fighter(BASE_FIGHTER | {"main_weapon": "Rebanadora"})
    claws = _make_fighter(BASE_FIGHTER | {"main_weapon": "Garras de Combate Eshin"})
    assert hammer[6] == WEAPON_SIGMARITE_HAMMER
    assert _attack_strength(hammer, WEAPON_SIGMARITE_HAMMER, False) == 4
    assert _attack_strength(choppa, WEAPON_CHOPPA, False, True) == 4
    assert _attack_strength(choppa, WEAPON_CHOPPA, False, False) == 3
    assert claws[6] == WEAPON_ESHIN_CLAWS
    assert claws[7] == OFF_NONE


def test_two_handed_and_paired_weapons_disable_offhand():
    for weapon in ("Mayal", "Pica", "Bagh Nakh", "Puños de Bronce"):
        fighter = _make_fighter(
            BASE_FIGHTER | {"main_weapon": weapon, "off_hand": "Espada"}
        )
        assert fighter[7] == OFF_NONE


def test_revised_spear_and_two_handed_shield_rules():
    spear = _make_fighter(BASE_FIGHTER | {"main_weapon": "Lanza", "off_hand": "Espada"})
    two_handed = _make_fighter(
        BASE_FIGHTER | {"main_weapon": "Arma 2H", "off_hand": "Escudo"}
    )
    assert spear[7] == OFF_NONE
    assert _make_fighter(
        BASE_FIGHTER | {"main_weapon": "Lanza", "off_hand": "Escudo"}
    )[8] == 6
    assert _make_fighter(
        BASE_FIGHTER | {"main_weapon": "Lanza", "off_hand": "Rodela"}
    )[7] == OFF_BUCKLER
    assert two_handed[8] == 7


def test_morning_star_only_accepts_a_shield_in_the_other_hand():
    invalid = _make_fighter(
        BASE_FIGHTER | {"main_weapon": "Mangual", "off_hand": "Espada"}
    )
    shield = _make_fighter(
        BASE_FIGHTER | {"main_weapon": "Mangual", "off_hand": "Escudo"}
    )
    buckler = _make_fighter(
        BASE_FIGHTER | {"main_weapon": "Mangual", "off_hand": "Rodela"}
    )
    assert invalid[7] == OFF_NONE
    assert shield[7] == OFF_SHIELD
    assert buckler[7] == OFF_NONE


def test_corrected_exclusive_weapon_hand_rules():
    witch_blade = _make_fighter(
        BASE_FIGHTER | {"off_hand": "Espada Bruja"}
    )
    sigmarite = _make_fighter(
        BASE_FIGHTER | {
            "main_weapon": "Martillo Sigmarita",
            "off_hand": "Espada",
        }
    )
    assert witch_blade[7] == WEAPON_WITCH_BLADE
    assert sigmarite[7] == WEAPON_SWORD


def test_beastmaster_whip_does_not_grant_global_attack_first():
    whip = _make_fighter(
        BASE_FIGHTER | {"main_weapon": "Látigo de Señor de las Bestias"}
    )
    assert not _weapon_attacks_first(whip[6])


def test_choppa_only_accepts_shield_or_spiked_gauntlet():
    invalid = _make_fighter(
        BASE_FIGHTER | {"main_weapon": "Rebanadora", "off_hand": "Espada"}
    )
    shield = _make_fighter(
        BASE_FIGHTER | {"main_weapon": "Rebanadora", "off_hand": "Escudo"}
    )
    gauntlet = _make_fighter(
        BASE_FIGHTER | {
            "main_weapon": "Rebanadora",
            "off_hand": "Guantelete con Pincho",
        }
    )
    assert invalid[7] == OFF_NONE
    assert shield[7] == OFF_SHIELD
    assert shield[8] == 6
    assert gauntlet[7] == WEAPON_SPIKED_GAUNTLET


def test_buckler_parries_without_granting_armour_or_an_attack():
    fighter = _make_fighter(BASE_FIGHTER | {"off_hand": "Rodela"})
    assert fighter[7] == OFF_BUCKLER
    assert fighter[8] == 7
    assert _parry_profile(fighter) == (1, True)


def test_new_manual_weapon_profiles_are_encoded():
    pistol = _make_fighter(BASE_FIGHTER | {"main_weapon": "Pistola"})
    duel = _make_fighter(BASE_FIGHTER | {"main_weapon": "Pistola de Duelo"})
    daggers = _make_fighter(BASE_FIGHTER | {"main_weapon": "Dagas Envenenadas"})
    sun = _make_fighter(BASE_FIGHTER | {"off_hand": "Guantelete Solar"})
    draich = _make_fighter(BASE_FIGHTER | {"main_weapon": "Draich"})
    death = _make_fighter(BASE_FIGHTER | {"main_weapon": "Cuchillo de Muerte"})
    assert pistol[6] == WEAPON_PISTOL
    assert duel[6] == WEAPON_DUELING_PISTOL
    assert daggers[6] == WEAPON_POISONED_DAGGERS
    assert _poison_for_attack(daggers, 0) == POISON_BLACK_LOTUS
    assert sun[7] == WEAPON_SUN_GAUNTLET
    assert _attack_strength(draich, WEAPON_DRAICH, False) == 5
    assert _attack_strength(death, WEAPON_DEATH_KNIFE, False) == 2
    assert _attack_strength(
        _make_fighter(BASE_FIGHTER | {"main_weapon": "Garfio Largo"}),
        WEAPON_LONG_HOOK,
        False,
    ) == 2


def test_additional_armour_profiles_use_their_melee_saves():
    assert _armor_base_save("Armadura de Ithilmar") == 5
    assert _armor_base_save("Cuero Endurecido") == 6
    assert _armor_base_save("Armadura de Placas") == 4
    assert _armor_base_save("Ropajes de Asesino Eshin") == 6


def test_pistols_only_add_their_melee_attack_in_the_first_round():
    offhand = _make_fighter(BASE_FIGHTER | {"off_hand": "Pistola"})
    main = _make_fighter(
        BASE_FIGHTER | {"main_weapon": "Pistola", "off_hand": "Espada"}
    )
    assert _phase_attack_count(offhand, True) == 2
    assert _phase_attack_count(offhand, False) == 1
    assert _phase_weapon_for_attack(main, 0, True) == WEAPON_SWORD
    assert _phase_weapon_for_attack(main, 1, True) == WEAPON_PISTOL
    assert _phase_weapon_for_attack(main, 0, False) == WEAPON_SWORD


def test_ball_and_chain_bundles_its_required_mushrooms_and_drops_other_gear():
    fighter = _make_fighter(
        BASE_FIGHTER | {
            "main_weapon": "Bola con Kadena",
            "off_hand": "Escudo",
            "armor": "Armadura Pesada",
            "has_helmet": True,
        }
    )
    assert fighter[6] == WEAPON_BALL_AND_CHAIN
    assert fighter[7] == OFF_NONE
    assert fighter[8] == 7
    assert fighter[10] == 0
    assert fighter[14] == PREPARATION_HEAD_SPLITTER
    assert _attack_strength(fighter, WEAPON_BALL_AND_CHAIN, False) == 5


def test_pirate_scourge_improves_enemy_armour_save():
    assert _nb_armour_save(7, WEAPON_PIRATE_SCOURGE) == 6


def test_double_blade_and_paired_parries_use_different_rules():
    double_blade = _make_fighter(
        BASE_FIGHTER | {"main_weapon": "Espada de Doble Hoja"}
    )
    eshin_claws = _make_fighter(
        BASE_FIGHTER | {"main_weapon": "Garras de Combate Eshin"}
    )
    two_swords = _make_fighter(
        BASE_FIGHTER | {"main_weapon": "Espada", "off_hand": "Espada"}
    )
    weeping_blades = _make_fighter(
        BASE_FIGHTER | {"main_weapon": "Espadas Supurantes"}
    )
    assert _parry_profile(double_blade) == (2, False)
    assert _parry_profile(eshin_claws) == (1, True)
    assert _parry_profile(two_swords) == (1, False)
    assert _parry_profile(weeping_blades) == (1, False)
    assert _extra_armour_penalty(eshin_claws, WEAPON_ESHIN_CLAWS) == 0


def test_priority_and_whip_attacks_keep_their_own_weapon():
    trident = _make_fighter(
        BASE_FIGHTER | {"main_weapon": "Espada", "off_hand": "Tridente"}
    )
    weapons, sources, kinds = _phase_attack_plan(trident, True)
    assert weapons == [WEAPON_SWORD, WEAPON_TRIDENT]
    assert sources == [0, BASE_FIGHTER["A"]]
    assert kinds == ["core", "core"]

    whip = _make_fighter(
        BASE_FIGHTER | {"main_weapon": "Espada", "off_hand": "Látigo Ofidio"}
    )
    weapons, sources, kinds = _phase_attack_plan(whip, True, include_whip=True)
    assert weapons == [WEAPON_SWORD, WEAPON_SERPENT_WHIP, WEAPON_SERPENT_WHIP]
    assert sources == [0, BASE_FIGHTER["A"], BASE_FIGHTER["A"]]
    assert kinds == ["core", "core", "whip"]
    assert not _weapon_attacks_first(WEAPON_SERPENT_WHIP)


def test_sun_gauntlet_is_only_encoded_in_the_secondary_hand():
    fighter = _make_fighter(BASE_FIGHTER | {"main_weapon": "Guantelete Solar"})
    assert fighter[6] == WEAPON_SUN_GAUNTLET
    assert fighter[7] == OFF_NONE


def test_heavy_weapon_bonus_expires_unless_tireless():
    flail = _make_fighter(BASE_FIGHTER | {"main_weapon": "Mayal"})
    tireless = _make_fighter(
        BASE_FIGHTER | {"main_weapon": "Mayal", "skills": ["Incansable"]}
    )
    assert _attack_strength(flail, WEAPON_FLAIL, False, True) == 5
    assert _attack_strength(flail, WEAPON_FLAIL, False, False) == 3
    assert _attack_strength(tireless, WEAPON_FLAIL, False, False) == 5


def test_weapon_materials_modify_combat_profile():
    gromril = _make_fighter(BASE_FIGHTER | {"main_weapon_material": "Gromril"})
    ithilmar = _make_fighter(BASE_FIGHTER | {"main_weapon_material": "Ithilmar"})
    obsidian = _make_fighter(BASE_FIGHTER | {"main_weapon_material": "Obsidiana"})
    assert _extra_armour_penalty(gromril, WEAPON_SWORD) == 1
    assert _combat_initiative(ithilmar) == BASE_FIGHTER["I"] + 1
    assert _attack_strength(obsidian, WEAPON_SWORD, False) == BASE_FIGHTER["F"] + 1


def test_offhand_material_only_affects_offhand_attacks():
    fighter = _make_fighter(
        BASE_FIGHTER | {
            "off_hand": "Espada",
            "main_weapon_material": "Sin material",
            "offhand_material": "Obsidiana",
        }
    )
    assert _attack_strength(fighter, WEAPON_SWORD, False, True, 0) == 3
    assert _attack_strength(fighter, WEAPON_SWORD, False, True, 1) == 4


def test_preparations_modify_the_compact_profile():
    crimson = _make_fighter(BASE_FIGHTER | {"preparations": ["Sombra Carmesí"]})
    mandrake = _make_fighter(BASE_FIGHTER | {"preparations": ["Raíz de Mandrágora"]})
    assert crimson[1] == BASE_FIGHTER["F"] + 1
    assert crimson[14] == PREPARATION_CRIMSON_SHADE
    assert mandrake[2] == BASE_FIGHTER["R"] + 1
    assert mandrake[14] == PREPARATION_MANDRAKE_ROOT


def test_multiple_preparations_accumulate_compatible_effects():
    combined = _make_fighter(BASE_FIGHTER | {
        "preparations": [
            "Sombra Carmesí", "Raíz de Mandrágora", "Lágrimas de Shallaya",
            "Hongos Sombrero Loco", "Hongos Pirakabezas",
        ],
    })
    assert combined[1] == BASE_FIGHTER["F"] + 1
    assert combined[2] == BASE_FIGHTER["R"] + 1
    assert combined[14] & PREPARATION_CRIMSON_SHADE
    assert combined[14] & PREPARATION_MANDRAKE_ROOT
    assert combined[14] & PREPARATION_MAD_CAP
    assert combined[14] & PREPARATION_HEAD_SPLITTER


def test_mushrooms_double_base_attacks_but_not_the_second_weapon():
    dual = _make_fighter(
        BASE_FIGHTER | {
            "A": 2,
            "off_hand": "Daga",
            "preparations": ["Hongos Sombrero Loco"],
        }
    )
    headsplitta = _make_fighter(
        BASE_FIGHTER | {"preparations": ["Hongos Pirakabezas"]}
    )
    assert dual[14] == PREPARATION_MAD_CAP
    assert headsplitta[14] == PREPARATION_HEAD_SPLITTER
    assert _phase_attack_count(dual, True, 0) == 3
    assert _phase_attack_count(dual, True, dual[5]) == 5


def test_black_venom_and_reptile_poison_have_different_penetration():
    black = _make_fighter(BASE_FIGHTER | {"main_poison": "Veneno Negro"})
    reptile = _make_fighter(BASE_FIGHTER | {"main_poison": "Veneno de Reptil"})
    assert black[15] == POISON_BLACK_VENOM
    assert reptile[15] == POISON_REPTILE
    assert _attack_strength(black, WEAPON_SWORD, False, True, 0) == 4
    assert _attack_strength(reptile, WEAPON_SWORD, False, True, 0) == 4
    assert _armour_strength(black, WEAPON_SWORD, True, 0) == 4
    assert _armour_strength(reptile, WEAPON_SWORD, True, 0) == 3


def test_weeping_blades_keep_their_permanent_black_lotus():
    blades = _make_fighter(
        BASE_FIGHTER
        | {"main_weapon": "Espadas Supurantes", "main_poison": "Veneno Negro"}
    )
    assert _poison_for_attack(blades, 0) == POISON_BLACK_LOTUS
