import numpy as np

from trollheim_simulator.engine import (
    STATE_KNOCKED_DOWN,
    STATE_OUT,
    STATE_STANDING,
    STATE_STUNNED,
    _can_parry,
    _make_fighter,
    _simulate_batch,
    _simulate_homogeneous_batch,
    _vector_injury,
)
from trollheim_simulator.rules import WEAPON_MACE, WEAPON_SWORD


def fighter(**changes):
    base = {
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
    return _make_fighter(base | changes)


class FixedRolls:
    def __init__(self, *rolls):
        self.rolls = iter(rolls)

    def integers(self, _low, _high, size):
        return np.full(size, next(self.rolls), dtype=np.int8)


def win_rate(attacker, defender, seed=123, simulations=20_000):
    wins, resolved = _simulate_homogeneous_batch(
        attacker, defender, simulations, np.random.default_rng(seed)
    )
    return wins / resolved


def test_attacks_with_double_strength_cannot_be_parried():
    assert _can_parry(5, 3)
    assert not _can_parry(6, 3)
    assert not _can_parry(7, 3)


def test_vector_injury_table_distinguishes_maces_from_swords():
    mace = _vector_injury(
        FixedRolls(2), 1, WEAPON_MACE, False, False, False, False, 0
    )
    sword = _vector_injury(
        FixedRolls(2), 1, WEAPON_SWORD, False, False, False, False, 0
    )
    out = _vector_injury(
        FixedRolls(6), 1, WEAPON_SWORD, False, False, False, False, 0
    )
    assert mace.tolist() == [STATE_STUNNED]
    assert sword.tolist() == [STATE_KNOCKED_DOWN]
    assert out.tolist() == [STATE_OUT]


def test_spring_up_does_not_cancel_a_helmet_knockdown():
    states = _vector_injury(
        FixedRolls(3, 4), 1, WEAPON_SWORD, True, True, False, False, 0
    )
    assert states.tolist() == [STATE_KNOCKED_DOWN]


def test_mandrake_knockdown_can_be_cancelled_by_spring_up():
    states = _vector_injury(
        FixedRolls(3), 1, WEAPON_SWORD, False, True, True, False, 0
    )
    assert states.tolist() == [STATE_STANDING]


def test_luck_amulet_reduces_the_attackers_win_rate():
    attacker = fighter(main_weapon="Maza")
    plain = fighter(HA=3, I=3, main_weapon="Maza")
    protected = fighter(
        HA=3, I=3, main_weapon="Maza", has_luck_amulet=True
    )
    assert win_rate(attacker, protected) < win_rate(attacker, plain)


def test_sigmarite_hammer_is_better_against_unholy_targets():
    attacker = fighter(main_weapon="Martillo Sigmarita")
    normal = fighter(R=4, HA=3, I=3, main_weapon="Maza")
    unholy = fighter(
        R=4, HA=3, I=3, main_weapon="Maza", undead_or_possessed=True
    )
    assert win_rate(attacker, unholy) > win_rate(attacker, normal) + 0.04


def test_chitin_armour_is_vulnerable_to_the_brazier_staff():
    attacker = fighter(main_weapon="Vara Brasero")
    light = fighter(H=2, HA=3, I=3, main_weapon="Maza", armor="Armadura Ligera")
    chitin = fighter(
        H=2, HA=3, I=3, main_weapon="Maza", armor="Armadura Kitinoza"
    )
    assert win_rate(attacker, chitin) > win_rate(attacker, light) + 0.03


def test_spider_spit_improves_the_poisoned_weapon():
    plain = fighter(A=2, main_weapon="Espada")
    poisoned = fighter(A=2, main_weapon="Espada", main_poison="Saliva de Araña")
    defender = fighter(HA=3, I=3, main_weapon="Maza")
    assert win_rate(poisoned, defender) > win_rate(plain, defender) + 0.02


def test_infallible_strike_improves_wound_rerolls():
    plain = fighter(F=2, main_weapon="Espada")
    infallible = fighter(F=2, main_weapon="Espada", skills=["Golpe Infalible"])
    defender = fighter(R=4, HA=3, I=3, main_weapon="Maza")
    assert win_rate(infallible, defender) > win_rate(plain, defender) + 0.04


def test_elven_agility_reduces_enemy_win_rate():
    attacker = fighter(A=2, main_weapon="Maza")
    plain = fighter(HA=3, I=3, main_weapon="Espada")
    agile = fighter(HA=3, I=3, main_weapon="Espada", skills=["Agilidad élfica"])
    assert win_rate(attacker, agile) < win_rate(attacker, plain) - 0.02


def test_unwinnable_duel_is_excluded_from_results():
    candidate = fighter(HA=1, F=1, R=10, I=1, main_weapon="Daga")
    enemies = np.stack([candidate.copy()])
    wins, resolved = _simulate_batch(
        candidate, enemies, np.zeros(20, dtype=np.int64), 20, 123
    )
    assert wins == 0
    assert resolved == 0
