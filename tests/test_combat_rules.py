import numpy as np

from trollheim_simulator.engine import (
    STATE_KNOCKED_DOWN,
    STATE_OUT,
    STATE_PARALYZED,
    STATE_STANDING,
    STATE_STUNNED,
    _apply_damage,
    _build_matchups,
    _can_parry,
    _injury_state_from_roll,
    _make_fighter,
    _recover_fighter,
    _resolve_attack_phase,
    _simulate_batch_precomputed,
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


def test_recovery_sequence():
    assert _recover_fighter(STATE_STUNNED) == (STATE_KNOCKED_DOWN, False)
    assert _recover_fighter(STATE_KNOCKED_DOWN) == (STATE_STANDING, True)
    assert _recover_fighter(STATE_STANDING) == (STATE_STANDING, False)


def test_paralysis_recovery_uses_resistance(monkeypatch):
    monkeypatch.setattr("trollheim_simulator.engine._nb_roll_d6", lambda: 4)
    assert _recover_fighter(STATE_PARALYZED, 4) == (STATE_STANDING, False)
    assert _recover_fighter(STATE_PARALYZED, 3) == (STATE_PARALYZED, False)


def test_mace_injury_table():
    assert _injury_state_from_roll(1, WEAPON_MACE) == STATE_KNOCKED_DOWN
    assert _injury_state_from_roll(2, WEAPON_MACE) == STATE_STUNNED
    assert _injury_state_from_roll(3, WEAPON_MACE) == STATE_STUNNED
    assert _injury_state_from_roll(4, WEAPON_MACE) == STATE_STUNNED
    assert _injury_state_from_roll(5, WEAPON_MACE) == STATE_OUT
    assert _injury_state_from_roll(2, WEAPON_SWORD) == STATE_KNOCKED_DOWN


def test_attacks_with_double_strength_cannot_be_parried():
    assert _can_parry(5, 3)
    assert not _can_parry(6, 3)
    assert not _can_parry(7, 3)


def test_amulet_is_spent_on_first_hit_and_works_roughly_half_the_time():
    attacker = fighter(A=1)
    defender = fighter(main_weapon="Maza", has_luck_amulet=True)
    ignored = 0
    for _ in range(2_000):
        wounds, state, used = _resolve_attack_phase(
            attacker, defender, 1, STATE_STANDING, False, 1,
            np.array([2], dtype=np.int64), np.array([7], dtype=np.int64), 1,
        )
        assert used
        ignored += wounds == 1 and state == STATE_STANDING
    # Además del 50% del amuleto, algunos golpes no llegan a herir.
    assert 1_350 < ignored < 1_650


def test_stunned_fighter_is_taken_out_automatically():
    attacker = fighter()
    defender = fighter()
    wounds, state, _ = _resolve_attack_phase(
        attacker,
        defender,
        1,
        STATE_STUNNED,
        False,
        6,
        np.array([6], dtype=np.int64),
        np.array([7], dtype=np.int64),
        1,
    )
    assert wounds == 1
    assert state == STATE_OUT


def test_mace_stuns_more_often_than_a_sword():
    # Una muestra grande verifica la regla por distribución.
    mace_stunned = 0
    sword_stunned = 0
    for _ in range(2_000):
        _, mace_state = _apply_damage(
            1, STATE_STANDING, 1, WEAPON_MACE, False, False, False, 0
        )
        _, sword_state = _apply_damage(
            1, STATE_STANDING, 1, WEAPON_SWORD, False, False, False, 0
        )
        mace_stunned += mace_state == STATE_STUNNED
        sword_stunned += sword_state == STATE_STUNNED
    assert mace_stunned > sword_stunned * 1.35


def test_helmet_reduces_stuns_but_never_cancels_damage():
    without_helmet_stuns = 0
    with_helmet_stuns = 0
    for _ in range(2_000):
        wounds_plain, state_plain = _apply_damage(
            1, STATE_STANDING, 1, WEAPON_SWORD, False, False, False, 0
        )
        wounds_helmet, state_helmet = _apply_damage(
            1, STATE_STANDING, 1, WEAPON_SWORD, True, False, False, 0
        )
        assert wounds_plain == 0
        assert wounds_helmet == 0
        without_helmet_stuns += state_plain == STATE_STUNNED
        with_helmet_stuns += state_helmet == STATE_STUNNED
    assert with_helmet_stuns < without_helmet_stuns * 0.65


def test_mandrake_turns_stunned_into_knocked_down(monkeypatch):
    monkeypatch.setattr("trollheim_simulator.engine._nb_roll_d6", lambda: 3)
    wounds, state = _apply_damage(
        1, STATE_STANDING, 1, WEAPON_SWORD, False, False, False, 0, True
    )
    assert wounds == 0
    assert state == STATE_KNOCKED_DOWN


def test_unwinnable_duel_is_excluded_from_results():
    candidate = fighter(HA=1, F=1, R=10, I=1, main_weapon="Daga")
    enemies = np.stack([candidate.copy()])
    matchup = _build_matchups(candidate, enemies)
    wins, resolved = _simulate_batch_precomputed(
        candidate,
        enemies,
        np.zeros(20, dtype=np.int64),
        matchup[0],
        matchup[1],
        matchup[2],
        matchup[3],
        matchup[4],
        matchup[5],
        matchup[6],
        20,
        123,
    )
    assert wins == 0
    assert resolved == 0
