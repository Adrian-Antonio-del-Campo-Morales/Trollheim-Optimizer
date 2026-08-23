"""Interfaz gráfica Tkinter del simulador."""

import os
import queue
import random
import re
import threading
import time
import tkinter as tk
import unicodedata
from concurrent.futures import ProcessPoolExecutor, as_completed
from itertools import combinations_with_replacement
from tkinter import filedialog, font as tkfont, messagebox, ttk

import numpy as np

from .engine import (
    ENEMY_VARIANTS_PER_PROFILE,
    _generate_shared_enemy_selection,
    effective_fighter_key,
    run_task_batch,
    run_single_task_optimized,
)
from .enemies import DIFFICULTIES, ENEMY_PROFILES, profiles_for_difficulties
from .candidate_catalog import (
    CATEGORY_LABELS,
    CATEGORY_ORDER,
    GENERAL_SKILL_CATEGORIES,
    GENERAL_SKILL_DESCRIPTIONS,
    armour_descriptions,
    find_profile,
    load_bands,
    usable_main_weapons,
    usable_offhand_options,
    weapon_descriptions,
)
from .rules import *
from .workbooks import CandidateWorkbookError, load_candidate_workbook, save_candidate_workbook


COMBAT_MODES = (
    ("Single", "Arma + mano libre"),
    ("Shield", "Arma + escudo"),
    ("Dual", "Dos armas"),
    ("TwoHand", "Arma a dos manos"),
)
DELTA_POSITIVE = "#16833b"
DELTA_NEGATIVE = "#c62828"
DELTA_NEUTRAL = "#666666"
DEFAULT_COMBO_SIMULATIONS = 10_000
PROGRESS_POLL_MS = 100
PROGRESS_ANIMATION_MS = 60
TASK_GROUP_SIZE = 2


def _configure_simulation_worker():
    """Deja que Windows atienda la interfaz antes que a los procesos de cálculo."""
    if os.name != "nt":
        return
    try:
        import ctypes

        below_normal_priority = 0x00004000
        process = ctypes.windll.kernel32.GetCurrentProcess()
        ctypes.windll.kernel32.SetPriorityClass(
            process, below_normal_priority
        )
    except (AttributeError, OSError):
        pass

# Tooltips

class ToolTip:

    def __init__(
        self,
        widget,
        text,
    ):
        self.widget = widget
        self.text = text
        self.tip_window = None

        self.widget.bind(
            "<Enter>",
            self.show_tip,
        )

        self.widget.bind(
            "<Leave>",
            self.hide_tip,
        )

    def show_tip(
        self,
        event=None,
    ):
        text = self.text() if callable(self.text) else self.text
        if self.tip_window or not text:
            return

        x, y, _cx, cy = (
            self.widget.bbox("insert")
            if self.widget.bbox("insert")
            else (0, 0, 0, 0)
        )

        x = (
            x
            + self.widget.winfo_rootx()
            + 25
        )

        y = (
            y
            + self.widget.winfo_rooty()
            + 20
        )

        self.tip_window = tw = tk.Toplevel(
            self.widget
        )

        tw.wm_overrideredirect(True)

        tw.wm_geometry(
            f"+{x}+{y}"
        )

        label = tk.Label(
            tw,
            text=text,
            justify=tk.LEFT,
            background="#ffffe0",
            relief=tk.SOLID,
            borderwidth=1,
            font=("tahoma", 8, "normal"),
            wraplength=420,
        )

        label.pack(
            ipadx=4,
            ipady=2,
        )

    def hide_tip(
        self,
        event=None,
    ):
        tw = self.tip_window
        self.tip_window = None
        if tw:
            tw.destroy()


# Editor de guerreros

class WarriorConfigFrame(ttk.LabelFrame):

    def __init__(
        self,
        parent,
        title,
        show_house_rules=False,
        skill_descriptions=None,
        skill_categories=None,
    ):
        super().__init__(
            parent,
            text=title,
        )

        self.stats = {
            "HA": 4,
            "F": 3,
            "R": 3,
            "H": 1,
            "I": 4,
            "A": 1,
        }

        self.skill_descriptions = skill_descriptions or SKILL_DESCRIPTIONS
        self.skill_categories = skill_categories or {
            skill: "combat" for skill in self.skill_descriptions
        }
        self.skills = {
            s: tk.BooleanVar()
            for s in self.skill_descriptions
        }

        self.eq_main_general = tk.StringVar(value=WEAPONS_GENERAL[0])
        self.eq_main_exclusive = tk.StringVar(value="Ninguna")

        self.eq_off_general = tk.StringVar(value="Ninguna")
        self.eq_off_exclusive = tk.StringVar(value="Ninguna")

        self.eq_main_material = tk.StringVar(value=WEAPON_MATERIALS[0])
        self.eq_off_material = tk.StringVar(value=WEAPON_MATERIALS[0])

        self.eq_has_helmet = tk.BooleanVar(
            value=False
        )

        self.eq_armor = tk.StringVar(
            value=ARMORS[0]
        )
        self.show_house_rules = show_house_rules
        self.house_rule_offhand_penalty = tk.BooleanVar(value=False)
        self.house_rule_dual_penalty = tk.BooleanVar(value=False)
        self.undead_or_possessed = tk.BooleanVar(value=False)

        self.attr_entries = {}
        self.attr_buttons = []
        self.interactable_widgets = []
        self.skill_widgets = {}
        self.option_filter = None

        self._build_gui()

    def _build_gui(self):

        ttk.Label(
            self,
            text="Atributos Básicos",
            font=("Arial", 12, "bold"),
        ).pack(
            pady=(5, 2)
        )

        attr_frame = ttk.Frame(self)

        attr_frame.pack(
            pady=2
        )

        for i, (attr, val) in enumerate(
            self.stats.items()
        ):

            col = i * 4

            ttk.Label(
                attr_frame,
                text=f"{attr}:",
                font=("Arial", 11, "bold"),
            ).grid(
                row=0,
                column=col,
                padx=(4, 2),
            )

            btn_sub = ttk.Button(
                attr_frame,
                text="-",
                width=3,
                command=lambda a=attr:
                    self.change_stat(a, -1),
            )

            btn_sub.grid(
                row=0,
                column=col + 1,
                padx=1,
            )

            ent = ttk.Entry(
                attr_frame,
                width=5,
                justify="center",
                font=("Arial", 11, "bold"),
            )

            ent.insert(
                0,
                str(val),
            )

            ent.grid(
                row=0,
                column=col + 2,
                padx=1,
            )

            btn_add = ttk.Button(
                attr_frame,
                text="+",
                width=3,
                command=lambda a=attr:
                    self.change_stat(a, 1),
            )

            btn_add.grid(
                row=0,
                column=col + 3,
                padx=(1, 5),
            )

            self.attr_entries[attr] = ent

            self.attr_buttons.extend(
                [
                    btn_sub,
                    btn_add,
                ]
            )

            self.interactable_widgets.extend(
                [
                    ent,
                    btn_sub,
                    btn_add,
                ]
            )

        ttk.Separator(
            self,
            orient="horizontal",
        ).pack(
            fill="x",
            pady=5,
        )

        ttk.Label(
            self,
            text="Equipamiento Base",
            font=("Arial", 10, "bold"),
        ).pack(
            pady=(5, 2)
        )

        eq_frame = ttk.Frame(self)

        eq_frame.pack(
            pady=2,
            fill="x",
            padx=15,
        )

        eq_frame.columnconfigure(0, weight=1, uniform="hands")
        eq_frame.columnconfigure(1, weight=1, uniform="hands")

        main_hand = ttk.LabelFrame(eq_frame, text=" Mano principal ")
        main_hand.grid(row=0, column=0, sticky="nsew", padx=(0, 4))
        main_hand.columnconfigure(1, weight=1)
        ttk.Label(main_hand, text="Generales:").grid(row=0, column=0, sticky="e", padx=(7, 2), pady=2)
        self.cb_main = ttk.Combobox(
            main_hand, textvariable=self.eq_main_general,
            values=("Ninguna", *WEAPONS_GENERAL),
            state="readonly", width=20,
        )
        self.cb_main.grid(row=0, column=1, sticky="ew", padx=(2, 7), pady=2)
        self.cb_main.bind("<<ComboboxSelected>>", lambda event: self._select_weapon("main", "general"))
        ToolTip(self.cb_main, lambda: weapon_descriptions().get(self.eq_main_general.get(), ""))
        ttk.Label(main_hand, text="Especiales:").grid(row=1, column=0, sticky="e", padx=(7, 2), pady=2)
        self.cb_main_exclusive = ttk.Combobox(
            main_hand, textvariable=self.eq_main_exclusive,
            values=(
                "Ninguna",
                *(weapon for weapon in WEAPONS_EXCLUSIVE
                  if weapon not in MAIN_HAND_FORBIDDEN_WEAPONS),
            ),
            state="readonly", width=20,
        )
        self.cb_main_exclusive.grid(row=1, column=1, sticky="ew", padx=(2, 7), pady=2)
        self.cb_main_exclusive.bind(
            "<<ComboboxSelected>>", lambda event: self._select_weapon("main", "exclusive")
        )
        ToolTip(self.cb_main_exclusive, lambda: weapon_descriptions().get(self.eq_main_exclusive.get(), ""))
        ttk.Label(main_hand, text="Material:").grid(row=2, column=0, sticky="e", padx=(7, 2), pady=2)
        self.cb_main_material = ttk.Combobox(
            main_hand, textvariable=self.eq_main_material, values=WEAPON_MATERIALS,
            state="readonly", width=20,
        )
        self.cb_main_material.grid(row=2, column=1, sticky="ew", padx=(2, 7), pady=2)

        off_hand = ttk.LabelFrame(eq_frame, text=" Mano secundaria ")
        off_hand.grid(row=0, column=1, sticky="nsew", padx=(4, 0))
        off_hand.columnconfigure(1, weight=1)
        ttk.Label(off_hand, text="Generales:").grid(row=0, column=0, sticky="e", padx=(7, 2), pady=2)
        self.cb_offhand = ttk.Combobox(
            off_hand, textvariable=self.eq_off_general, values=OFFHAND_GENERAL,
            state="readonly", width=20,
        )
        self.cb_offhand.grid(row=0, column=1, sticky="ew", padx=(2, 7), pady=2)
        self.cb_offhand.bind("<<ComboboxSelected>>", lambda event: self._select_weapon("off", "general"))
        ToolTip(self.cb_offhand, lambda: weapon_descriptions().get(self.eq_off_general.get(), ""))
        ttk.Label(off_hand, text="Especiales:").grid(row=1, column=0, sticky="e", padx=(7, 2), pady=2)
        self.cb_off_exclusive = ttk.Combobox(
            off_hand, textvariable=self.eq_off_exclusive, values=OFFHAND_EXCLUSIVE,
            state="readonly", width=20,
        )
        self.cb_off_exclusive.grid(row=1, column=1, sticky="ew", padx=(2, 7), pady=2)
        self.cb_off_exclusive.bind(
            "<<ComboboxSelected>>", lambda event: self._select_weapon("off", "exclusive")
        )
        ToolTip(self.cb_off_exclusive, lambda: weapon_descriptions().get(self.eq_off_exclusive.get(), ""))
        ttk.Label(off_hand, text="Material:").grid(row=2, column=0, sticky="e", padx=(7, 2), pady=2)
        self.cb_off_material = ttk.Combobox(
            off_hand, textvariable=self.eq_off_material, values=WEAPON_MATERIALS,
            state="readonly", width=20,
        )
        self.cb_off_material.grid(row=2, column=1, sticky="ew", padx=(2, 7), pady=2)

        ttk.Separator(eq_frame, orient="horizontal").grid(
            row=1, column=0, columnspan=2, sticky="ew", pady=5
        )

        defense = ttk.Frame(eq_frame)
        defense.grid(row=2, column=0, columnspan=2, sticky="ew")
        for column in range(2):
            defense.columnconfigure(column, weight=1, uniform="defense")

        armor_cell = ttk.Frame(defense)
        armor_cell.grid(row=0, column=0, sticky="ew")
        ttk.Label(armor_cell, text="Armadura:").pack(side="left", padx=(0, 4))

        self.cb_armor = ttk.Combobox(
            armor_cell,
            textvariable=self.eq_armor,
            values=ARMORS,
            state="readonly",
            width=18,
        )
        self.cb_armor.pack(side="left", fill="x", expand=True)
        self.cb_armor.bind("<<ComboboxSelected>>", self.on_equipment_change)
        ToolTip(self.cb_armor, lambda: armour_descriptions().get(self.eq_armor.get(), ""))

        self.chk_helmet = ttk.Checkbutton(
            defense,
            text="Casco",
            variable=self.eq_has_helmet,
        )
        self.chk_helmet.grid(row=0, column=1)

        self.interactable_widgets.extend(
            [
                self.cb_main,
                self.cb_main_exclusive,
                self.cb_offhand,
                self.cb_off_exclusive,
                self.cb_main_material,
                self.cb_off_material,
                self.cb_armor,
                self.chk_helmet,
            ]
        )

        if self.show_house_rules:
            house_rules = ttk.LabelFrame(self, text=" Reglas de la casa ")
            house_rules.pack(fill="x", padx=12, pady=(0, 5))
            black_rule = tk.Checkbutton(
                house_rules,
                text=(
                    "regla de la casa para hacer que llevar dos armas no este tan roto "
                    "y sea siempre la mejor alternativa sin importar lo ways que esten "
                    "tus armas o tus reglas ni nada en todo el juego"
                ),
                variable=self.house_rule_offhand_penalty,
                anchor="w",
                justify="left",
                wraplength=720,
            )
            black_rule.pack(fill="x", padx=6, pady=(3, 1))
            red_rule = tk.Checkbutton(
                house_rules,
                text=(
                    "regla de la casa para hacer que llevar dos armas no este tan roto "
                    "y sea siempre la mejor alternativa sin importar lo ways que esten "
                    "tus armas o tus reglas ni nada en todo el juego"
                ),
                variable=self.house_rule_dual_penalty,
                foreground="#c62828",
                activeforeground="#c62828",
                anchor="w",
                justify="left",
                wraplength=720,
            )
            red_rule.pack(fill="x", padx=6, pady=(1, 3))
            self.interactable_widgets.extend((black_rule, red_rule))

        ttk.Separator(
            self,
            orient="horizontal",
        ).pack(
            fill="x",
            pady=5,
        )

        ttk.Label(
            self,
            text="Habilidades Base",
            font=("Arial", 10, "bold"),
        ).pack(
            pady=(5, 2)
        )

        skill_frame = ttk.Frame(self)
        self.skill_frame = skill_frame

        skill_frame.pack(
            pady=2
        )

        self.skill_column_frames = {}
        for column, category in enumerate(CATEGORY_ORDER):
            skill_frame.columnconfigure(column, weight=1, uniform="skill_categories")
            category_frame = ttk.LabelFrame(
                skill_frame, text=f" {CATEGORY_LABELS[category]} "
            )
            category_frame.grid(row=0, column=column, sticky="nsew", padx=1)
            self.skill_column_frames[category] = category_frame

        for sk in self.skills:
            category = self.skill_categories.get(sk, "special")

            chk = ttk.Checkbutton(
                self.skill_column_frames[category],
                text=sk,
                variable=self.skills[sk],
            )

            chk.pack(
                anchor="w",
                padx=3,
                pady=1,
            )

            ToolTip(
                chk,
                self.skill_descriptions.get(
                    sk,
                    "Sin descripción",
                ),
            )

            self.interactable_widgets.append(
                chk
            )
            self.skill_widgets[sk] = chk

        traits = ttk.Frame(self)
        traits.pack(pady=(2, 4))
        unholy = ttk.Checkbutton(
            traits,
            text="No muerto o Poseído",
            variable=self.undead_or_possessed,
        )
        unholy.pack(side="left", padx=7)
        ToolTip(
            unholy,
            "Activa reglas condicionales como el +1 para herir del Martillo Sigmarita.",
        )
        self.interactable_widgets.append(unholy)

    def set_option_filter(self, profile=None, extra_skills=()):
        """Limita los controles a las opciones modeladas y legales del perfil."""
        self.option_filter = profile
        if profile is None:
            main_allowed = tuple(WEAPONS_MAIN)
            off_allowed = tuple(OFF_HAND_OPTIONS)
            armor_allowed = tuple(ARMORS)
            material_allowed = tuple(WEAPON_MATERIALS)
            skill_allowed = set(GENERAL_SKILL_DESCRIPTIONS) | set(extra_skills)
            helmet_allowed = True
        else:
            main_allowed = usable_main_weapons(profile)
            off_allowed = usable_offhand_options(profile)
            armor_allowed = ("Sin Armadura", *profile.armors)
            material_allowed = profile.materials
            skill_allowed = set(profile.skills)
            helmet_allowed = profile.helmet_allowed

        self._allowed_main = set(main_allowed)
        self._allowed_off = set(off_allowed)
        self._allowed_armor = set(armor_allowed)
        self._allowed_materials = set(material_allowed)
        self._helmet_allowed = helmet_allowed
        self.cb_main.config(values=("Ninguna", *(w for w in WEAPONS_GENERAL if w in self._allowed_main)))
        self.cb_main_exclusive.config(values=(
            "Ninguna", *(w for w in WEAPONS_EXCLUSIVE if w in self._allowed_main)
        ))
        self.cb_offhand.config(values=tuple(w for w in OFFHAND_GENERAL if w in self._allowed_off))
        self.cb_off_exclusive.config(values=tuple(w for w in OFFHAND_EXCLUSIVE if w in self._allowed_off))
        self.cb_armor.config(values=tuple(a for a in ARMORS if a in self._allowed_armor))
        self.cb_main_material.config(values=tuple(m for m in WEAPON_MATERIALS if m in self._allowed_materials))
        self.cb_off_material.config(values=tuple(m for m in WEAPON_MATERIALS if m in self._allowed_materials))

        visible = [skill for skill in self.skills if skill in skill_allowed]
        for widget in self.skill_widgets.values():
            widget.pack_forget()
        for skill in visible:
            self.skill_widgets[skill].pack(anchor="w", padx=3, pady=1)
        for skill, variable in self.skills.items():
            if skill not in skill_allowed:
                variable.set(False)

        if self._selected_main_weapon() not in self._allowed_main:
            replacement = next(iter(main_allowed), "Daga")
            self.eq_main_general.set(replacement if replacement in WEAPONS_GENERAL else "Ninguna")
            self.eq_main_exclusive.set(replacement if replacement in WEAPONS_EXCLUSIVE else "Ninguna")
        if self._selected_offhand() not in self._allowed_off:
            self.eq_off_general.set("Ninguna")
            self.eq_off_exclusive.set("Ninguna")
        if self.eq_armor.get() not in self._allowed_armor:
            self.eq_armor.set("Sin Armadura")
        if self.eq_main_material.get() not in self._allowed_materials:
            self.eq_main_material.set("Sin material")
        if self.eq_off_material.get() not in self._allowed_materials:
            self.eq_off_material.set("Sin material")
        if not helmet_allowed:
            self.eq_has_helmet.set(False)
        self.chk_helmet.config(state="normal" if helmet_allowed else "disabled")
        self.on_equipment_change()

    def change_stat(
        self,
        attr,
        delta,
    ):
        try:
            current = int(
                self.attr_entries[attr].get()
            )

        except ValueError:
            current = 0

        new_value = max(
            0,
            current + delta,
        )

        self.attr_entries[attr].delete(
            0,
            tk.END,
        )

        self.attr_entries[attr].insert(
            0,
            str(new_value),
        )

    def set_enabled(
        self,
        enabled=True,
    ):
        state = (
            "normal"
            if enabled
            else "disabled"
        )

        for widget in self.interactable_widgets:

            if isinstance(
                widget,
                ttk.Combobox,
            ):

                widget.config(
                    state=(
                        "readonly"
                        if enabled
                        else "disabled"
                    )
                )

            else:

                widget.config(
                    state=state
                )

        if enabled:
            self.on_equipment_change()

    def _select_weapon(self, hand, category):
        if hand == "main":
            if category == "general":
                self.eq_main_exclusive.set("Ninguna")
            elif self.eq_main_exclusive.get() != "Ninguna":
                self.eq_main_general.set("Ninguna")
            elif self.eq_main_general.get() == "Ninguna":
                self.eq_main_general.set("Daga")
        else:
            if category == "general":
                self.eq_off_exclusive.set("Ninguna")
            elif self.eq_off_exclusive.get() != "Ninguna":
                self.eq_off_general.set("Ninguna")
        self.on_equipment_change()

    def _selected_main_weapon(self):
        exclusive = self.eq_main_exclusive.get()
        general = self.eq_main_general.get()
        return exclusive if exclusive != "Ninguna" else (
            general if general != "Ninguna" else "Daga"
        )

    def _selected_offhand(self):
        exclusive = self.eq_off_exclusive.get()
        return exclusive if exclusive != "Ninguna" else self.eq_off_general.get()

    def on_equipment_change(self, event=None):
        main_weapon = self._selected_main_weapon()
        off_disabled = (
            main_weapon in TWO_HANDED_WEAPONS
            or main_weapon in PAIRED_WEAPONS
            or main_weapon == "Arma natural"
        )

        if main_weapon == "Lanza":
            self.cb_offhand.config(values=tuple(v for v in ("Ninguna", "Escudo", "Rodela") if v in self._allowed_off))
            self.cb_off_exclusive.config(state="disabled")
            self.eq_off_exclusive.set("Ninguna")
            if self.eq_off_general.get() not in ("Ninguna", "Escudo", "Rodela"):
                self.eq_off_general.set("Ninguna")
        elif main_weapon == "Mangual":
            self.cb_offhand.config(values=tuple(v for v in ("Ninguna", "Escudo") if v in self._allowed_off))
            self.cb_off_exclusive.config(state="disabled")
            self.eq_off_exclusive.set("Ninguna")
            if self.eq_off_general.get() not in ("Ninguna", "Escudo"):
                self.eq_off_general.set("Ninguna")
        elif main_weapon in ("Rebanadora", "Pinchagarrapatos"):
            self.cb_offhand.config(values=tuple(v for v in ("Ninguna", "Escudo") if v in self._allowed_off))
            self.cb_off_exclusive.config(
                values=tuple(v for v in ("Ninguna", "Guantelete con Pincho") if v in self._allowed_off),
                state="readonly",
            )
            if self.eq_off_general.get() not in ("Ninguna", "Escudo"):
                self.eq_off_general.set("Ninguna")
            if self.eq_off_exclusive.get() not in (
                "Ninguna", "Guantelete con Pincho",
            ):
                self.eq_off_exclusive.set("Ninguna")
        else:
            self.cb_offhand.config(values=tuple(v for v in OFFHAND_GENERAL if v in self._allowed_off))
            self.cb_off_exclusive.config(values=tuple(v for v in OFFHAND_EXCLUSIVE if v in self._allowed_off))
            self.cb_off_exclusive.config(state="readonly")

        armor = self.eq_armor.get()
        forbidden_defences = set()
        if armor in ("Cuero Endurecido", "Ropajes de Ninja"):
            forbidden_defences.add("Escudo")
        elif armor in ("Túnica de Mago", "Ropajes de Asesino Eshin"):
            forbidden_defences.update(("Escudo", "Rodela"))
        if forbidden_defences:
            allowed = tuple(
                value for value in self.cb_offhand.cget("values")
                if value not in forbidden_defences
            )
            self.cb_offhand.config(values=allowed)
            if self.eq_off_general.get() in forbidden_defences:
                self.eq_off_general.set("Ninguna")

        if off_disabled:
            self.eq_off_general.set("Ninguna")
            self.eq_off_exclusive.set("Ninguna")
            self.cb_offhand.config(state="disabled")
            self.cb_off_exclusive.config(state="disabled")
            self.cb_off_material.config(state="disabled")
        else:
            self.cb_offhand.config(state="readonly")
            self.cb_off_material.config(state="readonly")
        if not self._helmet_allowed:
            self.chk_helmet.config(state="disabled")

    def get_config_dict(self):

        result = {}

        for key, entry in (
            self.attr_entries.items()
        ):
            result[key] = int(
                entry.get()
            )

        result["skills"] = [
            skill
            for skill, variable
            in self.skills.items()
            if variable.get()
        ]

        result["main_weapon"] = self._selected_main_weapon()
        result["off_hand"] = self._selected_offhand()
        result["main_weapon_material"] = self.eq_main_material.get()
        result["offhand_material"] = self.eq_off_material.get()
        result["weapon_material"] = result["main_weapon_material"]
        result["preparation"] = "Ninguno"
        result["main_poison"] = "Sin veneno"
        result["offhand_poison"] = "Sin veneno"

        result["has_helmet"] = (
            self.eq_has_helmet.get()
        )

        result["has_luck_amulet"] = False
        result["house_rule_offhand_penalty"] = self.house_rule_offhand_penalty.get()
        result["house_rule_dual_penalty"] = self.house_rule_dual_penalty.get()
        result["undead_or_possessed"] = self.undead_or_possessed.get()

        result["armor"] = (
            self.eq_armor.get()
        )

        return result

    def load_config(self, config):
        for attribute, entry in self.attr_entries.items():
            entry.delete(0, tk.END)
            entry.insert(0, str(config.get(attribute, self.stats[attribute])))

        selected_skills = set(config.get("skills", ()))
        if "Experto en Esgrima (Cimitarra)" in selected_skills:
            selected_skills.discard("Experto en Esgrima (Cimitarra)")
            selected_skills.add("Experto en Esgrima")
        for skill, variable in self.skills.items():
            variable.set(skill in selected_skills)

        main_weapon = config.get("main_weapon", WEAPONS_GENERAL[0])
        off_hand = config.get("off_hand", "Ninguna")
        if main_weapon in MAIN_HAND_FORBIDDEN_WEAPONS:
            # Compatibilidad con configuraciones antiguas que guardaban el
            # Guantelete Solar en la mano equivocada.
            off_hand = main_weapon
            main_weapon = "Daga"
        self.eq_main_general.set(
            "Ninguna" if main_weapon in WEAPONS_EXCLUSIVE else main_weapon
        )
        self.eq_main_exclusive.set(
            main_weapon if main_weapon in WEAPONS_EXCLUSIVE else "Ninguna"
        )
        self.eq_off_general.set(
            "Ninguna" if off_hand in OFFHAND_EXCLUSIVE else off_hand
        )
        self.eq_off_exclusive.set(
            off_hand if off_hand in OFFHAND_EXCLUSIVE else "Ninguna"
        )
        self.eq_main_material.set(config.get("main_weapon_material", "Normal"))
        self.eq_off_material.set(config.get("offhand_material", "Normal"))
        self.eq_armor.set(config.get("armor", ARMORS[0]))
        self.eq_has_helmet.set(config.get("has_helmet", False))
        self.house_rule_offhand_penalty.set(
            config.get("house_rule_offhand_penalty", False)
        )
        self.house_rule_dual_penalty.set(config.get("house_rule_dual_penalty", False))
        self.undead_or_possessed.set(config.get("undead_or_possessed", False))
        self.on_equipment_change()


class EnemyProfileEditor(ttk.Frame):
    """Editor completo de un rival manual, materializado solo cuando se ve."""

    def __init__(self, parent, bands, initial=None, on_name_change=None):
        super().__init__(parent)
        self.bands = bands
        self.band_by_name = {band.name: band for band in bands}
        self.on_name_change = on_name_change
        self.name = tk.StringVar(value="Enemigo")
        self.band_id = tk.StringVar()
        self.profile_id = tk.StringVar()
        self.status = tk.StringVar(value="Selección libre")

        selector = ttk.Frame(self)
        selector.pack(fill="x", padx=8, pady=(5, 2))
        for column in (1, 3, 5):
            selector.columnconfigure(column, weight=1)
        ttk.Label(selector, text="Nombre:").grid(row=0, column=0, padx=(0, 3))
        name_entry = ttk.Entry(selector, textvariable=self.name)
        name_entry.grid(row=0, column=1, sticky="ew", padx=(0, 8))
        ttk.Label(selector, text="Banda:").grid(row=0, column=2, padx=(0, 3))
        self.band_combo = ttk.Combobox(
            selector, state="readonly",
            values=("Selección libre", *(band.name for band in bands)),
        )
        self.band_combo.grid(row=0, column=3, sticky="ew", padx=(0, 8))
        ttk.Label(selector, text="Guerrero:").grid(row=0, column=4, padx=(0, 3))
        self.profile_combo = ttk.Combobox(selector, state="disabled")
        self.profile_combo.grid(row=0, column=5, sticky="ew")
        ttk.Label(selector, textvariable=self.status, font=("Arial", 8, "italic")).grid(
            row=1, column=0, columnspan=6, sticky="w", pady=(3, 0)
        )
        self.band_combo.bind("<<ComboboxSelected>>", self._band_changed)
        self.profile_combo.bind("<<ComboboxSelected>>", self._profile_changed)
        self.name.trace_add("write", self._name_changed)

        descriptions = dict(GENERAL_SKILL_DESCRIPTIONS)
        categories = dict(GENERAL_SKILL_CATEGORIES)
        for band in bands:
            descriptions.update((skill.name, skill.description) for skill in band.skills)
            for skill in band.skills:
                categories.setdefault(skill.name, "special")
        self.config = WarriorConfigFrame(
            self, "Configuración del enemigo", skill_descriptions=descriptions,
            skill_categories=categories,
        )
        self.config.pack(fill="both", expand=True, padx=5, pady=(2, 5))
        self.config.set_option_filter(None)
        self.band_combo.set("Selección libre")
        if initial:
            self.load_config(initial)

    def _name_changed(self, *_args):
        if self.on_name_change:
            self.on_name_change(self.name.get().strip() or "Enemigo")

    def _band_changed(self, _event=None):
        band = self.band_by_name.get(self.band_combo.get())
        self.profile_id.set("")
        if band is None:
            self.band_id.set("")
            self.profile_combo.set("")
            self.profile_combo.config(values=(), state="disabled")
            self.config.set_option_filter(None)
            self.status.set("Selección libre: todas las opciones comunes.")
            return
        self.band_id.set(band.band_id)
        self.profile_combo.config(values=tuple(p.name for p in band.profiles), state="readonly")
        self.profile_combo.set("Selecciona un guerrero")
        self.config.set_option_filter(None, extra_skills=(s.name for s in band.skills))
        self.status.set(f"{len(band.profiles)} perfiles disponibles.")

    def _profile_changed(self, _event=None):
        band = next((band for band in self.bands if band.band_id == self.band_id.get()), None)
        if not band:
            return
        profile = next((p for p in band.profiles if p.name == self.profile_combo.get()), None)
        if not profile:
            return
        self.profile_id.set(profile.profile_id)
        self.name.set(profile.name)
        default_weapon = next(iter(usable_main_weapons(profile)), "Daga")
        self.config.load_config({
            **profile.stats, "skills": [], "main_weapon": default_weapon,
            "off_hand": "Ninguna", "armor": "Sin Armadura",
        })
        self.config.set_option_filter(profile)
        self.status.set(f"Perfil canónico: {profile.band_name} · {profile.profile_type}.")

    def get_config_dict(self):
        result = self.config.get_config_dict()
        profile = find_profile(self.band_id.get(), self.profile_id.get())
        result.update({
            "enemy_name": self.name.get().strip() or "Enemigo",
            "enemy_band_id": self.band_id.get(),
            "enemy_profile_id": self.profile_id.get(),
            "allowed_upgrade_skills": (
                [skill for skill in profile.skills if skill in SKILLS]
                if profile else list(SKILLS)
            ),
        })
        return result

    def load_config(self, data):
        self.name.set(data.get("enemy_name", "Enemigo"))
        band_id = data.get("enemy_band_id", "")
        profile_id = data.get("enemy_profile_id", "")
        profile = find_profile(band_id, profile_id)
        if profile:
            band = next(b for b in self.bands if b.band_id == band_id)
            self.band_id.set(band_id)
            self.profile_id.set(profile_id)
            self.band_combo.set(band.name)
            self.profile_combo.config(values=tuple(p.name for p in band.profiles), state="readonly")
            self.profile_combo.set(profile.name)
            self.config.load_config(data)
            self.config.set_option_filter(profile)
            self.status.set(f"Perfil cargado: {band.name} · {profile.name}.")
        else:
            self.band_id.set("")
            self.profile_id.set("")
            self.band_combo.set("Selección libre")
            self.profile_combo.config(values=(), state="disabled")
            self.config.load_config(data)
            self.config.set_option_filter(None)

    def set_enabled(self, enabled):
        self.config.set_enabled(enabled)
        for child in self.winfo_children()[0].winfo_children():
            try:
                if child is self.band_combo:
                    child.config(state="readonly" if enabled else "disabled")
                elif child is self.profile_combo:
                    child.config(
                        state="readonly" if enabled and self.band_id.get() else "disabled"
                    )
                else:
                    child.config(state="normal" if enabled else "disabled")
            except tk.TclError:
                pass


# Ventana principal

class TrollheimApp(tk.Tk):

    def __init__(self):

        super().__init__()

        self.title(
            "Trollheim Combat Simulator - Optimizado"
        )

        book_toolbar = ttk.Frame(self, padding=(10, 6))
        book_toolbar.pack(fill="x")
        ttk.Label(book_toolbar, text="Libro de simulación", font=("Arial", 9, "bold")).pack(
            side="left"
        )
        ttk.Button(book_toolbar, text="Guardar libro…", command=self._save_candidate).pack(
            side="right"
        )
        ttk.Button(book_toolbar, text="Cargar libro…", command=self._load_candidate).pack(
            side="right", padx=(0, 6)
        )

        self.notebook = ttk.Notebook(self)

        self.notebook.pack(
            fill="both",
            expand=True,
        )

        self.enemy_check_widgets = []
        self.enemy_difficulties = {
            difficulty: tk.BooleanVar(value=True)
            for difficulty in DIFFICULTIES
        }
        self.enemy_level = tk.IntVar(value=0)
        self.enemy_mode = tk.StringVar(value="sample")
        self.simulations_improvements = tk.StringVar(value=str(TOTAL_SIMULATIONS))
        self.simulations_combos = tk.StringVar(value=str(DEFAULT_COMBO_SIMULATIONS))
        self.simulations_equipment = tk.StringVar(value=str(DEFAULT_COMBO_SIMULATIONS))
        self.simulations_weapons = tk.StringVar(value=str(DEFAULT_COMBO_SIMULATIONS))
        self.results_view = tk.StringVar(value="optimal")
        self.combo_view = tk.StringVar(value="optimal")
        self.equipment_view = tk.StringVar(value="optimal")
        self.weapon_view = tk.StringVar(value="optimal")
        self.combo_search = tk.StringVar()
        self.equipment_max_items = tk.IntVar(value=3)
        self.result_visible_modes = {mode for mode, _title in COMBAT_MODES}
        self.combo_visible_modes = {mode for mode, _title in COMBAT_MODES}
        self.equipment_visible_modes = {mode for mode, _title in COMBAT_MODES}
        self.weapon_visible_modes = {mode for mode, _title in COMBAT_MODES}
        self.equipment_item_vars = {
            label: tk.BooleanVar(
                value=label in {
                    "Armadura Ligera", "Armadura Pesada", "Casco",
                    "Amuleto de la suerte",
                }
            )
            for label, _kind, _value in self._equipment_options()
        }
        common_weapons = {
            "Daga", "Maza", "Hacha", "Espada", "Lanza", "Alabarda",
            "Arma 2H", "Mayal", "Mangual",
        }
        self.weapon_item_vars = {
            weapon: tk.BooleanVar(value=weapon in common_weapons)
            for weapon in WEAPONS_ALL
        }
        self.candidate_name = tk.StringVar(value="Candidato")
        self.candidate_band_id = tk.StringVar(value="")
        self.candidate_profile_id = tk.StringVar(value="")
        self.candidate_catalog_status = tk.StringVar(value="Selección libre: todas las opciones del simulador.")
        self.candidate_workbook_path = None
        self._candidate_bands = load_bands()
        self._band_by_name = {band.name: band for band in self._candidate_bands}
        self._warrior_snapshots = {}
        self._enemy_profiles = []
        self._active_enemy_editor_index = None
        self._active_tab_key = "candidate"
        self._tab_transitioning = False

        tab_specs = (
            ("candidate", "Candidato", self.setup_tab_candidate),
            ("enemy", "Enemigo", self.setup_tab_enemy),
            ("results", "Resultados por Mejora", self.setup_tab_results),
            ("combos", "Combos Mejoras", self.setup_tab_combos),
            ("weapons", "Configuraciones de Armas", self.setup_tab_weapons),
            ("equipment", "Equipamiento", self.setup_tab_equipment),
        )
        self._lazy_tabs = {}
        self._built_tabs = set()
        for key, title, builder in tab_specs:
            tab = ttk.Frame(self.notebook)
            self.notebook.add(tab, text=title)
            self._lazy_tabs[str(tab)] = (key, tab, builder)

        self._build_lazy_tab("candidate")
        self.notebook.bind("<<NotebookTabChanged>>", self._on_tab_changed)

        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        width = min(1180, max(900, screen_width - 100))
        height = min(850, max(650, screen_height - 120))
        x = max(0, (screen_width - width) // 2)
        y = max(0, (screen_height - height) // 2)
        self.minsize(900, 650)
        self.geometry(f"{width}x{height}+{x}+{y}")

    def _build_lazy_tab(self, requested_key):
        if requested_key in self._built_tabs:
            return
        for key, tab, builder in self._lazy_tabs.values():
            if key == requested_key:
                self._built_tabs.add(key)
                builder(tab)
                return

    def _on_tab_changed(self, _event=None):
        if self._tab_transitioning:
            return
        selected = self.notebook.select()
        tab_data = self._lazy_tabs.get(selected)
        if not tab_data:
            return
        requested_key = tab_data[0]
        if requested_key == self._active_tab_key:
            return
        if getattr(self, "_simulation_running", False):
            self.notebook.select(self._tab_id_for(self._active_tab_key))
            return
        self._tab_transitioning = True
        try:
            self._unload_tab(self._active_tab_key)
            self._build_lazy_tab(requested_key)
            self._active_tab_key = requested_key
        finally:
            self._tab_transitioning = False

    def _tab_id_for(self, requested_key):
        for tab_id, (key, _tab, _builder) in self._lazy_tabs.items():
            if key == requested_key:
                return tab_id
        raise KeyError(requested_key)

    def _unload_tab(self, key):
        if key not in self._built_tabs:
            return
        if key == "candidate" and hasattr(self, "candidate_config"):
            self._warrior_snapshots[key] = self._candidate_config_dict()
        elif key == "enemy":
            pending = getattr(self, "_enemy_materialize_after_id", None)
            if pending is not None:
                self.after_cancel(pending)
                self._enemy_materialize_after_id = None
            self._save_active_enemy_editor()
            self._warrior_snapshots[key] = [dict(profile) for profile in self._enemy_profiles]

        tab = self.nametowidget(self._tab_id_for(key))
        # Marcarla como descargada antes de destruir evita una segunda descarga
        # si Tk cuela otro evento de cambio mientras procesa los widgets.
        self._built_tabs.discard(key)
        for child in tab.winfo_children():
            child.destroy()
        if key == "enemy":
            self.enemy_editor = None
            self.enemy_config = None

    def _candidate_for_simulation(self):
        if "candidate" in self._built_tabs:
            return self._candidate_config_dict()
        return self._warrior_snapshots["candidate"].copy()

    def _custom_enemies_for_simulation(self):
        if "enemy" in self._built_tabs:
            self._save_active_enemy_editor()
            return [dict(profile) for profile in self._enemy_profiles]
        stored = self._warrior_snapshots.get("enemy", self._enemy_profiles)
        return [dict(profile) for profile in stored]

    def _manual_enemy_indices(self, enemies, total_simulations, seed):
        variants = 24 if self.enemy_level.get() else 1
        count = max(1, len(enemies) * variants)
        rng = np.random.default_rng(seed + 808)
        return rng.integers(0, count, total_simulations, dtype=np.int64)

    def setup_tab_candidate(self, tab):

        selector = ttk.LabelFrame(tab, text=" Identidad y procedencia ")
        selector.pack(fill="x", padx=15, pady=(12, 3))
        selector.columnconfigure(1, weight=2)
        selector.columnconfigure(3, weight=2)
        selector.columnconfigure(5, weight=2)
        ttk.Label(selector, text="Nombre:").grid(row=0, column=0, padx=(10, 4), pady=7)
        ttk.Entry(selector, textvariable=self.candidate_name).grid(
            row=0, column=1, sticky="ew", padx=(0, 10), pady=7
        )
        ttk.Label(selector, text="Banda:").grid(row=0, column=2, padx=(0, 4), pady=7)
        self.candidate_band_combo = ttk.Combobox(
            selector, state="readonly",
            values=("Selección libre", *(band.name for band in self._candidate_bands)),
        )
        self.candidate_band_combo.grid(row=0, column=3, sticky="ew", padx=(0, 10), pady=7)
        self.candidate_band_combo.bind("<<ComboboxSelected>>", self._candidate_band_changed)
        ttk.Label(selector, text="Guerrero:").grid(row=0, column=4, padx=(0, 4), pady=7)
        self.candidate_profile_combo = ttk.Combobox(selector, state="disabled")
        self.candidate_profile_combo.grid(row=0, column=5, sticky="ew", padx=(0, 10), pady=7)
        self.candidate_profile_combo.bind("<<ComboboxSelected>>", self._candidate_profile_changed)

        action_frame = ttk.Frame(selector)
        action_frame.grid(row=1, column=0, columnspan=6, sticky="ew", padx=10, pady=(0, 7))
        ttk.Label(action_frame, textvariable=self.candidate_catalog_status).pack(side="left", fill="x", expand=True)

        candidate_skill_descriptions = dict(GENERAL_SKILL_DESCRIPTIONS)
        candidate_skill_categories = dict(GENERAL_SKILL_CATEGORIES)
        for band in self._candidate_bands:
            candidate_skill_descriptions.update(
                (skill.name, skill.description) for skill in band.skills
            )
            for skill in band.skills:
                candidate_skill_categories.setdefault(skill.name, "special")
        self.candidate_config = WarriorConfigFrame(
            tab,
            "Configuración del Guerrero Candidato",
            show_house_rules=False,
            skill_descriptions=candidate_skill_descriptions,
            skill_categories=candidate_skill_categories,
        )

        self.candidate_config.pack(
            fill="both",
            expand=True,
            padx=15,
            pady=(3, 12),
        )
        self.candidate_config.set_option_filter(None)
        if "candidate" in self._warrior_snapshots:
            self._restore_candidate_payload(self._warrior_snapshots["candidate"])
        else:
            self.candidate_band_combo.set("Selección libre")

    def _candidate_config_dict(self):
        config = self.candidate_config.get_config_dict()
        config.update({
            "candidate_name": self.candidate_name.get().strip() or "Candidato",
            "candidate_band_id": self.candidate_band_id.get(),
            "candidate_profile_id": self.candidate_profile_id.get(),
        })
        return config

    def _candidate_band_changed(self, _event=None):
        band = self._band_by_name.get(self.candidate_band_combo.get())
        if band is None:
            self.candidate_band_id.set("")
            self.candidate_profile_id.set("")
            self.candidate_profile_combo.set("")
            self.candidate_profile_combo.config(values=(), state="disabled")
            self.candidate_config.set_option_filter(None)
            self.candidate_catalog_status.set("Selección libre: todas las opciones del simulador.")
            return
        self.candidate_band_id.set(band.band_id)
        self.candidate_profile_id.set("")
        self.candidate_profile_combo.config(
            values=tuple(profile.name for profile in band.profiles), state="readonly"
        )
        self.candidate_profile_combo.set("Selecciona un guerrero")
        self.candidate_config.set_option_filter(
            None, extra_skills=(skill.name for skill in band.skills)
        )
        self.candidate_catalog_status.set(
            f"{len(band.profiles)} perfiles disponibles. Elige uno para aplicar sus restricciones."
        )

    def _candidate_profile_changed(self, _event=None):
        band = next((b for b in self._candidate_bands if b.band_id == self.candidate_band_id.get()), None)
        if band is None:
            return
        profile = next((p for p in band.profiles if p.name == self.candidate_profile_combo.get()), None)
        if profile is None:
            return
        self.candidate_profile_id.set(profile.profile_id)
        self.candidate_name.set(profile.name)
        default_weapon = next(iter(usable_main_weapons(profile)), "Daga")
        self.candidate_config.load_config({
            **profile.stats, "skills": [], "main_weapon": default_weapon,
            "off_hand": "Ninguna", "armor": "Sin Armadura",
        })
        self.candidate_config.set_option_filter(profile)
        omitted = []
        if profile.fixed_equipment:
            omitted.append("equipo fijo documentado")
        if profile.rules:
            omitted.append("reglas propias en la ficha")
        suffix = f" · {' y '.join(omitted)}" if omitted else ""
        self.candidate_catalog_status.set(
            f"Perfil canónico aplicado: {profile.band_name} · {profile.profile_type}{suffix}."
        )

    def _candidate_metadata(self):
        profile = find_profile(self.candidate_band_id.get(), self.candidate_profile_id.get())
        metadata = {
            "name": self.candidate_name.get().strip() or "Candidato",
            "band_id": self.candidate_band_id.get(),
            "profile_id": self.candidate_profile_id.get(),
            "band_name": "Selección libre",
            "profile_name": "Perfil libre",
        }
        if profile:
            metadata.update({
                "band_name": profile.band_name, "profile_name": profile.name,
                "profile_type": profile.profile_type, "fixed_equipment": profile.fixed_equipment,
                "restrictions": profile.restrictions, "rules": profile.rules,
                "source": profile.source,
            })
        return metadata

    def _candidate_workbook_payload(self):
        difficulties = [name for name, variable in self.enemy_difficulties.items() if variable.get()]
        opponent = {
            "mode": "Muestra aleatoria" if self.enemy_mode.get() == "sample" else "Rival configurable",
            "level": self.enemy_level.get(),
            "description": ", ".join(difficulties) if self.enemy_mode.get() == "sample" else "Perfil configurable",
        }
        enemy_profiles = (
            self._custom_enemies_for_simulation()
            if self.enemy_mode.get() == "custom" else []
        )
        return {
            "config": self._candidate_config_dict(), "candidate": self._candidate_metadata(),
            "opponent": opponent,
            "enemies": {
                "mode": self.enemy_mode.get(), "level": self.enemy_level.get(),
                "difficulties": difficulties, "profiles": enemy_profiles,
            },
        }

    def _save_candidate(self):
        default_name = re.sub(r"[^\w.-]+", "_", self.candidate_name.get().strip(), flags=re.UNICODE).strip("_") or "Candidato"
        path = filedialog.asksaveasfilename(
            title="Guardar libro de simulación", defaultextension=".xlsx",
            filetypes=(("Libro de Excel", "*.xlsx"),), initialfile=f"{default_name}.xlsx",
        )
        if not path:
            return
        try:
            save_candidate_workbook(path, self._candidate_workbook_payload())
        except (OSError, ValueError) as exc:
            messagebox.showerror("No se pudo guardar", str(exc))
            return
        self.candidate_workbook_path = path
        messagebox.showinfo(
            "Libro guardado",
            "Se han guardado el candidato, los enemigos y la configuración de la muestra.",
        )

    def _load_candidate(self):
        path = filedialog.askopenfilename(
            title="Cargar libro de simulación", filetypes=(("Libro de Excel", "*.xlsx"),)
        )
        if not path:
            return
        try:
            payload = load_candidate_workbook(path)
            self._restore_candidate_payload(payload["config"])
            enemies = payload.get("enemies") or {}
            self.enemy_mode.set(enemies.get("mode", self.enemy_mode.get()))
            self.enemy_level.set(int(enemies.get("level", self.enemy_level.get())))
            selected_difficulties = set(enemies.get("difficulties", ()))
            if selected_difficulties:
                for name, variable in self.enemy_difficulties.items():
                    variable.set(name in selected_difficulties)
            profiles = enemies.get("profiles") or ()
            if profiles:
                self._enemy_profiles = [dict(profile) for profile in profiles]
                self._warrior_snapshots["enemy"] = [dict(profile) for profile in profiles]
        except (OSError, CandidateWorkbookError, KeyError, ValueError) as exc:
            messagebox.showerror("No se pudo cargar", str(exc))
            return
        self.candidate_workbook_path = path
        messagebox.showinfo("Libro cargado", "El candidato y los enemigos se han recuperado correctamente.")

    def _restore_candidate_payload(self, config):
        self.candidate_name.set(config.get("candidate_name", "Candidato"))
        band_id = config.get("candidate_band_id", "")
        profile_id = config.get("candidate_profile_id", "")
        profile = find_profile(band_id, profile_id)
        if profile:
            self.candidate_band_id.set(band_id)
            self.candidate_profile_id.set(profile_id)
            self.candidate_band_combo.set(profile.band_name)
            band = next(b for b in self._candidate_bands if b.band_id == band_id)
            self.candidate_profile_combo.config(values=tuple(p.name for p in band.profiles), state="readonly")
            self.candidate_profile_combo.set(profile.name)
            self.candidate_config.set_option_filter(profile)
            self.candidate_catalog_status.set(f"Perfil cargado: {profile.band_name} · {profile.name}.")
        else:
            self.candidate_band_id.set("")
            self.candidate_profile_id.set("")
            self.candidate_band_combo.set("Selección libre")
            self.candidate_profile_combo.set("")
            self.candidate_profile_combo.config(values=(), state="disabled")
            self.candidate_config.set_option_filter(None)
            self.candidate_catalog_status.set("Selección libre cargada.")
        self.candidate_config.load_config(config)
        self.candidate_config.set_option_filter(profile)

    def setup_tab_enemy(self, tab):

        self.enemy_check_widgets = []

        ttk.Label(
            tab,
            text="Elige cómo se construye el rival",
            font=("Arial", 11, "bold"),
        ).pack(anchor="w", padx=15, pady=(10, 4))

        level_frame = ttk.LabelFrame(
            tab,
            text=" NIVEL DEL RIVAL · SE APLICA A LAS DOS OPCIONES ",
        )
        level_frame.pack(fill="x", padx=15, pady=(0, 7))
        ttk.Label(
            level_frame,
            text="Subidas de nivel:",
            font=("Arial", 10, "bold"),
        ).pack(side="left", padx=(12, 6), pady=8)
        self.enemy_level_spin = ttk.Spinbox(
            level_frame, from_=0, to=20, textvariable=self.enemy_level,
            width=6, justify="center", font=("Arial", 10, "bold"),
        )
        self.enemy_level_spin.pack(side="left", pady=8)
        ttk.Label(
            level_frame,
            text="Cada subida añade una mejora aleatoria nueva en cada combate.",
        ).pack(side="left", padx=12, pady=8)
        ToolTip(
            self.enemy_level_spin,
            "Se aplica a cualquiera de las dos opciones. Cada nivel añade una mejora aleatoria al rival.",
        )

        sample_frame = ttk.LabelFrame(
            tab,
            text=" Opción 1 ",
        )

        sample_frame.pack(
            fill="x",
            padx=15,
            pady=(10, 5),
        )

        r1 = ttk.Radiobutton(
            sample_frame,
            text=(
                "Muestra aleatoria: el simulador elige perfiles, equipo legal y mejoras "
                "para cada combate, respetando la frecuencia de cada grupo de dificultad."
            ),
            variable=self.enemy_mode,
            value="sample",
            command=self.toggle_enemy_mode,
        )

        r1.pack(
            anchor="w",
            padx=10,
            pady=6,
        )

        self.checklist_frame = ttk.Frame(
            sample_frame
        )

        self.checklist_frame.pack(
            fill="x",
            padx=30,
            pady=(2, 10),
        )

        difficulty_row = ttk.Frame(self.checklist_frame)
        difficulty_row.pack(fill="x", pady=(0, 5))
        ttk.Label(difficulty_row, text="Dificultad:", font=("Arial", 9, "bold")).pack(side="left")
        for difficulty in DIFFICULTIES:
            checkbox = ttk.Checkbutton(
                difficulty_row,
                text=difficulty,
                variable=self.enemy_difficulties[difficulty],
            )
            checkbox.pack(side="left", padx=8)
            self.enemy_check_widgets.append(checkbox)

        custom_frame = ttk.LabelFrame(
            tab,
            text=" Opción 2 ",
        )

        custom_frame.pack(
            fill="x",
            padx=15,
            pady=5,
        )

        ttk.Radiobutton(
            custom_frame,
            text=(
                "Rivales configurables: cada pestaña representa un rival posible; "
                "el nivel añade mejoras aleatorias a todos ellos."
            ),
            variable=self.enemy_mode,
            value="custom",
            command=self.toggle_enemy_mode,
        ).pack(
            anchor="w",
            padx=10,
            pady=6,
        )

        enemy_tools = ttk.Frame(tab)
        enemy_tools.pack(fill="x", padx=15, pady=(4, 0))
        self.btn_add_enemy = ttk.Button(
            enemy_tools, text="＋ Añadir enemigo", command=self._add_enemy_profile
        )
        self.btn_add_enemy.pack(side="left")
        self.btn_remove_enemy = ttk.Button(
            enemy_tools, text="− Eliminar enemigo", command=self._remove_enemy_profile
        )
        self.btn_remove_enemy.pack(side="left", padx=6)

        self.enemy_notebook = ttk.Notebook(tab)
        self.enemy_notebook.pack(fill="both", expand=True, padx=15, pady=(3, 5))
        self.enemy_notebook.bind("<<NotebookTabChanged>>", self._enemy_tab_changed)

        stored = self._warrior_snapshots.get("enemy", self._enemy_profiles)
        self._enemy_profiles = [dict(profile) for profile in stored]
        if not self._enemy_profiles:
            self._enemy_profiles = [{"enemy_name": "Enemigo 1"}]
        self._active_enemy_editor_index = None
        self.enemy_editor = None
        self.enemy_config = None
        for index, profile in enumerate(self._enemy_profiles):
            page = ttk.Frame(self.enemy_notebook)
            self.enemy_notebook.add(page, text=profile.get("enemy_name", f"Enemigo {index + 1}"))
        self._enemy_materialize_after_id = self.after_idle(self._materialize_selected_enemy)

        self.toggle_enemy_mode()

    def toggle_enemy_mode(self):

        is_custom = (
            self.enemy_mode.get()
            == "custom"
        )

        if is_custom:

            for checkbox in (
                self.enemy_check_widgets
            ):
                checkbox.config(
                    state="disabled"
                )

            if self._enemy_editor_exists():
                self.enemy_editor.set_enabled(True)

        else:

            for checkbox in (
                self.enemy_check_widgets
            ):
                checkbox.config(
                    state="normal"
                )

            if self._enemy_editor_exists():
                self.enemy_editor.set_enabled(False)

        if hasattr(self, "btn_remove_enemy"):
            self.btn_remove_enemy.config(state="normal" if is_custom else "disabled")
        if hasattr(self, "btn_add_enemy"):
            self.btn_add_enemy.config(state="normal" if is_custom else "disabled")
        if hasattr(self, "enemy_notebook"):
            self.enemy_notebook.state(("!disabled",) if is_custom else ("disabled",))

    def _save_active_enemy_editor(self):
        index = self._active_enemy_editor_index
        if index is not None and self._enemy_editor_exists():
            self._enemy_profiles[index] = self.enemy_editor.get_config_dict()

    def _enemy_editor_exists(self):
        editor = getattr(self, "enemy_editor", None)
        if editor is None:
            return False
        try:
            return bool(editor.winfo_exists())
        except tk.TclError:
            return False

    def _materialize_selected_enemy(self):
        self._enemy_materialize_after_id = None
        if not hasattr(self, "enemy_notebook") or not self.enemy_notebook.tabs():
            return
        selected = self.enemy_notebook.select()
        index = self.enemy_notebook.index(selected)
        if index == self._active_enemy_editor_index and self._enemy_editor_exists():
            return
        self._save_active_enemy_editor()
        if self._enemy_editor_exists():
            self.enemy_editor.destroy()
        page = self.nametowidget(selected)
        self._active_enemy_editor_index = index
        self.enemy_editor = EnemyProfileEditor(
            page, self._candidate_bands, self._enemy_profiles[index],
            on_name_change=lambda name, page_id=selected: self.enemy_notebook.tab(page_id, text=name),
        )
        self.enemy_editor.pack(fill="both", expand=True)
        self.enemy_config = self.enemy_editor.config  # Compatibilidad con controles comunes.
        self.enemy_editor.set_enabled(self.enemy_mode.get() == "custom")

    def _enemy_tab_changed(self, _event=None):
        self._materialize_selected_enemy()

    def _add_enemy_profile(self):
        self._save_active_enemy_editor()
        number = len(self._enemy_profiles) + 1
        self._enemy_profiles.append({"enemy_name": f"Enemigo {number}"})
        page = ttk.Frame(self.enemy_notebook)
        self.enemy_notebook.add(page, text=f"Enemigo {number}")
        self.enemy_notebook.select(page)
        self._materialize_selected_enemy()

    def _remove_enemy_profile(self):
        if len(self._enemy_profiles) <= 1:
            messagebox.showinfo("Enemigos", "Debe quedar al menos un perfil manual.")
            return
        index = self.enemy_notebook.index(self.enemy_notebook.select())
        self._save_active_enemy_editor()
        page_id = self.enemy_notebook.tabs()[index]
        if hasattr(self, "enemy_editor"):
            self.enemy_editor.destroy()
        self._active_enemy_editor_index = None
        self.enemy_notebook.forget(page_id)
        del self._enemy_profiles[index]
        self._materialize_selected_enemy()

    def _sort_treeview(self, tree, column, descending=False):
        rows = [(tree.set(item, column), item) for item in tree.get_children("")]
        rows.sort(key=lambda row: self._tree_sort_key(row[0]), reverse=descending)
        for index, (_, item) in enumerate(rows):
            tree.move(item, "", index)
        tree.heading(column, command=lambda: self._sort_treeview(tree, column, not descending))

    @staticmethod
    def _tree_sort_key(value):
        value = str(value)
        text = value.replace("★", "").replace("%", "").replace("+", "").replace("−", "-").strip()
        number = re.search(r"-?\d+(?:[.,]\d+)?", text)
        if number:
            return 0, float(number.group().replace(",", ".")), ""
        return 1, 0.0, value.casefold()

    def _configure_sortable_tree(self, tree, columns):
        tree.configure(show="tree headings")
        tree.heading("#0", text="")
        tree.column("#0", width=0, minwidth=0, stretch=False)
        for column, title in columns:
            tree.heading(
                column,
                text=title,
                anchor="center",
                command=lambda c=column: self._sort_treeview(tree, c, False),
            )
            tree.column(column, anchor="center")
        tree.bind(
            "<Configure>",
            lambda _event, result_tree=tree: self._center_tree_columns(result_tree),
            add="+",
        )

    @staticmethod
    def _visible_tree_columns(tree):
        columns = tree.cget("displaycolumns")
        if columns == "#all":
            return tuple(tree.cget("columns"))
        return tuple(columns)

    def _autosize_tree_columns(self, tree):
        """Ajusta las columnas mostradas y deja el bloque centrado."""
        text_font = tkfont.nametofont("TkDefaultFont")
        for column in self._visible_tree_columns(tree):
            widest = text_font.measure(tree.heading(column, "text"))
            for item in tree.get_children(""):
                widest = max(widest, text_font.measure(str(tree.set(item, column))))
            tree.column(column, width=widest + 28, minwidth=30, stretch=False)
        self._center_tree_columns(tree)

    @staticmethod
    def _center_tree_columns(tree):
        """Usa la columna de árbol vacía como margen izquierdo dinámico."""
        try:
            columns = TrollheimApp._visible_tree_columns(tree)
            content_width = sum(int(tree.column(column, "width")) for column in columns)
            margin = max(0, (tree.winfo_width() - content_width) // 2)
            tree.column("#0", width=margin, minwidth=margin, stretch=False)
        except tk.TclError:
            pass

    @staticmethod
    def _pack_scrollable_tree(tree, pady=(4, 10)):
        frame = tree.master
        frame.pack(fill="both", expand=True, padx=10, pady=pady)
        frame.rowconfigure(0, weight=1)
        frame.columnconfigure(0, weight=1)

        vertical = ttk.Scrollbar(frame, orient="vertical", command=tree.yview)
        horizontal = ttk.Scrollbar(frame, orient="horizontal", command=tree.xview)
        tree.configure(
            yscrollcommand=vertical.set,
            xscrollcommand=horizontal.set,
        )
        tree.grid(row=0, column=0, sticky="nsew")
        vertical.grid(row=0, column=1, sticky="ns")
        horizontal.grid(row=1, column=0, sticky="ew")
        ttk.Sizegrip(frame).grid(row=1, column=1, sticky="se")
        return frame

    def _create_mode_cards(self, parent, target):
        ttk.Label(
            parent,
            text=(
                "CONFIGURACIONES DE MANOS · Cada tarjeta controla su columna. "
                "Usa el botón para mostrarla u ocultarla."
            ),
            font=("Arial", 9, "bold"),
            anchor="center",
        ).pack(fill="x", padx=10, pady=(8, 0))

        container = ttk.Frame(parent)
        container.pack(fill="x", padx=10, pady=(4, 4))
        cards = {}

        for column, (mode, title) in enumerate(COMBAT_MODES):
            container.columnconfigure(column, weight=1, uniform="mode_cards")
            card = ttk.LabelFrame(container, text=title)
            card.grid(row=0, column=column, sticky="nsew", padx=3)
            equipment = ttk.Label(
                card,
                text="Equipo por calcular",
                anchor="center",
                justify="center",
                wraplength=210,
            )
            equipment.pack(fill="x", padx=6, pady=(5, 1))
            rate_line = ttk.Frame(card)
            rate_line.pack(anchor="center", padx=6, pady=1)
            rate = ttk.Label(rate_line, text="Sin resultados", font=("Arial", 13, "bold"))
            rate.pack(side="left")
            delta = ttk.Label(rate_line, text="", font=("Arial", 10, "bold"))
            delta.pack(side="left", padx=(5, 0))

            badges = ttk.Frame(card)
            badges.pack(fill="x", padx=6, pady=(2, 1))
            current_badge = ttk.Label(
                badges,
                text="",
                font=("Arial", 8, "bold"),
                foreground="#1b5eaa",
                anchor="center",
            )
            current_badge.pack(side="left", expand=True)
            best_badge = ttk.Label(
                badges,
                text="",
                font=("Arial", 8, "bold"),
                foreground="#9a6700",
                anchor="center",
            )
            best_badge.pack(side="left", expand=True)

            visibility = ttk.Label(
                card,
                text="VISIBLE EN LA TABLA",
                font=("Arial", 8, "bold"),
                foreground=DELTA_POSITIVE,
                anchor="center",
            )
            visibility.pack(fill="x", padx=6, pady=(1, 2))
            toggle = ttk.Button(
                card,
                text="Ocultar columna",
                command=lambda m=mode, t=target: self._toggle_mode_column(t, m),
            )
            toggle.pack(fill="x", padx=8, pady=(0, 6))

            cards[mode] = {
                "equipment": equipment,
                "rate": rate,
                "delta": delta,
                "current_badge": current_badge,
                "best_badge": best_badge,
                "visibility": visibility,
                "toggle": toggle,
            }

        return cards

    def _toggle_mode_column(self, target, mode):
        if target == "results":
            visible, cards = self.result_visible_modes, self.result_cards
        elif target == "combos":
            visible, cards = self.combo_visible_modes, self.combo_cards
        elif target == "equipment":
            visible, cards = self.equipment_visible_modes, self.equipment_cards
        else:
            visible, cards = self.weapon_visible_modes, self.weapon_cards

        if mode in visible:
            if len(visible) == 1:
                return
            visible.remove(mode)
        else:
            visible.add(mode)

        self._apply_result_view(target)
        renderers = {
            "results": self._render_results_table,
            "combos": self._render_combo_table,
            "equipment": self._render_equipment_table,
            "weapons": self._render_weapon_table,
        }
        renderers[target]()
        self._refresh_mode_card_visibility(cards, visible)

    @staticmethod
    def _refresh_mode_card_visibility(cards, visible):
        for mode, _title in COMBAT_MODES:
            is_visible = mode in visible
            cards[mode]["visibility"].config(
                text="VISIBLE EN LA TABLA" if is_visible else "OCULTA EN LA TABLA",
                foreground=DELTA_POSITIVE if is_visible else DELTA_NEGATIVE,
            )
            if is_visible and len(visible) == 1:
                cards[mode]["toggle"].config(
                    text="Única columna visible",
                    state="disabled",
                )
            else:
                cards[mode]["toggle"].config(
                    text="Ocultar columna" if is_visible else "Mostrar columna",
                    state="normal",
                )

    @staticmethod
    def _reset_mode_cards(cards, visible):
        for card in cards.values():
            card["equipment"].config(text="Preparando equipo...")
            card["rate"].config(text="Calculando...")
            card["delta"].config(text="")
            card["current_badge"].config(text="")
            card["best_badge"].config(text="")
        TrollheimApp._refresh_mode_card_visibility(cards, visible)

    def _apply_result_view(self, target):
        if target == "results":
            tree, view_var = self.results_tree, self.results_view
            visible, fixed = self.result_visible_modes, ("Mejora",)
        elif target == "combos":
            tree, view_var = self.combo_tree, self.combo_view
            visible, fixed = self.combo_visible_modes, ("Mejora1", "Mejora2")
        elif target == "equipment":
            tree, view_var = self.equipment_tree, self.equipment_view
            visible, fixed = self.equipment_visible_modes, ("Item1", "Item2", "Item3")
        else:
            tree, view_var = self.weapon_tree, self.weapon_view
            visible, fixed = self.weapon_visible_modes, ("Main", "Off")

        if view_var.get() == "optimal":
            optimal_columns = (*fixed, "Optimal")
            if target != "weapons":
                optimal_columns += ("Equipment",)
            tree.configure(displaycolumns=optimal_columns)
        else:
            tree.configure(
                displaycolumns=(
                    *fixed,
                    *(mode for mode, _title in COMBAT_MODES if mode in visible),
                )
            )

    def _change_result_view(self, target):
        self._apply_result_view(target)
        renderers = {
            "results": self._render_results_table,
            "combos": self._render_combo_table,
            "equipment": self._render_equipment_table,
            "weapons": self._render_weapon_table,
        }
        renderers[target]()

    def _restore_simulation_tab(self, target):
        if target == "results":
            table_name, cards_name = "_results_table_data", "_results_card_data"
            cards, renderer = self.result_cards, self._render_results_table
        elif target == "combos":
            table_name, cards_name = "_combo_table_data", "_combo_card_data"
            cards, renderer = self.combo_cards, self._render_combo_table
        elif target == "equipment":
            table_name, cards_name = "_equipment_table_data", "_equipment_card_data"
            cards, renderer = self.equipment_cards, self._render_equipment_table
        else:
            table_name, cards_name = "_weapon_table_data", "_weapon_card_data"
            cards, renderer = self.weapon_cards, self._render_weapon_table
        card_data = getattr(self, cards_name, None)
        if card_data:
            base_rates, user_mode_key, equipment = card_data
            self._update_mode_cards(cards, base_rates, user_mode_key, equipment)
        self._apply_result_view(target)
        if getattr(self, table_name, None):
            renderer()

    def _clear_combo_filters(self):
        self.combo_search.set("")
        self._render_combo_table()

    @staticmethod
    def _combo_parts(label):
        return tuple(label.split(" + ", 1))

    @staticmethod
    def _combo_matches(parts, search):
        normalize = lambda text: "".join(
            character for character in unicodedata.normalize("NFD", text.casefold())
            if unicodedata.category(character) != "Mn"
        )
        query = normalize(search.strip())
        return not query or query in normalize(" + ".join(parts))

    @staticmethod
    def _best_visible_mode(values, visible_modes):
        available = set(values).intersection(visible_modes)
        if not available:
            return None
        return max(available, key=lambda mode: values[mode][0])

    @staticmethod
    def _equipment_description(candidate):
        main = candidate.get("main_weapon", "—")
        off = candidate.get("off_hand", "Ninguna")
        main_material = candidate.get("main_weapon_material", "Sin material")
        off_material = candidate.get("offhand_material", "Sin material")

        if main_material not in ("Sin material", "Normal"):
            main = f"{main} ({main_material})"
        if off_material not in ("Sin material", "Normal") and off not in ("Ninguna", "Escudo"):
            off = f"{off} ({off_material})"
        return main if off == "Ninguna" else f"{main} + {off}"

    def _update_mode_cards(self, cards, base_rates, user_mode_key, equipment):
        best_rate = max(base_rates.values())
        user_rate = base_rates[user_mode_key]
        if cards is getattr(self, "result_cards", None):
            visible = self.result_visible_modes
        elif cards is getattr(self, "combo_cards", None):
            visible = self.combo_visible_modes
        elif cards is getattr(self, "equipment_cards", None):
            visible = self.equipment_visible_modes
        else:
            visible = self.weapon_visible_modes
        for mode, _title in COMBAT_MODES:
            rate = base_rates[mode]
            delta = rate - user_rate
            cards[mode]["equipment"].config(text=equipment.get(mode, "—"))
            marker = "★ " if abs(rate - best_rate) < 0.00001 else ""
            cards[mode]["rate"].config(text=f"{marker}{rate:.2f}%")
            if delta > 0.00001:
                arrow, color = "▲", DELTA_POSITIVE
            elif delta < -0.00001:
                arrow, color = "▼", DELTA_NEGATIVE
            else:
                arrow, color = "=", DELTA_NEUTRAL
            cards[mode]["delta"].config(
                text=f"{arrow} {abs(delta):.2f}%",
                foreground=color,
            )
            cards[mode]["current_badge"].config(
                text="● EQUIPO ACTUAL" if mode == user_mode_key else ""
            )
            cards[mode]["best_badge"].config(
                text="★ MEJOR" if abs(rate - best_rate) < 0.00001 else ""
            )
        self._refresh_mode_card_visibility(cards, visible)

    def setup_tab_results(self, tab):

        controls = ttk.Frame(tab)
        controls.pack(pady=7)
        ttk.Label(controls, text="Simulaciones:").pack(side="left", padx=(0, 5))
        ttk.Entry(controls, textvariable=self.simulations_improvements, width=12).pack(side="left", padx=(0, 10))
        self.btn_run = ttk.Button(
            controls,
            text="Calcular Comparativa de Mejoras",
            command=self.start_simulation_thread,
        )
        self.btn_run.pack(side="left")

        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(tab, variable=self.progress_var, maximum=100)
        self.progress_bar.pack(fill="x", padx=20, pady=5)

        self.status_label = ttk.Label(tab, text="Estado: Listo", font=("Arial", 9, "italic"))
        self.status_label.pack(pady=2)

        view_controls = ttk.Frame(tab)
        view_controls.pack(pady=(3, 0))
        ttk.Label(view_controls, text="Vista:").pack(side="left", padx=(0, 6))
        ttk.Radiobutton(
            view_controls, text="Por equipo", variable=self.results_view,
            value="equipment", command=lambda: self._change_result_view("results"),
        ).pack(side="left", padx=3)
        ttk.Radiobutton(
            view_controls, text="Óptima", variable=self.results_view,
            value="optimal", command=lambda: self._change_result_view("results"),
        ).pack(side="left", padx=3)

        self.result_cards = self._create_mode_cards(tab, "results")
        results_table = ttk.Frame(tab)
        self.results_tree = ttk.Treeview(
            results_table,
            columns=("Mejora", "Single", "Shield", "Dual", "TwoHand", "Optimal", "Equipment"),
            show="headings",
        )
        self._configure_sortable_tree(self.results_tree, [
            ("Mejora", "Mejora evaluada"),
            ("Single", "Mano libre"),
            ("Shield", "Escudo"),
            ("Dual", "Dos armas"),
            ("TwoHand", "Dos manos"),
            ("Optimal", "Mejor resultado"),
            ("Equipment", "Equipo utilizado"),
        ])
        self.results_tree.column("Mejora", width=180)
        for mode, _title in COMBAT_MODES:
            self.results_tree.column(mode, width=165, anchor="center")
        self.results_tree.column("Optimal", width=180, anchor="center")
        self.results_tree.column("Equipment", width=240, anchor="center")
        self.results_tree.configure(displaycolumns=("Mejora", "Single", "Shield", "Dual", "TwoHand"))
        self._pack_scrollable_tree(self.results_tree)
        self._restore_simulation_tab("results")

    def setup_tab_equipment(self, tab):

        controls = ttk.Frame(tab)
        controls.pack(pady=7)
        ttk.Label(controls, text="Simulaciones:").pack(side="left", padx=(0, 5))
        ttk.Entry(
            controls, textvariable=self.simulations_equipment, width=12
        ).pack(side="left", padx=(0, 10))
        ttk.Label(controls, text="Máximo de objetos:").pack(side="left", padx=(0, 5))
        ttk.Combobox(
            controls,
            textvariable=self.equipment_max_items,
            values=(1, 2, 3),
            state="readonly",
            width=3,
            justify="center",
        ).pack(side="left", padx=(0, 10))
        self.btn_equipment_run = ttk.Button(
            controls,
            text="Calcular Objetos y Combinaciones",
            command=self.start_equipment_thread,
        )
        self.btn_equipment_run.pack(side="left")

        self.equipment_filter_button = ttk.Menubutton(
            controls, text="Objetos incluidos ▾"
        )
        self.equipment_filter_button.pack(side="left", padx=(10, 0))
        equipment_menu = tk.Menu(self.equipment_filter_button, tearoff=False)
        for label, variable in self.equipment_item_vars.items():
            equipment_menu.add_checkbutton(label=label, variable=variable)
        equipment_menu.add_separator()
        equipment_menu.add_command(
            label="Marcar todos",
            command=lambda: self._set_equipment_filters(True),
        )
        equipment_menu.add_command(
            label="Desmarcar todos",
            command=lambda: self._set_equipment_filters(False),
        )
        self.equipment_filter_button.config(menu=equipment_menu)

        ttk.Label(
            tab,
            text=(
                "Compara armaduras, objetos y consumibles desde uno hasta el máximo seleccionado. "
                "La referencia no lleva ninguno de ellos."
            ),
            font=("Arial", 8, "italic"),
        ).pack(pady=(0, 3))

        self.equipment_progress_var = tk.DoubleVar()
        self.equipment_progress_bar = ttk.Progressbar(
            tab, variable=self.equipment_progress_var, maximum=100
        )
        self.equipment_progress_bar.pack(fill="x", padx=20, pady=5)
        self.equipment_status_label = ttk.Label(
            tab, text="Estado: Listo", font=("Arial", 9, "italic")
        )
        self.equipment_status_label.pack(pady=2)

        view_controls = ttk.Frame(tab)
        view_controls.pack(pady=(3, 0))
        ttk.Label(view_controls, text="Vista:").pack(side="left", padx=(0, 6))
        ttk.Radiobutton(
            view_controls, text="Por equipo", variable=self.equipment_view,
            value="equipment", command=lambda: self._change_result_view("equipment"),
        ).pack(side="left", padx=3)
        ttk.Radiobutton(
            view_controls, text="Óptima", variable=self.equipment_view,
            value="optimal", command=lambda: self._change_result_view("equipment"),
        ).pack(side="left", padx=3)

        self.equipment_cards = self._create_mode_cards(tab, "equipment")

        equipment_table = ttk.Frame(tab)
        self.equipment_tree = ttk.Treeview(
            equipment_table,
            columns=(
                "Item1", "Item2", "Item3", "Single", "Shield", "Dual",
                "TwoHand", "Optimal", "Equipment",
            ),
            show="headings",
        )
        self._configure_sortable_tree(self.equipment_tree, [
            ("Item1", "Objeto 1"),
            ("Item2", "Objeto 2"),
            ("Item3", "Objeto 3"),
            ("Single", "Mano libre"),
            ("Shield", "Escudo"),
            ("Dual", "Dos armas"),
            ("TwoHand", "Dos manos"),
            ("Optimal", "Mejor resultado"),
            ("Equipment", "Equipo utilizado"),
        ])
        self.equipment_tree.column("Item1", width=170)
        self.equipment_tree.column("Item2", width=170)
        self.equipment_tree.column("Item3", width=170)
        for mode, _title in COMBAT_MODES:
            self.equipment_tree.column(mode, width=150, anchor="center")
        self.equipment_tree.column("Optimal", width=180, anchor="center")
        self.equipment_tree.column("Equipment", width=220, anchor="center")
        self.equipment_tree.configure(
            displaycolumns=(
                "Item1", "Item2", "Item3", "Single", "Shield", "Dual", "TwoHand",
            )
        )
        self._pack_scrollable_tree(self.equipment_tree, pady=(6, 10))
        self._restore_simulation_tab("equipment")

    def setup_tab_weapons(self, tab):

        controls = ttk.Frame(tab)
        controls.pack(pady=7)
        ttk.Label(controls, text="Simulaciones:").pack(side="left", padx=(0, 5))
        ttk.Entry(
            controls, textvariable=self.simulations_weapons, width=12
        ).pack(side="left", padx=(0, 10))
        self.btn_weapons_run = ttk.Button(
            controls,
            text="Calcular Configuraciones de Armas",
            command=self.start_weapon_thread,
        )
        self.btn_weapons_run.pack(side="left")

        self.weapon_filter_button = ttk.Menubutton(
            controls, text="Armas incluidas ▾"
        )
        self.weapon_filter_button.pack(side="left", padx=(10, 0))
        weapon_menu = tk.Menu(self.weapon_filter_button, tearoff=False)
        for weapon, variable in self.weapon_item_vars.items():
            weapon_menu.add_checkbutton(label=weapon, variable=variable)
        weapon_menu.add_separator()
        weapon_menu.add_command(
            label="Marcar todas", command=lambda: self._set_weapon_filters(True)
        )
        weapon_menu.add_command(
            label="Desmarcar todas", command=lambda: self._set_weapon_filters(False)
        )
        self.weapon_filter_button.config(menu=weapon_menu)

        ttk.Label(
            tab,
            text=(
                "Compara cada arma sola, con escudo, en parejas legales y las "
                "armas que ocupan ambas manos."
            ),
            font=("Arial", 8, "italic"),
        ).pack(pady=(0, 3))

        self.weapon_progress_var = tk.DoubleVar()
        self.weapon_progress_bar = ttk.Progressbar(
            tab, variable=self.weapon_progress_var, maximum=100
        )
        self.weapon_progress_bar.pack(fill="x", padx=20, pady=5)
        self.weapon_status_label = ttk.Label(
            tab, text="Estado: Listo", font=("Arial", 9, "italic")
        )
        self.weapon_status_label.pack(pady=2)

        view_controls = ttk.Frame(tab)
        view_controls.pack(pady=(3, 0))
        ttk.Label(view_controls, text="Vista:").pack(side="left", padx=(0, 6))
        ttk.Radiobutton(
            view_controls, text="Por equipo", variable=self.weapon_view,
            value="equipment", command=lambda: self._change_result_view("weapons"),
        ).pack(side="left", padx=3)
        ttk.Radiobutton(
            view_controls, text="Óptima", variable=self.weapon_view,
            value="optimal", command=lambda: self._change_result_view("weapons"),
        ).pack(side="left", padx=3)

        self.weapon_cards = self._create_mode_cards(tab, "weapons")
        weapon_table = ttk.Frame(tab)
        self.weapon_tree = ttk.Treeview(
            weapon_table,
            columns=(
                "Main", "Off", "Single", "Shield", "Dual", "TwoHand",
                "Optimal", "Equipment",
            ),
            show="headings",
        )
        self._configure_sortable_tree(self.weapon_tree, [
            ("Main", "Arma principal"),
            ("Off", "Mano secundaria"),
            ("Single", "Mano libre"),
            ("Shield", "Escudo"),
            ("Dual", "Dos armas"),
            ("TwoHand", "Dos manos"),
            ("Optimal", "Mejor resultado"),
            ("Equipment", "Equipo utilizado"),
        ])
        self.weapon_tree.column("Main", width=230)
        self.weapon_tree.column("Off", width=230)
        for mode, _title in COMBAT_MODES:
            self.weapon_tree.column(mode, width=150, anchor="center")
        self.weapon_tree.column("Optimal", width=180, anchor="center")
        self.weapon_tree.column("Equipment", width=220, anchor="center")
        self.weapon_tree.configure(
            displaycolumns=("Main", "Off", "Single", "Shield", "Dual", "TwoHand")
        )
        self._pack_scrollable_tree(self.weapon_tree, pady=(6, 10))
        self._restore_simulation_tab("weapons")

    def setup_tab_combos(self, tab):

        controls = ttk.Frame(tab)
        controls.pack(pady=7)
        ttk.Label(controls, text="Simulaciones:").pack(side="left", padx=(0, 5))
        ttk.Entry(controls, textvariable=self.simulations_combos, width=12).pack(side="left", padx=(0, 10))
        self.btn_combo_run = ttk.Button(
            controls,
            text="Calcular Combos de 2 Mejoras",
            command=self.start_combo_thread,
        )
        self.btn_combo_run.pack(side="left")

        self.combo_progress_var = tk.DoubleVar()
        self.combo_progress_bar = ttk.Progressbar(tab, variable=self.combo_progress_var, maximum=100)
        self.combo_progress_bar.pack(fill="x", padx=20, pady=5)

        self.combo_status_label = ttk.Label(tab, text="Estado: Listo", font=("Arial", 9, "italic"))
        self.combo_status_label.pack(pady=2)

        view_controls = ttk.Frame(tab)
        view_controls.pack(pady=(3, 0))
        ttk.Label(view_controls, text="Vista:").pack(side="left", padx=(0, 6))
        ttk.Radiobutton(
            view_controls, text="Por equipo", variable=self.combo_view,
            value="equipment", command=lambda: self._change_result_view("combos"),
        ).pack(side="left", padx=3)
        ttk.Radiobutton(
            view_controls, text="Óptima", variable=self.combo_view,
            value="optimal", command=lambda: self._change_result_view("combos"),
        ).pack(side="left", padx=3)

        self.combo_cards = self._create_mode_cards(tab, "combos")

        filter_controls = ttk.Frame(tab)
        filter_controls.pack(fill="x", padx=10, pady=(5, 1))
        ttk.Label(filter_controls, text="Buscar combinación:").pack(side="left", padx=(0, 5))
        if not getattr(self, "_combo_search_trace_added", False):
            self.combo_search.trace_add(
                "write", lambda *_args: self._render_combo_table()
            )
            self._combo_search_trace_added = True
        ttk.Entry(filter_controls, textvariable=self.combo_search, width=32).pack(
            side="left", fill="x", expand=True
        )
        ttk.Button(
            filter_controls,
            text="Limpiar",
            command=self._clear_combo_filters,
        ).pack(side="left", padx=(8, 0))

        combo_table = ttk.Frame(tab)
        self.combo_tree = ttk.Treeview(
            combo_table,
            columns=("Mejora1", "Mejora2", "Single", "Shield", "Dual", "TwoHand", "Optimal", "Equipment"),
            show="headings",
        )
        self._configure_sortable_tree(self.combo_tree, [
            ("Mejora1", "Mejora 1"),
            ("Mejora2", "Mejora 2"),
            ("Single", "Mano libre"),
            ("Shield", "Escudo"),
            ("Dual", "Dos armas"),
            ("TwoHand", "Dos manos"),
            ("Optimal", "Mejor resultado"),
            ("Equipment", "Equipo utilizado"),
        ])
        self.combo_tree.column("Mejora1", width=145)
        self.combo_tree.column("Mejora2", width=145)
        for mode, _title in COMBAT_MODES:
            self.combo_tree.column(mode, width=150, anchor="center")
        self.combo_tree.column("Optimal", width=180, anchor="center")
        self.combo_tree.column("Equipment", width=220, anchor="center")
        self.combo_tree.configure(displaycolumns=("Mejora1", "Mejora2", "Single", "Shield", "Dual", "TwoHand"))
        self._pack_scrollable_tree(self.combo_tree)
        self._restore_simulation_tab("combos")

    def get_user_mode_key(
        self,
        candidate,
    ):

        main_weapon = candidate.get(
            "main_weapon"
        )

        off_hand = candidate.get(
            "off_hand"
        )

        if main_weapon in TWO_HANDED_WEAPONS:
            return "TwoHand"

        if off_hand in ("Escudo", "Rodela"):
            return "Shield"

        if off_hand not in ("Ninguna", "Escudo", "Rodela") or main_weapon in PAIRED_WEAPONS:
            return "Dual"

        return "Single"

    def build_setup(
        self,
        base_candidate,
        mode,
    ):

        candidate = base_candidate.copy()

        main_weapon = (
            base_candidate["main_weapon"]
        )

        one_handed_weapon = (
            main_weapon
            if main_weapon not in TWO_HANDED_WEAPONS
            else "Espada"
        )

        if mode == "Single":

            candidate["main_weapon"] = (
                one_handed_weapon
            )

            candidate["off_hand"] = (
                "Ninguna"
            )

        elif mode == "Shield":

            candidate["main_weapon"] = (
                one_handed_weapon
            )

            candidate["off_hand"] = (
                "Escudo"
            )

        elif mode == "Dual":

            candidate["main_weapon"] = (
                one_handed_weapon
            )

            off_hand = base_candidate[
                "off_hand"
            ]

            if off_hand in (
                "Ninguna",
                "Escudo",
                "Rodela",
            ):
                off_hand = "Daga"

            candidate["off_hand"] = (
                off_hand
            )

        elif mode == "TwoHand":

            candidate["main_weapon"] = (
                "Arma 2H"
            )

            candidate["off_hand"] = (
                "Ninguna"
            )

        return candidate

    def _apply_upgrade(self, candidate, upgrade):
        """Devuelve una copia mejorada; la ficha base no se toca."""
        result = candidate.copy()
        result["skills"] = list(candidate.get("skills", []))

        if not upgrade:
            return result

        upgrade_type, value = upgrade

        if upgrade_type == "attr":
            result[value] += 1
        elif upgrade_type == "skill":
            if value not in result["skills"]:
                result["skills"].append(value)
        elif upgrade_type == "item":
            result[value] = True

        return result

    def _build_upgrade_list(self, base_candidate):
        """Lista las mejoras que todavía tienen sentido para esta ficha."""
        upgrades = []

        for attr in ["I", "HA", "F", "R", "A", "H"]:
            upgrades.append(
                (
                    f"+1 {attr}",
                    ("attr", attr),
                )
            )

        for skill in SKILLS:
            if skill not in base_candidate.get("skills", []):
                upgrades.append(
                    (
                        skill,
                        ("skill", skill),
                    )
                )

        return upgrades

    @staticmethod
    def _equipment_options():
        options = []
        for armor in ARMORS:
            if armor != "Sin Armadura":
                options.append((armor, "armor", armor))
        options.extend([
            ("Casco", "helmet", True),
            ("Amuleto de la suerte", "amulet", True),
        ])
        options.extend(
            (name, "preparation", name)
            for name in PREPARATIONS if name != "Ninguno"
        )
        options.extend(
            (name, "poison", name)
            for name in POISONS if name != "Sin veneno"
        )
        return options

    def _set_equipment_filters(self, selected):
        for variable in self.equipment_item_vars.values():
            variable.set(selected)

    def _selected_equipment_options(self):
        selected = self.equipment_item_vars
        return [
            option for option in self._equipment_options()
            if selected[option[0]].get()
        ]

    @staticmethod
    def _equipment_combination_is_legal(items):
        exclusive_slots = {"armor", "preparation"}
        kinds = [item[1] for item in items]
        if any(kinds.count(kind) > 1 for kind in exclusive_slots):
            return False
        if kinds.count("poison") > 2:
            return False
        non_poisons = [item for item in items if item[1] != "poison"]
        return len(non_poisons) == len(set(non_poisons))

    @staticmethod
    def _equipment_loadouts(options, maximum_items):
        loadouts = []
        for size in range(1, maximum_items + 1):
            for items in combinations_with_replacement(options, size):
                if TrollheimApp._equipment_combination_is_legal(items):
                    loadouts.append((tuple(item[0] for item in items), items))
        return loadouts

    def _set_weapon_filters(self, selected):
        for variable in self.weapon_item_vars.values():
            variable.set(selected)

    def _selected_weapons(self):
        return [
            weapon for weapon, variable in self.weapon_item_vars.items()
            if variable.get()
        ]

    @staticmethod
    def _weapon_loadouts(weapons):
        loadouts = []
        one_handed = [
            weapon for weapon in weapons
            if weapon not in TWO_HANDED_WEAPONS and weapon not in PAIRED_WEAPONS
        ]
        offhand = [weapon for weapon in one_handed if weapon in OFFHAND_CODES]
        main_hand = [
            weapon for weapon in one_handed
            if weapon not in MAIN_HAND_FORBIDDEN_WEAPONS
        ]
        for weapon in main_hand:
            loadouts.append(("Single", weapon, "Ninguna"))
            loadouts.append(("Shield", weapon, "Escudo"))
        for main in main_hand:
            if main == "Mangual":
                continue
            if main in {"Rebanadora", "Pinchagarrapatos"}:
                if "Guantelete con Pincho" in offhand:
                    loadouts.append(("Dual", main, "Guantelete con Pincho"))
                continue
            if main == "Lanza":
                continue
            for off in offhand:
                loadouts.append(("Dual", main, off))
        for weapon in weapons:
            if weapon in TWO_HANDED_WEAPONS or weapon in PAIRED_WEAPONS:
                loadouts.append(("TwoHand", weapon, "Ninguna"))
        return loadouts

    @staticmethod
    def _without_optional_equipment(candidate):
        result = candidate.copy()
        result.update({
            "armor": "Sin Armadura",
            "has_helmet": False,
            "has_luck_amulet": False,
            "preparation": "Ninguno",
            "main_poison": "Sin veneno",
            "offhand_poison": "Sin veneno",
        })
        return result

    @staticmethod
    def _apply_equipment_items(candidate, items):
        result = TrollheimApp._without_optional_equipment(candidate)
        poison_slot = 0
        for _label, kind, value in items:
            if kind == "armor":
                result["armor"] = value
            elif kind == "helmet":
                result["has_helmet"] = True
            elif kind == "amulet":
                result["has_luck_amulet"] = True
            elif kind == "preparation":
                result["preparation"] = value
            elif kind == "poison":
                key = "main_poison" if poison_slot == 0 else "offhand_poison"
                result[key] = value
                poison_slot += 1
        return result

    @staticmethod
    def _read_simulation_count(variable):
        total = int(variable.get().replace("_", "").strip())
        if total < 1:
            raise ValueError("El número de simulaciones debe ser mayor que cero.")
        return total

    def _active_enemy_names(self):
        difficulties = [
            name for name, variable in self.enemy_difficulties.items()
            if variable.get()
        ]
        return profiles_for_difficulties(difficulties)

    def _disable_simulation_buttons(self):
        for name in (
            "btn_run", "btn_equipment_run", "btn_weapons_run", "btn_combo_run",
        ):
            button = getattr(self, name, None)
            if button is not None:
                try:
                    button.config(state="disabled")
                except tk.TclError:
                    # La pestaña dueña del botón puede estar descargada.
                    pass

    @staticmethod
    def _run_tasks(tasks, progress_queue, total_simulations, completion_weights=None):
        """Reparte comparaciones completas sin partir ningún combate."""
        completion_weights = completion_weights or {}
        process_tasks = [
            (*task[:10], None, task[11], *task[12:])
            for task in tasks
        ]

        def report(result):
            if progress_queue is not None:
                weight = completion_weights.get((result[0], result[1]), 1)
                progress_queue.put(("chunk", 0, total_simulations * weight))

        if len(tasks) < 4 or len(tasks) * total_simulations < 100_000:
            results = []
            for task in process_tasks:
                result = run_single_task_optimized(task)
                results.append(result)
                report(result)
            return results

        available_cpus = os.cpu_count() or 4
        # La interfaz también quiere respirar mientras los dados hacen horas extra.
        worker_limit = max(1, available_cpus - 1)
        worker_count = min(8, worker_limit, len(tasks))
        groups = [
            process_tasks[index:index + TASK_GROUP_SIZE]
            for index in range(0, len(process_tasks), TASK_GROUP_SIZE)
        ]
        results = []

        with ProcessPoolExecutor(
            max_workers=worker_count,
            initializer=_configure_simulation_worker,
        ) as executor:
            futures = {
                executor.submit(run_task_batch, group): len(group)
                for group in groups if group
            }
            for future in as_completed(futures):
                batch = future.result()
                results.extend(batch)
                for result in batch:
                    report(result)
        return results

    @staticmethod
    def _deduplicate_tasks(tasks):
        """Agrupa combos que producen exactamente el mismo combatiente efectivo."""
        unique_tasks = []
        aliases = {}
        canonical_by_key = {}

        for task in tasks:
            mode, label, candidate = task[0], task[1], task[2]
            key = (mode, effective_fighter_key(candidate))
            canonical = canonical_by_key.get(key)
            if canonical is None:
                canonical = (mode, label)
                canonical_by_key[key] = canonical
                unique_tasks.append(task)
                aliases[canonical] = []
            aliases[canonical].append((label, task[9]))

        return unique_tasks, aliases

    def _enable_simulation_buttons(self):
        for name in (
            "btn_run", "btn_equipment_run", "btn_weapons_run", "btn_combo_run",
        ):
            button = getattr(self, name, None)
            if button is not None:
                try:
                    button.config(state="normal")
                except tk.TclError:
                    # Igual que arriba: no hay botón que reactivar si la pestaña no existe.
                    pass

    def start_simulation_thread(self):

        try:

            base_candidate = self._candidate_for_simulation()
            total_simulations = self._read_simulation_count(
                self.simulations_improvements
            )

        except ValueError:

            messagebox.showerror(
                "Error",
                "Introduce valores numéricos válidos.",
            )

            return

        if self.enemy_mode.get() == "sample":

            active_enemies = self._active_enemy_names()

            if not active_enemies:

                messagebox.showerror(
                    "Error de Muestra",
                    "Debes seleccionar al menos un enemigo.",
                )

                return

        self._disable_simulation_buttons()
        self._active_progress_var = self.progress_var
        self._active_status_label = self.status_label
        self._active_progress_bar = self.progress_bar
        self._active_button = self.btn_run
        self._progress_target = 0.0
        self._simulation_started_at = time.perf_counter()
        self._progress_indeterminate = True
        self._cancel_progress_poll()

        self.progress_var.set(0)
        self.progress_bar.config(mode="indeterminate")
        self.progress_bar.start(PROGRESS_ANIMATION_MS)

        self.status_label.config(
            text=(
                "Preparando simulación..."
            )
        )

        for row in self.results_tree.get_children():
            self.results_tree.delete(row)
        self._reset_mode_cards(self.result_cards, self.result_visible_modes)

        enemy_mode = (
            self.enemy_mode.get()
        )

        self._simulation_running = True

        thread = threading.Thread(
            target=self.run_simulations_threadpool,
            args=(
                base_candidate,
                enemy_mode,
                total_simulations,
            ),
            daemon=True,
        )

        thread.start()

    def run_simulations_threadpool(
        self,
        base_candidate,
        enemy_mode,
        total_simulations,
    ):

        try:
            custom_enemy = None
            active_pool_names = []

            if enemy_mode == "custom":

                custom_enemy = self._custom_enemies_for_simulation()

            else:

                active_pool_names = self._active_enemy_names()

            upgrades = [
                ("ESTADO BASE", None),
                *self._build_upgrade_list(base_candidate),
            ]

            modes = [
                "Single",
                "Shield",
                "Dual",
                "TwoHand",
            ]

            master_seed = random.randint(
                1,
                2_147_483_647,
            )

            # Misma muestra para todos: comparar dados distintos sería hacer trampas.
            if enemy_mode == "sample":

                self.after(
                    0,
                    self._set_status,
                    "Generando muestra compartida de enemigos...",
                )

                shared_enemy_indices = (
                    _generate_shared_enemy_selection(
                        active_pool_names,
                        total_simulations,
                        master_seed,
                        ENEMY_VARIANTS_PER_PROFILE,
                    )
                )

            else:

                shared_enemy_indices = self._manual_enemy_indices(
                    custom_enemy, total_simulations, master_seed
                )

            progress_queue = queue.Queue()
            self._progress_queue = progress_queue
            self._progress_chunks_done = 0
            self._progress_chunk_total = 0

            tasks = []

            for mode in modes:

                for idx, (
                    label,
                    upgrade,
                ) in enumerate(
                    upgrades
                ):

                    candidate_test = self._apply_upgrade(
                        base_candidate,
                        upgrade,
                    )

                    candidate_test = (
                        self.build_setup(
                            candidate_test,
                            mode,
                        )
                    )

                    is_base = (
                        idx == 0
                    )

                    tasks.append(
                        (
                            mode,
                            label,
                            candidate_test,
                            enemy_mode,
                            custom_enemy,
                            active_pool_names,
                            shared_enemy_indices,
                            total_simulations,
                            master_seed
                            + idx
                            + (
                                modes.index(mode)
                                * 1000
                            ),
                            is_base,
                            progress_queue,
                            len(tasks),
                            self.enemy_level.get(),
                        )
                    )

            total_tasks = len(tasks)

            unique_tasks, aliases = self._deduplicate_tasks(tasks)
            completion_weights = {
                canonical: len(group) for canonical, group in aliases.items()
            }

            raw_results = {
                mode: []
                for mode in modes
            }

            self.after(
                0,
                self._set_status,
                f"Ejecutando {total_tasks} combinaciones vectorizadas...",
            )

            self._progress_chunk_total = (
                total_tasks * total_simulations
            )

            self._progress_poll_id = self.after(
                PROGRESS_POLL_MS, self._poll_simulation_progress
            )

            for mode, label, win_rate, _is_base in self._run_tasks(
                unique_tasks,
                progress_queue,
                total_simulations,
                completion_weights,
            ):
                for alias_label, alias_is_base in aliases[(mode, label)]:
                    raw_results[mode].append(
                        (alias_label, win_rate, alias_is_base)
                    )


            mode_results = {}

            for mode, data in (
                raw_results.items()
            ):

                base_rate = next(
                    rate
                    for label, rate, is_base
                    in data
                    if is_base
                )

                base_tuple = (
                    "ESTADO BASE",
                    base_rate,
                    0.0,
                )

                others = []

                for (
                    label,
                    rate,
                    is_base,
                ) in data:

                    if not is_base:

                        others.append(
                            (
                                label,
                                rate,
                                rate - base_rate,
                            )
                        )

                mode_results[
                    mode
                ] = (
                    base_tuple,
                    others,
                )

            user_mode_key = (
                self.get_user_mode_key(
                    base_candidate
                )
            )

            self._simulation_running = False

            self.after(
                0,
                self.update_ui_with_results,
                mode_results,
                user_mode_key,
                {
                    mode: self._equipment_description(self.build_setup(base_candidate, mode))
                    for mode, _title in COMBAT_MODES
                },
            )

        except Exception as exc:

            self._simulation_running = False

            self.after(
                0,
                self._simulation_error,
                exc,
            )

    def start_equipment_thread(self):
        try:
            base_candidate = self._without_optional_equipment(
                self._candidate_for_simulation()
            )
            total_simulations = self._read_simulation_count(
                self.simulations_equipment
            )
            selected_options = self._selected_equipment_options()
            if not selected_options:
                raise ValueError("Selecciona al menos un objeto para comparar.")
            maximum_items = int(self.equipment_max_items.get())
        except ValueError:
            messagebox.showerror("Error", "Introduce valores numéricos válidos.")
            return

        if self.enemy_mode.get() == "sample" and not self._active_enemy_names():
            messagebox.showerror(
                "Error de Muestra", "Debes seleccionar al menos un enemigo."
            )
            return

        self._disable_simulation_buttons()
        self._active_progress_var = self.equipment_progress_var
        self._active_status_label = self.equipment_status_label
        self._active_progress_bar = self.equipment_progress_bar
        self._active_button = self.btn_equipment_run
        self._progress_target = 0.0
        self._simulation_started_at = time.perf_counter()
        self._progress_indeterminate = True
        self._cancel_progress_poll()

        self.equipment_progress_var.set(0)
        self.equipment_progress_bar.config(mode="indeterminate")
        self.equipment_progress_bar.start(PROGRESS_ANIMATION_MS)
        self.equipment_status_label.config(text="Preparando combinaciones de objetos...")
        for row in self.equipment_tree.get_children():
            self.equipment_tree.delete(row)
        self._reset_mode_cards(
            self.equipment_cards, self.equipment_visible_modes
        )

        self._simulation_running = True
        threading.Thread(
            target=self.run_equipment_simulations_threadpool,
            args=(
                base_candidate, self.enemy_mode.get(), total_simulations,
                selected_options, maximum_items,
            ),
            daemon=True,
        ).start()

    def run_equipment_simulations_threadpool(
        self, base_candidate, enemy_mode, total_simulations, options,
        maximum_items,
    ):
        try:
            custom_enemy = None
            active_pool_names = []
            if enemy_mode == "custom":
                custom_enemy = self._custom_enemies_for_simulation()
            else:
                active_pool_names = self._active_enemy_names()

            loadouts = self._equipment_loadouts(options, maximum_items)
            modes = [mode for mode, _title in COMBAT_MODES]
            master_seed = random.randint(1, 2_147_483_647)

            if enemy_mode == "sample":
                self.after(
                    0, self._set_status,
                    "Generando muestra compartida de enemigos...",
                )
                shared_enemy_indices = _generate_shared_enemy_selection(
                    active_pool_names, total_simulations, master_seed,
                    ENEMY_VARIANTS_PER_PROFILE,
                )
            else:
                shared_enemy_indices = self._manual_enemy_indices(
                    custom_enemy, total_simulations, master_seed
                )

            progress_queue = queue.Queue()
            self._progress_queue = progress_queue
            self._progress_chunks_done = 0
            tasks = []
            for mode_index, mode in enumerate(modes):
                base_test = self.build_setup(base_candidate, mode)
                tasks.append((
                    mode, "ESTADO BASE", base_test, enemy_mode, custom_enemy,
                    active_pool_names, shared_enemy_indices, total_simulations,
                    master_seed + mode_index * 100_000, True, progress_queue,
                    len(tasks), self.enemy_level.get(),
                ))
                for loadout_index, (labels, items) in enumerate(loadouts, 1):
                    candidate_test = self._apply_equipment_items(base_candidate, items)
                    candidate_test = self.build_setup(candidate_test, mode)
                    padded_labels = (*labels, *("",) * (3 - len(labels)))
                    label = " || ".join(padded_labels)
                    tasks.append((
                        mode, label, candidate_test, enemy_mode, custom_enemy,
                        active_pool_names, shared_enemy_indices, total_simulations,
                        master_seed + mode_index * 100_000 + loadout_index,
                        False, progress_queue, len(tasks), self.enemy_level.get(),
                    ))

            total_tasks = len(tasks)
            unique_tasks, aliases = self._deduplicate_tasks(tasks)
            completion_weights = {
                canonical: len(group) for canonical, group in aliases.items()
            }
            self._progress_chunk_total = total_tasks * total_simulations
            self.after(
                0, self._set_status,
                f"Ejecutando {len(unique_tasks)} combates efectivos para "
                f"{total_tasks} resultados...",
            )
            self._progress_poll_id = self.after(
                PROGRESS_POLL_MS, self._poll_simulation_progress
            )

            raw_results = {mode: [] for mode in modes}
            for mode, label, win_rate, _is_base in self._run_tasks(
                unique_tasks, progress_queue, total_simulations, completion_weights
            ):
                for alias_label, alias_is_base in aliases[(mode, label)]:
                    raw_results[mode].append(
                        (alias_label, win_rate, alias_is_base)
                    )

            equipment_results = {}
            for mode, data in raw_results.items():
                base_rate = next(rate for _label, rate, is_base in data if is_base)
                equipment_results[mode] = (
                    base_rate,
                    [
                        (label, rate, rate - base_rate)
                        for label, rate, is_base in data if not is_base
                    ],
                )

            self._simulation_running = False
            self.after(
                0, self.update_ui_with_equipment_results, equipment_results,
                self.get_user_mode_key(base_candidate),
                {
                    mode: self._equipment_description(self.build_setup(base_candidate, mode))
                    for mode, _title in COMBAT_MODES
                },
            )
        except Exception as exc:
            self._simulation_running = False
            self.after(0, self._simulation_error, exc)

    def update_ui_with_equipment_results(
        self, equipment_results, user_mode_key, equipment
    ):
        base_rates = {mode: data[0] for mode, data in equipment_results.items()}
        self._update_mode_cards(
            self.equipment_cards, base_rates, user_mode_key, equipment
        )
        self._equipment_card_data = (base_rates, user_mode_key, equipment)
        self._equipment_table_data = (equipment_results, equipment)
        self._render_equipment_table()

        self._finish_progress(
            self.equipment_progress_var,
            self.equipment_status_label,
            "Análisis de equipamiento completado",
        )
        self._enable_simulation_buttons()

    def _render_equipment_table(self):
        table_data = getattr(self, "_equipment_table_data", None)
        if not table_data:
            return
        equipment_results, equipment = table_data
        rows = {}
        for mode, (_base_rate, results) in equipment_results.items():
            for label, rate, impact in results:
                rows.setdefault(label, {})[mode] = (rate, impact)

        for item in self.equipment_tree.get_children():
            self.equipment_tree.delete(item)
        ordered = sorted(
            rows.items(),
            key=lambda item: max(
                (
                    value[0] for mode, value in item[1].items()
                    if mode in self.equipment_visible_modes
                ),
                default=-1.0,
            ),
            reverse=True,
        )
        for label, values in ordered:
            first, second, third = label.split(" || ", 2)
            best_mode = self._best_visible_mode(
                values, self.equipment_visible_modes,
            )
            if best_mode is None:
                continue
            cells = []
            for mode, _title in COMBAT_MODES:
                if mode not in values:
                    cells.append("")
                    continue
                rate, impact = values[mode]
                marker = "★ " if mode == best_mode else ""
                cells.append(f"{marker}{rate:.2f}% ({impact:+.2f}%)")
            best_rate, best_impact = values[best_mode]
            self.equipment_tree.insert(
                "", "end",
                values=(
                    first,
                    second or "—",
                    third or "—",
                    *cells,
                    f"★ {best_rate:.2f}% ({best_impact:+.2f}%)",
                    equipment[best_mode],
                ),
            )
        self._autosize_tree_columns(self.equipment_tree)

    def start_weapon_thread(self):
        try:
            base_candidate = self._candidate_for_simulation()
            total_simulations = self._read_simulation_count(self.simulations_weapons)
            weapons = self._selected_weapons()
            if not weapons:
                raise ValueError("Selecciona al menos un arma para comparar.")
        except ValueError as exc:
            messagebox.showerror("Error", str(exc))
            return

        if self.enemy_mode.get() == "sample" and not self._active_enemy_names():
            messagebox.showerror(
                "Error de Muestra", "Debes seleccionar al menos un enemigo."
            )
            return

        self._disable_simulation_buttons()
        self._active_progress_var = self.weapon_progress_var
        self._active_status_label = self.weapon_status_label
        self._active_progress_bar = self.weapon_progress_bar
        self._active_button = self.btn_weapons_run
        self._simulation_started_at = time.perf_counter()
        self._progress_indeterminate = True
        self._cancel_progress_poll()
        self.weapon_progress_var.set(0)
        self.weapon_progress_bar.config(mode="indeterminate")
        self.weapon_progress_bar.start(PROGRESS_ANIMATION_MS)
        self.weapon_status_label.config(text="Preparando configuraciones de armas...")
        for row in self.weapon_tree.get_children():
            self.weapon_tree.delete(row)
        self._reset_mode_cards(self.weapon_cards, self.weapon_visible_modes)

        self._simulation_running = True
        threading.Thread(
            target=self.run_weapon_simulations_threadpool,
            args=(base_candidate, self.enemy_mode.get(), total_simulations, weapons),
            daemon=True,
        ).start()

    def run_weapon_simulations_threadpool(
        self, base_candidate, enemy_mode, total_simulations, weapons
    ):
        try:
            custom_enemy = None
            active_pool_names = []
            if enemy_mode == "custom":
                custom_enemy = self._custom_enemies_for_simulation()
            else:
                active_pool_names = self._active_enemy_names()

            modes = [mode for mode, _title in COMBAT_MODES]
            loadouts = self._weapon_loadouts(weapons)
            master_seed = random.randint(1, 2_147_483_647)
            if enemy_mode == "sample":
                self.after(
                    0, self._set_status,
                    "Generando muestra compartida de enemigos...",
                )
                shared_enemy_indices = _generate_shared_enemy_selection(
                    active_pool_names, total_simulations, master_seed,
                    ENEMY_VARIANTS_PER_PROFILE,
                )
            else:
                shared_enemy_indices = self._manual_enemy_indices(
                    custom_enemy, total_simulations, master_seed
                )

            progress_queue = queue.Queue()
            self._progress_queue = progress_queue
            self._progress_chunks_done = 0
            tasks = []
            for mode_index, mode in enumerate(modes):
                current = self.build_setup(base_candidate, mode)
                tasks.append((
                    mode, "ESTADO BASE", current, enemy_mode, custom_enemy,
                    active_pool_names, shared_enemy_indices, total_simulations,
                    master_seed + mode_index * 100_000, True, progress_queue,
                    len(tasks), self.enemy_level.get(),
                ))

            for index, (mode, main, off) in enumerate(loadouts, 1):
                candidate = base_candidate.copy()
                candidate["main_weapon"] = main
                candidate["off_hand"] = off
                label = f"{main} || {off}"
                tasks.append((
                    mode, label, candidate, enemy_mode, custom_enemy,
                    active_pool_names, shared_enemy_indices, total_simulations,
                    master_seed + modes.index(mode) * 100_000 + index,
                    False, progress_queue, len(tasks), self.enemy_level.get(),
                ))

            total_tasks = len(tasks)
            unique_tasks, aliases = self._deduplicate_tasks(tasks)
            completion_weights = {
                canonical: len(group) for canonical, group in aliases.items()
            }
            self._progress_chunk_total = total_tasks * total_simulations
            self.after(
                0, self._set_status,
                f"Ejecutando {len(unique_tasks)} combates efectivos para "
                f"{total_tasks} configuraciones...",
            )
            self._progress_poll_id = self.after(
                PROGRESS_POLL_MS, self._poll_simulation_progress
            )

            raw_results = {mode: [] for mode in modes}
            for mode, label, win_rate, _is_base in self._run_tasks(
                unique_tasks, progress_queue, total_simulations, completion_weights
            ):
                for alias_label, alias_is_base in aliases[(mode, label)]:
                    raw_results[mode].append((alias_label, win_rate, alias_is_base))

            weapon_results = {}
            for mode, data in raw_results.items():
                base_rate = next(rate for _label, rate, is_base in data if is_base)
                weapon_results[mode] = (
                    base_rate,
                    [
                        (label, rate, rate - base_rate)
                        for label, rate, is_base in data if not is_base
                    ],
                )

            self._simulation_running = False
            self.after(
                0, self.update_ui_with_weapon_results, weapon_results,
                self.get_user_mode_key(base_candidate),
                {
                    mode: self._equipment_description(self.build_setup(base_candidate, mode))
                    for mode, _title in COMBAT_MODES
                },
            )
        except Exception as exc:
            self._simulation_running = False
            self.after(0, self._simulation_error, exc)

    def update_ui_with_weapon_results(
        self, weapon_results, user_mode_key, equipment
    ):
        base_rates = {mode: data[0] for mode, data in weapon_results.items()}
        self._update_mode_cards(
            self.weapon_cards, base_rates, user_mode_key, equipment
        )
        self._weapon_card_data = (base_rates, user_mode_key, equipment)
        self._weapon_table_data = (weapon_results, equipment)
        self._render_weapon_table()
        self._finish_progress(
            self.weapon_progress_var,
            self.weapon_status_label,
            "Análisis de armas completado",
        )
        self._enable_simulation_buttons()

    def _render_weapon_table(self):
        table_data = getattr(self, "_weapon_table_data", None)
        if not table_data:
            return
        weapon_results, equipment = table_data
        rows = {}
        for mode, (_base_rate, results) in weapon_results.items():
            for label, rate, impact in results:
                rows.setdefault(label, {})[mode] = (rate, impact)

        for item in self.weapon_tree.get_children():
            self.weapon_tree.delete(item)
        ordered = sorted(
            rows.items(),
            key=lambda item: max(
                (
                    value[0] for mode, value in item[1].items()
                    if mode in self.weapon_visible_modes
                ),
                default=-1.0,
            ),
            reverse=True,
        )
        for label, values in ordered:
            main, off = label.split(" || ", 1)
            best_mode = self._best_visible_mode(values, self.weapon_visible_modes)
            if best_mode is None:
                continue
            cells = []
            for mode, _title in COMBAT_MODES:
                if mode not in values:
                    cells.append("")
                    continue
                rate, impact = values[mode]
                marker = "★ " if mode == best_mode else ""
                cells.append(f"{marker}{rate:.2f}% ({impact:+.2f}%)")
            best_rate, best_impact = values[best_mode]
            self.weapon_tree.insert(
                "", "end",
                values=(
                    main,
                    off if off != "Ninguna" else "—",
                    *cells,
                    f"★ {best_rate:.2f}% ({best_impact:+.2f}%)",
                    equipment[best_mode],
                ),
            )
        self._autosize_tree_columns(self.weapon_tree)

    def start_combo_thread(self):
        try:
            base_candidate = self._candidate_for_simulation()
            total_simulations = self._read_simulation_count(self.simulations_combos)
        except ValueError:
            messagebox.showerror(
                "Error",
                "Introduce valores numéricos válidos.",
            )
            return

        if self.enemy_mode.get() == "sample":
            active_enemies = self._active_enemy_names()
            if not active_enemies:
                messagebox.showerror(
                    "Error de Muestra",
                    "Debes seleccionar al menos un enemigo.",
                )
                return

        self._disable_simulation_buttons()
        self._active_progress_var = self.combo_progress_var
        self._active_status_label = self.combo_status_label
        self._active_progress_bar = self.combo_progress_bar
        self._active_button = self.btn_combo_run
        self._progress_target = 0.0
        self._simulation_started_at = time.perf_counter()
        self._progress_indeterminate = True
        self._cancel_progress_poll()

        self.combo_progress_var.set(0)
        self.combo_progress_bar.config(mode="indeterminate")
        self.combo_progress_bar.start(PROGRESS_ANIMATION_MS)
        self.combo_status_label.config(text="Preparando combos...")

        for row in self.combo_tree.get_children():
            self.combo_tree.delete(row)
        self._reset_mode_cards(self.combo_cards, self.combo_visible_modes)

        enemy_mode = self.enemy_mode.get()
        self._simulation_running = True

        threading.Thread(
            target=self.run_combo_simulations_threadpool,
            args=(base_candidate, enemy_mode, total_simulations),
            daemon=True,
        ).start()

    def run_combo_simulations_threadpool(self, base_candidate, enemy_mode, total_simulations):
        try:
            custom_enemy = None
            active_pool_names = []

            if enemy_mode == "custom":
                custom_enemy = self._custom_enemies_for_simulation()
            else:
                active_pool_names = self._active_enemy_names()

            upgrade_options = self._build_upgrade_list(base_candidate)
            if len(upgrade_options) < 2:
                raise ValueError("No hay suficientes mejoras disponibles para formar combos de 2 mejoras.")

            modes = ["Single", "Shield", "Dual", "TwoHand"]
            master_seed = random.randint(1, 2_147_483_647)

            if enemy_mode == "sample":
                self.after(0, self._set_status, "Generando muestra compartida de enemigos...")
                shared_enemy_indices = _generate_shared_enemy_selection(
                    active_pool_names,
                    total_simulations,
                    master_seed,
                    ENEMY_VARIANTS_PER_PROFILE,
                )
            else:
                shared_enemy_indices = self._manual_enemy_indices(
                    custom_enemy, total_simulations, master_seed
                )

            progress_queue = queue.Queue()
            self._progress_queue = progress_queue
            self._progress_chunks_done = 0
            self._progress_chunk_total = 0

            tasks = []

            # Una referencia por táctica; sin ella el delta sería puro humo.
            for mode_index, mode in enumerate(modes):
                base_test = self.build_setup(base_candidate, mode)
                tasks.append((
                    mode,
                    "ESTADO BASE",
                    base_test,
                    enemy_mode,
                    custom_enemy,
                    active_pool_names,
                    shared_enemy_indices,
                    total_simulations,
                    master_seed + mode_index * 1000,
                    True,
                    progress_queue,
                    len(tasks),
                    self.enemy_level.get(),
                ))

            for mode_index, mode in enumerate(modes):
                for i in range(len(upgrade_options)):
                    for j in range(i + 1, len(upgrade_options)):
                        label_a, upgrade_a = upgrade_options[i]
                        label_b, upgrade_b = upgrade_options[j]

                        candidate_test = self._apply_upgrade(
                            base_candidate,
                            upgrade_a,
                        )
                        candidate_test = self._apply_upgrade(
                            candidate_test,
                            upgrade_b,
                        )
                        candidate_test = self.build_setup(
                            candidate_test,
                            mode,
                        )

                        tasks.append((
                            mode,
                            f"{label_a} + {label_b}",
                            candidate_test,
                            enemy_mode,
                            custom_enemy,
                            active_pool_names,
                            shared_enemy_indices,
                            total_simulations,
                            master_seed + mode_index * 100_000 + i * 100 + j,
                            False,
                            progress_queue,
                            len(tasks),
                            self.enemy_level.get(),
                        ))

            total_tasks = len(tasks)
            unique_tasks, aliases = self._deduplicate_tasks(tasks)
            completion_weights = {
                canonical: len(group)
                for canonical, group in aliases.items()
            }
            raw_results = {mode: [] for mode in modes}

            self.after(
                0,
                self._set_status,
                f"Ejecutando {len(unique_tasks)} combates efectivos para "
                f"{total_tasks} resultados...",
            )

            self._progress_chunk_total = total_tasks * total_simulations
            self._progress_poll_id = self.after(
                PROGRESS_POLL_MS, self._poll_simulation_progress
            )

            for mode, label, win_rate, _is_base in self._run_tasks(
                unique_tasks, progress_queue, total_simulations, completion_weights
            ):
                for alias_label, alias_is_base in aliases[(mode, label)]:
                    raw_results[mode].append((alias_label, win_rate, alias_is_base))

            combo_results = {}
            for mode, data in raw_results.items():
                base_rate = next(
                    rate for label, rate, is_base in data if is_base
                )
                combos = [
                    (label, rate, rate - base_rate)
                    for label, rate, is_base in data
                    if not is_base
                ]
                combo_results[mode] = (base_rate, combos)

            self._simulation_running = False
            self.after(
                0,
                self.update_ui_with_combo_results,
                combo_results,
                self.get_user_mode_key(base_candidate),
                {
                    mode: self._equipment_description(self.build_setup(base_candidate, mode))
                    for mode, _title in COMBAT_MODES
                },
            )

        except Exception as exc:
            self._simulation_running = False
            self.after(0, self._simulation_error, exc)

    def update_ui_with_combo_results(self, combo_results, user_mode_key, equipment):
        base_rates = {mode: data[0] for mode, data in combo_results.items()}
        self._update_mode_cards(self.combo_cards, base_rates, user_mode_key, equipment)
        self._combo_card_data = (base_rates, user_mode_key, equipment)

        self._combo_table_data = (combo_results, equipment)
        self._render_combo_table()

        active_progress_var = self._active_progress_var
        active_status_label = self._active_status_label

        self._finish_progress(active_progress_var, active_status_label, "Análisis de combos completado")
        self._enable_simulation_buttons()

    def _render_combo_table(self):
        if not getattr(self, "_combo_table_data", None):
            return
        combo_results, equipment = self._combo_table_data
        visible_modes = self.combo_visible_modes
        search = self.combo_search.get()
        for item in self.combo_tree.get_children():
            self.combo_tree.delete(item)

        rows = {}
        for mode, (_base_rate, combos) in combo_results.items():
            for label, rate, impact in combos:
                rows.setdefault(label, {})[mode] = (rate, impact)

        ordered_rows = sorted(
            rows.items(),
            key=lambda item: max(
                item[1][mode][0] for mode in visible_modes
            ),
            reverse=True,
        )
        for label, values in ordered_rows:
            parts = self._combo_parts(label)
            if not self._combo_matches(parts, search):
                continue
            best_mode = self._best_visible_mode(values, visible_modes)
            cells = []
            for mode, _title in COMBAT_MODES:
                rate, impact = values[mode]
                marker = "★ " if mode == best_mode else ""
                cells.append(f"{marker}{rate:.2f}% ({impact:+.2f}%)")
            optimal = f"★ {values[best_mode][0]:.2f}% ({values[best_mode][1]:+.2f}%)"
            first, second = parts
            self.combo_tree.insert(
                "", "end",
                values=(first, second, *cells, optimal, equipment[best_mode]),
            )
        self._autosize_tree_columns(self.combo_tree)

    def _set_status(
        self,
        text,
    ):
        label = getattr(self, "_active_status_label", None)
        if label is not None:
            label.config(text=text)

    def _switch_progress_to_determinate(self):
        if not getattr(self, "_progress_indeterminate", False):
            return
        bar = getattr(self, "_active_progress_bar", None)
        if bar is None:
            return
        bar.stop()
        bar.config(mode="determinate")
        self._active_progress_var.set(0.0)
        self._progress_indeterminate = False

    def _cancel_progress_poll(self):
        poll_id = getattr(self, "_progress_poll_id", None)
        if poll_id is not None:
            try:
                self.after_cancel(poll_id)
            except tk.TclError:
                pass
        self._progress_poll_id = None

    def _finish_progress(self, progress_var, status_label, message):
        self._cancel_progress_poll()
        self._switch_progress_to_determinate()
        progress_var.set(100.0)
        elapsed = time.perf_counter() - self._simulation_started_at
        status_label.config(
            text=f"100% · {message} · Tiempo total: {self._format_elapsed(elapsed)}"
        )

    @staticmethod
    def _format_elapsed(seconds):
        if seconds < 60:
            return f"{seconds:.1f} s"
        minutes, remaining = divmod(int(round(seconds)), 60)
        return f"{minutes} min {remaining:02d} s"

    def _poll_simulation_progress(self):
        """Vacía la cola de progreso sin bloquear a Tkinter."""
        self._progress_poll_id = None
        q = getattr(self, "_progress_queue", None)
        if q is None:
            return

        received = 0
        try:
            while True:
                kind, _task_id, amount = q.get_nowait()
                if kind == "chunk":
                    received += amount
        except queue.Empty:
            pass

        if received:
            self._switch_progress_to_determinate()
            self._progress_chunks_done += received

        total = max(1, int(self._progress_chunk_total))
        target = min(
            100.0,
            self._progress_chunks_done * 100.0 / total,
        )

        progress_var = getattr(self, "_active_progress_var", None)
        status_label = getattr(self, "_active_status_label", None)
        if progress_var is None or status_label is None:
            return

        if not getattr(self, "_progress_indeterminate", False):
            current = target
            progress_var.set(current)
        else:
            current = 0.0

        completed = min(
            int(self._progress_chunks_done),
            total,
        )
        if getattr(self, "_progress_indeterminate", False):
            status_label.config(text="Iniciando trabajadores y preparando combates...")
        else:
            status_label.config(
                text=(
                    f"Procesando combates... "
                    f"{completed:,}/{total:,} "
                    f"({current:.1f}%)"
                )
            )

        if getattr(self, "_simulation_running", False):
            self._progress_poll_id = self.after(
                PROGRESS_POLL_MS, self._poll_simulation_progress
            )

    def _simulation_error(
        self,
        exc,
    ):

        self._enable_simulation_buttons()
        self._cancel_progress_poll()
        self._switch_progress_to_determinate()

        active_status_label = getattr(self, "_active_status_label", None)
        if active_status_label is not None:
            active_status_label.config(text="Error.")

        messagebox.showerror(
            "Error del simulador",
            str(exc),
        )

    def update_ui_with_results(
        self,
        mode_results,
        user_mode_key,
        equipment,
    ):
        base_rates = {mode: data[0][1] for mode, data in mode_results.items()}
        self._update_mode_cards(self.result_cards, base_rates, user_mode_key, equipment)
        self._results_card_data = (base_rates, user_mode_key, equipment)

        self._results_table_data = (mode_results, equipment)
        self._render_results_table()

        active_progress_var = self._active_progress_var
        active_status_label = self._active_status_label

        self._finish_progress(active_progress_var, active_status_label, "Análisis completado")

        self._enable_simulation_buttons()

    def _render_results_table(self):
        if not getattr(self, "_results_table_data", None):
            return
        mode_results, equipment = self._results_table_data
        visible_modes = self.result_visible_modes
        for item in self.results_tree.get_children():
            self.results_tree.delete(item)

        rows = {}
        for mode, (_base_item, others) in mode_results.items():
            for label, rate, impact in others:
                rows.setdefault(label, {})[mode] = (rate, impact)

        ordered_rows = sorted(
            rows.items(),
            key=lambda item: max(
                item[1][mode][0] for mode in visible_modes
            ),
            reverse=True,
        )
        for label, values in ordered_rows:
            best_mode = self._best_visible_mode(values, visible_modes)
            cells = []
            for mode, _title in COMBAT_MODES:
                rate, impact = values[mode]
                marker = "★ " if mode == best_mode else ""
                cells.append(f"{marker}{rate:.2f}% ({impact:+.2f}%)")
            optimal = f"★ {values[best_mode][0]:.2f}% ({values[best_mode][1]:+.2f}%)"
            self.results_tree.insert(
                "", "end",
                values=(label, *cells, optimal, equipment[best_mode]),
            )
        self._autosize_tree_columns(self.results_tree)
