"""Motor de simulación de combates, independiente de la interfaz."""

import numpy as np

from .enemies import ENEMY_PROFILES
from .rules import *

ENEMY_VARIANTS_PER_PROFILE = 6
_ENEMY_VARIANT_CACHE = {}

STATE_STANDING = 0
STATE_KNOCKED_DOWN = 1
STATE_STUNNED = 2
STATE_PARALYZED = 3
STATE_OUT = 4


def _skill_mask(skills):
    mask = 0
    for skill in skills:
        if skill == "Combatiente Experto":
            mask |= SKILL_EXPERT
        elif skill == "A Fondo":
            mask |= SKILL_CHARGE
        elif skill == "Echarse a un Lado":
            mask |= SKILL_SIDESTEP
        elif skill == "Golpe Poderoso":
            mask |= SKILL_POWER
        elif skill == "Curtido":
            mask |= SKILL_SEASONED
        elif skill == "Experto en Esgrima":
            mask |= SKILL_FENCER
        elif skill == "Carga Imparable":
            mask |= SKILL_UNSTOPPABLE
        elif skill == "Reflejos Felinos":
            mask |= SKILL_CAT_REFLEXES
        elif skill == "En Pie de un Salto":
            mask |= SKILL_SPRING_UP
        elif skill == "Fortachón":
            mask |= SKILL_STRONGMAN
        elif skill == "Incansable":
            mask |= SKILL_TIRELESS
        elif skill == "Maestro del Hacha":
            mask |= SKILL_AXE_MASTER
        elif skill == "Experto en Hachas":
            mask |= SKILL_AXE_EXPERT
        elif skill == "Golpe con el Escudo":
            mask |= SKILL_SHIELD_STRIKE
    return mask


def _armor_base_save(armor):
    if armor == "Armadura Ligera":
        return 6
    if armor == "Armadura Pesada":
        return 5
    if armor == "Armadura de Gromril":
        return 4
    return 7


def _make_fighter(config):
    """Convierte una ficha en el array compacto usado por el motor."""
    main = WEAPON_CODES.get(config.get("main_weapon", "Espada"), WEAPON_SWORD)
    off = OFFHAND_CODES.get(config.get("off_hand", "Ninguna"), OFF_NONE)
    legacy_material = config.get("weapon_material", "Sin material")
    main_material = MATERIAL_CODES.get(
        config.get("main_weapon_material", legacy_material), MATERIAL_NORMAL
    )
    offhand_material = MATERIAL_CODES.get(
        config.get("offhand_material", "Sin material"), MATERIAL_NORMAL
    )
    skills = _skill_mask(config.get("skills", []))
    preparation = PREPARATION_CODES.get(
        config.get("preparation", "Ninguno"), PREPARATION_NONE
    )
    main_poison = POISON_CODES.get(
        config.get("main_poison", "Sin veneno"), POISON_NONE
    )
    offhand_poison = POISON_CODES.get(
        config.get("offhand_poison", "Sin veneno"), POISON_NONE
    )

    if (
        _is_two_handed(main)
        or _is_paired(main)
        or main == WEAPON_SPEAR
        or (main == WEAPON_CHOPPA and off != WEAPON_SPIKED_GAUNTLET)
    ):
        off_weapon = OFF_NONE
    elif off != OFF_NONE and off != OFF_SHIELD:
        off_weapon = off
    else:
        off_weapon = OFF_NONE

    armor_save = _armor_base_save(config.get("armor", "Sin Armadura"))
    if off == OFF_SHIELD and not (_is_two_handed(main) or _is_paired(main)):
        armor_save -= 1

    return np.array(
        [
            config["HA"],
            config["F"] + (preparation == PREPARATION_CRIMSON_SHADE),
            config["R"] + (preparation == PREPARATION_MANDRAKE_ROOT),
            config["H"],
            config["I"],
            config["A"],
            main,
            off_weapon,
            armor_save,
            skills,
            int(bool(config.get("has_helmet", False))),
            int(bool(config.get("has_luck_amulet", False))),
            main_material,
            offhand_material,
            preparation,
            main_poison,
            offhand_poison,
        ],
        dtype=np.int64,
    )


def effective_fighter_key(config):
    """Identifica fichas equivalentes para las reglas y equipo actuales."""
    fighter = _make_fighter(config)
    main = int(fighter[6])
    off = int(fighter[7])
    skills = int(fighter[9])
    attack_weapons = {main}
    if off >= 0:
        attack_weapons.add(off)

    fencing_weapons = {
        WEAPON_SWORD, WEAPON_ELVEN_2H, WEAPON_SCIMITAR, WEAPON_GREAT_SCIMITAR,
    }
    axe_weapons = {WEAPON_AXE, WEAPON_DWARF_AXE}
    tireless_weapons = {WEAPON_FLAIL, WEAPON_MORNING_STAR, WEAPON_CHOPPA}

    if not attack_weapons & fencing_weapons:
        skills &= ~SKILL_FENCER
    if not attack_weapons & axe_weapons:
        skills &= ~SKILL_AXE_EXPERT
    if main != WEAPON_AXE:
        skills &= ~SKILL_AXE_MASTER
    if config.get("off_hand") != "Escudo":
        skills &= ~SKILL_SHIELD_STRIKE
    if not _is_two_handed(main):
        skills &= ~SKILL_STRONGMAN
    if not attack_weapons & tireless_weapons:
        skills &= ~SKILL_TIRELESS

    fighter[9] = skills
    return tuple(int(value) for value in fighter)


def _nb_to_hit(ha_att, ha_def):
    if ha_def == 0:
        return 2
    if ha_att > ha_def:
        return 3
    if ha_def > 2 * ha_att:
        return 5
    return 4


def _nb_to_wound(f_att, r_def):
    diff = f_att - r_def
    if diff >= 2:
        return 2
    if diff == 1:
        return 3
    if diff == 0:
        return 4
    if diff == -1:
        return 5
    if diff >= -3:
        return 6
    return 7


def _nb_armour_save(base_save, weapon):
    if weapon in (WEAPON_DAGGER, WEAPON_YAMBIYA, WEAPON_PIRATE_SCOURGE):
        return min(6, base_save - 1)
    return base_save


def _is_two_handed(weapon):
    return weapon in (
        WEAPON_2H, WEAPON_FLAIL, WEAPON_HALBERD, WEAPON_SCYTHE,
        WEAPON_PIKE, WEAPON_ELVEN_2H, WEAPON_GREAT_SCIMITAR,
        WEAPON_BRAZIER_STAFF, WEAPON_WAR_MAUL, WEAPON_DOUBLE_BLADE,
        WEAPON_SERPENT_STAFF,
        WEAPON_KUSARA_KAMA, WEAPON_LONG_HOOK,
    )


def _is_paired(weapon):
    return weapon in (
        WEAPON_BAGH_NAKH, WEAPON_BRASS_KNUCKLES, WEAPON_ESHIN_CLAWS,
        WEAPON_WEEPING_BLADES,
    )


def _weapon_has_parry(weapon):
    return weapon in (
        WEAPON_SWORD, WEAPON_RAPIER, WEAPON_ELVEN_2H, WEAPON_CUTLASS,
        WEAPON_SCIMITAR, WEAPON_SWORD_BREAKER, WEAPON_DWARF_AXE,
        WEAPON_TRIDENT, WEAPON_SPIKED_GAUNTLET, WEAPON_ESHIN_CLAWS,
        WEAPON_WEEPING_BLADES, WEAPON_SERPENT_STAFF, WEAPON_WITCH_BLADE,
    )


def _parry_profile(fighter):
    main = int(fighter[6])
    off = int(fighter[7])
    axe_parry = bool(int(fighter[9]) & SKILL_AXE_MASTER and main == WEAPON_AXE)
    sources = int(_weapon_has_parry(main) or axe_parry)
    sources += int(_weapon_has_parry(off))
    if main == WEAPON_DOUBLE_BLADE:
        return 2, False
    paired_parry = main in (WEAPON_ESHIN_CLAWS, WEAPON_WEEPING_BLADES)
    return (1 if sources or paired_parry else 0), (sources >= 2 or paired_parry)


def _weapon_attacks_first(weapon):
    return weapon in (
        WEAPON_SPEAR, WEAPON_PIKE, WEAPON_ANKUS, WEAPON_TRIDENT,
        WEAPON_CHAINED_SQUIG, WEAPON_SQUIG_PROD, WEAPON_LONG_HOOK,
    )


def _weapon_attacks_last(fighter):
    weapon = int(fighter[6])
    material = int(fighter[12])
    offhand_is_obsidian = int(fighter[7]) >= 0 and int(fighter[13]) == MATERIAL_OBSIDIAN
    if int(fighter[9]) & SKILL_STRONGMAN and _is_two_handed(weapon):
        return material == MATERIAL_OBSIDIAN or offhand_is_obsidian
    return weapon in (WEAPON_2H, WEAPON_ELVEN_2H, WEAPON_GREAT_SCIMITAR, WEAPON_WAR_MAUL) or material == MATERIAL_OBSIDIAN or offhand_is_obsidian


def _has_frenzy_preparation(fighter):
    return int(fighter[14]) in (PREPARATION_MAD_CAP, PREPARATION_HEAD_SPLITTER)


def _attack_count(fighter):
    count = int(fighter[5]) + (int(fighter[7]) != OFF_NONE)
    if int(fighter[7]) == OFF_SHIELD:
        count = int(fighter[5]) + bool(int(fighter[9]) & SKILL_SHIELD_STRIKE)
    if _is_paired(int(fighter[6])) or int(fighter[6]) == WEAPON_DOUBLE_BLADE:
        count += 1
    return count


def _frenzy_attack_count(fighter, active):
    return _attack_count(fighter) + (int(fighter[5]) if active else 0)


def _source_attack_index(fighter, attack_index):
    """Los ataques extra de Furia Asesina usan el arma principal."""
    return attack_index if attack_index < _attack_count(fighter) else 0


def _nb_roll_d6():
    return np.random.randint(1, 7)


def _weapon_for_attack(fighter, attack_index):
    if attack_index < int(fighter[5]):
        return int(fighter[6])
    offhand = int(fighter[7])
    if offhand == OFF_SHIELD and int(fighter[9]) & SKILL_SHIELD_STRIKE:
        return WEAPON_DAGGER
    if offhand >= 0:
        return offhand
    return WEAPON_SWORD


def _material_for_attack(attacker, attack_index):
    if attack_index >= int(attacker[5]) and int(attacker[7]) >= 0:
        return int(attacker[13])
    return int(attacker[12])


def _poison_for_attack(attacker, attack_index):
    if _weapon_for_attack(attacker, attack_index) == WEAPON_WEEPING_BLADES:
        return POISON_BLACK_LOTUS
    if attack_index >= int(attacker[5]) and int(attacker[7]) >= 0:
        return int(attacker[16])
    return int(attacker[15])


def _poison_is_active(attacker, defender, attack_index):
    if int(defender[14]) == PREPARATION_SHALLAYA_TEARS:
        return POISON_NONE
    return _poison_for_attack(attacker, attack_index)


def _attack_strength(attacker, weapon, defender_is_seasoned, first_round=True, attack_index=-1):
    strength = int(attacker[1])
    if int(attacker[9]) & SKILL_POWER:
        strength += 1
    tireless = bool(int(attacker[9]) & SKILL_TIRELESS)
    if weapon in (WEAPON_2H, WEAPON_ELVEN_2H, WEAPON_GREAT_SCIMITAR, WEAPON_WAR_MAUL):
        strength += 2
    elif weapon == WEAPON_FLAIL:
        strength += 2 if first_round or tireless else 0
    elif weapon in (WEAPON_MORNING_STAR, WEAPON_HALBERD, WEAPON_BRAZIER_STAFF, WEAPON_BRASS_KNUCKLES, WEAPON_BAGH_NAKH):
        strength += 1 if first_round or tireless or weapon not in (WEAPON_MORNING_STAR,) else 0
    elif weapon == WEAPON_SIGMARITE_HAMMER:
        strength += 1
    elif weapon == WEAPON_CHOPPA:
        strength += 1 if first_round or tireless else 0
    elif weapon == WEAPON_CHAINED_SQUIG:
        strength = 3
    elif weapon == WEAPON_WITCH_BLADE:
        strength += 1 if first_round else 0
    elif weapon == WEAPON_RAPIER:
        strength -= 1
    material = int(attacker[12]) if attack_index < 0 else _material_for_attack(attacker, attack_index)
    if material == MATERIAL_OBSIDIAN:
        strength += 1
    poison = _poison_for_attack(attacker, attack_index)
    if poison in (POISON_BLACK_VENOM, POISON_REPTILE):
        strength += 1
    if defender_is_seasoned:
        strength = max(1, strength - 1)
    return strength


def _armour_strength(attacker, weapon, first_round=True, attack_index=-1):
    strength = _attack_strength(attacker, weapon, False, first_round, attack_index)
    if _poison_for_attack(attacker, attack_index) == POISON_REPTILE:
        strength -= 1
    return strength


def _extra_armour_penalty(attacker, weapon, attack_index=-1):
    penalty = 0
    if weapon in (WEAPON_AXE, WEAPON_KATAR, WEAPON_SCYTHE, WEAPON_SCIMITAR,
                  WEAPON_GREAT_SCIMITAR, WEAPON_BAGH_NAKH, WEAPON_WAR_MAUL,
                  WEAPON_DWARF_AXE, WEAPON_CHOPPA, WEAPON_ESHIN_CLAWS,
                  WEAPON_KUSARA_KAMA):
        penalty += 1
    material = int(attacker[12]) if attack_index < 0 else _material_for_attack(attacker, attack_index)
    if material == MATERIAL_GROMRIL:
        penalty += 1
    return penalty


def _build_matchups(candidate, enemies):
    """Precalcula los objetivos de impacto, herida y salvación por rival."""
    n_enemies = enemies.shape[0]
    candidate_attacks = _attack_count(candidate)
    enemy_attack_counts = np.empty(n_enemies, dtype=np.int64)
    max_attacks = candidate_attacks

    for e in range(n_enemies):
        count = _attack_count(enemies[e])
        enemy_attack_counts[e] = count
        max_attacks = max(max_attacks, count)

    hit_ce = np.empty(n_enemies, dtype=np.int64)
    hit_ec = np.empty(n_enemies, dtype=np.int64)
    wound_ce = np.full((n_enemies, max_attacks), 7, dtype=np.int64)
    save_ce = np.full((n_enemies, max_attacks), 7, dtype=np.int64)
    wound_ec = np.full((n_enemies, max_attacks), 7, dtype=np.int64)
    save_ec = np.full((n_enemies, max_attacks), 7, dtype=np.int64)

    candidate_is_seasoned = bool(int(candidate[9]) & SKILL_SEASONED)

    for e in range(n_enemies):
        enemy = enemies[e]
        enemy_is_seasoned = bool(int(enemy[9]) & SKILL_SEASONED)
        hit_ce[e] = _nb_to_hit(int(candidate[0]), int(enemy[0]))
        hit_ec[e] = _nb_to_hit(int(enemy[0]), int(candidate[0]))

        for i in range(candidate_attacks):
            weapon = _weapon_for_attack(candidate, i)
            wound_strength = _attack_strength(candidate, weapon, enemy_is_seasoned, True, i)
            armour_strength = _armour_strength(candidate, weapon, True, i)
            wound_ce[e, i] = _nb_to_wound(wound_strength, int(enemy[2]))
            save_ce[e, i] = (
                _nb_armour_save(int(enemy[8]), weapon)
                + max(0, armour_strength - 3)
                + _extra_armour_penalty(candidate, weapon, i)
            )

        for i in range(int(enemy_attack_counts[e])):
            weapon = _weapon_for_attack(enemy, i)
            wound_strength = _attack_strength(enemy, weapon, candidate_is_seasoned, True, i)
            armour_strength = _armour_strength(enemy, weapon, True, i)
            wound_ec[e, i] = _nb_to_wound(wound_strength, int(candidate[2]))
            save_ec[e, i] = (
                _nb_armour_save(int(candidate[8]), weapon)
                + max(0, armour_strength - 3)
                + _extra_armour_penalty(enemy, weapon, i)
            )

    return (
        hit_ce,
        wound_ce,
        save_ce,
        hit_ec,
        wound_ec,
        save_ec,
        enemy_attack_counts,
        max_attacks,
    )


def _recover_fighter(state, resistance=0):
    if state == STATE_PARALYZED:
        return (STATE_STANDING if _nb_roll_d6() <= resistance else state), False
    if state == STATE_STUNNED:
        return STATE_KNOCKED_DOWN, False
    if state == STATE_KNOCKED_DOWN:
        return STATE_STANDING, True
    return state, False


def _injury_state_from_roll(roll, weapon):
    if weapon in (
        WEAPON_MACE, WEAPON_STONE_AXE, WEAPON_ANKUS, WEAPON_SIGMARITE_HAMMER,
    ) and 2 <= roll <= 4:
        return STATE_STUNNED
    if roll <= 2:
        return STATE_KNOCKED_DOWN
    if roll <= 4:
        return STATE_STUNNED
    return STATE_OUT


def _injury_result(weapon, helmet, spring_up, mandrake, dark_steel, injury_modifier):
    roll = min(6, _nb_roll_d6() + injury_modifier)
    state = _injury_state_from_roll(roll, weapon)

    if dark_steel and 2 <= roll <= 4:
        state = STATE_STUNNED

    if state == STATE_STUNNED and mandrake:
        state = STATE_KNOCKED_DOWN

    if state == STATE_STUNNED and helmet and _nb_roll_d6() >= 4:
        # El casco provoca este derribo: En Pie de un Salto no lo evita.
        return STATE_KNOCKED_DOWN
    if state == STATE_KNOCKED_DOWN and spring_up:
        return STATE_STANDING
    return state


def _critical_effect(critical_roll):
    return 2, critical_roll >= 3, 2 if critical_roll >= 5 else 0


def _can_parry(attacker_strength, defender_basic_strength):
    return attacker_strength < 2 * defender_basic_strength


def _apply_damage(
    wounds, state, damage, weapon, helmet, spring_up, dark_steel,
    injury_modifier, mandrake=False,
):
    worst_state = state
    for _ in range(damage):
        if wounds > 0:
            wounds -= 1
        if wounds <= 0:
            injury = _injury_result(
                weapon, helmet, spring_up, mandrake, dark_steel, injury_modifier
            )
            if injury > worst_state:
                worst_state = injury
    return wounds, worst_state


def _resolve_attack_phase(
    attacker,
    defender,
    defender_wounds,
    defender_state,
    defender_amulet_used,
    hit_target,
    wound_targets,
    save_targets,
    attack_count,
    first_round=True,
    charging=False,
    charged=False,
):
    """Resuelve todos los ataques de un guerrero contra el otro."""
    if attacker[5] <= 0 or attack_count <= 0 or defender_state == STATE_OUT:
        return defender_wounds, defender_state, defender_amulet_used

    if defender_state == STATE_STUNNED:
        return defender_wounds, STATE_OUT, defender_amulet_used

    automatic_hits = defender_state in (STATE_KNOCKED_DOWN, STATE_PARALYZED)
    knocked_down = defender_state == STATE_KNOCKED_DOWN
    # Un estoque puede generar ataques adicionales. Doce es el máximo útil:
    # después sólo impactaría encadenando seises como un tahúr poseído.
    if int(attacker[6]) in (WEAPON_STEEL_WHIP, WEAPON_PIRATE_SCOURGE) and (
        charging or charged
    ):
        attack_count += 1
    capacity = attack_count + 12
    hit_rolls = np.zeros(capacity, dtype=np.int64)
    hit_active = np.zeros(capacity, dtype=np.uint8)
    attack_weapons = np.zeros(capacity, dtype=np.int64)
    rapier_penalties = np.zeros(capacity, dtype=np.int64)

    for i in range(attack_count):
        source_index = _source_attack_index(attacker, i)
        if automatic_hits:
            hit_rolls[i] = 6
            hit_active[i] = 1
            attack_weapons[i] = _weapon_for_attack(attacker, source_index)
        else:
            roll = _nb_roll_d6()
            hit_rolls[i] = roll
            weapon = _weapon_for_attack(attacker, source_index)
            attack_weapons[i] = weapon
            current_hit_target = hit_target
            if charging and int(attacker[9]) & SKILL_UNSTOPPABLE:
                current_hit_target = _nb_to_hit(int(attacker[0]) + 1, int(defender[0]))
            rerolls_sword = int(attacker[9]) & SKILL_FENCER and weapon in (
                WEAPON_SWORD, WEAPON_ELVEN_2H, WEAPON_SCIMITAR, WEAPON_GREAT_SCIMITAR,
            )
            rerolls_axe = int(attacker[9]) & SKILL_AXE_EXPERT and weapon in (
                WEAPON_AXE, WEAPON_DWARF_AXE,
            )
            if roll < current_hit_target and charging and (rerolls_sword or rerolls_axe):
                if rerolls_sword or rerolls_axe:
                    roll = _nb_roll_d6()
                    hit_rolls[i] = roll
            if roll >= current_hit_target:
                hit_active[i] = 1

    parry_attempts, reroll_failed_parry = _parry_profile(defender)
    attacker_blocks_parry = int(attacker[6]) in (
        WEAPON_WAR_MAUL, WEAPON_STEEL_WHIP, WEAPON_CHAINED_SQUIG,
        WEAPON_PIRATE_SCOURGE,
    )
    if defender_state == STATE_STANDING and parry_attempts and not attacker_blocks_parry:
        eligible_hits = []
        defender_basic_strength = int(defender[1])
        for i in range(attack_count):
            if hit_active[i] == 0:
                continue
            weapon = int(attack_weapons[i])
            defender_is_seasoned = bool(int(defender[9]) & SKILL_SEASONED)
            strength = _attack_strength(attacker, weapon, defender_is_seasoned, first_round, i)
            if not _can_parry(strength, defender_basic_strength):
                continue
            eligible_hits.append(i)
        eligible_hits.sort(key=lambda index: hit_rolls[index], reverse=True)
        for best_index in eligible_hits[:parry_attempts]:
            best_roll = hit_rolls[best_index]
            parry_roll = _nb_roll_d6()
            if reroll_failed_parry and parry_roll <= best_roll:
                parry_roll = _nb_roll_d6()
            if parry_roll > best_roll:
                hit_active[best_index] = 0

    critical_used = False
    attacker_skills = int(attacker[9])
    defender_has_amulet = int(defender[11]) != 0
    defender_has_helmet = int(defender[10]) != 0
    defender_used_mandrake = int(defender[14]) == PREPARATION_MANDRAKE_ROOT

    queued_attacks = attack_count
    i = 0
    while i < queued_attacks:
        if hit_active[i] == 0:
            i += 1
            continue

        if defender_has_amulet and not defender_amulet_used:
            defender_amulet_used = True
            if _nb_roll_d6() >= 4:
                i += 1
                continue

        weapon = int(attack_weapons[i])
        source_index = _source_attack_index(attacker, i)
        poison = _poison_for_attack(attacker, source_index)
        if int(defender[14]) == PREPARATION_SHALLAYA_TEARS:
            poison = POISON_NONE
        if poison == POISON_SPIDER_SPIT and _nb_roll_d6() > int(defender[2]):
            defender_state = STATE_PARALYZED
        defender_is_seasoned = bool(int(defender[9]) & SKILL_SEASONED)
        strength = _attack_strength(
            attacker, weapon, defender_is_seasoned, first_round, source_index
        )
        if int(defender[14]) == PREPARATION_SHALLAYA_TEARS and _poison_for_attack(attacker, source_index) in (
            POISON_BLACK_VENOM, POISON_REPTILE,
        ):
            strength -= 1
        wound_target = _nb_to_wound(strength, int(defender[2]))
        lotus_wound = poison == POISON_BLACK_LOTUS and hit_rolls[i] == 6
        if wound_target > 6 and not lotus_wound:
            i += 1
            continue

        raw_wound = _nb_roll_d6()
        effective_wound = raw_wound
        if attacker_skills & SKILL_EXPERT:
            effective_wound += 1
        if poison == POISON_MANBANE:
            effective_wound += 1
            if raw_wound == 1:
                effective_wound = 0
        rerolled_wound = False
        if effective_wound < wound_target and poison == POISON_DEVIL_TOXIN:
            raw_wound = _nb_roll_d6()
            effective_wound = raw_wound + bool(attacker_skills & SKILL_EXPERT)
            rerolled_wound = True
        if effective_wound < wound_target and not lotus_wound:
            if weapon == WEAPON_RAPIER and queued_attacks < capacity:
                penalty = int(rapier_penalties[i]) + 1
                extra_roll = _nb_roll_d6()
                if extra_roll == 6 or extra_roll >= hit_target + penalty:
                    hit_rolls[queued_attacks] = extra_roll
                    hit_active[queued_attacks] = 1
                    attack_weapons[queued_attacks] = WEAPON_RAPIER
                    rapier_penalties[queued_attacks] = penalty
                    queued_attacks += 1
            i += 1
            continue

        if weapon == WEAPON_SERPENT_STAFF and _nb_roll_d6() == 6:
            return _apply_damage(
                defender_wounds, defender_state, 1, weapon,
                defender_has_helmet, bool(int(defender[9]) & SKILL_SPRING_UP),
                False, 0, defender_used_mandrake,
            ) + (defender_amulet_used,)

        critical_roll_needed = 5 if poison == POISON_WOLFSBANE else 6
        critical = (
            raw_wound >= critical_roll_needed
            and (lotus_wound or wound_target < 6)
            and not critical_used and not rerolled_wound
        )
        damage = 1
        ignore_armour = False
        injury_modifier = 0

        if critical:
            critical_used = True
            critical_roll = _nb_roll_d6()
            if attacker_skills & SKILL_CHARGE:
                critical_roll = min(6, critical_roll + 1)
            attack_material = _material_for_attack(attacker, source_index)
            if attack_material == MATERIAL_DARK_STEEL:
                critical_roll = min(6, critical_roll + 1)
            damage, ignore_armour, injury_modifier = _critical_effect(critical_roll)


        if not ignore_armour:
            armour_strength = _armour_strength(attacker, weapon, first_round, source_index)
            if (
                int(defender[14]) == PREPARATION_SHALLAYA_TEARS
                and _poison_for_attack(attacker, source_index) == POISON_BLACK_VENOM
            ):
                armour_strength -= 1
            save_target = (
                _nb_armour_save(int(defender[8]), weapon)
                + max(0, armour_strength - 3)
                + _extra_armour_penalty(attacker, weapon, source_index)
            )
            if save_target <= 6 and _nb_roll_d6() >= save_target:
                i += 1
                continue

        if weapon == WEAPON_WEEPING_BLADES and _nb_roll_d6() == 6:
            damage += 1
        if poison == POISON_BLOODROOT:
            damage *= 2

        if int(defender[9]) & SKILL_SIDESTEP:
            if _nb_roll_d6() >= 5:
                i += 1
                continue

        if poison == POISON_NIGHTSHADE:
            defender[4] = max(1, int(defender[4]) - 1)

        if knocked_down:
            return defender_wounds, STATE_OUT, defender_amulet_used

        defender_wounds, defender_state = _apply_damage(
            defender_wounds,
            defender_state,
            damage,
            weapon,
            defender_has_helmet,
            bool(int(defender[9]) & SKILL_SPRING_UP),
            _material_for_attack(attacker, source_index) == MATERIAL_DARK_STEEL,
            injury_modifier,
            defender_used_mandrake,
        )
        if defender_state != STATE_STANDING:
            break
        i += 1

    return defender_wounds, defender_state, defender_amulet_used


def _attacks_last(fighter, stood_up):
    return stood_up or _weapon_attacks_last(fighter)


def _combat_initiative(fighter, crimson_bonus=0):
    has_ithilmar = int(fighter[12]) == MATERIAL_ITHILMAR or (
        int(fighter[7]) >= 0 and int(fighter[13]) == MATERIAL_ITHILMAR
    )
    initiative = int(fighter[4]) + has_ithilmar + crimson_bonus
    if int(fighter[6]) in (WEAPON_BRASS_KNUCKLES, WEAPON_WAR_MAUL):
        initiative -= 2 if int(fighter[6]) == WEAPON_BRASS_KNUCKLES else 1
    return initiative


def _prevents_first_reply(fighter, first_round):
    return first_round and int(fighter[6]) == WEAPON_PIKE


def _simulate_one_precomputed_fast(
    candidate,
    enemy,
    hit_ce,
    wound_ce,
    save_ce,
    hit_ec,
    wound_ec,
    save_ec,
    enemy_attack_count,
):
    """Simula un duelo; 1 gana, 0 pierde y -1 queda sin resolver."""
    candidate = candidate.copy()
    enemy = enemy.copy()
    wounds1 = int(candidate[3])
    wounds2 = int(enemy[3])
    state1 = STATE_STANDING
    state2 = STATE_STANDING
    amulet1_used = False
    amulet2_used = False
    crimson1 = (_nb_roll_d6() + 1) // 2 if int(candidate[14]) == PREPARATION_CRIMSON_SHADE else 0
    crimson2 = (_nb_roll_d6() + 1) // 2 if int(enemy[14]) == PREPARATION_CRIMSON_SHADE else 0
    frenzy1 = _has_frenzy_preparation(candidate)
    frenzy2 = _has_frenzy_preparation(enemy)

    # Dos fases por ronda: una oportunidad de actuar para cada combatiente.
    for phase in range(50 * 2):
        candidate_turn = phase % 2 == 0
        first_round = phase < 2
        stood1 = False
        stood2 = False

        if candidate_turn:
            state1, stood1 = _recover_fighter(state1, int(candidate[2]))
        else:
            state2, stood2 = _recover_fighter(state2, int(enemy[2]))

        if state1 == STATE_OUT:
            return 0.0
        if state2 == STATE_OUT:
            return 1.0

        can_attack1 = state1 == STATE_STANDING
        can_attack2 = state2 == STATE_STANDING

        if not can_attack1 and not can_attack2:
            continue
        if can_attack1 and not can_attack2:
            first = 1
        elif can_attack2 and not can_attack1:
            first = 2
        else:
            first1 = first_round and _weapon_attacks_first(int(candidate[6]))
            first2 = first_round and _weapon_attacks_first(int(enemy[6]))
            last1 = _attacks_last(candidate, stood1)
            last2 = _attacks_last(enemy, stood2)
            enemy_uses_reflexes = bool(int(enemy[9]) & SKILL_CAT_REFLEXES)
            if phase == 0:
                first1 = True
                first2 = first2 or enemy_uses_reflexes

            # "Ataca último" manda incluso si otra regla concede atacar primero.
            if last1 != last2:
                first = 2 if last1 else 1
            elif first1 != first2:
                first = 1 if first1 else 2
            elif _combat_initiative(candidate, crimson1) > _combat_initiative(enemy, crimson2):
                first = 1
            elif _combat_initiative(enemy, crimson2) > _combat_initiative(candidate, crimson1):
                first = 2
            else:
                first = 1 if np.random.random() < 0.5 else 2

        if first == 1:
            wounds2, state2, amulet2_used = _resolve_attack_phase(
                candidate, enemy, wounds2, state2, amulet2_used,
                hit_ce, wound_ce, save_ce, _frenzy_attack_count(candidate, frenzy1),
                first_round, phase == 0,
            )
            if state2 == STATE_OUT:
                return 1.0
            if state2 == STATE_STANDING and not _prevents_first_reply(candidate, first_round):
                wounds1, state1, amulet1_used = _resolve_attack_phase(
                    enemy, candidate, wounds1, state1, amulet1_used,
                    hit_ec, wound_ec, save_ec, _frenzy_attack_count(enemy, frenzy2),
                    first_round, False, phase == 0,
                )
        else:
            wounds1, state1, amulet1_used = _resolve_attack_phase(
                enemy, candidate, wounds1, state1, amulet1_used,
                hit_ec, wound_ec, save_ec, _frenzy_attack_count(enemy, frenzy2),
                first_round, False, phase == 0,
            )
            if state1 == STATE_OUT:
                return 0.0
            if state1 == STATE_STANDING and not _prevents_first_reply(enemy, first_round):
                wounds2, state2, amulet2_used = _resolve_attack_phase(
                    candidate, enemy, wounds2, state2, amulet2_used,
                    hit_ce, wound_ce, save_ce, _frenzy_attack_count(candidate, frenzy1),
                    first_round, phase == 0,
                )

        if state1 == STATE_OUT:
            return 0.0
        if state2 == STATE_OUT:
            return 1.0
        if state1 in (STATE_KNOCKED_DOWN, STATE_STUNNED):
            frenzy1 = False
        if state2 in (STATE_KNOCKED_DOWN, STATE_STUNNED):
            frenzy2 = False

    return -1.0


def _simulate_one_precomputed(
    candidate,
    enemy,
    hit_ce,
    wound_ce,
    save_ce,
    hit_ec,
    wound_ec,
    save_ec,
    enemy_attack_count,
):
    return _simulate_one_precomputed_fast(
        candidate,
        enemy,
        int(hit_ce[0]),
        wound_ce[0],
        save_ce[0],
        int(hit_ec[0]),
        wound_ec[0],
        save_ec[0],
        enemy_attack_count,
    )


def _simulate_batch_precomputed(
    candidate,
    enemies,
    enemy_indices,
    hit_ce_all,
    wound_ce_all,
    save_ce_all,
    hit_ec_all,
    wound_ec_all,
    save_ec_all,
    enemy_attack_counts,
    total_sims,
    seed,
):
    """Simula el lote por variantes homogéneas usando arrays de NumPy."""
    rng = np.random.default_rng(seed)
    wins = 0
    resolved = 0
    selected = np.asarray(enemy_indices[:total_sims], dtype=np.int64)
    counts = np.bincount(selected, minlength=len(enemies))
    active = np.flatnonzero(counts)
    unique_enemies, inverse = np.unique(enemies[active], axis=0, return_inverse=True)
    grouped_counts = np.zeros(len(unique_enemies), dtype=np.int64)
    np.add.at(grouped_counts, inverse, counts[active])
    for enemy, amount in zip(unique_enemies, grouped_counts):
        batch_wins, batch_resolved = _simulate_homogeneous_batch(
            candidate, enemy, int(amount), rng
        )
        wins += batch_wins
        resolved += batch_resolved
    return wins, resolved


def _vector_injury(
    rng, count, weapon, helmet, spring_up, mandrake, dark_steel, modifier,
):
    rolls = np.minimum(6, rng.integers(1, 7, count) + modifier)
    if weapon in (WEAPON_MACE, WEAPON_STONE_AXE, WEAPON_ANKUS, WEAPON_SIGMARITE_HAMMER):
        states = np.where(rolls == 1, STATE_KNOCKED_DOWN,
                          np.where(rolls <= 4, STATE_STUNNED, STATE_OUT))
    else:
        states = np.where(rolls <= 2, STATE_KNOCKED_DOWN,
                          np.where(rolls <= 4, STATE_STUNNED, STATE_OUT))
    if dark_steel:
        states = np.where((rolls >= 2) & (rolls <= 4), STATE_STUNNED, states)
    if mandrake:
        states[states == STATE_STUNNED] = STATE_KNOCKED_DOWN
    if helmet:
        saved = (states == STATE_STUNNED) & (rng.integers(1, 7, count) >= 4)
        states[saved] = STATE_KNOCKED_DOWN
    if spring_up:
        states[states == STATE_KNOCKED_DOWN] = STATE_STANDING
    return states


def _vector_attack_phase(
    attacker, defender, indices, defender_wounds, defender_state,
    defender_amulet_used, rng, first_round, charging=False, charged=False,
    defender_initiative_penalty=None, attacker_frenzy=None,
):
    """Resuelve una fase para muchos duelos con los mismos combatientes."""
    if indices.size == 0:
        return
    standing = defender_state[indices] == STATE_STANDING
    stunned = defender_state[indices] == STATE_STUNNED
    defender_state[indices[stunned]] = STATE_OUT
    rows = indices[
        standing
        | (defender_state[indices] == STATE_KNOCKED_DOWN)
        | (defender_state[indices] == STATE_PARALYZED)
    ]
    if rows.size == 0:
        return

    automatic = np.isin(defender_state[rows], (STATE_KNOCKED_DOWN, STATE_PARALYZED))
    knocked_down = defender_state[rows] == STATE_KNOCKED_DOWN
    frenzy_rows = (
        attacker_frenzy[rows]
        if attacker_frenzy is not None
        else np.zeros(rows.size, dtype=bool)
    )
    frenzy_active = bool(np.any(frenzy_rows))
    base_attack_count = _attack_count(attacker)
    attack_count = _frenzy_attack_count(attacker, frenzy_active)
    if int(attacker[6]) in (WEAPON_STEEL_WHIP, WEAPON_PIRATE_SCOURGE) and (charging or charged):
        attack_count += 1
    capacity = attack_count + 12
    hit_rolls = np.zeros((rows.size, capacity), dtype=np.int8)
    hit_active = np.zeros((rows.size, capacity), dtype=bool)
    weapons = np.empty(capacity, dtype=np.int64)
    penalties = np.zeros(capacity, dtype=np.int8)

    hit_target = _nb_to_hit(int(attacker[0]), int(defender[0]))
    if charging and int(attacker[9]) & SKILL_UNSTOPPABLE:
        hit_target = _nb_to_hit(int(attacker[0]) + 1, int(defender[0]))
    for attack in range(attack_count):
        source_index = _source_attack_index(attacker, attack)
        weapon = _weapon_for_attack(attacker, source_index)
        weapons[attack] = weapon
        rolls = rng.integers(1, 7, rows.size)
        rolls[automatic] = 6
        reroll = np.zeros(rows.size, dtype=bool)
        if charging and int(attacker[9]) & SKILL_FENCER and weapon in (
            WEAPON_SWORD, WEAPON_ELVEN_2H, WEAPON_SCIMITAR, WEAPON_GREAT_SCIMITAR,
        ):
            reroll = rolls < hit_target
        if charging and int(attacker[9]) & SKILL_AXE_EXPERT and weapon in (
            WEAPON_AXE, WEAPON_DWARF_AXE,
        ):
            reroll = rolls < hit_target
        rolls[reroll] = rng.integers(1, 7, int(reroll.sum()))
        hit_rolls[:, attack] = rolls
        hit_active[:, attack] = automatic | (rolls >= hit_target)
        if attack >= base_attack_count:
            hit_active[~frenzy_rows, attack] = False

    parry_attempts, reroll_failed_parry = _parry_profile(defender)
    blocks_parry = int(attacker[6]) in (
        WEAPON_WAR_MAUL, WEAPON_STEEL_WHIP, WEAPON_CHAINED_SQUIG,
        WEAPON_PIRATE_SCOURGE,
    )
    if parry_attempts and not blocks_parry:
        eligible = hit_active[:, :attack_count].copy()
        for attack in range(attack_count):
            source_index = _source_attack_index(attacker, attack)
            strength = _attack_strength(
                attacker, int(weapons[attack]), bool(int(defender[9]) & SKILL_SEASONED),
                first_round, source_index,
            )
            if not _can_parry(strength, int(defender[1])):
                eligible[:, attack] = False
        eligible[automatic] = False
        values = np.where(eligible, hit_rolls[:, :attack_count], 0)
        best = values.argmax(axis=1)
        best_roll = values[np.arange(rows.size), best]
        parry_rolls = rng.integers(1, 7, rows.size)
        if reroll_failed_parry:
            failed = (best_roll > 0) & (parry_rolls <= best_roll)
            parry_rolls[failed] = rng.integers(1, 7, int(failed.sum()))
        parried = (best_roll > 0) & (parry_rolls > best_roll)
        hit_active[np.arange(rows.size)[parried], best[parried]] = False
        if parry_attempts == 2:
            eligible[np.arange(rows.size), best] = False
            values = np.where(eligible, hit_rolls[:, :attack_count], 0)
            best = values.argmax(axis=1)
            best_roll = values[np.arange(rows.size), best]
            parried = (best_roll > 0) & (rng.integers(1, 7, rows.size) > best_roll)
            hit_active[np.arange(rows.size)[parried], best[parried]] = False

    queued = attack_count
    attack = 0
    critical_used = np.zeros(rows.size, dtype=bool)
    while attack < queued:
        local = hit_active[:, attack] & np.isin(
            defender_state[rows],
            (STATE_STANDING, STATE_KNOCKED_DOWN, STATE_PARALYZED),
        )
        if not local.any():
            attack += 1
            continue
        targets = np.flatnonzero(local)
        global_rows = rows[targets]
        amulet = bool(int(defender[11])) & ~defender_amulet_used[global_rows]
        if np.any(amulet):
            defender_amulet_used[global_rows[amulet]] = True
            ignored = rng.integers(1, 7, int(np.sum(amulet))) >= 4
            local_targets = targets[amulet][ignored]
            hit_active[local_targets, attack] = False
            targets = np.flatnonzero(hit_active[:, attack] & (defender_state[rows] != STATE_OUT))
            global_rows = rows[targets]
        if targets.size == 0:
            attack += 1
            continue

        weapon = int(weapons[attack])
        source_index = _source_attack_index(attacker, attack)
        poison = _poison_for_attack(attacker, source_index)
        if int(defender[14]) == PREPARATION_SHALLAYA_TEARS:
            poison = POISON_NONE
        if poison == POISON_SPIDER_SPIT:
            paralyzed = rng.integers(1, 7, targets.size) > int(defender[2])
            defender_state[global_rows[paralyzed]] = STATE_PARALYZED
        strength = _attack_strength(
            attacker, weapon, bool(int(defender[9]) & SKILL_SEASONED),
            first_round, source_index
        )
        if (
            int(defender[14]) == PREPARATION_SHALLAYA_TEARS
            and _poison_for_attack(attacker, source_index) in (POISON_BLACK_VENOM, POISON_REPTILE)
        ):
            strength -= 1
        wound_target = _nb_to_wound(strength, int(defender[2]))
        lotus = np.zeros(targets.size, dtype=bool)
        if poison == POISON_BLACK_LOTUS:
            lotus = hit_rolls[targets, attack] == 6
        if wound_target > 6 and not lotus.any():
            attack += 1
            continue
        wound_rolls = rng.integers(1, 7, targets.size)
        effective = wound_rolls + bool(int(attacker[9]) & SKILL_EXPERT)
        if poison == POISON_MANBANE:
            effective += 1
            effective[wound_rolls == 1] = 0
        wounded = (effective >= wound_target) | lotus
        rerolled = np.zeros(targets.size, dtype=bool)
        if poison == POISON_DEVIL_TOXIN:
            failed = ~wounded
            if failed.any():
                wound_rolls[failed] = rng.integers(1, 7, int(failed.sum()))
                effective[failed] = wound_rolls[failed] + bool(int(attacker[9]) & SKILL_EXPERT)
                wounded[failed] = effective[failed] >= wound_target
                rerolled[failed] = True
        if weapon == WEAPON_RAPIER and queued < capacity:
            failed = targets[~wounded]
            if failed.size:
                penalty = int(penalties[attack]) + 1
                extra = rng.integers(1, 7, failed.size)
                made = (extra == 6) | (extra >= hit_target + penalty)
                if made.any():
                    hit_rolls[failed[made], queued] = extra[made]
                    hit_active[failed[made], queued] = True
                    weapons[queued] = WEAPON_RAPIER
                    penalties[queued] = penalty
                    queued += 1
        targets = targets[wounded]
        wound_rolls = wound_rolls[wounded]
        rerolled = rerolled[wounded]
        lotus = lotus[wounded]
        if targets.size == 0:
            attack += 1
            continue
        global_rows = rows[targets]

        if weapon == WEAPON_SERPENT_STAFF:
            instant = rng.integers(1, 7, targets.size) == 6
            if instant.any():
                instant_rows = global_rows[instant]
                defender_wounds[instant_rows] -= 1
                injured = instant_rows[defender_wounds[instant_rows] <= 0]
                if injured.size:
                    defender_state[injured] = _vector_injury(
                        rng, injured.size, weapon, bool(defender[10]),
                        bool(int(defender[9]) & SKILL_SPRING_UP),
                        int(defender[14]) == PREPARATION_MANDRAKE_ROOT, False, 0,
                    )
                targets = targets[~instant]
                wound_rolls = wound_rolls[~instant]
                lotus = lotus[~instant]
                global_rows = rows[targets]
                if targets.size == 0:
                    attack += 1
                    continue

        critical_needed = 5 if poison == POISON_WOLFSBANE else 6
        critical = (
            (wound_rolls >= critical_needed) & (lotus | (wound_target < 6))
            & ~critical_used[targets] & ~rerolled
        )
        critical_used[targets[critical]] = True
        damage = np.ones(targets.size, dtype=np.int8)
        ignore_armour = np.zeros(targets.size, dtype=bool)
        injury_modifier = np.zeros(targets.size, dtype=np.int8)
        if critical.any():
            rolls = rng.integers(1, 7, int(critical.sum()))
            if int(attacker[9]) & SKILL_CHARGE:
                rolls = np.minimum(6, rolls + 1)
            if _material_for_attack(attacker, source_index) == MATERIAL_DARK_STEEL:
                rolls = np.minimum(6, rolls + 1)
            damage[critical] = 2
            ignore_armour[critical] = rolls >= 3
            injury_modifier[critical] = np.where(rolls >= 5, 2, 0)

        armour_strength = _armour_strength(attacker, weapon, first_round, source_index)
        if (
            int(defender[14]) == PREPARATION_SHALLAYA_TEARS
            and _poison_for_attack(attacker, source_index) == POISON_BLACK_VENOM
        ):
            armour_strength -= 1
        save_target = (
            _nb_armour_save(int(defender[8]), weapon)
            + max(0, armour_strength - 3)
            + _extra_armour_penalty(attacker, weapon, source_index)
        )
        saved = np.zeros(targets.size, dtype=bool)
        can_save = ~ignore_armour & (save_target <= 6)
        saved[can_save] = rng.integers(1, 7, int(can_save.sum())) >= save_target
        targets = targets[~saved]
        damage = damage[~saved]
        injury_modifier = injury_modifier[~saved]
        global_rows = rows[targets]
        if targets.size == 0:
            attack += 1
            continue
        if weapon == WEAPON_WEEPING_BLADES:
            damage += rng.integers(1, 7, targets.size) == 6
        if poison == POISON_BLOODROOT:
            damage *= 2
        if int(defender[9]) & SKILL_SIDESTEP:
            dodged = rng.integers(1, 7, targets.size) >= 5
            targets = targets[~dodged]
            damage = damage[~dodged]
            injury_modifier = injury_modifier[~dodged]
            global_rows = rows[targets]
        if targets.size == 0:
            attack += 1
            continue

        if (
            poison == POISON_NIGHTSHADE
            and defender_initiative_penalty is not None
            and targets.size
        ):
            defender_initiative_penalty[global_rows] += 1
        auto_rows = global_rows[knocked_down[targets]]
        defender_state[auto_rows] = STATE_OUT
        normal = ~knocked_down[targets]
        for amount in (1, 2, 3, 4):
            for modifier in (0, 2):
                group = normal & (damage == amount) & (injury_modifier == modifier)
                affected = global_rows[group]
                for _ in range(amount):
                    alive = affected[defender_state[affected] != STATE_OUT]
                    if alive.size == 0:
                        break
                    defender_wounds[alive] -= 1
                    injured = alive[defender_wounds[alive] <= 0]
                    if injured.size:
                        injury = _vector_injury(
                            rng, injured.size, weapon, bool(defender[10]),
                            bool(int(defender[9]) & SKILL_SPRING_UP),
                            int(defender[14]) == PREPARATION_MANDRAKE_ROOT,
                            _material_for_attack(attacker, source_index) == MATERIAL_DARK_STEEL,
                            modifier,
                        )
                        defender_state[injured] = np.maximum(
                            defender_state[injured], injury
                        )
        attack += 1


def _simulate_homogeneous_batch(candidate, enemy, total, rng):
    wounds1 = np.full(total, int(candidate[3]), dtype=np.int16)
    wounds2 = np.full(total, int(enemy[3]), dtype=np.int16)
    state1 = np.zeros(total, dtype=np.int8)
    state2 = np.zeros(total, dtype=np.int8)
    amulet1 = np.zeros(total, dtype=bool)
    amulet2 = np.zeros(total, dtype=bool)
    crimson1 = (
        rng.integers(1, 4, total)
        if int(candidate[14]) == PREPARATION_CRIMSON_SHADE else np.zeros(total, dtype=np.int8)
    )
    crimson2 = (
        rng.integers(1, 4, total)
        if int(enemy[14]) == PREPARATION_CRIMSON_SHADE else np.zeros(total, dtype=np.int8)
    )
    initiative_penalty1 = np.zeros(total, dtype=np.int8)
    initiative_penalty2 = np.zeros(total, dtype=np.int8)
    frenzy1 = np.full(total, _has_frenzy_preparation(candidate), dtype=bool)
    frenzy2 = np.full(total, _has_frenzy_preparation(enemy), dtype=bool)

    for phase in range(100):
        unresolved = (state1 != STATE_OUT) & (state2 != STATE_OUT)
        if not unresolved.any():
            break
        candidate_turn = phase % 2 == 0
        if candidate_turn:
            paralyzed = unresolved & (state1 == STATE_PARALYZED)
            recovered = paralyzed & (rng.integers(1, 7, total) <= int(candidate[2]))
            state1[recovered] = STATE_STANDING
            stunned = unresolved & (state1 == STATE_STUNNED)
            state1[stunned] = STATE_KNOCKED_DOWN
            knocked = unresolved & (state1 == STATE_KNOCKED_DOWN) & ~stunned
            state1[knocked] = STATE_STANDING
            stood1 = knocked
            stood2 = np.zeros(total, dtype=bool)
        else:
            paralyzed = unresolved & (state2 == STATE_PARALYZED)
            recovered = paralyzed & (rng.integers(1, 7, total) <= int(enemy[2]))
            state2[recovered] = STATE_STANDING
            stunned = unresolved & (state2 == STATE_STUNNED)
            state2[stunned] = STATE_KNOCKED_DOWN
            knocked = unresolved & (state2 == STATE_KNOCKED_DOWN) & ~stunned
            state2[knocked] = STATE_STANDING
            stood2 = knocked
            stood1 = np.zeros(total, dtype=bool)

        both = unresolved & (state1 == STATE_STANDING) & (state2 == STATE_STANDING)
        only1 = unresolved & (state1 == STATE_STANDING) & ~both
        only2 = unresolved & (state2 == STATE_STANDING) & ~both
        first_is_candidate = only1.copy()
        first_round = phase < 2
        if both.any():
            first1 = first_round and _weapon_attacks_first(int(candidate[6]))
            first2 = first_round and _weapon_attacks_first(int(enemy[6]))
            if phase == 0:
                first1 = True
                first2 = first2 or bool(int(enemy[9]) & SKILL_CAT_REFLEXES)
            last1 = _weapon_attacks_last(candidate)
            last2 = _weapon_attacks_last(enemy)
            last1_rows = last1 | stood1
            last2_rows = last2 | stood2
            decided1 = both & ~last1_rows & last2_rows
            decided2 = both & last1_rows & ~last2_rows
            first_is_candidate[decided1] = True
            undecided = both & ~(decided1 | decided2)
            if first1 != first2:
                if first1:
                    first_is_candidate[undecided] = True
                undecided[:] = False
            if undecided.any():
                i1 = np.maximum(
                    1, _combat_initiative(candidate) + crimson1 - initiative_penalty1
                )
                i2 = np.maximum(
                    1, _combat_initiative(enemy) + crimson2 - initiative_penalty2
                )
                first_is_candidate[undecided & (i1 > i2)] = True
                tied = undecided & (i1 == i2)
                first_is_candidate[tied] = rng.random(int(tied.sum())) < 0.5

        first1_rows = np.flatnonzero(unresolved & first_is_candidate)
        first2_rows = np.flatnonzero(unresolved & ~first_is_candidate)
        _vector_attack_phase(
            candidate, enemy, first1_rows, wounds2, state2, amulet2, rng,
            first_round, phase == 0, False, initiative_penalty2, frenzy1,
        )
        frenzy2[(state2 == STATE_KNOCKED_DOWN) | (state2 == STATE_STUNNED)] = False
        reply2 = first1_rows[(state2[first1_rows] == STATE_STANDING)]
        if _prevents_first_reply(candidate, first_round):
            reply2 = np.empty(0, dtype=np.int64)
        _vector_attack_phase(
            enemy, candidate, reply2, wounds1, state1, amulet1, rng,
            first_round, False, phase == 0, initiative_penalty1, frenzy2,
        )
        frenzy1[(state1 == STATE_KNOCKED_DOWN) | (state1 == STATE_STUNNED)] = False
        _vector_attack_phase(
            enemy, candidate, first2_rows, wounds1, state1, amulet1, rng,
            first_round, False, phase == 0, initiative_penalty1, frenzy2,
        )
        frenzy1[(state1 == STATE_KNOCKED_DOWN) | (state1 == STATE_STUNNED)] = False
        reply1 = first2_rows[(state1[first2_rows] == STATE_STANDING)]
        if _prevents_first_reply(enemy, first_round):
            reply1 = np.empty(0, dtype=np.int64)
        _vector_attack_phase(
            candidate, enemy, reply1, wounds2, state2, amulet2, rng,
            first_round, phase == 0, False, initiative_penalty2, frenzy1,
        )
        frenzy2[(state2 == STATE_KNOCKED_DOWN) | (state2 == STATE_STUNNED)] = False

    wins = int(np.count_nonzero((state2 == STATE_OUT) & (state1 != STATE_OUT)))
    resolved = int(np.count_nonzero((state1 == STATE_OUT) | (state2 == STATE_OUT)))
    return wins, resolved


def _choice_weight(cost, rarity):
    return 1.0 / (1.0 + cost / 35.0 + rarity / 5.0)


def _weighted_choice(rng, options):
    weights = np.array([_choice_weight(cost, rarity) for _, cost, rarity in options])
    weights /= weights.sum()
    return options[int(rng.choice(len(options), p=weights))][0]


def _random_enemy_config(name, level, rng):
    profile = ENEMY_PROFILES[name]
    equipment = profile["equipment"]
    config = {key: profile[key] for key in ("HA", "F", "R", "H", "I", "A")}
    config["skills"] = list(profile.get("skills", []))
    config["main_weapon"] = _weighted_choice(rng, equipment["main"])
    config["off_hand"] = _weighted_choice(rng, equipment["off"])
    config["armor"] = _weighted_choice(rng, equipment["armor"])
    config["weapon_material"] = "Normal"
    config["has_luck_amulet"] = False
    config["preparation"] = "Ninguno"
    config["main_poison"] = "Sin veneno"
    config["offhand_poison"] = "Sin veneno"
    consumables = equipment.get("consumables", [])
    can_use_consumables = name in {
        "Veterano humano", "Espadachín o duelista", "Hermana de Sigmar",
        "Jefe humano", "Jefe orco", "Asesino Skaven", "Héroe elfo",
    }
    if consumables and can_use_consumables and rng.random() < 0.18:
        weights = np.array([
            _choice_weight(cost, rarity) for _, _, cost, rarity in consumables
        ])
        weights /= weights.sum()
        kind, item_name, _, _ = consumables[
            int(rng.choice(len(consumables), p=weights))
        ]
        if kind == "preparation":
            config["preparation"] = item_name
        elif kind == "poison":
            config["main_poison"] = item_name
    helmet = equipment.get("helmet")
    config["has_helmet"] = bool(
        helmet and rng.random() < min(0.35, 2.5 * _choice_weight(*helmet) / 10.0)
    )

    advance_skills = list(SKILLS)
    for skill in config["skills"]:
        if skill in advance_skills:
            advance_skills.remove(skill)
    for _ in range(max(0, int(level))):
        choices = ["HA", "F", "R", "H", "I", "A", *advance_skills]
        choice = choices[int(rng.integers(len(choices)))]
        if choice in ("HA", "F", "R", "H", "I", "A"):
            config[choice] += 1
        elif choice not in config["skills"]:
            config["skills"].append(choice)
            advance_skills.remove(choice)
    return config


def _build_enemy_variants(names, level, seed, variants_per_profile=24):
    rng = np.random.default_rng(seed)
    fighters = []
    owners = []
    for owner, name in enumerate(names):
        for _ in range(variants_per_profile):
            fighters.append(_make_fighter(_random_enemy_config(name, level, rng)))
            owners.append(owner)
    return np.stack(fighters), np.asarray(owners, dtype=np.int64)


def _cached_enemy_variants(names, level):
    key = (tuple(names), int(level))
    variants = _ENEMY_VARIANT_CACHE.get(key)
    if variants is None:
        # El catálogo se comparte entre todas las mejoras de la misma ejecución.
        variants = _build_enemy_variants(
            key[0], key[1], 17_071 + key[1] * 997, ENEMY_VARIANTS_PER_PROFILE
        )[0]
        _ENEMY_VARIANT_CACHE[key] = variants
    return variants


def _build_cumulative_weights(names):
    weights = np.array(
        [
            ENEMY_PROFILES[name]["weight"]
            if name in ENEMY_PROFILES
            else RACIAL_WEIGHTS[name]
            for name in names
        ],
        dtype=np.float64,
    )
    cumulative = np.cumsum(weights)
    cumulative /= cumulative[-1]
    cumulative[-1] = 1.0
    return cumulative


def _generate_shared_enemy_selection(names, total_simulations, seed, variants_per_profile=1):
    cumulative = _build_cumulative_weights(names)
    rng = np.random.default_rng(seed)
    profiles = np.searchsorted(
        cumulative,
        rng.random(total_simulations),
        side="right",
    ).astype(np.int64, copy=False)
    if variants_per_profile <= 1:
        return profiles
    variants = rng.integers(0, variants_per_profile, total_simulations)
    return profiles * variants_per_profile + variants


def run_single_task_optimized(args):
    enemy_level = int(args[12]) if len(args) > 12 else 0
    (
        mode, label, candidate_dict, enemy_mode, custom_enemy_dict,
        active_pool_names, enemy_indices, total_sims, seed, is_base,
        progress_queue, task_id,
    ) = args[:12]

    candidate = _make_fighter(candidate_dict)
    if enemy_mode == "custom":
        if enemy_level:
            rng = np.random.default_rng(seed + 404)
            configs = []
            base = {**custom_enemy_dict, "equipment": {
                "main": [(custom_enemy_dict["main_weapon"], 0, 0)],
                "off": [(custom_enemy_dict["off_hand"], 0, 0)],
                "armor": [(custom_enemy_dict["armor"], 0, 0)],
                "helmet": None,
            }}
            for _ in range(24):
                config = dict(custom_enemy_dict)
                config["skills"] = list(custom_enemy_dict.get("skills", []))
                for _ in range(enemy_level):
                    available_skills = [
                        skill for skill in SKILLS if skill not in config["skills"]
                    ]
                    options = ["HA", "F", "R", "H", "I", "A", *available_skills]
                    upgrade = options[int(rng.integers(len(options)))]
                    if upgrade in ("HA", "F", "R", "H", "I", "A"):
                        config[upgrade] += 1
                    elif upgrade not in config["skills"]:
                        config["skills"].append(upgrade)
                configs.append(_make_fighter(config))
            enemies = np.stack(configs)
        else:
            enemies = np.stack([_make_fighter(custom_enemy_dict)])
    else:
        enemies = _cached_enemy_variants(active_pool_names, enemy_level)

    if enemy_mode == "custom" and len(enemies) > 1:
        selection_rng = np.random.default_rng(seed + 808)
        enemy_indices = selection_rng.integers(0, len(enemies), total_sims, dtype=np.int64)

    matchup = _build_matchups(candidate, enemies)
    wins, resolved = _simulate_batch_precomputed(
        candidate, enemies, enemy_indices,
        matchup[0], matchup[1], matchup[2], matchup[3], matchup[4],
        matchup[5], matchup[6], total_sims, seed,
    )
    if progress_queue is not None:
        progress_queue.put(("chunk", task_id, total_sims))

    win_rate = (wins / resolved) * 100.0 if resolved else 0.0
    return mode, label, win_rate, is_base


def run_task_batch(tasks):
    """Ejecuta un grupo de comparaciones dentro de un proceso trabajador."""
    return [run_single_task_optimized(task) for task in tasks]
