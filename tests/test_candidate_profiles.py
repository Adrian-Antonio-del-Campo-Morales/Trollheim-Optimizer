from pathlib import Path

from openpyxl import load_workbook

from trollheim_simulator.candidate_catalog import find_profile, load_bands
from trollheim_simulator.workbooks import (
    DATA_SHEET,
    ENEMIES_SHEET,
    RESULTS_INDEX_SHEET,
    SUMMARY_SHEET,
    load_candidate_workbook,
    save_candidate_workbook,
)


def _payload():
    return {
        "config": {
            "candidate_name": "Rata con papeles",
            "candidate_band_id": "trollheim-skaven",
            "candidate_profile_id": "eshin-assassin",
            "HA": 4, "F": 4, "R": 3, "H": 1, "I": 5, "A": 1,
            "skills": ["Golpe Poderoso"], "main_weapon": "Espada",
            "off_hand": "Daga", "main_weapon_material": "Sin material",
            "offhand_material": "Sin material", "armor": "Armadura Ligera",
            "has_helmet": True,
        },
        "candidate": {
            "name": "Rata con papeles", "band_name": "Skaven del Clan Eshin",
            "profile_name": "Asesino", "profile_type": "hero",
            "rules": ["Luchador Consumado: -1 adicional a la salvación."],
        },
        "opponent": {"mode": "Muestra aleatoria", "level": 2, "description": "Baja, Media"},
        "enemies": {
            "mode": "custom", "level": 2, "difficulties": [],
            "profiles": [
                {
                    "enemy_name": "Bruto", "HA": 3, "F": 4, "R": 4,
                    "H": 1, "I": 2, "A": 1, "skills": [],
                    "main_weapon": "Maza", "off_hand": "Ninguna",
                    "main_weapon_material": "Sin material",
                    "offhand_material": "Sin material", "armor": "Sin Armadura",
                    "has_helmet": False,
                },
                {
                    "enemy_name": "Rápido", "HA": 4, "F": 3, "R": 3,
                    "H": 1, "I": 5, "A": 2, "skills": ["Reflejos Felinos"],
                    "main_weapon": "Espada", "off_hand": "Daga",
                    "main_weapon_material": "Sin material",
                    "offhand_material": "Sin material", "armor": "Armadura Ligera",
                    "has_helmet": True,
                },
            ],
        },
    }


def test_canonical_candidate_catalog_is_complete():
    bands = load_bands()
    assert len(bands) == 34
    assert sum(len(band.profiles) for band in bands) == 222
    assassin = find_profile("trollheim-skaven", "eshin-assassin")
    assert assassin.stats == {"HA": 4, "F": 4, "R": 3, "H": 1, "I": 5, "A": 1}
    assert {"Espada", "Daga", "Mayal", "Lanza", "Alabarda"} <= set(assassin.weapons)
    assert "Armadura Ligera" in assassin.armors
    assert assassin.helmet_allowed
    assert "Golpe Poderoso" in assassin.skills


def test_natural_profiles_receive_a_neutral_natural_weapon():
    rat_ogre = find_profile("trollheim-skaven", "rat-ogre")
    assert rat_ogre.weapons == ("Arma natural",)
    assert not rat_ogre.armors
    assert not rat_ogre.skills


def test_band_skills_are_contextual_and_profile_access_is_respected():
    bands = load_bands()
    skaven = next(band for band in bands if band.band_id == "trollheim-skaven")
    assert {"Hambre Negra", "Arte del Combate sin Armas"} <= {
        skill.name for skill in skaven.skills
    }
    assassin = find_profile("trollheim-skaven", "eshin-assassin")
    verminkin = find_profile("trollheim-skaven", "verminkin")
    assert "Hambre Negra" in assassin.skills
    assert "Hambre Negra" not in verminkin.skills


def test_high_elf_profiles_keep_distinct_skill_columns_and_restrictions():
    loremaster = find_profile("lustria-altos-elfos", "high-elf-loremaster")
    explorer = find_profile("lustria-altos-elfos", "high-elf-explorer")
    assert "academic" in loremaster.skills_by_category
    assert "shooting" not in loremaster.skills_by_category
    assert "shooting" in explorer.skills_by_category
    assert "academic" not in explorer.skills_by_category
    assert "Maestro de las runas" in loremaster.skills_by_category["special"]
    assert "Maestro de las runas" not in explorer.skills_by_category["special"]
    assert "Suerte" in explorer.skills_by_category["special"]
    assert "Suerte" not in loremaster.skills_by_category["special"]


def test_candidate_workbook_round_trip_and_preserves_result_sheets(tmp_path: Path):
    path = tmp_path / "candidato.xlsx"
    save_candidate_workbook(path, _payload())
    restored = load_candidate_workbook(path)
    assert restored["config"]["candidate_name"] == "Rata con papeles"
    assert [profile["enemy_name"] for profile in restored["enemies"]["profiles"]] == [
        "Bruto", "Rápido"
    ]

    workbook = load_workbook(path)
    assert workbook.sheetnames[:3] == [SUMMARY_SHEET, ENEMIES_SHEET, RESULTS_INDEX_SHEET]
    assert workbook[DATA_SHEET].sheet_state == "veryHidden"
    assert workbook[SUMMARY_SHEET]["A1"].value == "TROLLHEIM · FICHA DE SIMULACIÓN"
    assert workbook[SUMMARY_SHEET].auto_filter.ref is None
    enemy_values = [
        cell.value for row in workbook[ENEMIES_SHEET].iter_rows() for cell in row
    ]
    assert "ENEMIGO 1 · Bruto" in enemy_values
    assert "ENEMIGO 2 · Rápido" in enemy_values
    summary_values = [
        cell.value for row in workbook[SUMMARY_SHEET].iter_rows() for cell in row
    ]
    assert "CONSULTA RÁPIDA" in summary_values
    assert "Habilidad: Golpe Poderoso" in summary_values
    workbook.create_sheet("Mejoras 001")["A1"] = "resultado futuro"
    workbook.save(path)

    changed = _payload()
    changed["config"]["HA"] = 5
    save_candidate_workbook(path, changed)
    workbook = load_workbook(path, data_only=False)
    assert "Mejoras 001" in workbook.sheetnames
    assert workbook["Mejoras 001"]["A1"].value == "resultado futuro"
    assert load_candidate_workbook(path)["config"]["HA"] == 5
