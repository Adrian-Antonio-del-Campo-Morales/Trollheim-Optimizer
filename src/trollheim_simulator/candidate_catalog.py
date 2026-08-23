"""Catálogo de candidatos construido a partir de la base canónica."""

from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path
import re
import sys
import unicodedata

import yaml

from .rules import (
    ARMORS,
    MAIN_HAND_FORBIDDEN_WEAPONS,
    OFF_HAND_OPTIONS,
    POISONS,
    PREPARATIONS,
    SKILLS,
    WEAPON_MATERIALS,
    WEAPONS_ALL,
)


CATEGORY_ORDER = ("combat", "shooting", "academic", "strength", "speed", "special")
CATEGORY_LABELS = {
    "combat": "Combate", "shooting": "Disparo", "academic": "Académicas",
    "strength": "Fuerza", "speed": "Velocidad", "special": "Especial",
}

GENERAL_SKILLS = {
    "combat": {
        "Combatiente Experto": "+1 a las tiradas para herir en cuerpo a cuerpo.",
        "Maestro en Combate": "+1 Ataque al combatir contra más de un enemigo.",
        "Entrenamiento Extensivo": "Permite utilizar cualquier arma de cuerpo a cuerpo.",
        "A Fondo": "+1 a la tirada de efecto del impacto crítico.",
        "Experto en Esgrima": "Repite fallos al cargar con espada o cimitarra.",
        "Echarse a un Lado": "Salvación especial de 5+ contra heridas cuerpo a cuerpo.",
        "Maestro del Hacha": "Permite parar con hachas normales.",
        "Desarmar": "Renuncia a los ataques para intentar inutilizar un arma enemiga.",
        "Estocada Mortal": "Cambia todos los ataques por uno con +2 F que ataca último.",
        "Pugilista": "Combate desarmado sin penalización y obtiene un ataque adicional.",
        "Barrido": "Cambia los ataques por un impacto si el rival falla Iniciativa.",
        "Mover a Través": "Tras neutralizar a sus rivales puede efectuar un movimiento de 5 cm.",
        "Experto en Hachas": "Repite fallos para impactar con hachas al cargar.",
        "Golpe con el Escudo": "Obtiene un ataque adicional cuando combate con escudo.",
    },
    "shooting": {
        "Tiro Rápido": "Puede disparar dos veces si no se ha movido.",
        "Pistolero": "Puede disparar dos pistolas o pistolas de duelo.",
        "Vista de Águila": "+15 cm al alcance de las armas de proyectiles.",
        "Experto en Armas": "Permite utilizar cualquier arma de proyectiles.",
        "Ágil": "Permite mover y disparar con armas que normalmente no pueden hacerlo.",
        "Tirador Experto": "Ignora los modificadores por cobertura.",
        "Cazador": "Puede disparar cada turno con armas que normalmente deben recargarse.",
        "Lanzador Experto": "Puede lanzar hasta tres cuchillos o estrellas arrojadizas.",
        "Disparo Vital": "+1 en la tabla de críticos con armas de proyectiles.",
        "Artesano de Flechas": "+1 en la Tabla de Heridas al disparar con arco.",
        "Disparo Poderoso": "+1 F a los ataques efectuados con arco.",
        "Tirador de Clima Lluvioso": "Ignora los penalizadores de disparo por lluvia.",
    },
    "academic": {
        "Lenguaje de Batalla": "El jefe aumenta 15 cm el alcance de su regla Jefe.",
        "Hechicería": "+1 a las tiradas para lanzar hechizos.",
        "Contactos": "+2 para encontrar objetos raros.",
        "Regatear": "Reduce el precio de un objeto en cada visita al mercado.",
        "Conocimientos Arcanos": "Permite aprender Magia Menor con un Tomo de Magia.",
        "Buscador de Piedra Bruja": "Permite repetir un dado de exploración.",
        "Hechicero Guerrero": "Permite llevar armadura y lanzar hechizos.",
        "Escriba": "Permite preparar un pergamino con un hechizo o plegaria.",
        "Enfoque Mental": "Permite repetir una tirada de lanzamiento de hechizo.",
        "Táctico": "El líder puede recolocar guerreros después del despliegue rival.",
        "Corazonada": "El líder puede desplegar hasta tres guerreros de forma avanzada.",
        "Aptitud Mágica": "Un hechicero puede intentar lanzar dos hechizos por turno.",
        "Conductor de Carros": "Permite conducir un carro eficazmente en combate.",
        "Conocimientos Elementales": "Permite aprender una lista elemental con el tomo adecuado.",
    },
    "strength": {
        "Golpe Poderoso": "+1 F en cuerpo a cuerpo.",
        "Luchador de Pozo": "+1 HA y +1 A dentro de edificios o ruinas.",
        "Curtido": "Resta 1 a la Fuerza de los impactos cuerpo a cuerpo recibidos.",
        "Temible": "El guerrero causa miedo.",
        "Fortachón": "Las armas a dos manos dejan de atacar últimas.",
        "Carga Imparable": "+1 HA durante la carga.",
        "Incansable": "Mantiene el bonificador de Fuerza de las armas Pesadas.",
    },
    "speed": {
        "Salto": "Permite efectuar un salto adicional durante el movimiento.",
        "Carrera": "Permite triplicar el Movimiento al correr o cargar.",
        "Acróbata": "Mejora saltos, caídas y cargas desde altura.",
        "Reflejos Felinos": "Al recibir una carga, el orden se decide por Iniciativa.",
        "En Pie de un Salto": "Ignora resultados de Derribado salvo excepciones.",
        "Esquivar": "Salvación de 5+ contra impactos de proyectiles.",
        "Escalar Superficies Verticales": "Permite escalar el doble del Movimiento sin chequeos.",
    },
}

GENERAL_SKILL_DESCRIPTIONS = {
    name: description for skills in GENERAL_SKILLS.values() for name, description in skills.items()
}
GENERAL_SKILL_CATEGORIES = {
    name: category for category, skills in GENERAL_SKILLS.items() for name in skills
}

# Un mismo objeto recibe nombres distintos entre listas. Aquí termina la poesía.
ITEM_TO_OPTION = {
    "dagger": "Daga", "sword": "Espada", "club": "Maza",
    "mace": "Maza", "hammer": "Maza", "hammer_or_mace": "Maza", "axe": "Hacha",
    "bronze_axe": "Hacha", "bronze_dagger": "Daga", "bronze_spear": "Lanza",
    "bronze_sword": "Espada", "sacrifice_dagger": "Daga",
    "flail": "Mayal", "morning_star": "Mangual", "halberd": "Alabarda",
    "spear": "Lanza", "great_weapon": "Arma 2H", "stone_axe": "Hacha de Piedra",
    "rapier": "Estoque", "pike": "Pica", "elven_greatsword": "Espada Élfica 2H",
    "ankus": "Ankus", "yambiya": "Yambiya", "katar": "Katar",
    "scythe": "Guadaña", "cutlass": "Alfanje", "scimitar": "Cimitarra",
    "great_scimitar": "Gran Cimitarra", "bagh_nakh": "Bagh Nakh",
    "sword_breaker": "Rompe Espadas", "pistol": "Pistola",
    "duelling_pistol": "Pistola de Duelo", "brazier_staff": "Vara Brasero",
    "brass_knuckles": "Puños de Bronce", "war_maul": "Mazo de Guerra",
    "double_blade_sword": "Espada de Doble Hoja", "dwarf_axe": "Hacha Enana",
    "trident": "Tridente", "spiked_gauntlet": "Guantelete con Pincho",
    "sigmarite_hammer": "Martillo Sigmarita", "steel_whip": "Látigo de Acero",
    "choppa": "Rebanadora", "fighting_claws": "Garras de Combate Eshin",
    "weeping_blades": "Espadas Supurantes", "serpent_staff": "Báculo de Serpiente",
    "chained_squig": "Garrapato Encadenado", "squig_prodder": "Pinchagarrapatos",
    "kusara_kama": "Kusara Kama", "witch_sword": "Espada Bruja",
    "long_boathook": "Garfio Largo", "scourge": "Azote Pirata", "bo": "Bo",
    "poisoned_daggers": "Dagas Envenenadas", "snake_whip": "Látigo Ofidio",
    "beastmaster_whip": "Látigo de Señor de las Bestias",
    "solar_gauntlet": "Guantelete Solar",
    "unholy_transformation_sword": "Espada de Transformación Impía",
    "stiletto": "Estilete", "ancestral_claw": "Garra de los Ancestrales",
    "draich": "Draich", "death_knife": "Cuchillo de Muerte",
    "plague_dagger": "Daga de Ponzoña", "censer": "Incensario",
    "ball_and_chain": "Bola con Kadena", "shield": "Escudo", "buckler": "Rodela",
    "two_handed_club": "Arma 2H", "chained_club": "Garrapato Encadenado",
    "weeping_dagger": "Daga de Ponzoña", "whip": "Látigo de Acero",
    "yari": "Yari (una mano)", "pursuer_style_skink_trident": "Tridente",
    "pursuer_style_witch_elf_spear": "Lanza",
    "pursuer_style_witch_elf_swords": "Espada",
    "light_armour": "Armadura Ligera", "heavy_armour": "Armadura Pesada",
    "gromril_armour": "Armadura de Gromril", "ithilmar_armour": "Armadura de Ithilmar",
    "hardened_leather": "Cuero Endurecido", "plate_armour": "Armadura de Placas",
    "wizard_robe": "Túnica de Mago", "mage_robes": "Túnica de Mago",
    "ninja_robes": "Ropajes de Ninja",
    "eshin_assassin_clothes": "Ropajes de Asesino Eshin",
    "spider_chitin_armour": "Armadura Kitinoza",
    "sea_dragon_cloak": "Capa de Dragón Marino", "helmet": "Casco",
    "bronze_helmet": "Casco",
}

EQUIPMENT_ITEM_TO_OPTION = {
    **ITEM_TO_OPTION,
    "lucky_charm": "Amuleto de la suerte",
    "mad_mushrooms": "Hongos Sombrero Loco",
    "mad_cap_mushrooms": "Hongos Pirakabezas",
    "crimson_shade": "Sombra Carmesí",
    "mandrake_root": "Raíz de Mandrágora",
    "tears_of_shallaya": "Lágrimas de Shallaya",
    "black_lotus": "Loto Negro",
    "black_venom": "Veneno Negro",
    "dark_venom": "Veneno Negro",
    "reptile_venom": "Veneno de Reptil",
    "manbane": "Matahombres",
    "aconite": "Acónito",
    "nightshade": "Sombra Nocturna",
    "blood_root": "Raíz Sangrienta",
    "bloodroot": "Raíz Sangrienta",
    "devil_toxin": "Toxina del Diablo",
    "devils_toxin": "Toxina del Diablo",
    "spider_spittle": "Saliva de Araña",
}

SUPPORTED_EQUIPMENT_OPTIONS = frozenset({
    *(armor for armor in ARMORS if armor not in {"Sin Armadura", "Ropajes de Ninja"}),
    "Casco", "Amuleto de la suerte",
    *(value for value in PREPARATIONS if value != "Ninguno"),
    *(value for value in POISONS if value != "Sin veneno"),
})

MATERIAL_ITEMS = {
    "gromril_weapon": "Gromril", "ithilmar_weapon": "Ithilmar",
    "obsidian_weapon": "Obsidiana", "dark_steel_weapon": "Acero Oscuro",
}

COMPOSITE_ITEMS = {
    "pit_style_orc": ("Casco", "Daga", "Hacha", "Escudo"),
    "pit_style_undead": ("Casco", "Daga", "Guantelete con Pincho", "Espada"),
    "pit_style_empire": ("Casco", "Daga", "Arma 2H", "Armadura Ligera"),
    "pit_style_chaos": ("Casco", "Daga", "Mangual", "Armadura Ligera"),
    "pursuer_style_skink_trident": ("Casco", "Daga", "Tridente", "Rodela"),
    "pursuer_style_skink_javelin": ("Casco", "Daga", "Rodela"),
    "pursuer_style_witch_elf_swords": ("Casco", "Daga", "Espada"),
    "pursuer_style_witch_elf_spear": ("Casco", "Daga", "Lanza"),
}


@dataclass(frozen=True)
class CandidateProfile:
    band_id: str
    band_name: str
    profile_id: str
    name: str
    profile_type: str
    stats: dict[str, int]
    weapons: tuple[str, ...]
    armors: tuple[str, ...]
    defenses: tuple[str, ...]
    materials: tuple[str, ...]
    skills: tuple[str, ...]
    skills_by_category: dict[str, tuple[str, ...]]
    helmet_allowed: bool
    fixed_equipment: tuple[str, ...]
    restrictions: tuple[str, ...]
    rules: tuple[str, ...]
    source: dict


@dataclass(frozen=True)
class BandSkill:
    skill_id: str
    name: str
    description: str
    category: str = "special"
    access_tags: tuple[str, ...] = ("special",)


@dataclass(frozen=True)
class Band:
    band_id: str
    name: str
    profiles: tuple[CandidateProfile, ...]
    skills: tuple[BandSkill, ...]


def _knowledge_root() -> Path:
    candidates = []
    if getattr(sys, "frozen", False):
        candidates.append(Path(sys._MEIPASS) / "sources" / "knowledge" / "bands")
    candidates.extend((
        Path(__file__).resolve().parents[2] / "sources" / "knowledge" / "bands",
        Path(sys.prefix) / "share" / "trollheim_simulator" / "knowledge" / "bands",
    ))
    for candidate in candidates:
        if candidate.is_dir():
            return candidate
    raise FileNotFoundError("No se encuentra sources/knowledge/bands")


def _rule_text(rule) -> str:
    if isinstance(rule, dict):
        name = str(rule.get("name", "Regla"))
        effect = str(rule.get("effect", "")).strip()
        return f"{name}: {effect}" if effect else name
    return str(rule)


def _band_skills(raw_band: dict) -> tuple[BandSkill, ...]:
    result = []
    seen = set()
    for rule in raw_band.get("band_rules") or ():
        section = str((rule.get("source") or {}).get("section", "")).casefold()
        if "habil" not in section and "poder" not in section:
            continue
        name = str(rule.get("name", "Habilidad")).strip()
        if name.casefold() in seen:
            continue
        seen.add(name.casefold())
        access_tags = ("special",)
        if "poder" in section:
            tags = []
            for marker, tag in (
                ("von carstein", "von_carstein_powers"),
                ("dragón sangriento", "blood_dragon_powers"),
                ("necrarca", "necrarch_powers"),
                ("lahmia", "lahmia_powers"),
                ("strigoi", "strigoi_powers"),
            ):
                if marker in section:
                    tags.append(tag)
            access_tags = tuple(tags)
        result.append(BandSkill(
            str(rule.get("id", name)), name, str(rule.get("effect", "")),
            access_tags=access_tags,
        ))
    return tuple(result)


def _special_skill_allowed(skill: BandSkill, profile: dict) -> bool:
    text = skill.description.casefold()
    profile_name = str(profile.get("name", "")).casefold()
    rules = " ".join(
        f"{rule.get('id', '')} {rule.get('name', '')}" if isinstance(rule, dict) else str(rule)
        for rule in profile.get("rules") or ()
    ).casefold()
    if "solo el jefe" in text or "solo el jefe actual" in text:
        return "jefe" in rules or "leader" in rules
    explicit = {
        "solo maestro": ("maestro",),
        "solo el maestro del conocimiento": ("maestro del conocimiento",),
        "solo explorador": ("explorador",),
        "solo exploradores": ("explorador",),
        "solo matatrolls": ("matatrolls", "matador"),
        "solo capitán": ("capitán",),
        "solo khann": ("khann",),
        "solo sacerdote guerrero": ("sacerdote",),
        "solo la matriarca": ("matriarca",),
        "solo médiko brujo": ("médiko brujo",),
        "solo montarazes": ("montaraz",),
        "solo eslizones": ("eslizón",),
        "solo saurios": ("saurio",),
    }
    for marker, allowed_names in explicit.items():
        if marker in text:
            return any(name in profile_name for name in allowed_names)
    if skill.name == "Golpe Mortal":
        return int((profile.get("characteristics") or {}).get("A", 0)) >= 2
    if skill.name == "Constitución fuerte" and "hechicera" in profile_name:
        return False
    return True


def _general_skill_allowed(name: str, band: dict, profile: dict) -> bool:
    rules = profile.get("rules") or ()
    rule_text = " ".join(
        f"{rule.get('id', '')} {rule.get('name', '')}" if isinstance(rule, dict) else str(rule)
        for rule in rules
    ).casefold()
    is_leader = "jefe" in rule_text or "leader" in rule_text
    is_caster = any(word in rule_text for word in ("hechicero", "wizard", "sorcer", "brujo"))
    uses_prayers = any(word in rule_text for word in ("plegaria", "sacerdote", "priest"))
    if name in {"Lenguaje de Batalla", "Táctico", "Corazonada"}:
        return is_leader
    if name in {"Hechicería", "Hechicero Guerrero", "Aptitud Mágica"}:
        return is_caster
    if name in {"Escriba", "Enfoque Mental"}:
        return is_caster or uses_prayers
    if name == "Estocada Mortal":
        return int((profile.get("characteristics") or {}).get("A", 0)) > 1
    if name == "Conocimientos Arcanos":
        forbidden = ("Cazadores de Brujas", "Hermanas de Sigmar")
        return str(band.get("name", "")) not in forbidden and not uses_prayers
    return True


def _build_profile(band, profile, equipment_lists, band_skills) -> CandidateProfile:
    item_ids = []
    for list_id in profile.get("equipment_lists") or ():
        item_ids.extend(equipment_lists.get(list_id, ()))

    options = {ITEM_TO_OPTION[item] for item in item_ids if item in ITEM_TO_OPTION}
    for item in item_ids:
        options.update(COMPOSITE_ITEMS.get(item, ()))
    has_natural_attacks = not profile.get("equipment_lists") and (
        profile.get("fixed_equipment") or profile.get("equipment_restrictions")
    )
    if has_natural_attacks:
        options.add("Arma natural")
    weapons = tuple(option for option in WEAPONS_ALL if option in options)
    # El yari puede usarse de ambas formas aunque la lista lo compre una sola vez.
    if "Yari (una mano)" in options or "Yari (dos manos)" in options:
        weapons = tuple(dict.fromkeys((*weapons, "Yari (una mano)", "Yari (dos manos)")))
    armors = tuple(armor for armor in ARMORS if armor in options)
    materials = ("Sin material", *(material for item, material in MATERIAL_ITEMS.items() if item in item_ids))
    materials = tuple(material for material in WEAPON_MATERIALS if material in materials)

    skill_categories = set(profile.get("skill_access") or ())
    skills_by_category = {
        category: tuple(
            skill for skill in GENERAL_SKILLS.get(category, ())
            if _general_skill_allowed(skill, band, profile)
        )
        for category in CATEGORY_ORDER[:-1] if category in skill_categories
    }
    special_access = {
        category for category in skill_categories
        if "special" in category or category.endswith("_powers")
    }
    if special_access:
        skills_by_category["special"] = tuple(
            skill.name for skill in band_skills
            if _special_skill_allowed(skill, profile)
            and (
                "special" in skill.access_tags
                or bool(special_access.intersection(skill.access_tags))
            )
        )
    # Algunas bandas repiten como especial una habilidad general con el mismo
    # nombre (por ejemplo, Contactos). Se muestra una sola vez, conservando la
    # primera categoría canónica a la que tiene acceso el guerrero.
    seen_skills = set()
    for category in CATEGORY_ORDER:
        unique = tuple(
            skill for skill in skills_by_category.get(category, ())
            if skill not in seen_skills
        )
        if category in skills_by_category:
            skills_by_category[category] = unique
        seen_skills.update(unique)
    allowed_skills = tuple(
        name for category in CATEGORY_ORDER for name in skills_by_category.get(category, ())
    )
    characteristics = profile.get("characteristics") or {}
    stats = {
        "HA": int(characteristics.get("WS", 0)), "F": int(characteristics.get("S", 0)),
        "R": int(characteristics.get("T", 0)), "H": int(characteristics.get("W", 0)),
        "I": int(characteristics.get("I", 0)), "A": int(characteristics.get("A", 0)),
    }
    return CandidateProfile(
        band_id=str(band["id"]), band_name=str(band["name"]),
        profile_id=str(profile["id"]), name=str(profile["name"]),
        profile_type=str(profile.get("type", "warrior")), stats=stats,
        weapons=weapons, armors=armors,
        defenses=tuple(value for value in ("Escudo", "Rodela") if value in options),
        materials=materials,
        skills=allowed_skills,
        skills_by_category=skills_by_category,
        helmet_allowed="Casco" in options,
        fixed_equipment=tuple(str(value) for value in profile.get("fixed_equipment") or ()),
        restrictions=tuple(str(value) for value in profile.get("equipment_restrictions") or ()),
        rules=tuple(_rule_text(value) for value in profile.get("rules") or ()),
        source=dict(profile.get("source") or {}),
    )


@lru_cache(maxsize=1)
def load_bands() -> tuple[Band, ...]:
    bands = []
    for path in sorted(_knowledge_root().glob("*.yaml")):
        with path.open("r", encoding="utf-8") as stream:
            raw = yaml.safe_load(stream)
        equipment_lists = {
            entry["id"]: tuple(item["item_id"] for item in entry.get("items") or ())
            for entry in raw.get("equipment_lists") or ()
        }
        band_skills = _band_skills(raw)
        profiles = tuple(
            _build_profile(raw, profile, equipment_lists, band_skills)
            for profile in raw.get("profiles") or ()
        )
        bands.append(Band(str(raw["id"]), str(raw["name"]), profiles, band_skills))
    return tuple(sorted(bands, key=lambda band: band.name.casefold()))


def find_profile(band_id: str, profile_id: str) -> CandidateProfile | None:
    for band in load_bands():
        if band.band_id == band_id:
            return next((profile for profile in band.profiles if profile.profile_id == profile_id), None)
    return None


def _expected_cost(value) -> float | None:
    """Convierte costes con D6 a su valor esperado para comparaciones MOTTA."""
    if isinstance(value, (int, float)):
        return float(value)
    text = str(value).casefold().replace(" ", "").replace("×", "x")
    if re.fullmatch(r"\d+(?:[.,]\d+)?", text):
        return float(text.replace(",", "."))
    total = 0.0
    for term in text.split("+"):
        dice = re.fullmatch(r"(?:(\d+))?d6(?:x(\d+))?", term)
        if dice:
            amount = int(dice.group(1) or 1)
            multiplier = int(dice.group(2) or 1)
            total += amount * 3.5 * multiplier
            continue
        try:
            total += float(term)
        except ValueError:
            return None
    return total


def _profile_allows_equipment_item(item: dict, profile: dict) -> bool:
    notes = str(item.get("notes", "")).casefold()
    if "solo" not in notes or "solo durante" in notes:
        return True
    name = str(profile.get("name", "")).casefold()
    profile_type = str(profile.get("type", "")).casefold()
    rules = " ".join(
        f"{rule.get('id', '')} {rule.get('name', '')}"
        if isinstance(rule, dict) else str(rule)
        for rule in profile.get("rules") or ()
    ).casefold()
    if "solo héroes" in notes:
        return profile_type == "hero" or "corsario" in name
    if "solo jefe" in notes:
        return "jefe" in rules or "leader" in rules
    allowed_names = {
        "cazador silencioso": ("cazador silencioso",),
        "rufianes y matones": ("rufián", "rufian", "matón", "maton"),
        "médiko brujo": ("médiko brujo", "mediko brujo"),
        "sacerdote eslizón": ("sacerdote eslizón", "sacerdote eslizon"),
    }
    for marker, names in allowed_names.items():
        if marker in notes:
            return any(value in name for value in names)
    return True


def _global_misc_equipment_for_profile(band: dict, profile: dict) -> set[str]:
    """Equipo de mercado: los Héroes no están limitados a la lista de banda."""
    if str(profile.get("type", "")).casefold() != "hero":
        return set()
    context = f"{band.get('id', '')} {band.get('name', '')}".casefold()
    profile_name = str(profile.get("name", "")).casefold()
    options = {
        "Amuleto de la suerte", "Hongos Sombrero Loco", "Sombra Carmesí",
        "Raíz de Mandrágora", "Lágrimas de Shallaya", "Loto Negro",
        "Veneno Negro", "Veneno de Reptil", "Matahombres", "Acónito",
        "Sombra Nocturna", "Raíz Sangrienta", "Toxina del Diablo",
        "Saliva de Araña",
    }
    if "goblin" not in context and "goblin" not in profile_name:
        options.discard("Hongos Pirakabezas")
    if any(marker in context for marker in ("no-muertos", "no muertos", "poseídos", "poseidos")):
        options.discard("Lágrimas de Shallaya")
    if any(marker in context for marker in ("hermanas-de-sigmar", "hermanas de sigmar", "cazadores-de-brujas", "cazadores de brujas")):
        options.discard("Loto Negro")
        options.discard("Veneno Negro")
        options.discard("Matahombres")
    return options


@lru_cache(maxsize=None)
def equipment_options_for_profile(
    band_id: str = "", profile_id: str = "",
) -> tuple[str, ...]:
    if not band_id or not profile_id:
        return tuple(sorted(SUPPORTED_EQUIPMENT_OPTIONS, key=str.casefold))
    for path in sorted(_knowledge_root().glob("*.yaml")):
        with path.open("r", encoding="utf-8") as stream:
            raw = yaml.safe_load(stream)
        if str(raw.get("id", "")) != band_id:
            continue
        profile = next(
            (row for row in raw.get("profiles") or () if str(row.get("id", "")) == profile_id),
            None,
        )
        if profile is None:
            return ()
        lists = {
            row["id"]: row.get("items") or ()
            for row in raw.get("equipment_lists") or ()
        }
        allowed = set()
        for list_id in profile.get("equipment_lists") or ():
            for item in lists.get(list_id, ()):
                if not _profile_allows_equipment_item(item, profile):
                    continue
                option = EQUIPMENT_ITEM_TO_OPTION.get(item.get("item_id"))
                if option in SUPPORTED_EQUIPMENT_OPTIONS:
                    allowed.add(option)
                allowed.update(
                    value for value in COMPOSITE_ITEMS.get(item.get("item_id"), ())
                    if value in SUPPORTED_EQUIPMENT_OPTIONS
                )
        allowed.update(_global_misc_equipment_for_profile(raw, profile))
        return tuple(sorted(allowed, key=str.casefold))
    return ()


@lru_cache(maxsize=None)
def equipment_costs_for_profile(band_id: str = "", profile_id: str = "") -> dict[str, float]:
    """Devuelve costes por opción; usa la lista de banda si hay un perfil."""
    costs: dict[str, float] = {}
    if band_id and profile_id:
        for path in sorted(_knowledge_root().glob("*.yaml")):
            with path.open("r", encoding="utf-8") as stream:
                raw = yaml.safe_load(stream)
            if str(raw.get("id", "")) != band_id:
                continue
            profile = next(
                (row for row in raw.get("profiles") or () if str(row.get("id", "")) == profile_id),
                None,
            )
            if profile is None:
                break
            lists = {
                row["id"]: row.get("items") or ()
                for row in raw.get("equipment_lists") or ()
            }
            for list_id in profile.get("equipment_lists") or ():
                for item in lists.get(list_id, ()):
                    if not _profile_allows_equipment_item(item, profile):
                        continue
                    option = EQUIPMENT_ITEM_TO_OPTION.get(item.get("item_id"))
                    value = _expected_cost(item.get("cost"))
                    if option and value is not None:
                        costs[option] = min(costs.get(option, value), value)
            if "Yari (una mano)" in costs:
                costs["Yari (dos manos)"] = costs["Yari (una mano)"]
            return {**equipment_costs_for_profile(), **costs}

    catalog = _knowledge_root().parent / "catalog" / "market-prices.yaml"
    if catalog.is_file():
        with catalog.open("r", encoding="utf-8") as stream:
            raw = yaml.safe_load(stream)
        general = raw.get("general") or {}
        rows = (
            *general.get("melee_weapons", ()), *general.get("armour", ()),
            *general.get("drugs_and_poisons", ()),
        )
        for item in rows:
            option = EQUIPMENT_ITEM_TO_OPTION.get(item.get("id"))
            value = _expected_cost(item.get("cost"))
            if option and value is not None:
                costs[option] = value
        for section in (raw.get("lustria") or {}).values():
            if not isinstance(section, (list, tuple)):
                continue
            for item in section:
                option = EQUIPMENT_ITEM_TO_OPTION.get(item.get("id"))
                value = _expected_cost(item.get("cost"))
                if option and value is not None:
                    costs.setdefault(option, value)
    khemri_catalog = _knowledge_root().parent / "catalog" / "market-prices-khemri.yaml"
    if khemri_catalog.is_file():
        with khemri_catalog.open("r", encoding="utf-8") as stream:
            raw_khemri = yaml.safe_load(stream)
        for section in raw_khemri.values():
            if not isinstance(section, (list, tuple)):
                continue
            for item in section:
                if not isinstance(item, dict):
                    continue
                option = EQUIPMENT_ITEM_TO_OPTION.get(item.get("id"))
                value = _expected_cost(item.get("cost"))
                if option and value is not None:
                    costs.setdefault(option, value)
    costs.setdefault("Arma natural", 0.0)
    for path in sorted(_knowledge_root().glob("*.yaml")):
        with path.open("r", encoding="utf-8") as stream:
            band = yaml.safe_load(stream)
        for equipment_list in band.get("equipment_lists") or ():
            for item in equipment_list.get("items") or ():
                option = EQUIPMENT_ITEM_TO_OPTION.get(item.get("item_id"))
                value = _expected_cost(item.get("cost"))
                if option and option not in costs and value is not None:
                    costs[option] = value
    if "Yari (una mano)" in costs:
        costs["Yari (dos manos)"] = costs["Yari (una mano)"]
    return costs


def usable_main_weapons(profile: CandidateProfile) -> tuple[str, ...]:
    return tuple(weapon for weapon in profile.weapons if weapon not in MAIN_HAND_FORBIDDEN_WEAPONS)


def usable_offhand_options(profile: CandidateProfile) -> tuple[str, ...]:
    allowed = set(profile.weapons)
    allowed.update(profile.defenses)
    return tuple(option for option in OFF_HAND_OPTIONS if option == "Ninguna" or option in allowed)


@lru_cache(maxsize=1)
def weapon_descriptions() -> dict[str, str]:
    path = _knowledge_root().parent / "catalog" / "weapons.yaml"
    if not path.is_file():
        return {}
    with path.open("r", encoding="utf-8") as stream:
        records = yaml.safe_load(stream).get("records", ())
    descriptions = {str(row["name"]): str(row.get("rule_summary", "")) for row in records}
    aliases = {
        "Maza": "Maza, martillo o garrote",
        "Arma 2H": "Arma a dos manos",
        "Espada Élfica 2H": "Espada élfica a dos manos",
        "Pistola": "Pistola y pistola de duelo",
        "Pistola de Duelo": "Pistola y pistola de duelo",
        "Látigo de Señor de las Bestias": "Látigo del Señor de las Bestias",
        "Yari (una mano)": "Yari",
        "Yari (dos manos)": "Yari",
    }
    for target, source in aliases.items():
        if source in descriptions:
            descriptions[target] = descriptions[source]
    def normalized(value):
        value = unicodedata.normalize("NFKD", value).encode("ascii", "ignore").decode().casefold()
        return " ".join(value.replace("2h", "a dos manos").replace(" de ", " ").split())
    by_normalized = {normalized(name): description for name, description in descriptions.items()}
    for weapon in WEAPONS_ALL:
        descriptions.setdefault(weapon, by_normalized.get(normalized(weapon), ""))
    descriptions["Arma natural"] = (
        "Ataques innatos sin modificadores de arma; no ocupa una segunda mano."
    )
    return descriptions


@lru_cache(maxsize=1)
def armour_descriptions() -> dict[str, str]:
    path = _knowledge_root().parent / "catalog" / "armour-and-equipment.yaml"
    if not path.is_file():
        return {}
    with path.open("r", encoding="utf-8") as stream:
        records = yaml.safe_load(stream).get("records", ())
    return {str(row["name"]): str(row.get("rule_summary", "")) for row in records}
