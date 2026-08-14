"""Arranque de la aplicación y gestión de errores fatales."""

import ctypes
import os
import sys
import tkinter as tk
import traceback
from multiprocessing import freeze_support
from tkinter import messagebox

from .ui import TrollheimApp


def _configure_windows_dpi():
    if sys.platform != "win32":
        return
    try:
        # Evita el salto de tamaño al mover la ventana entre monitores con DPI distinto.
        ctypes.windll.user32.SetProcessDpiAwarenessContext(ctypes.c_void_p(-4))
    except (AttributeError, OSError):
        try:
            ctypes.windll.shcore.SetProcessDpiAwareness(1)
        except (AttributeError, OSError):
            pass


def _show_fatal_startup_error(exc):
    error_text = "".join(
        traceback.format_exception(type(exc), exc, exc.__traceback__)
    )
    try:
        root = tk.Tk()
        root.withdraw()
        messagebox.showerror(
            "Trollheim - Error al iniciar",
            "Trollheim no ha podido iniciarse.\n\n" + error_text,
        )
        root.destroy()
    except Exception:
        try:
            base = (
                os.path.dirname(sys.executable)
                if getattr(sys, "frozen", False)
                else os.getcwd()
            )
            with open(
                os.path.join(base, "Trollheim_startup_error.txt"),
                "w",
                encoding="utf-8",
            ) as error_file:
                error_file.write(error_text)
        except Exception:
            pass


def _configure_frozen_runtime():
    if getattr(sys, "frozen", False):
        try:
            os.chdir(os.path.dirname(sys.executable))
        except Exception:
            pass


def main():
    try:
        freeze_support()
        _configure_frozen_runtime()
        _configure_windows_dpi()
        app = TrollheimApp()
        app.mainloop()
    except Exception as exc:
        _show_fatal_startup_error(exc)
        return 1
    return 0
