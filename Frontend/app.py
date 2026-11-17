"""
app.py - the main window: a header and one tab per module.
"""

import tkinter as tk
from tkinter import ttk

from . import theme
from .analysis_tab import AnalysisTab
from .ds_tab import DataStructuresTab
from .recursion_tab import RecursionTab
from .sorting_tab import SortingTab

GROUP = "Group 11"


class AlgorithmExplorer(tk.Tk):
    def __init__(self):
        super().__init__()
        theme.apply(self)
        self.title("Algorithm Explorer — CSC2107 %s" % GROUP)
        # Fit smaller (or scaled) laptop screens.
        width = min(1280, self.winfo_screenwidth() - 40)
        height = min(820, self.winfo_screenheight() - 90)
        self.geometry("%dx%d" % (width, height))
        self.minsize(1000, 620)

        header = tk.Frame(self, bg=theme.ACCENT_DARK, height=56)
        header.pack(fill="x")
        tk.Label(header, text="Algorithm Explorer", bg=theme.ACCENT_DARK, fg="#ffffff",
                 font=theme.font(16, "bold")).pack(side="left", padx=(18, 10), pady=10)
        tk.Label(header, text="CSC2107 Design and Analysis of Algorithms  ·  %s  ·  Uganda Christian University" % GROUP,
                 bg=theme.ACCENT_DARK, fg="#c9d6f0", font=theme.font(10)).pack(side="left", pady=10)

        self.book = ttk.Notebook(self)
        self.book.pack(fill="both", expand=True, padx=8, pady=(8, 8))
        self.book.add(RecursionTab(self.book), text="A · Recursion Lab")
        self.book.add(DataStructuresTab(self.book), text="B · Data Structures Lab")
        self.book.add(SortingTab(self.book), text="C · Sorting Lab")
        self.book.add(AnalysisTab(self.book), text="D · Complexity Analysis")


def main():
    app = AlgorithmExplorer()
    app.mainloop()

