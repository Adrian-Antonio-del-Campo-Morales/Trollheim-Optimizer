"""Catálogo de perfiles, equipo y constantes del simulador."""

# Reglas opcionales que alteran globalmente una simulación. Las claves se
# guardan en los libros de Excel para que una partida pueda reproducirse.
HOUSE_RULES = {
    "anti_offhand": {
        "name": "Anti Arma Secundaria",
        "description": (
            "El ataque extra concedido por un arma secundaria sufre -1 a las "
            "tiradas para impactar."
        ),
    },
    "anti_dual": {
        "name": "Anti Dos Armas",
        "description": (
            "Mientras un guerrero combate con dos armas, todos sus ataques "
            "sufren -1 a las tiradas para impactar."
        ),
    },
    "cheap_armour": {
        "name": "Armaduras Baratas",
        "description": (
            "Armaduras, cascos, escudos y rodelas cuestan la mitad, redondeando "
            "hacia arriba."
        ),
    },
    "better_armour": {
        "name": "Armaduras Mejores",
        "description": "Todas las armaduras corporales otorgan +1 punto de armadura.",
    },
    "hard_armour": {
        "name": "Armaduras Duras",
        "description": (
            "La penetración de armadura debida a la Fuerza comienza en F5 en "
            "lugar de F4."
        ),
    },
    "useful_shields": {
        "name": "Escudos útiles",
        "description": (
            "Un escudo usado con un arma de mano otorga +1 punto de armadura "
            "adicional contra ataques cuerpo a cuerpo."
        ),
    },
    "expensive_junk": {
        "name": "Basura Cara",
        "description": "Las mazas y las hondas pasan a costar 5 co.",
    },
}

HOUSE_RULE_CONFIG_KEYS = {
    "anti_offhand": "house_rule_offhand_penalty",
    "anti_dual": "house_rule_dual_penalty",
    "cheap_armour": "house_rule_cheap_armour",
    "better_armour": "house_rule_better_armour",
    "hard_armour": "house_rule_hard_armour",
    "useful_shields": "house_rule_useful_shields",
    "expensive_junk": "house_rule_expensive_junk",
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
    "Carga Feroz",
    "Reflejos Felinos",
    "En Pie de un Salto",
    "Fortachón",
    "Incansable",
    "Maestro del Hacha",
    "Experto en Hachas",
    "Golpe con el Escudo",
    "Barrido",
    "Agilidad Élfica",
    "Agilidad élfica",
    "Armas del Norte",
    "Arte del Combate sin Armas",
    "Bíceps Muy Desarrollados",
    "El Arte del Combate sin Armas",
    "Furia Roja",
    "Fuerza del Acero",
    "Golpe Demoledor",
    "Golpe Infalible",
    "Infalible",
    "Ignorar el dolor",
    "Inocencia Perdida",
    "Inocencia Pérdida",
    "Maestro de la Espada",
    "Guerrero Imbatible",
    "Lucha con Cuchillo",
    "Maestría con el Escudo",
    "Machacabezas",
    "Maldición del Renacido",
    "Matador de Monstruos",
    "Miniath",
    "Monstruosidad",
    "Muy Duro",
    "Odio Infinito",
    "Postura Defensiva",
    "Piel endurecida",
    "Reflejos de Vampiro",
    "Rugido de batalla",
    "Sermón Estimulante",
    "Señal de Sigmar",
    "Tendones de Hierro",
    "Constitución resistente",
    "Cráneo de Piedra",
    "Duro como el Acero",
    "Enloquecido",
    "Kabezadura",
    "Suerte",
    "Virtud del Valor",
]

SKILL_DESCRIPTIONS = {
    "Combatiente Experto":
        "Suma +1 a la tirada para Herir.",
    "A Fondo":
        "Suma +1 a la tirada de la tabla de Impactos Críticos.",
    "Experto en Esgrima":
        "Permite repetir los ataques fallidos al cargar con espadas normales o cimitarras.",
    "Echarse a un Lado":
        "Otorga una tirada de salvación especial de 5+ no modificable.",
    "Golpe Poderoso":
        "Suma +1 a la Fuerza base del guerrero.",
    "Curtido":
        "Reduce en -1 la Fuerza efectiva de los ataques recibidos (mínimo F1).",
    "Carga Imparable":
        "Suma +1 a la Habilidad de Armas durante la carga.",
    "Carga Feroz": "Duplica los Ataques al cargar, con -1 para impactar ese turno.",
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
    "Agilidad Élfica": "Salvación especial de 6+ cuerpo a cuerpo; mejora a 4+ con Echarse a un Lado.",
    "Agilidad élfica": "Salvación especial de 6+ cuerpo a cuerpo; mejora a 4+ con Echarse a un Lado.",
    "Armas del Norte": "Repite las tiradas para impactar fallidas con hacha o arma a dos manos.",
    "Arte del Combate sin Armas": "Obtiene +1 Ataque al combatir desarmado o con garras.",
    "Bíceps Muy Desarrollados": "Mantiene el bonificador de Fuerza de las armas Pesadas.",
    "El Arte del Combate sin Armas": "Obtiene +1 Ataque al combatir desarmado o con garras.",
    "Furia Roja": "+1 Ataque.",
    "Fuerza del Acero": "+1 Fuerza durante la carga.",
    "Golpe Demoledor": "Sus ataques no pueden pararse.",
    "Golpe Infalible": "Repite las tiradas para herir fallidas.",
    "Infalible": "Repite las tiradas para impactar fallidas durante la carga.",
    "Ignorar el dolor": "Los resultados de Aturdido pasan a Derribado.",
    "Inocencia Perdida": "Ataca primero en cuerpo a cuerpo.",
    "Inocencia Pérdida": "Ataca primero en cuerpo a cuerpo.",
    "Maestro de la Espada": "Para igualando la tirada y repite una parada fallida.",
    "Guerrero Imbatible": "Mejora las paradas y permite dos con dos armas de Parada.",
    "Lucha con Cuchillo": "+1 HA y +1 en la Tabla de Heridas con daga o yambiya.",
    "Maestría con el Escudo": "El escudo permite parar y conserva su salvación.",
    "Machacabezas": "Convierte los resultados de Derribado que causa en Aturdido.",
    "Maldición del Renacido": "Regenera heridas no salvadas con 4+.",
    "Matador de Monstruos": "Hiere como mínimo con 4+.",
    "Miniath": "Repite una parada fallida cuando usa un arma con Parada.",
    "Monstruosidad": "+1 Herida.",
    "Muy Duro": "+1 a la salvación por armadura.",
    "Odio Infinito": "Repite las tiradas para impactar fallidas.",
    "Postura Defensiva": "Puede parar con cualquier arma; las armas con Parada igualan la tirada.",
    "Piel endurecida": "Solo queda fuera de combate con un 6 en la Tabla de Heridas.",
    "Reflejos de Vampiro": "Salvación especial de 6+ contra heridas.",
    "Rugido de batalla": "Los enemigos sufren -1 para impactar en la primera ronda.",
    "Sermón Estimulante": "+1 Ataque durante el turno.",
    "Señal de Sigmar": "No Muertos y Poseídos pierden un ataque en la primera ronda.",
    "Tendones de Hierro": "+1 Fuerza.",
    "Constitución resistente": "Ignora un impacto crítico con 5+.",
    "Cráneo de Piedra": "Convierte Aturdido en Derribado con 3+, o 2+ con Casco.",
    "Duro como el Acero": "Solo queda fuera de combate con un 6 en la Tabla de Heridas.",
    "Enloquecido": "+1 para impactar durante la carga.",
    "Kabezadura": "Convierte Aturdido en Derribado con 3+, o 2+ con Casco.",
    "Suerte": "Repite una tirada propia una vez por batalla.",
    "Virtud del Valor": "Repite para impactar contra enemigos con Fuerza superior.",
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
    "Arma natural",
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

MAIN_HAND_FORBIDDEN_WEAPONS = {"Guantelete Solar"}
WEAPONS_ALL = [*WEAPONS_GENERAL, *WEAPONS_EXCLUSIVE]
WEAPONS_MAIN = [
    weapon for weapon in WEAPONS_ALL
    if weapon not in MAIN_HAND_FORBIDDEN_WEAPONS
]

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
]

# La capa concede una tirada de salvación, pero es equipo especial y no una
# armadura corporal.
BODY_ARMORS = tuple(ARMORS)

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

EQUIPMENT_SELECTOR_OPTIONS = (
    "Casco",
    "Amuleto de la suerte",
    "Capa de Dragón Marino",
    *(value for value in PREPARATIONS if value != "Ninguno"),
)

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
WEAPON_NATURAL = 58
WEAPON_UNARMED = 59

OFF_NONE = -1
OFF_SHIELD = -2
OFF_BUCKLER = -3

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
}

PREPARATION_NONE = 0
PREPARATION_CRIMSON_SHADE = 1
PREPARATION_MANDRAKE_ROOT = 2
PREPARATION_SHALLAYA_TEARS = 4
PREPARATION_MAD_CAP = 8
PREPARATION_HEAD_SPLITTER = 16

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
    "Arma natural": WEAPON_NATURAL,
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
SKILL_ELVEN_AGILITY = 1 << 15
SKILL_NORTHERN_WEAPONS = 1 << 16
SKILL_UNARMED_ART = 1 << 17
SKILL_RED_FURY = 1 << 18
SKILL_UNPARRYABLE = 1 << 19
SKILL_REROLL_WOUNDS = 1 << 20
SKILL_IGNORE_PAIN = 1 << 21
SKILL_ALWAYS_FIRST = 1 << 22
SKILL_SWORD_MASTER = 1 << 23
SKILL_SHIELD_MASTERY = 1 << 24
SKILL_MINIATH = 1 << 25
SKILL_MONSTROUS = 1 << 26
SKILL_VERY_TOUGH = 1 << 27
SKILL_REROLL_HITS = 1 << 28
SKILL_DEFENSIVE_STANCE = 1 << 29
SKILL_VAMPIRE_REFLEXES = 1 << 30
SKILL_IRON_SINEWS = 1 << 31
SKILL_CHARGE_REROLL = 1 << 32
SKILL_HEAD_CRUSHER = 1 << 33
SKILL_REGENERATION = 1 << 34
SKILL_MONSTER_SLAYER = 1 << 35
SKILL_HARDENED_SKIN = 1 << 36
SKILL_CRITICAL_RESISTANCE = 1 << 37
SKILL_FEROCIOUS_CHARGE = 1 << 38
SKILL_CHARGE_STRENGTH = 1 << 39
SKILL_UNBEATABLE = 1 << 40
SKILL_KNIFE_FIGHT = 1 << 41
SKILL_BATTLE_ROAR = 1 << 42
SKILL_SIGMAR_SIGNAL = 1 << 43
SKILL_VALOUR = 1 << 44
SKILL_STONE_SKULL = 1 << 45
SKILL_LUCK = 1 << 46
