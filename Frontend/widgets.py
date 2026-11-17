"""
widgets.py - small reusable interface pieces: cards, message line, tables,
a scrollable canvas and a line chart drawn on a Tk Canvas (no matplotlib needed).
"""

import math
import tkinter as tk
from tkinter import ttk

from . import theme


def card(parent, padding=12):
    """A white panel with a thin border."""
    outer = tk.Frame(parent, bg=theme.LINE, bd=0)
    inner = ttk.Frame(outer, style="Card.TFrame", padding=padding)
    inner.pack(fill="both", expand=True, padx=1, pady=1)
    outer.inner = inner
    return outer


class MessageLine(tk.Label):
    """One-line status message: green for success, red for errors."""

    def __init__(self, parent, **kw):
        super().__init__(parent, text="", anchor="w", justify="left", bg=theme.CARD,
                         fg=theme.MUTED, font=theme.font(10, "bold"), wraplength=900, **kw)

    def ok(self, text):
        self.configure(text="✔  " + text, fg=theme.OK)

    def error(self, text):
        self.configure(text="✖  " + text, fg=theme.ERROR)

    def info(self, text):
        self.configure(text=text, fg=theme.INFO)

    def warn(self, text):
        self.configure(text="⚠  " + text, fg=theme.WARN)


class Table(ttk.Frame):
    """A Treeview with headings and a vertical scrollbar."""

    def __init__(self, parent, columns, widths, height=8, anchors=None):
        super().__init__(parent, style="Card.TFrame")
        self.tree = ttk.Treeview(self, columns=columns, show="headings", height=height)
        i = 0
        while i < len(columns):
            anchor = anchors[i] if anchors else ("w" if i == 0 else "e")
            self.tree.heading(columns[i], text=columns[i], anchor=anchor)
            self.tree.column(columns[i], width=widths[i], anchor=anchor, stretch=True)
            i += 1
        bar = ttk.Scrollbar(self, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=bar.set)
        self.tree.pack(side="left", fill="both", expand=True)
        bar.pack(side="right", fill="y")

    def clear(self):
        self.tree.delete(*self.tree.get_children())

    def add(self, values, tag=None):
        return self.tree.insert("", "end", values=values, tags=(tag,) if tag else ())


def labelled_entry(parent, label, width=10, default=""):
    """Label + Entry side by side; returns the Entry."""
    frame = ttk.Frame(parent, style="Card.TFrame")
    ttk.Label(frame, text=label, style="Card.TLabel").pack(side="left", padx=(0, 6))
    entry = ttk.Entry(frame, width=width)
    entry.insert(0, default)
    entry.pack(side="left")
    frame.entry = entry
    return frame


def explanation(parent, text, wrap=900):
    """Muted paragraph used for on-screen explanations."""
    return tk.Label(parent, text=text, bg=theme.CARD, fg=theme.MUTED, font=theme.font(9),
                    justify="left", anchor="w", wraplength=wrap)


class ScrollCanvas(ttk.Frame):
    """A Canvas with horizontal and vertical scrollbars."""

    def __init__(self, parent, height=260):
        super().__init__(parent, style="Card.TFrame")
        self.canvas = tk.Canvas(self, bg="#fbfbf9", height=height, highlightthickness=1,
                                highlightbackground=theme.LINE)
        xbar = ttk.Scrollbar(self, orient="horizontal", command=self.canvas.xview)
        ybar = ttk.Scrollbar(self, orient="vertical", command=self.canvas.yview)
        self.canvas.configure(xscrollcommand=xbar.set, yscrollcommand=ybar.set)
        self.canvas.grid(row=0, column=0, sticky="nsew")
        ybar.grid(row=0, column=1, sticky="ns")
        xbar.grid(row=1, column=0, sticky="ew")
        self.rowconfigure(0, weight=1)
        self.columnconfigure(0, weight=1)

    def fit(self):
        box = self.canvas.bbox("all")
        if box:
            self.canvas.configure(scrollregion=(0, 0, box[2] + 30, box[3] + 20))


def nice_ticks(high, count=5):
    """Return a 'nice' tick step for an axis going from 0 to high."""
    if high <= 0:
        return 1
    raw = high / count
    power = 10 ** math.floor(math.log10(raw))
    for m in (1, 2, 2.5, 5, 10):
        if raw <= m * power:
            return m * power
    return 10 * power


class LineChart(tk.Canvas):
    """Simple multi-series line chart with axes, legend and a hover tooltip.

    set_data(title, x_label, y_label, series) where series is a sequence of
    (name, colour, points) and points is a sequence of (x, y) sorted by x."""

    PAD_L, PAD_R, PAD_T, PAD_B = 62, 18, 54, 44

    def __init__(self, parent, width=460, height=300):
        super().__init__(parent, width=width, height=height, bg=theme.CARD, highlightthickness=0)
        self.title = ""
        self.x_label = ""
        self.y_label = ""
        self.series = ()
        self._points = []                    # screen points for hover: (sx, sy, text)
        self.bind("<Configure>", lambda e: self.redraw())
        self.bind("<Motion>", self._hover)
        self.bind("<Leave>", lambda e: self.delete("tip"))

    def set_data(self, title, x_label, y_label, series):
        self.title, self.x_label, self.y_label, self.series = title, x_label, y_label, series
        self.redraw()

    def redraw(self):
        self.delete("all")
        w = max(self.winfo_width(), 200)
        h = max(self.winfo_height(), 160)
        self.create_text(self.PAD_L - 50, 16, text=self.title, anchor="w", fill=theme.INK,
                         font=theme.font(10, "bold"))
        x_max, y_max = 0, 0
        has_data = False
        for _, _, pts in self.series:
            for x, y in pts:
                has_data = True
                if x > x_max:
                    x_max = x
                if y > y_max:
                    y_max = y
        left, right, top, bottom = self.PAD_L, w - self.PAD_R, self.PAD_T, h - self.PAD_B
        if not has_data:
            self.create_text(w / 2, h / 2, text="No data yet - run the analysis.", fill=theme.MUTED,
                             font=theme.font(9))
            return
        if y_max <= 0:
            y_max = 1
        if x_max <= 0:
            x_max = 1
        y_step = nice_ticks(y_max)
        y_top = y_step * math.ceil(y_max / y_step)
        x_step = nice_ticks(x_max, 4)
        x_top = x_step * math.ceil(x_max / x_step)

        def sx(x):
            return left + (right - left) * x / x_top

        def sy(y):
            return bottom - (bottom - top) * y / y_top

        v = 0
        while v <= y_top + 1e-9:                       # horizontal grid + y labels
            self.create_line(left, sy(v), right, sy(v), fill="#ecebe6")
            self.create_text(left - 6, sy(v), text=_fmt(v), anchor="e", fill=theme.MUTED, font=theme.font(8))
            v += y_step
        v = 0
        while v <= x_top + 1e-9:                       # x labels
            self.create_text(sx(v), bottom + 12, text="{:,.0f}".format(v), fill=theme.MUTED, font=theme.font(8))
            v += x_step
        self.create_line(left, bottom, right, bottom, fill="#8a8984")
        self.create_text((left + right) / 2, h - 10, text=self.x_label, fill=theme.MUTED, font=theme.font(8))
        self.create_text(12, (top + bottom) / 2, text=self.y_label, angle=90, fill=theme.MUTED, font=theme.font(8))

        self._points = []
        lx = left
        for name, colour, pts in self.series:          # legend row under the title
            if len(pts) == 0:
                continue
            self.create_line(lx, 36, lx + 18, 36, fill=colour, width=2)
            self.create_oval(lx + 5, 32, lx + 13, 40, fill=colour, outline=theme.CARD, width=2)
            label = self.create_text(lx + 24, 36, text=name, anchor="w", fill=theme.INK, font=theme.font(8))
            lx = self.bbox(label)[2] + 16
            coords = []
            for x, y in pts:
                coords += [sx(x), sy(y)]
            if len(pts) > 1:
                self.create_line(*coords, fill=colour, width=2, smooth=False)
            for x, y in pts:
                self.create_oval(sx(x) - 4, sy(y) - 4, sx(x) + 4, sy(y) + 4, fill=colour,
                                 outline=theme.CARD, width=2)
                self._points.append((sx(x), sy(y), "%s\nn = %s\n%s ms" % (name, "{:,}".format(x), _fmt(y))))

    def _hover(self, event):
        self.delete("tip")
        best, best_d = None, 14 * 14
        for px, py, text in self._points:
            d = (px - event.x) ** 2 + (py - event.y) ** 2
            if d < best_d:
                best, best_d = (px, py, text), d
        if best is None:
            return
        px, py, text = best
        t = self.create_text(px + 10, py - 10, text=text, anchor="sw", fill=theme.INK,
                             font=theme.font(8), tags="tip")
        x1, y1, x2, y2 = self.bbox(t)
        if x2 > self.winfo_width() - 4:
            self.move(t, -(x2 - x1) - 20, 0)
            x1, y1, x2, y2 = self.bbox(t)
        r = self.create_rectangle(x1 - 5, y1 - 4, x2 + 5, y2 + 4, fill="#ffffff", outline=theme.LINE, tags="tip")
        self.tag_raise(t, r)


def _fmt(v):
    if v >= 100:
        return "{:,.0f}".format(v)
    if v >= 10:
        return "%.1f" % v
    if v >= 1:
        return "%.2f" % v
    return "%.3f" % v
