"""
sorting_tab.py - Module C screen: enter or generate numbers, run a sort,
step through the recorded frames (or auto-play them), see comparison / swap
counts and time, compare all algorithms, and read the complexity table.
"""

import threading
import tkinter as tk
from tkinter import ttk

from backend import sorting
from backend.core import array_to_text, format_ns, format_number, make_input, parse_int, parse_number_list

from . import theme
from .widgets import MessageLine, Table, explanation

MAX_N = 20_000


class SortingTab(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent, padding=10)
        self.data = None
        self.result = None
        self.frame_index = 0
        self.playing = False
        self.after_id = None
        self.worker = None
        self.pending = None

        # ---- input card ---------------------------------------------------
        top = ttk.Frame(self, style="Card.TFrame", padding=(12, 8))
        top.pack(fill="x")
        row1 = ttk.Frame(top, style="Card.TFrame")
        row1.pack(fill="x")
        ttk.Label(row1, text="Input", style="Title.TLabel").pack(side="left", padx=(0, 10))
        self.entry = ttk.Entry(row1)
        self.entry.insert(0, "38, 27, 43, 3, 9, 82, 10, 55, 21, 67, 14, 5")
        self.entry.pack(side="left", fill="x", expand=True)
        ttk.Button(row1, text="Generate", command=self.generate).pack(side="right", padx=(4, 0))
        self.gen_kind = ttk.Combobox(row1, values=("random", "sorted", "reverse"), width=8, state="readonly")
        self.gen_kind.set("random")
        self.gen_kind.pack(side="right", padx=4)
        self.gen_n = ttk.Spinbox(row1, from_=1, to=MAX_N, width=7)
        self.gen_n.set("20")
        self.gen_n.pack(side="right")
        ttk.Label(row1, text="or generate  n =", style="Card.TLabel").pack(side="right", padx=(14, 4))

        row2 = ttk.Frame(top, style="Card.TFrame")
        row2.pack(fill="x", pady=(8, 0))
        ttk.Label(row2, text="Algorithm", style="Card.TLabel").pack(side="left")
        names = [a.name for a in sorting.ALGORITHMS]
        self.algo = ttk.Combobox(row2, values=names, width=24, state="readonly")
        self.algo.set(names[0])
        self.algo.pack(side="left", padx=(4, 12))
        self.level = tk.IntVar(value=sorting.RECORD_PASSES)
        ttk.Radiobutton(row2, text="Show each pass / merge / partition", value=sorting.RECORD_PASSES,
                        variable=self.level).pack(side="left", padx=4)
        ttk.Radiobutton(row2, text="Every comparison & swap (n ≤ %d)" % sorting.MAX_RECORD_N_DETAILED,
                        value=sorting.RECORD_DETAILED, variable=self.level).pack(side="left", padx=4)
        self.cmp_btn = ttk.Button(row2, text="Compare all", command=self.compare_all)
        self.cmp_btn.pack(side="right", padx=(4, 0))
        self.run_btn = ttk.Button(row2, text="Sort", style="Accent.TButton", command=self.run)
        self.run_btn.pack(side="right", padx=4)
        self.msg = MessageLine(top)
        self.msg.pack(fill="x", pady=(6, 0))

        panes = ttk.PanedWindow(self, orient="vertical")
        panes.pack(fill="both", expand=True, pady=(8, 0))

        # ---- visualisation ----------------------------------------------------
        middle = ttk.Frame(panes, style="Card.TFrame", padding=12)
        panes.add(middle, weight=3)
        left = ttk.Frame(middle, style="Card.TFrame")
        left.pack(side="left", fill="both", expand=True)
        self.caption = tk.Label(left, text="Press Sort to start.", bg=theme.CARD, fg=theme.INK,
                                font=theme.font(10, "bold"), anchor="w", justify="left")
        self.caption.pack(fill="x")
        self.canvas = tk.Canvas(left, bg="#fbfbf9", highlightthickness=1, highlightbackground=theme.LINE, height=180)
        self.canvas.pack(fill="both", expand=True, pady=4)
        self.canvas.bind("<Configure>", lambda e: self.draw())
        controls = ttk.Frame(left, style="Card.TFrame")
        controls.pack(fill="x")
        ttk.Button(controls, text="⏮ Start", command=lambda: self.goto(0)).pack(side="left", padx=2)
        ttk.Button(controls, text="◀ Back", command=lambda: self.goto(self.frame_index - 1)).pack(side="left", padx=2)
        ttk.Button(controls, text="Step ▶", command=lambda: self.goto(self.frame_index + 1)).pack(side="left", padx=2)
        self.play_btn = ttk.Button(controls, text="▶ Auto-play", command=self.toggle_play)
        self.play_btn.pack(side="left", padx=2)
        ttk.Button(controls, text="End ⏭", command=lambda: self.goto(self._frame_count() - 1)).pack(side="left", padx=2)
        ttk.Label(controls, text="Speed", style="Card.TLabel").pack(side="left", padx=(14, 4))
        self.speed = ttk.Scale(controls, from_=1, to=10, length=130)
        self.speed.set(5)
        self.speed.pack(side="left")
        self.step_label = ttk.Label(controls, text="", style="Muted.TLabel")
        self.step_label.pack(side="right")
        legend = tk.Frame(left, bg=theme.CARD)
        legend.pack(fill="x", pady=(6, 0))
        i = 0
        while i < len(theme.BAR_COLORS):
            tk.Label(legend, bg=theme.BAR_COLORS[i], width=2).pack(side="left", padx=(8 if i else 0, 3))
            tk.Label(legend, text=theme.BAR_LABELS[i], bg=theme.CARD, fg=theme.MUTED,
                     font=theme.font(8)).pack(side="left")
            i += 1

        stats = ttk.Frame(middle, style="Card.TFrame", padding=(16, 0, 0, 0))
        stats.pack(side="right", fill="y")
        self.stat_vars = {}
        for key, label in (("algo", "Algorithm"), ("n", "n"), ("comparisons", "Comparisons"),
                           ("moves", "Swaps / moves"), ("time", "Execution time"), ("result", "Sorted?")):
            ttk.Label(stats, text=label, style="Muted.TLabel").pack(anchor="w", pady=(2, 0))
            var = tk.StringVar(value="–")
            tk.Label(stats, textvariable=var, bg=theme.CARD, fg=theme.INK,
                     font=theme.font(12, "bold")).pack(anchor="w")
            self.stat_vars[key] = var
        explanation(stats, "Timed with perf_counter_ns,\nwithout step recording.", wrap=210).pack(anchor="w", pady=(10, 0))

        # ---- bottom notebook ----------------------------------------------
        book = ttk.Notebook(panes, style="Sub.TNotebook")
        panes.add(book, weight=1)
        steps_frame = ttk.Frame(book, style="Card.TFrame", padding=6)
        self.steps_text = tk.Text(steps_frame, height=4, font=theme.mono(9), relief="flat", wrap="none",
                                  bg="#fbfbf9", highlightthickness=1, highlightbackground=theme.LINE)
        bar = ttk.Scrollbar(steps_frame, command=self.steps_text.yview)
        self.steps_text.configure(yscrollcommand=bar.set)
        self.steps_text.pack(side="left", fill="both", expand=True)
        bar.pack(side="right", fill="y")
        book.add(steps_frame, text="Array after every step")
        cmp_frame = ttk.Frame(book, style="Card.TFrame", padding=6)
        self.cmp_table = Table(cmp_frame, ("Algorithm", "Comparisons", "Swaps / moves", "Time", "Sorted correctly"),
                               (220, 140, 160, 120, 130), height=4)
        self.cmp_table.pack(fill="both", expand=True)
        book.add(cmp_frame, text="Compare all")
        cx_frame = ttk.Frame(book, style="Card.TFrame", padding=6)
        cx = Table(cx_frame, ("Algorithm", "Best", "Average", "Worst", "Extra space", "Stable"),
                   (220, 110, 110, 110, 110, 80), height=4, anchors=("w", "center", "center", "center", "center", "center"))
        for a in sorting.ALGORITHMS:
            cx.add((a.name, a.best, a.average, a.worst, a.space, a.stable))
        cx.pack(fill="both", expand=True)
        explanation(cx_frame, sorting.COMPLEXITY_NOTES).pack(anchor="w")
        book.add(cx_frame, text="Complexity help")
        self.book = book
        self.panes = panes
        self.sash_placed = False
        panes.bind("<Configure>", lambda e: self._place_sash())

    def _place_sash(self):
        """The first time the tab is shown, give the bars most of the height
        (the step log gets about 135 px); after that the user can drag it."""
        h = self.panes.winfo_height()
        if not self.sash_placed and h > 300:
            self.sash_placed = True
            self.after_idle(lambda: self.panes.sashpos(0, h - 135))

    # ---- input -------------------------------------------------------------
    def generate(self):
        n, error = parse_int(self.gen_n.get(), "n", 1, MAX_N)
        if error:
            self.msg.error(error)
            return
        data = make_input(self.gen_kind.get(), n)
        self.entry.delete(0, "end")
        self.entry.insert(0, array_to_text(data, MAX_N)[1:-1])
        self.msg.ok("Generated %d %s values." % (n, self.gen_kind.get()))

    def read_input(self):
        data, error = parse_number_list(self.entry.get(), MAX_N)
        if error:
            self.msg.error(error)
            return None
        return data

    def selected_key(self):
        for a in sorting.ALGORITHMS:
            if a.name == self.algo.get():
                return a.key
        return sorting.ALGORITHMS[0].key

    # ---- running (in a background thread so the window never freezes) ------
    def _busy(self, busy):
        state = "disabled" if busy else "normal"
        self.run_btn.configure(state=state)
        self.cmp_btn.configure(state=state)

    def _start_worker(self, job, done):
        self._busy(True)
        self.pending = None

        def work():
            try:
                self.pending = ("ok", job())
            except Exception as e:          # show unexpected errors instead of crashing
                self.pending = ("error", e)
        self.worker = threading.Thread(target=work, daemon=True)
        self.worker.start()
        self._poll(done)

    def _poll(self, done):
        if self.pending is None:
            self.after(60, lambda: self._poll(done))
            return
        self._busy(False)
        status, value = self.pending
        if status == "error":
            self.msg.error("Unexpected error: %s" % value)
        else:
            done(value)

    def run(self):
        data = self.read_input()
        if data is None:
            return
        self.stop()
        n = len(data)
        level = self.level.get()
        note = ""
        if level == sorting.RECORD_DETAILED and n > sorting.MAX_RECORD_N_DETAILED:
            level = sorting.RECORD_PASSES
            note = " Every-comparison view needs n ≤ %d, showing passes instead." % sorting.MAX_RECORD_N_DETAILED
        if n > sorting.MAX_RECORD_N_PASSES:
            level = sorting.RECORD_OFF
            note = " Step display is available for n ≤ %d; counts and time are still shown." % sorting.MAX_RECORD_N_PASSES
        key = self.selected_key()
        self.data = data
        self.msg.info("Sorting %d values with %s…" % (n, self.algo.get()))
        self._start_worker(lambda: sorting.run_sort(key, data, level), lambda r: self._show(r, note))

    def _show(self, r, note):
        self.result = r
        self.stat_vars["algo"].set(r.name)
        self.stat_vars["n"].set("{:,}".format(len(r.array)))
        self.stat_vars["comparisons"].set("{:,}".format(r.comparisons))
        self.stat_vars["moves"].set("{:,} {}".format(r.moves, r.moves_label))
        self.stat_vars["time"].set(format_ns(r.time_ns))
        self.stat_vars["result"].set("Yes ✔" if sorting.is_sorted(r.array) else "No ✖")
        self.steps_text.delete("1.0", "end")
        if r.frames is not None:
            i = 0
            while i < r.frames.size():
                f = r.frames.get(i)
                self.steps_text.insert("end", "%4d  %-60s  %s\n" % (i, f.text, array_to_text(f.array, 200)))
                i += 1
            if r.truncated:
                self.steps_text.insert("end", "… (recording stopped after %d frames)\n" % sorting.MAX_FRAMES)
        else:
            self.steps_text.insert("end", "Sorted result: %s\n" % array_to_text(r.array, 500))
        self.frame_index = 0
        self.msg.ok("%s finished: %s comparisons, %s %s in %s.%s"
                    % (r.name, "{:,}".format(r.comparisons), "{:,}".format(r.moves), r.moves_label,
                       format_ns(r.time_ns), note))
        self.draw()

    def compare_all(self):
        data = self.read_input()
        if data is None:
            return
        self.stop()
        self.msg.info("Running all %d algorithms on the same %d values…" % (len(sorting.ALGORITHMS), len(data)))

        def done(results):
            self.cmp_table.clear()
            i = 0
            while i < len(results):
                r = results[i]
                self.cmp_table.add((r.name, "{:,}".format(r.comparisons), "{:,} {}".format(r.moves, r.moves_label),
                                    format_ns(r.time_ns), "Yes" if sorting.is_sorted(r.array) else "NO"))
                i += 1
            self.book.select(1)
            self.msg.ok("Compare all finished - see the table below (same input for every algorithm).")
        self._start_worker(lambda: sorting.compare_all(data), done)

    # ---- playback ----------------------------------------------------------
    def _frame_count(self):
        if self.result is None or self.result.frames is None:
            return 0
        return self.result.frames.size()

    def goto(self, index):
        count = self._frame_count()
        if count == 0:
            return
        if index < 0:
            index = 0
        if index > count - 1:
            index = count - 1
        self.frame_index = index
        self.draw()

    def toggle_play(self):
        if self.playing:
            self.stop()
            return
        if self._frame_count() == 0:
            return
        if self.frame_index >= self._frame_count() - 1:
            self.frame_index = 0
        self.playing = True
        self.play_btn.configure(text="⏸ Pause")
        self._play()

    def _play(self):
        if not self.playing:
            return
        if self.frame_index >= self._frame_count() - 1:
            self.stop()
            return
        self.goto(self.frame_index + 1)
        delay = int(1500 / float(self.speed.get()) ** 1.4)
        self.after_id = self.after(max(delay, 15), self._play)

    def stop(self):
        self.playing = False
        self.play_btn.configure(text="▶ Auto-play")
        if self.after_id is not None:
            self.after_cancel(self.after_id)
            self.after_id = None

    # ---- drawing -------------------------------------------------------------
    def draw(self):
        c = self.canvas
        c.delete("all")
        if self.result is None:
            return
        if self.result.frames is not None and self.result.frames.size() > 0:
            frame = self.result.frames.get(self.frame_index)
            values, tags, text = frame.array, frame.tags, frame.text
            self.step_label.configure(text="Step %d of %d" % (self.frame_index, self._frame_count() - 1))
        else:
            values, tags, text = self.result.array, None, "Sorted result (step display off for large inputs)"
            self.step_label.configure(text="")
        self.caption.configure(text=text)
        n = len(values)
        if n == 0:
            return
        w = max(c.winfo_width(), 300)
        h = max(c.winfo_height(), 150)
        low, high = values[0], values[0]
        i = 1
        while i < n:
            if values[i] < low:
                low = values[i]
            if values[i] > high:
                high = values[i]
            i += 1
        span = (high - low) or 1
        pad = 10
        label_space = 18 if n <= 40 else 0
        bar_w = (w - 2 * pad) / n
        gap = 2 if bar_w > 6 else 0
        i = 0
        while i < n:
            frac = 0.08 + 0.92 * (values[i] - low) / span
            x1 = pad + i * bar_w
            y1 = h - pad - label_space - frac * (h - 2 * pad - label_space - 16)
            colour = theme.BAR_COLORS[tags[i]] if tags is not None else theme.BAR_COLORS[sorting.TAG_SORTED]
            c.create_rectangle(x1 + gap / 2, y1, x1 + bar_w - gap / 2, h - pad - label_space, fill=colour, outline="")
            if n <= 40:
                c.create_text(x1 + bar_w / 2, y1 - 8, text=format_number(values[i]), fill=theme.INK,
                              font=theme.font(8 if n > 20 else 9))
                c.create_text(x1 + bar_w / 2, h - pad - 8, text=str(i), fill=theme.MUTED, font=theme.font(7))
            i += 1
