"""Catálogo de perfiles, equipo y constantes del simulador."""

# Ajuste gordo. Bájalo para probar cosas sin quemar la CPU.

TOTAL_SIMULATIONS = 100_000

# Perfiles jugables

HEROES_DATABASE = {
    "Héroe Humano": {
        "M": 4, "HA": 4, "HP": 4, "F": 3, "R": 3,
        "H": 1, "I": 4, "A": 1, "Ld": 8
    },
    "Héroe Enano": {
        "M": 3, "HA": 5, "HP": 4, "F": 3, "R": 4,
        "H": 1, "I": 2, "A": 1, "Ld": 9
    },
    "Héroe Poseído": {
        "M": 5, "HA": 4, "HP": 0, "F": 4, "R": 4,
        "H": 2, "I": 4, "A": 2, "Ld": 7
    },
    "Troll": {
        "M": 6, "HA": 3, "HP": 1, "F": 5, "R": 4,
        "H": 3, "I": 1, "A": 3, "Ld": 4
    },
    "Héroe Elfo": {
        "M": 5, "HA": 5, "HP": 4, "F": 3, "R": 3,
        "H": 1, "I": 6, "A": 1, "Ld": 9
    },
    "Héroe Bárbaro": {
        "M": 4, "HA": 5, "HP": 3, "F": 4, "R": 4,
        "H": 1, "I": 5, "A": 1, "Ld": 8
    },
    "Héroe Asesino": {
        "M": 6, "HA": 4, "HP": 4, "F": 4, "R": 3,
        "H": 1, "I": 5, "A": 1, "Ld": 7
    },
}

HEROES_WEIGHTS = {
    "Héroe Humano": 1.0,
    "Héroe Enano": 0.5,
    "Héroe Poseído": 0.5,
    "Troll": 0.5,
    "Héroe Elfo": 0.5,
    "Héroe Bárbaro": 0.5,
    "Héroe Asesino": 0.5,
}


# Carne de cañón, monstruos y demás gente con malas intenciones

NORMAL_ENEMIES_DATABASE = {
    "Humano": {
        "M": 4, "HA": 3, "HP": 3, "F": 3, "R": 3,
        "H": 1, "I": 3, "A": 1, "Ld": 7
    },
    "Enano": {
        "M": 3, "HA": 4, "HP": 3, "F": 3, "R": 4,
        "H": 1, "I": 2, "A": 1, "Ld": 9
    },
    "Bestia": {
        "M": 5, "HA": 4, "HP": 3, "F": 4, "R": 4,
        "H": 1, "I": 3, "A": 1, "Ld": 7
    },
    "Orco": {
        "M": 4, "HA": 4, "HP": 3, "F": 3, "R": 4,
        "H": 1, "I": 3, "A": 1, "Ld": 7
    },
    "Elfo": {
        "M": 5, "HA": 4, "HP": 4, "F": 3, "R": 3,
        "H": 1, "I": 6, "A": 1, "Ld": 8
    },
    "Bárbaro": {
        "M": 4, "HA": 4, "HP": 3, "F": 3, "R": 3,
        "H": 1, "I": 4, "A": 1, "Ld": 7
    },
    "Lobo": {
        "M": 7, "HA": 4, "HP": 0, "F": 4, "R": 3,
        "H": 1, "I": 3, "A": 1, "Ld": 5
    },
    "Ogro": {
        "M": 6, "HA": 3, "HP": 2, "F": 4, "R": 4,
        "H": 3, "I": 2, "A": 3, "Ld": 7
    },
    "Vampiro": {
        "M": 6, "HA": 4, "HP": 4, "F": 4, "R": 4,
        "H": 2, "I": 5, "A": 2, "Ld": 8
    },
    "Zombie": {
        "M": 4, "HA": 2, "HP": 0, "F": 3, "R": 3,
        "H": 1, "I": 1, "A": 1, "Ld": 5
    },
    "Rata": {
        "M": 5, "HA": 3, "HP": 3, "F": 3, "R": 3,
        "H": 1, "I": 4, "A": 1, "Ld": 5
    },
}

NORMAL_ENEMIES_WEIGHTS = {
    "Humano": 2.0,
    "Enano": 1.0,
    "Bestia": 1.0,
    "Orco": 1.0,
    "Elfo": 1.0,
    "Bárbaro": 1.0,
    "Lobo": 1.0,
    "Ogro": 1.0,
    "Vampiro": 1.0,
    "Zombie": 1.0,
    "Rata": 1.0,
}


ENEMIES_DATABASE = {
    **HEROES_DATABASE,
    **NORMAL_ENEMIES_DATABASE,
}

RACIAL_WEIGHTS = {
    **HEROES_WEIGHTS,
    **NORMAL_ENEMIES_WEIGHTS,
}


# Habilidades y equipo

SKILLS = [
    "Combatiente Experto",
    "A Fondo",
    "Experto en Esgrima",
    "Echarse a un Lado",
    "Golpe Poderoso",
    "Curtido",
    "Carga Imparable",
    "Reflejos Felinos",
    "En Pie de un Salto",
    "Fortachón",
    "Incansable",
    "Maestro del Hacha",
    "Experto en Hachas",
    "Golpe con el Escudo",
    "Barrido",
]

SKILL_DESCRIPTIONS = {
    "Combatiente Experto":
        "Suma +1 a la tirada para Herir.",
    "A Fondo":
        "Suma +1 a la tirada de la tabla de Impactos Críticos.",
    "Experto en Esgrima":
        "Permite repetir los ataques fallidos con espadas al cargar.",
    "Echarse a un Lado":
        "Otorga una tirada de salvación especial de 5+ no modificable.",
    "Golpe Poderoso":
        "Suma +1 a la Fuerza base del guerrero.",
    "Curtido":
        "Reduce en -1 la Fuerza efectiva de los ataques recibidos (mínimo F1).",
    "Carga Imparable":
        "Suma +1 a la Habilidad de Armas durante la carga.",
    "Reflejos Felinos":
        "Si recibe una carga, el orden de ataque se decide por Iniciativa.",
    "En Pie de un Salto":
        "Ignora los resultados de derribado, salvo los provocados por el casco.",
    "Fortachón":
        "Permite usar armas a dos manos sin atacar en último lugar.",
    "Incansable":
        "Mantiene en rondas posteriores la Fuerza de las armas Pesadas.",
    "Maestro del Hacha":
        "Permite parar ataques con hachas normales.",
    "Experto en Hachas":
        "Permite repetir los ataques fallidos con hachas al cargar.",
    "Golpe con el Escudo":
        "Concede un ataque adicional con Fuerza de usuario y mala penetración.",
    "Barrido":
        "Con un arma a dos manos, cambia todos los ataques por un impacto automático si el rival falla Iniciativa.",
}

WEAPONS_GENERAL = [
    "Espada",
    "Maza",
    "Daga",
    "Hacha",
    "Mayal",
    "Mangual",
    "Alabarda",
    "Lanza",
    "Arma 2H",
    "Hacha de Piedra",
    "Estoque",
    "Pica",
    "Espada Élfica 2H",
    "Ankus",
    "Yambiya",
    "Katar",
    "Guadaña",
    "Alfanje",
    "Cimitarra",
    "Gran Cimitarra",
    "Bagh Nakh",
    "Rompe Espadas",
    "Pistola",
    "Pistola de Duelo",
]

WEAPONS_EXCLUSIVE = [
    "Vara Brasero",
    "Puños de Bronce",
    "Mazo de Guerra",
    "Espada de Doble Hoja",
    "Hacha Enana",
    "Tridente",
    "Guantelete con Pincho",
    "Martillo Sigmarita",
    "Látigo de Acero",
    "Rebanadora",
    "Garras de Combate Eshin",
    "Espadas Supurantes",
    "Báculo de Serpiente",
    "Garrapato Encadenado",
    "Pinchagarrapatos",
    "Kusara Kama",
    "Espada Bruja",
    "Garfio Largo",
    "Azote Pirata",
    "Bo",
    "Dagas Envenenadas",
    "Látigo Ofidio",
    "Látigo de Señor de las Bestias",
    "Guantelete Solar",
    "Espada de Transformación Impía",
    "Estilete",
    "Garra de los Ancestrales",
    "Draich",
    "Yari (una mano)",
    "Yari (dos manos)",
    "Cuchillo de Muerte",
    "Daga de Ponzoña",
    "Incensario",
    "Bola con Kadena",
]

WEAPONS_MAIN = [*WEAPONS_GENERAL, *WEAPONS_EXCLUSIVE]

TWO_HANDED_WEAPONS = {
    "Arma 2H", "Mayal", "Alabarda", "Guadaña", "Pica",
    "Espada Élfica 2H", "Gran Cimitarra", "Vara Brasero",
    "Mazo de Guerra", "Espada de Doble Hoja", "Báculo de Serpiente",
    "Kusara Kama", "Garfio Largo", "Bo", "Draich", "Yari (dos manos)",
    "Incensario", "Bola con Kadena",
}

PAIRED_WEAPONS = {
    "Bagh Nakh", "Puños de Bronce", "Garras de Combate Eshin",
    "Espadas Supurantes", "Dagas Envenenadas",
}

# El mangual exige atención completa y no puede ir acompañado de otra arma ni
# rodelas. La lanza solo admite escudo o rodela. Rebanadora y Pinchagarrapatos
# tienen su propia excepción con escudo o guantelete.
OFFHAND_RESTRICTED_WEAPONS = {
    *TWO_HANDED_WEAPONS,
    *PAIRED_WEAPONS,
    "Mangual",
    "Lanza",
    "Rebanadora",
    "Pinchagarrapatos",
}

OFFHAND_GENERAL = [
    "Ninguna",
    "Escudo",
    "Rodela",
    *(weapon for weapon in WEAPONS_GENERAL if weapon not in OFFHAND_RESTRICTED_WEAPONS),
]

OFFHAND_EXCLUSIVE = [
    "Ninguna",
    *(weapon for weapon in WEAPONS_EXCLUSIVE if weapon not in OFFHAND_RESTRICTED_WEAPONS),
]

OFF_HAND_OPTIONS = list(dict.fromkeys([*OFFHAND_GENERAL, *OFFHAND_EXCLUSIVE]))

WEAPON_MATERIALS = ["Sin material", "Gromril", "Ithilmar", "Obsidiana", "Acero Oscuro"]

ARMORS = [
    "Sin Armadura",
    "Armadura Ligera",
    "Armadura Pesada",
    "Armadura de Gromril",
    "Armadura de Ithilmar",
    "Cuero Endurecido",
    "Armadura de Placas",
    "Túnica de Mago",
    "Ropajes de Ninja",
    "Ropajes de Asesino Eshin",
    "Armadura Kitinoza",
    "Capa de Dragón Marino",
]

PREPARATIONS = [
    "Ninguno",
    "Hongos Sombrero Loco",
    "Hongos Pirakabezas",
    "Sombra Carmesí",
    "Raíz de Mandrágora",
    "Lágrimas de Shallaya",
]

PREPARATION_DESCRIPTIONS = {
    "Ninguno": "Sin drogas ni antídotos.",
    "Hongos Sombrero Loco": "Furia asesina: duplica A hasta quedar Derribado o Aturdido.",
    "Hongos Pirakabezas": "Furia asesina; además permiten usar una Bola con Kadena.",
    "Sombra Carmesí": "+1 F y +1D3 I durante toda la batalla.",
    "Raíz de Mandrágora": "+1 R y los resultados de Aturdido pasan a Derribado.",
    "Lágrimas de Shallaya": "Inmunidad a todos los venenos durante la batalla.",
}

POISONS = [
    "Sin veneno",
    "Loto Negro",
    "Veneno Negro",
    "Veneno de Reptil",
    "Matahombres",
    "Acónito",
    "Sombra Nocturna",
    "Raíz Sangrienta",
    "Toxina del Diablo",
    "Saliva de Araña",
]

POISON_DESCRIPTIONS = {
    "Sin veneno": "El arma conserva sus reglas normales.",
    "Loto Negro": "Un 6 natural para impactar hiere automáticamente.",
    "Veneno Negro": "+1 F al herir y al calcular la penetración.",
    "Veneno de Reptil": "+1 F al herir, sin aumentar la penetración.",
    "Matahombres": "+1 a las tiradas para herir; un 1 natural siempre falla.",
    "Acónito": "Causa críticos con 5-6 cuando no necesita un 6 natural para herir.",
    "Sombra Nocturna": "Cada herida no salvada reduce la I rival en 1, hasta I1.",
    "Raíz Sangrienta": "Duplica las heridas causadas.",
    "Toxina del Diablo": "Repite tiradas para herir fallidas; la repetición no causa crítico.",
    "Saliva de Araña": "Al impactar, el rival chequea R o queda paralizado.",
}


# El motor trabaja con enteros para que los lotes sean compactos y rápidos.

WEAPON_SWORD = 0
WEAPON_MACE = 1
WEAPON_DAGGER = 2
WEAPON_2H = 3
WEAPON_AXE = 4
WEAPON_FLAIL = 5
WEAPON_MORNING_STAR = 6
WEAPON_HALBERD = 7
WEAPON_SPEAR = 8
WEAPON_STONE_AXE = 9
WEAPON_RAPIER = 10
WEAPON_PIKE = 11
WEAPON_ELVEN_2H = 12
WEAPON_ANKUS = 13
WEAPON_YAMBIYA = 14
WEAPON_KATAR = 15
WEAPON_SCYTHE = 16
WEAPON_CUTLASS = 17
WEAPON_SCIMITAR = 18
WEAPON_GREAT_SCIMITAR = 19
WEAPON_BAGH_NAKH = 20
WEAPON_SWORD_BREAKER = 21
WEAPON_BRAZIER_STAFF = 22
WEAPON_BRASS_KNUCKLES = 23
WEAPON_WAR_MAUL = 24
WEAPON_DOUBLE_BLADE = 25
WEAPON_DWARF_AXE = 26
WEAPON_TRIDENT = 27
WEAPON_SPIKED_GAUNTLET = 28
WEAPON_SIGMARITE_HAMMER = 29
WEAPON_STEEL_WHIP = 30
WEAPON_CHOPPA = 31
WEAPON_ESHIN_CLAWS = 32
WEAPON_WEEPING_BLADES = 33
WEAPON_SERPENT_STAFF = 34
WEAPON_CHAINED_SQUIG = 35
WEAPON_SQUIG_PROD = 36
WEAPON_KUSARA_KAMA = 37
WEAPON_WITCH_BLADE = 38
WEAPON_LONG_HOOK = 39
WEAPON_PIRATE_SCOURGE = 40
WEAPON_PISTOL = 41
WEAPON_DUELING_PISTOL = 42
WEAPON_BO = 43
WEAPON_POISONED_DAGGERS = 44
WEAPON_SERPENT_WHIP = 45
WEAPON_BEASTMASTER_WHIP = 46
WEAPON_SUN_GAUNTLET = 47
WEAPON_UNHOLY_SWORD = 48
WEAPON_STILETTO = 49
WEAPON_ANCESTRAL_CLAW = 50
WEAPON_DRAICH = 51
WEAPON_YARI_ONE = 52
WEAPON_YARI_TWO = 53
WEAPON_DEATH_KNIFE = 54
WEAPON_PLAGUE_DAGGER = 55
WEAPON_CENSER = 56
WEAPON_BALL_AND_CHAIN = 57

OFF_NONE = -1
OFF_SHIELD = -2
OFF_BUCKLER = -3
OFF_DAGGER = WEAPON_DAGGER
OFF_SWORD = WEAPON_SWORD
OFF_MACE = WEAPON_MACE

MATERIAL_NORMAL = 0
MATERIAL_GROMRIL = 1
MATERIAL_ITHILMAR = 2
MATERIAL_OBSIDIAN = 3
MATERIAL_DARK_STEEL = 4

ARMOR_NONE = 0
ARMOR_LIGHT = 1
ARMOR_HEAVY = 2
ARMOR_GROMRIL = 3
ARMOR_ITHILMAR = 4
ARMOR_HARDENED_LEATHER = 5
ARMOR_PLATE = 6
ARMOR_WIZARD_ROBE = 7
ARMOR_NINJA_GARB = 8
ARMOR_ESHIN_ROBES = 9
ARMOR_CHITIN = 10
ARMOR_SEA_DRAGON_CLOAK = 11

ARMOR_CODES = {
    "Sin Armadura": ARMOR_NONE,
    "Armadura Ligera": ARMOR_LIGHT,
    "Armadura Pesada": ARMOR_HEAVY,
    "Armadura de Gromril": ARMOR_GROMRIL,
    "Armadura de Ithilmar": ARMOR_ITHILMAR,
    "Cuero Endurecido": ARMOR_HARDENED_LEATHER,
    "Armadura de Placas": ARMOR_PLATE,
    "Túnica de Mago": ARMOR_WIZARD_ROBE,
    "Ropajes de Ninja": ARMOR_NINJA_GARB,
    "Ropajes de Asesino Eshin": ARMOR_ESHIN_ROBES,
    "Armadura Kitinoza": ARMOR_CHITIN,
    "Capa de Dragón Marino": ARMOR_SEA_DRAGON_CLOAK,
}

PREPARATION_NONE = 0
PREPARATION_CRIMSON_SHADE = 1
PREPARATION_MANDRAKE_ROOT = 2
PREPARATION_SHALLAYA_TEARS = 3
PREPARATION_MAD_CAP = 4
PREPARATION_HEAD_SPLITTER = 5

PREPARATION_CODES = {
    "Ninguno": PREPARATION_NONE,
    "Sombra Carmesí": PREPARATION_CRIMSON_SHADE,
    "Raíz de Mandrágora": PREPARATION_MANDRAKE_ROOT,
    "Lágrimas de Shallaya": PREPARATION_SHALLAYA_TEARS,
    "Hongos Sombrero Loco": PREPARATION_MAD_CAP,
    "Hongos Pirakabezas": PREPARATION_HEAD_SPLITTER,
}

POISON_NONE = 0
POISON_BLACK_LOTUS = 1
POISON_BLACK_VENOM = 2
POISON_REPTILE = 3
POISON_MANBANE = 4
POISON_WOLFSBANE = 5
POISON_NIGHTSHADE = 6
POISON_BLOODROOT = 7
POISON_DEVIL_TOXIN = 8
POISON_SPIDER_SPIT = 9

POISON_CODES = {
    "Sin veneno": POISON_NONE,
    "Loto Negro": POISON_BLACK_LOTUS,
    "Veneno Negro": POISON_BLACK_VENOM,
    "Veneno de Reptil": POISON_REPTILE,
    "Matahombres": POISON_MANBANE,
    "Acónito": POISON_WOLFSBANE,
    "Sombra Nocturna": POISON_NIGHTSHADE,
    "Raíz Sangrienta": POISON_BLOODROOT,
    "Toxina del Diablo": POISON_DEVIL_TOXIN,
    "Saliva de Araña": POISON_SPIDER_SPIT,
}

WEAPON_CODES = {
    "Espada": WEAPON_SWORD,
    "Maza": WEAPON_MACE,
    "Daga": WEAPON_DAGGER,
    "Arma 2H": WEAPON_2H,
    "Hacha": WEAPON_AXE,
    "Mayal": WEAPON_FLAIL,
    "Mangual": WEAPON_MORNING_STAR,
    "Alabarda": WEAPON_HALBERD,
    "Lanza": WEAPON_SPEAR,
    "Hacha de Piedra": WEAPON_STONE_AXE,
    "Estoque": WEAPON_RAPIER,
    "Pica": WEAPON_PIKE,
    "Espada Élfica 2H": WEAPON_ELVEN_2H,
    "Ankus": WEAPON_ANKUS,
    "Yambiya": WEAPON_YAMBIYA,
    "Katar": WEAPON_KATAR,
    "Guadaña": WEAPON_SCYTHE,
    "Alfanje": WEAPON_CUTLASS,
    "Cimitarra": WEAPON_SCIMITAR,
    "Gran Cimitarra": WEAPON_GREAT_SCIMITAR,
    "Bagh Nakh": WEAPON_BAGH_NAKH,
    "Rompe Espadas": WEAPON_SWORD_BREAKER,
    "Vara Brasero": WEAPON_BRAZIER_STAFF,
    "Puños de Bronce": WEAPON_BRASS_KNUCKLES,
    "Mazo de Guerra": WEAPON_WAR_MAUL,
    "Espada de Doble Hoja": WEAPON_DOUBLE_BLADE,
    "Hacha Enana": WEAPON_DWARF_AXE,
    "Tridente": WEAPON_TRIDENT,
    "Guantelete con Pincho": WEAPON_SPIKED_GAUNTLET,
    "Martillo Sigmarita": WEAPON_SIGMARITE_HAMMER,
    "Látigo de Acero": WEAPON_STEEL_WHIP,
    "Rebanadora": WEAPON_CHOPPA,
    "Garras de Combate Eshin": WEAPON_ESHIN_CLAWS,
    "Espadas Supurantes": WEAPON_WEEPING_BLADES,
    "Báculo de Serpiente": WEAPON_SERPENT_STAFF,
    "Garrapato Encadenado": WEAPON_CHAINED_SQUIG,
    "Pinchagarrapatos": WEAPON_SQUIG_PROD,
    "Kusara Kama": WEAPON_KUSARA_KAMA,
    "Espada Bruja": WEAPON_WITCH_BLADE,
    "Garfio Largo": WEAPON_LONG_HOOK,
    "Azote Pirata": WEAPON_PIRATE_SCOURGE,
    "Pistola": WEAPON_PISTOL,
    "Pistola de Duelo": WEAPON_DUELING_PISTOL,
    "Bo": WEAPON_BO,
    "Dagas Envenenadas": WEAPON_POISONED_DAGGERS,
    "Látigo Ofidio": WEAPON_SERPENT_WHIP,
    "Látigo de Señor de las Bestias": WEAPON_BEASTMASTER_WHIP,
    "Guantelete Solar": WEAPON_SUN_GAUNTLET,
    "Espada de Transformación Impía": WEAPON_UNHOLY_SWORD,
    "Estilete": WEAPON_STILETTO,
    "Garra de los Ancestrales": WEAPON_ANCESTRAL_CLAW,
    "Draich": WEAPON_DRAICH,
    "Yari (una mano)": WEAPON_YARI_ONE,
    "Yari (dos manos)": WEAPON_YARI_TWO,
    "Cuchillo de Muerte": WEAPON_DEATH_KNIFE,
    "Daga de Ponzoña": WEAPON_PLAGUE_DAGGER,
    "Incensario": WEAPON_CENSER,
    "Bola con Kadena": WEAPON_BALL_AND_CHAIN,
}

OFFHAND_CODES = {
    "Ninguna": OFF_NONE,
    "Escudo": OFF_SHIELD,
    "Rodela": OFF_BUCKLER,
}
OFFHAND_CODES.update(
    {
        weapon: WEAPON_CODES[weapon]
        for weapon in OFF_HAND_OPTIONS
        if weapon not in OFFHAND_CODES
    }
)

MATERIAL_CODES = {
    "Sin material": MATERIAL_NORMAL,
    "Normal": MATERIAL_NORMAL,
    "Gromril": MATERIAL_GROMRIL,
    "Ithilmar": MATERIAL_ITHILMAR,
    "Obsidiana": MATERIAL_OBSIDIAN,
    "Acero Oscuro": MATERIAL_DARK_STEEL,
}


# Una máscara por habilidad; así el kernel no carga listas ni diccionarios.
SKILL_EXPERT = 1 << 0
SKILL_CHARGE = 1 << 1
SKILL_SIDESTEP = 1 << 2
SKILL_POWER = 1 << 3
SKILL_SEASONED = 1 << 4
SKILL_FENCER = 1 << 5
SKILL_UNSTOPPABLE = 1 << 6
SKILL_CAT_REFLEXES = 1 << 7
SKILL_SPRING_UP = 1 << 8
SKILL_STRONGMAN = 1 << 9
SKILL_TIRELESS = 1 << 10
SKILL_AXE_MASTER = 1 << 11
SKILL_AXE_EXPERT = 1 << 12
SKILL_SHIELD_STRIKE = 1 << 13
SKILL_SWEEP = 1 << 14
