"""Perfiles representativos y equipo legal para los rivales aleatorios."""

DIFFICULTIES = ("Baja", "Media", "Alta")


def _profile(difficulty, weight, bands, equipment, **stats):
    return {
        **stats,
        "difficulty": difficulty,
        "weight": float(weight),
        "bands": bands,
        "equipment": equipment,
    }


# Coste y rareza sólo intervienen en la elección aleatoria. Un valor de rareza
# cero representa un objeto común; cuanto más alto, menos acaba saliendo del saco.
COMMON_HUMAN = {
    "main": [("Daga", 2, 0), ("Maza", 3, 0), ("Hacha", 5, 0),
             ("Espada", 10, 0), ("Lanza", 10, 0), ("Alabarda", 10, 0),
             ("Arma 2H", 15, 0), ("Mayal", 15, 0), ("Pistola", 15, 0),
             ("Pistola de Duelo", 30, 10)],
    "off": [("Ninguna", 0, 0), ("Daga", 2, 0), ("Maza", 3, 0),
            ("Hacha", 5, 0), ("Espada", 10, 0), ("Escudo", 5, 0),
            ("Rodela", 5, 0), ("Pistola", 15, 0)],
    "armor": [("Sin Armadura", 0, 0), ("Armadura Ligera", 20, 0),
              ("Armadura Pesada", 50, 0), ("Armadura de Ithilmar", 90, 11),
              ("Armadura de Placas", 80, 9)],
    "helmet": (10, 0),
    "consumables": [
        ("preparation", "Sombra Carmesí", 39, 8),
        ("preparation", "Raíz de Mandrágora", 29, 9),
        ("preparation", "Lágrimas de Shallaya", 17, 12),
        ("poison", "Loto Negro", 14, 9),
        ("poison", "Veneno Negro", 37, 8),
    ],
}

LIGHT_HUMAN = {
    **COMMON_HUMAN,
    "main": [("Daga", 2, 0), ("Maza", 3, 0), ("Hacha", 5, 0),
             ("Espada", 10, 0), ("Lanza", 10, 0)],
    "armor": [("Sin Armadura", 0, 0), ("Armadura Ligera", 20, 0)],
}

DWARF = {
    "main": [("Maza", 3, 0), ("Hacha", 5, 0), ("Espada", 10, 0),
             ("Arma 2H", 15, 0), ("Hacha Enana", 15, 8)],
    "off": [("Ninguna", 0, 0), ("Daga", 2, 0), ("Maza", 3, 0),
            ("Hacha", 5, 0), ("Escudo", 5, 0), ("Hacha Enana", 15, 8)],
    "armor": [("Sin Armadura", 0, 0), ("Armadura Ligera", 20, 0),
              ("Armadura Pesada", 50, 0), ("Armadura de Gromril", 150, 9)],
    "helmet": (10, 0),
}

SKAVEN = {
    "main": [("Daga", 2, 0), ("Maza", 3, 0), ("Espada", 10, 0),
             ("Lanza", 10, 0), ("Garras de Combate Eshin", 35, 8),
             ("Espadas Supurantes", 50, 10), ("Daga de Ponzoña", 10, 6),
             ("Incensario", 40, 9), ("Yari (una mano)", 10, 6),
             ("Yari (dos manos)", 15, 7), ("Cuchillo de Muerte", 20, 8)],
    "off": [("Ninguna", 0, 0), ("Daga", 2, 0), ("Espada", 10, 0),
            ("Escudo", 5, 0)],
    "armor": [("Sin Armadura", 0, 0), ("Armadura Ligera", 20, 0),
              ("Ropajes de Asesino Eshin", 50, 10)],
    "helmet": (10, 0),
    "consumables": [
        ("poison", "Loto Negro", 14, 7),
        ("poison", "Veneno Negro", 37, 8),
        ("poison", "Toxina del Diablo", 22, 7),
        ("poison", "Matahombres", 37, 9),
    ],
}

ORC = {
    "main": [("Daga", 2, 0), ("Maza", 3, 0), ("Hacha", 5, 0),
             ("Espada", 10, 0), ("Lanza", 10, 0), ("Rebanadora", 15, 0),
             ("Arma 2H", 15, 0), ("Garrapato Encadenado", 10, 0),
             ("Pinchagarrapatos", 15, 0)],
    "off": [("Ninguna", 0, 0), ("Daga", 2, 0), ("Maza", 3, 0),
            ("Hacha", 5, 0), ("Escudo", 5, 0)],
    "armor": [("Sin Armadura", 0, 0), ("Armadura Ligera", 20, 0),
              ("Armadura Pesada", 50, 0)],
    "helmet": (10, 0),
    "consumables": [
        ("poison", "Loto Negro", 14, 7),
        ("poison", "Veneno Negro", 37, 6),
        ("poison", "Toxina del Diablo", 22, 7),
    ],
}

GOBLIN = {
    **ORC,
    "main": [*ORC["main"], ("Bola con Kadena", 15, 0)],
}

SIGMAR = {
    **COMMON_HUMAN,
    "main": [("Maza", 3, 0), ("Mayal", 15, 0),
             ("Martillo Sigmarita", 15, 0), ("Látigo de Acero", 10, 0),
             ("Arma 2H", 15, 0)],
}

PIRATE = {
    **COMMON_HUMAN,
    "main": [("Daga", 2, 0), ("Maza", 3, 0), ("Hacha", 5, 0),
             ("Garfio Largo", 8, 0), ("Azote Pirata", 8, 0),
             ("Espada", 10, 0), ("Alfanje", 15, 0)],
}

LIZARD = {
    "main": [("Maza", 3, 0), ("Hacha", 5, 0), ("Lanza", 10, 0),
             ("Hacha de Piedra", 15, 0)],
    "off": [("Ninguna", 0, 0), ("Maza", 3, 0), ("Hacha", 5, 0),
            ("Escudo", 5, 0)],
    "armor": [("Sin Armadura", 0, 0), ("Armadura Ligera", 20, 0)],
    "helmet": (10, 0),
    "consumables": [
        ("poison", "Veneno de Reptil", 5, 0),
        ("poison", "Loto Negro", 14, 0),
        ("poison", "Veneno Negro", 37, 0),
        ("poison", "Sombra Nocturna", 19, 6),
        ("poison", "Matahombres", 37, 9),
    ],
}

UNARMED = {
    "main": [("Maza", 0, 0)],
    "off": [("Ninguna", 0, 0)],
    "armor": [("Sin Armadura", 0, 0)],
    "helmet": None,
}


# Los pesos no son porcentajes oficiales. Se obtienen agrupando perfiles iguales
# o casi iguales y combinando: apariciones en listas de banda, cupo permitido y
# condición de obligatorio/opcional. Así un guerrero de tropa pesa bastante más
# que el bicho gordo 0-1 que todo el mundo presume de llevar y luego no compra.
ENEMY_PROFILES = {
    "Recluta humano": _profile("Baja", 22, 12, LIGHT_HUMAN,
        HA=2, F=3, R=3, H=1, I=3, A=1),
    "Guerrero humano": _profile("Baja", 48, 18, COMMON_HUMAN,
        HA=3, F=3, R=3, H=1, I=3, A=1),
    "Tirador humano": _profile("Baja", 25, 13, LIGHT_HUMAN,
        HA=3, F=3, R=3, H=1, I=3, A=1),
    "Zelote o fanático novato": _profile("Baja", 13, 6, LIGHT_HUMAN,
        HA=2, F=3, R=3, H=1, I=3, A=1),
    "Goblin": _profile("Baja", 18, 5, GOBLIN,
        HA=2, F=3, R=3, H=1, I=3, A=1),
    "Eslizón": _profile("Baja", 14, 3, LIZARD,
        HA=2, F=3, R=2, H=1, I=4, A=1),
    "Zombi": _profile("Baja", 17, 4, UNARMED,
        HA=2, F=3, R=3, H=1, I=1, A=1),
    "Esqueleto": _profile("Baja", 13, 4, LIGHT_HUMAN,
        HA=2, F=3, R=3, H=1, I=2, A=1),
    "Rata gigante o alimaña menor": _profile("Baja", 14, 5, UNARMED,
        HA=2, F=3, R=3, H=1, I=4, A=1),

    "Veterano humano": _profile("Media", 24, 15, COMMON_HUMAN,
        HA=4, F=3, R=3, H=1, I=4, A=1),
    "Espadachín o duelista": _profile("Media", 12, 6, COMMON_HUMAN,
        HA=4, F=3, R=3, H=1, I=4, A=1, skills=["Experto en Esgrima"]),
    "Hermana de Sigmar": _profile("Media", 12, 2, SIGMAR,
        HA=4, F=3, R=3, H=1, I=4, A=1),
    "Guerrero enano": _profile("Media", 14, 5, DWARF,
        HA=4, F=3, R=4, H=1, I=2, A=1),
    "Orco": _profile("Media", 18, 5, ORC,
        HA=3, F=3, R=4, H=1, I=2, A=1),
    "Skaven": _profile("Media", 20, 5, SKAVEN,
        HA=3, F=3, R=3, H=1, I=4, A=1),
    "Elfo guerrero": _profile("Media", 10, 6, COMMON_HUMAN,
        HA=4, F=3, R=3, H=1, I=5, A=1),
    "Saurio": _profile("Media", 10, 2, LIZARD,
        HA=3, F=4, R=4, H=1, I=2, A=1),
    "Hombre bestia": _profile("Media", 11, 4, COMMON_HUMAN,
        HA=4, F=4, R=4, H=1, I=3, A=1),
    "Necrófago": _profile("Media", 12, 4, UNARMED,
        HA=3, F=3, R=4, H=1, I=3, A=2),
    "Lobo o felino de guerra": _profile("Media", 9, 6, UNARMED,
        HA=4, F=4, R=3, H=1, I=4, A=1),
    "Pirata": _profile("Media", 9, 1, PIRATE,
        HA=3, F=3, R=3, H=1, I=3, A=1),

    "Jefe humano": _profile("Alta", 10, 18, COMMON_HUMAN,
        HA=4, F=3, R=3, H=1, I=4, A=1),
    "Jefe enano": _profile("Alta", 5, 5, DWARF,
        HA=5, F=3, R=4, H=1, I=3, A=1),
    "Jefe orco": _profile("Alta", 5, 4, ORC,
        HA=4, F=4, R=4, H=1, I=3, A=1),
    "Asesino Skaven": _profile("Alta", 5, 4, SKAVEN,
        HA=4, F=4, R=3, H=1, I=5, A=2),
    "Héroe elfo": _profile("Alta", 5, 6, COMMON_HUMAN,
        HA=5, F=3, R=3, H=1, I=6, A=1),
    "Poseído": _profile("Alta", 5, 1, UNARMED,
        HA=4, F=4, R=4, H=2, I=4, A=2),
    "Vampiro": _profile("Alta", 4, 3, COMMON_HUMAN,
        HA=4, F=4, R=4, H=2, I=5, A=2),
    "Ogro": _profile("Alta", 4, 4, COMMON_HUMAN,
        HA=3, F=4, R=4, H=3, I=2, A=3),
    "Rata ogro": _profile("Alta", 3, 2, UNARMED,
        HA=3, F=5, R=4, H=3, I=4, A=3),
    "Troll": _profile("Alta", 2, 2, UNARMED,
        HA=3, F=5, R=4, H=3, I=1, A=3),
}


def profiles_for_difficulties(difficulties):
    selected = set(difficulties)
    return [name for name, profile in ENEMY_PROFILES.items()
            if profile["difficulty"] in selected]
