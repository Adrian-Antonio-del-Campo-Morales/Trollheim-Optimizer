"""Compara rendimiento y resultados del kernel Cython con el motor NumPy."""

import argparse
import math
from pathlib import Path
import sys
import time

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from trollheim_simulator import engine  # noqa: E402


BASE = {
    "HA": 3, "F": 3, "R": 3, "H": 1, "I": 3, "A": 1,
    "skills": [], "main_weapon": "Espada", "off_hand": "Ninguna",
    "armor": "Sin Armadura",
}

CASES = (
    ("Espada contra maza", {}, {"main_weapon": "Maza"}),
    ("Dos armas", {"off_hand": "Daga"}, {"off_hand": "Maza"}),
    (
        "Arma 2H contra escudo",
        {"main_weapon": "Arma a dos manos"},
        {"off_hand": "Escudo", "armor": "Armadura Ligera"},
    ),
    (
        "Varios ataques y heridas",
        {"HA": 4, "A": 3, "off_hand": "Hacha"},
        {"HA": 4, "H": 2, "R": 4, "armor": "Armadura Pesada"},
    ),
    (
        "Armadura pesada",
        {"main_weapon": "Hacha", "armor": "Armadura de Gromril", "off_hand": "Escudo"},
        {"main_weapon": "Daga", "armor": "Armadura de Gromril", "off_hand": "Escudo"},
    ),
)


def run_engine(candidate, enemy, total, seed, native):
    previous = engine._simulate_simple_native
    engine._simulate_simple_native = native
    try:
        started = time.perf_counter()
        wins, resolved = engine._simulate_batch(
            candidate,
            np.asarray([enemy]),
            np.zeros(total, dtype=np.int8),
            total,
            seed,
        )
        return wins / resolved, resolved, time.perf_counter() - started
    finally:
        engine._simulate_simple_native = previous


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-n", "--simulations", type=int, default=500_000)
    args = parser.parse_args()
    native = engine._simulate_simple_native
    if native is None:
        raise SystemExit("Compila primero el kernel con build_NATIVE_KERNEL.bat.")

    print(f"Muestra independiente por motor: {args.simulations:,}")
    worst_z = 0.0
    speedups = []
    for index, (label, candidate_changes, enemy_changes) in enumerate(CASES):
        candidate = engine._make_fighter(BASE | candidate_changes)
        enemy = engine._make_fighter(BASE | enemy_changes)
        native_rate, native_resolved, native_time = run_engine(
            candidate, enemy, args.simulations, 1_000 + index, native
        )
        python_rate, python_resolved, python_time = run_engine(
            candidate, enemy, args.simulations, 9_000 + index, None
        )
        standard_error = math.sqrt(
            native_rate * (1 - native_rate) / native_resolved
            + python_rate * (1 - python_rate) / python_resolved
        )
        z_score = (native_rate - python_rate) / standard_error
        speedup = python_time / native_time
        worst_z = max(worst_z, abs(z_score))
        speedups.append(speedup)
        print(
            f"{label:28} Cython {native_rate:8.4%}  NumPy {python_rate:8.4%}  "
            f"Dif. {(native_rate - python_rate) * 100:+.3f} %  "
            f"z {z_score:+.2f}  {speedup:.1f}x"
        )
    print(f"Aceleración media: {sum(speedups) / len(speedups):.1f}x; |z| máximo: {worst_z:.2f}")


if __name__ == "__main__":
    main()
