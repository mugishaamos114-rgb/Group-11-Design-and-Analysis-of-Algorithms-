
"""
recursion_tab.py - Module A screens: Fibonacci, Factorial and the animated
Tower of Hanoi.  All computation is done by backend.recursion.
"""

import tkinter as tk
from tkinter import ttk

from backend import recursion
from backend.core import format_ns, parse_int
from backend.stack import ArrayStack

from . import theme
from .widgets import MessageLine, Table, card, explanation, labelled_entry


def short_number(value):
    """Show very long integers as 'first…last (N digits)'."""
    text = str(value)
    if len(text) <= 36:
        return text
    head = ""
    tail = ""
    i = 0
    while i < 14:
        head += text[i]
        tail += text[len(text) - 14 + i]
        i += 1
    return head + "…" + tail + "  (" + "{:,}".format(len(text)) + " digits)"


class RecursionTab(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent, padding=10)
        book = ttk.Notebook(self, style="Sub.TNotebook")
        book.pack(fill="both", expand=True)
        book.add(FibonacciPanel(book), text="Fibonacci")
        book.add(FactorialPanel(book), text="Factorial")
        book.add(HanoiPanel(book), text="Tower of Hanoi")


# ===========================================================================
class FibonacciPanel(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent, style="Card.TFrame", padding=14)
        ttk.Label(self, text="Fibonacci numbers - three ways", style="Title.TLabel").pack(anchor="w")
        explanation(self, "fib(0) = 0, fib(1) = 1, fib(n) = fib(n-1) + fib(n-2). Enter n and compare naive "
                          "recursion (O(1.6ⁿ)), memoized recursion (O(n)) and bottom-up dynamic programming "
                          "(O(n) time, O(1) space).").pack(anchor="w", pady=(2, 10))
        row = ttk.Frame(self, style="Card.TFrame")
        row.pack(anchor="w")
        self.n_box = labelled_entry(row, "n =", 8, "25")
        self.n_box.pack(side="left")
        self.n_box.entry.bind("<Return>", lambda e: self.run())
        ttk.Button(row, text="Compute all three", style="Accent.TButton", command=self.run).pack(side="left", padx=10)
        for n in (10, 30, 100, 1000):
            ttk.Button(row, text="n = %d" % n, command=lambda v=n: self._quick(v)).pack(side="left", padx=2)

        self.msg = MessageLine(self)
        self.msg.pack(fill="x", pady=8)
        self.table = Table(self, ("Method", "Result", "Calls / iterations", "Time", "Complexity"),
                           (180, 330, 150, 110, 120), height=4)
        self.table.pack(fill="x")

        why = card(self)
        why.pack(fill="x", pady=(12, 0))
        ttk.Label(why.inner, text="Why is naive recursion limited to n ≤ %d?" % recursion.FIB_NAIVE_MAX,
                  style="Title.TLabel").pack(anchor="w")
        explanation(why.inner, recursion.FIB_NAIVE_EXPLANATION).pack(anchor="w", pady=(4, 0))
        ttk.Label(self, text="Full value of fib(n):", style="Card.TLabel").pack(anchor="w", pady=(12, 2))
        self.full = tk.Text(self, height=4, wrap="char", font=theme.mono(9), relief="flat",
                            bg="#f7f6f2", highlightthickness=1, highlightbackground=theme.LINE)
        self.full.pack(fill="both", expand=True)

    def _quick(self, n):
        self.n_box.entry.delete(0, "end")
        self.n_box.entry.insert(0, str(n))
        self.run()

    def run(self):
        n, error = parse_int(self.n_box.entry.get(), "n", 0, recursion.FIB_BOTTOM_UP_MAX)
        if error:
            self.msg.error(error)
            return
        self.table.clear()
        if n <= recursion.FIB_NAIVE_MAX:
            r = recursion.fib_naive(n)
            self.table.add((r.name, short_number(r.value), "{:,} calls".format(r.operations),
                            format_ns(r.time_ns), "O(1.6ⁿ)"))
        else:
            self.table.add(("Naive recursion", "skipped: n > %d" % recursion.FIB_NAIVE_MAX,
                            "≈ {:,.0f} calls".format(1.618 ** n * 1.17), "would take too long", "O(1.6ⁿ)"))
        if n <= recursion.FIB_MEMO_MAX:
            r = recursion.fib_memo(n)
            self.table.add((r.name, short_number(r.value), "{:,} calls".format(r.operations),
                            format_ns(r.time_ns), "O(n)"))
        else:
            self.table.add(("Memoized recursion", "skipped: n > %d (recursion depth)" % recursion.FIB_MEMO_MAX,
                            "", "", "O(n)"))
        r = recursion.fib_bottom_up(n)
        self.table.add((r.name, short_number(r.value), "{:,} iterations".format(r.operations),
                        format_ns(r.time_ns), "O(n)"))
        self.full.delete("1.0", "end")
        self.full.insert("1.0", str(r.value))
        self.msg.ok("fib(%d) computed. It has %d digit(s)." % (n, len(str(r.value))))


# ===========================================================================
class FactorialPanel(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent, style="Card.TFrame", padding=14)
        ttk.Label(self, text="Factorial - recursive and iterative", style="Title.TLabel").pack(anchor="w")
        explanation(self, "n! = n × (n-1)!, with 0! = 1. Both versions are O(n); the recursive one also uses "
                          "O(n) stack space for the n nested calls. Negative n is rejected.").pack(anchor="w", pady=(2, 10))
        row = ttk.Frame(self, style="Card.TFrame")
        row.pack(anchor="w")
        self.n_box = labelled_entry(row, "n =", 8, "10")
        self.n_box.pack(side="left")
        self.n_box.entry.bind("<Return>", lambda e: self.run())
        ttk.Button(row, text="Compute", style="Accent.TButton", command=self.run).pack(side="left", padx=10)
        for n in (0, 5, 20, 500):
            ttk.Button(row, text="n = %d" % n, command=lambda v=n: self._quick(v)).pack(side="left", padx=2)
        self.msg = MessageLine(self)
        self.msg.pack(fill="x", pady=8)
        self.table = Table(self, ("Method", "Result", "Calls / iterations", "Time", "Complexity"),
                           (150, 360, 150, 110, 120), height=3)
        self.table.pack(fill="x")
        ttk.Label(self, text="Full value of n!:", style="Card.TLabel").pack(anchor="w", pady=(12, 2))
        self.full = tk.Text(self, height=6, wrap="char", font=theme.mono(9), relief="flat",
                            bg="#f7f6f2", highlightthickness=1, highlightbackground=theme.LINE)
        self.full.pack(fill="both", expand=True)

    def _quick(self, n):
        self.n_box.entry.delete(0, "end")
        self.n_box.entry.insert(0, str(n))
        self.run()

    def run(self):
        n, error = parse_int(self.n_box.entry.get(), "n", -10 ** 9, recursion.FACT_ITER_MAX)
        if error:
            self.msg.error(error)
            return
        if n < 0:
            self.msg.error("Factorial is not defined for negative numbers - please enter n ≥ 0.")
            return
        self.table.clear()
        if n <= recursion.FACT_REC_MAX:
            r = recursion.factorial_recursive(n)
            self.table.add((r.name, short_number(r.value), "{:,} calls".format(r.operations),
                            format_ns(r.time_ns), "O(n)"))
        else:
            self.table.add(("Recursive", "skipped: n > %d (Python recursion depth)" % recursion.FACT_REC_MAX,
                            "", "", "O(n)"))
        r = recursion.factorial_iterative(n)
        self.table.add((r.name, short_number(r.value), "{:,} iterations".format(r.operations),
                        format_ns(r.time_ns), "O(n)"))
        self.full.delete("1.0", "end")
        self.full.insert("1.0", str(r.value))
        self.msg.ok("%d! computed%s." % (n, " (0! = 1 by definition)" if n == 0 else ""))


# ===========================================================================
class HanoiPanel(ttk.Frame):
    PEGS = ("A", "B", "C")

    def __init__(self, parent):
        super().__init__(parent, style="Card.TFrame", padding=14)
        self.moves = None            # DynamicArray of HanoiMove
        self.next_move = 0
        self.pegs = None             # peg name -> ArrayStack of disk sizes
        self.disk_count = 0
        self.running = False
        self.anim = None             # current animation state
        self.after_id = None

        top = ttk.Frame(self, style="Card.TFrame")
        top.pack(fill="x")
        ttk.Label(top, text="Tower of Hanoi (animated)", style="Title.TLabel").pack(side="left")

        controls = ttk.Frame(self, style="Card.TFrame")
        controls.pack(fill="x", pady=(8, 4))
        ttk.Label(controls, text="Disks", style="Card.TLabel").pack(side="left")
        self.disks = ttk.Spinbox(controls, from_=1, to=recursion.HANOI_MAX_DISKS, width=4)
        self.disks.set("4")
        self.disks.pack(side="left", padx=(4, 12))
        self.source = self._peg_box(controls, "Source", "A")
        self.dest = self._peg_box(controls, "Destination", "C")
        self.aux = self._peg_box(controls, "Auxiliary", "B")
        ttk.Button(controls, text="Solve", style="Accent.TButton", command=self.solve).pack(side="left", padx=(8, 3))
        controls = ttk.Frame(self, style="Card.TFrame")
        controls.pack(fill="x", pady=(2, 4))
        self.start_btn = ttk.Button(controls, text="▶ Start", command=self.start)
        self.start_btn.pack(side="left", padx=3)
        ttk.Button(controls, text="⏸ Pause", command=self.pause).pack(side="left", padx=3)
        ttk.Button(controls, text="Step ⏭", command=self.step).pack(side="left", padx=3)
        ttk.Button(controls, text="↺ Reset", command=self.reset).pack(side="left", padx=3)
        ttk.Label(controls, text="Speed", style="Card.TLabel").pack(side="left", padx=(14, 4))
        self.speed = ttk.Scale(controls, from_=1, to=10, orient="horizontal", length=120)
        self.speed.set(5)
        self.speed.pack(side="left")

        self.msg = MessageLine(self)
        self.msg.pack(fill="x", pady=4)

        body = ttk.Frame(self, style="Card.TFrame")
        body.pack(fill="both", expand=True)
        self.canvas = tk.Canvas(body, bg="#fbfbf9", highlightthickness=1, highlightbackground=theme.LINE,
                                height=260)
        self.canvas.pack(side="left", fill="both", expand=True)
        self.canvas.bind("<Configure>", lambda e: self.draw())
        side = ttk.Frame(body, style="Card.TFrame", padding=(10, 0, 0, 0))
        side.pack(side="right", fill="y")
        self.counter = tk.Label(side, text="Moves: 0 / 0", bg=theme.CARD, fg=theme.INK, font=theme.font(14, "bold"))
        self.counter.pack(anchor="w")
        self.formula = tk.Label(side, text="", bg=theme.CARD, fg=theme.MUTED, font=theme.font(9), justify="left")
        self.formula.pack(anchor="w", pady=(0, 6))
        self.listbox = tk.Listbox(side, width=30, height=14, font=theme.mono(9), activestyle="none",
                                  selectbackground=theme.ACCENT_LIGHT, selectforeground=theme.INK,
                                  highlightthickness=1, highlightbackground=theme.LINE, relief="flat")
        self.listbox.pack(fill="y", expand=True)
        self.solve()

    def _peg_box(self, parent, label, default):
        ttk.Label(parent, text=label, style="Card.TLabel").pack(side="left")
        box = ttk.Combobox(parent, values=self.PEGS, width=3, state="readonly")
        box.set(default)
        box.pack(side="left", padx=(4, 10))
        return box

    # ---- solving and state ---------------------------------------------
    def solve(self):
        self.pause()
        n, error = parse_int(self.disks.get(), "Number of disks", 1, recursion.HANOI_MAX_DISKS)
        if error:
            self.msg.error(error)
            return
        s, d, a = self.source.get(), self.dest.get(), self.aux.get()
        if s == d or s == a or d == a:
            self.msg.error("Source, destination and auxiliary must be three different pegs.")
            return
        result = recursion.hanoi(n, s, d, a)
        self.moves = result.value
        self.disk_count = n
        self.listbox.delete(0, "end")
        i = 0
        while i < self.moves.size():
            self.listbox.insert("end", "%3d. %s" % (i + 1, self.moves.get(i)))
            i += 1
        self.formula.configure(text="Expected: 2^%d − 1 = %d\nRecursive calls: %d\nSolved in %s"
                               % (n, 2 ** n - 1, result.extra, format_ns(result.time_ns)))
        self.msg.info("Solved recursively: %d moves from %s to %s using %s. Press Start or Step."
                      % (self.moves.size(), s, d, a))
        self.reset_pegs()

    def reset_pegs(self):
        self.pegs = {}
        for name in self.PEGS:
            self.pegs[name] = ArrayStack(max(self.disk_count, 1))
        size = self.disk_count
        while size >= 1:                                   # largest disk at the bottom
            self.pegs[self.source.get()].push(size)
            size -= 1
        self.next_move = 0
        self.anim = None
        self.listbox.selection_clear(0, "end")
        self.update_counter()
        self.draw()

    def reset(self):
        self.pause()
        if self.moves is not None:
            self.reset_pegs()
            self.msg.info("Reset - all disks back on peg %s." % self.source.get())

    def update_counter(self):
        total = self.moves.size() if self.moves else 0
        self.counter.configure(text="Moves: %d / %d" % (self.next_move, total))

    # ---- animation -------------------------------------------------------
    def start(self):
        if self.moves is None:
            return
        if self.next_move >= self.moves.size():
            self.reset_pegs()
        self.running = True
        if self.anim is None:
            self._begin_move()
        self._tick()

    def pause(self):
        self.running = False
        if self.after_id is not None:
            self.after_cancel(self.after_id)
            self.after_id = None

    def step(self):
        """Perform exactly one move (animated quickly)."""
        if self.moves is None or self.anim is not None:
            return
        if self.next_move >= self.moves.size():
            self.msg.info("Puzzle already solved - press Reset to start again.")
            return
        self.pause()
        self._begin_move(fast=True)
        self._tick()

    def _begin_move(self, fast=False):
        if self.next_move >= self.moves.size():
            self._finished()
            return
        move = self.moves.get(self.next_move)
        disk = self.pegs[move.source].pop()
        self.anim = {"move": move, "disk": disk, "phase": 0, "t": 0.0, "fast": fast}
        self.listbox.selection_clear(0, "end")
        self.listbox.selection_set(self.next_move)
        self.listbox.see(self.next_move)

    def _frames_per_phase(self):
        if self.anim and self.anim["fast"]:
            return 4
        return max(2, int(26 / float(self.speed.get())))

    def _tick(self):
        self.after_id = None
        if self.anim is None:
            return
        self.anim["t"] += 1.0 / self._frames_per_phase()
        if self.anim["t"] >= 1.0:
            self.anim["t"] = 0.0
            self.anim["phase"] += 1
            if self.anim["phase"] == 3:                    # lift, slide, drop done
                move = self.anim["move"]
                self.pegs[move.target].push(self.anim["disk"])
                self.anim = None
                self.next_move += 1
                self.update_counter()
                self.draw()
                if self.next_move >= self.moves.size():
                    self._finished()
                    return
                if self.running:
                    self._begin_move()
                else:
                    self.msg.info(str(move))
                    return
        self.draw()
        self.after_id = self.after(16, self._tick)

    def _finished(self):
        self.running = False
        n = self.disk_count
        ok = self.moves.size() == 2 ** n - 1
        self.msg.ok("Done! All %d disks are on peg %s. Total moves %d %s 2^%d − 1 = %d."
                    % (n, self.dest.get(), self.moves.size(), "=" if ok else "≠", n, 2 ** n - 1))

    # ---- drawing ---------------------------------------------------------
    def _geometry(self):
        w = max(self.canvas.winfo_width(), 300)
        h = max(self.canvas.winfo_height(), 200)
        base = h - 40
        disk_h = min(26, (h - 120) / max(self.disk_count + 1, 2))
        peg_x = {}
        i = 0
        while i < 3:
            peg_x[self.PEGS[i]] = w * (i * 2 + 1) / 6
            i += 1
        max_w = w / 3 - 24
        return w, h, base, disk_h, peg_x, max_w

    def _disk_rect(self, size, x_center, y_bottom, disk_h, max_w):
        width = 30 + (max_w - 30) * (size - 1) / max(self.disk_count - 1, 1)
        return x_center - width / 2, y_bottom - disk_h, x_center + width / 2, y_bottom

    def _draw_disk(self, size, rect):
        colour = theme.SERIES[(size - 1) % len(theme.SERIES)]
        x1, y1, x2, y2 = rect
        self.canvas.create_rectangle(x1, y1 + 1, x2, y2 - 1, fill=colour, outline="#ffffff", width=2)
        self.canvas.create_text((x1 + x2) / 2, (y1 + y2) / 2, text=str(size), fill="#ffffff",
                                font=theme.font(9, "bold"))

    def draw(self):
        c = self.canvas
        c.delete("all")
        if self.pegs is None:
            return
        w, h, base, disk_h, peg_x, max_w = self._geometry()
        c.create_rectangle(20, base, w - 20, base + 10, fill="#8d7b68", outline="")
        roles = {self.source.get(): "source", self.dest.get(): "destination", self.aux.get(): "auxiliary"}
        for name in self.PEGS:
            x = peg_x[name]
            c.create_rectangle(x - 4, base - (self.disk_count + 1.5) * disk_h - 10, x + 4, base,
                               fill="#b9a68f", outline="")
            c.create_text(x, base + 24, text="%s  (%s)" % (name, roles.get(name, "")), fill=theme.INK,
                          font=theme.font(10, "bold"))
            stack = self.pegs[name]
            disks = stack.display()
            level = 0
            while level < len(disks):
                self._draw_disk(disks[level], self._disk_rect(disks[level], x, base - level * disk_h,
                                                              disk_h, max_w))
                level += 1
        if self.anim is not None:                           # the moving disk
            move = self.anim["move"]
            sx, tx = peg_x[move.source], peg_x[move.target]
            lift_y = base - (self.disk_count + 2.5) * disk_h - 10
            start_y = base - self.pegs[move.source].size() * disk_h
            end_y = base - self.pegs[move.target].size() * disk_h
            t = self.anim["t"]
            if self.anim["phase"] == 0:
                x, y = sx, start_y + (lift_y - start_y) * t
            elif self.anim["phase"] == 1:
                x, y = sx + (tx - sx) * t, lift_y
            else:
                x, y = tx, lift_y + (end_y - lift_y) * t
            self._draw_disk(self.anim["disk"], self._disk_rect(self.anim["disk"], x, y, disk_h, max_w))
