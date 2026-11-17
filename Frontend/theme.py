"""
theme.py - colours, fonts and ttk styles shared by every screen.
"""

import tkinter as tk
import tkinter.font as tkfont
from tkinter import ttk

BG = "#f4f3ef"          # window background
CARD = "#ffffff"        # panels
INK = "#1d1d1b"         # main text
MUTED = "#5f5e5a"       # secondary text
LINE = "#dcdad3"        # borders and grid lines
ACCENT = "#1f4fa3"      # buttons, headings
ACCENT_DARK = "#173c7d"
ACCENT_LIGHT = "#e8eef9"
OK = "#1a7f37"
ERROR = "#b42318"
WARN = "#a15c00"
INFO = "#1f4fa3"

# Colours of the sorting bars, indexed by the TAG_* constants in backend.sorting
BAR_COLORS = [
    "#a9b8cc",   # 0 normal
    "#eb6834",   # 1 compared
    "#d92d2d",   # 2 swapped / moved
    "#6250d6",   # 3 pivot
    "#0f766e",   # 4 in final place
    "#f2c230",   # 5 yellow region (< pivot)
    "#5fc98a",   # 6 green region (>= pivot)
    "#5b8fd6",   # 7 range being merged / partitioned
]
BAR_LABELS = ["Unsorted", "Compared", "Swapped / moved", "Pivot", "Final place",
              "Yellow: < pivot", "Green: ≥ pivot", "Current range"]

# Categorical colours (validated colour-blind-safe order) for chart series and disks
SERIES = ["#2a78d6", "#eb6834", "#1baf7a", "#eda100", "#e87ba4", "#008300", "#6250d6", "#e34948"]

FONT_FAMILY = "TkDefaultFont"
MONO_FAMILY = "TkFixedFont"


def _first_available(wanted, available):
    """Return the first font in `wanted` that exists in `available` (a tuple)."""
    i = 0
    while i < len(wanted):
        j = 0
        while j < len(available):
            if available[j] == wanted[i]:
                return wanted[i]
            j += 1
        i += 1
    return None


def font(size=10, weight="normal"):
    return (FONT_FAMILY, size, weight)


def mono(size=10):
    return (MONO_FAMILY, size)


def apply(root):
    """Configure fonts and ttk styles.  Call once after creating the Tk root."""
    global FONT_FAMILY, MONO_FAMILY
    families = tkfont.families(root)
    FONT_FAMILY = _first_available(("Segoe UI", "SF Pro Text", "Helvetica Neue", "Ubuntu",
                                    "DejaVu Sans", "Arial"), families) or "TkDefaultFont"
    MONO_FAMILY = _first_available(("Cascadia Mono", "Consolas", "Menlo", "DejaVu Sans Mono",
                                    "Courier New"), families) or "TkFixedFont"

    root.configure(bg=BG)
    style = ttk.Style(root)
    style.theme_use("clam")
    style.configure(".", background=BG, foreground=INK, font=font(10), bordercolor=LINE,
                    lightcolor=BG, darkcolor=BG, troughcolor="#e7e5df", focuscolor=ACCENT)
    style.configure("TFrame", background=BG)
    style.configure("Card.TFrame", background=CARD, relief="flat")
    style.configure("TLabel", background=BG, foreground=INK)
    style.configure("Card.TLabel", background=CARD)
    style.configure("Muted.TLabel", background=CARD, foreground=MUTED, font=font(9))
    style.configure("Title.TLabel", background=CARD, foreground=ACCENT_DARK, font=font(12, "bold"))
    style.configure("Big.TLabel", background=CARD, foreground=INK, font=font(16, "bold"))
    style.configure("TLabelframe", background=CARD, bordercolor=LINE, relief="solid")
    style.configure("TLabelframe.Label", background=CARD, foreground=ACCENT_DARK, font=font(10, "bold"))
    style.configure("TCheckbutton", background=CARD)
    style.configure("TRadiobutton", background=CARD)
    style.map("TCheckbutton", background=[("active", CARD)])
    style.map("TRadiobutton", background=[("active", CARD)])

    style.configure("TButton", padding=(10, 5), background="#f1f0ec", foreground=INK,
                    bordercolor=LINE, font=font(10))
    style.map("TButton", background=[("active", "#e6e4de"), ("disabled", "#f4f3ef")],
              foreground=[("disabled", "#a3a29d")])
    style.configure("Accent.TButton", background=ACCENT, foreground="#ffffff", bordercolor=ACCENT_DARK,
                    font=font(10, "bold"))
    style.map("Accent.TButton", background=[("active", ACCENT_DARK), ("disabled", "#9fb0cf")],
              foreground=[("disabled", "#eef1f7")])

    style.configure("TEntry", fieldbackground="#ffffff", bordercolor=LINE, padding=4)
    style.configure("TSpinbox", fieldbackground="#ffffff", bordercolor=LINE, padding=3)
    style.configure("TCombobox", fieldbackground="#ffffff", bordercolor=LINE, padding=3)

    style.configure("TNotebook", background=BG, borderwidth=0, tabmargins=(8, 6, 8, 0))
    style.configure("TNotebook.Tab", padding=(16, 7), background="#e7e5df", foreground=MUTED,
                    font=font(10, "bold"), bordercolor=LINE)
    style.map("TNotebook.Tab", background=[("selected", CARD)], foreground=[("selected", ACCENT_DARK)])
    style.configure("Sub.TNotebook", background=CARD, tabmargins=(4, 4, 4, 0))
    style.configure("Sub.TNotebook.Tab", padding=(12, 5), font=font(9, "bold"))

    style.configure("Treeview", background="#ffffff", fieldbackground="#ffffff", foreground=INK,
                    rowheight=24, bordercolor=LINE, font=font(9))
    style.configure("Treeview.Heading", background="#efeee9", foreground=INK, font=font(9, "bold"),
                    bordercolor=LINE, relief="flat")
    style.map("Treeview", background=[("selected", ACCENT_LIGHT)], foreground=[("selected", INK)])
    style.configure("Horizontal.TProgressbar", background=ACCENT, troughcolor="#e7e5df",
                    bordercolor=LINE, lightcolor=ACCENT, darkcolor=ACCENT)
    style.configure("Horizontal.TScale", background=CARD)

