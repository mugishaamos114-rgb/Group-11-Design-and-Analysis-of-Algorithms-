"""
analysis_tab.py - Module D screen: run timing experiments inside the app,
show the averages in a table and plot time against n (one chart for the
O(n²) sorts, one for the O(n log n) sorts).

For the report use benchmark/run_benchmark.py, which runs the full set of
sizes (including 50,000 and 100,000) and writes LaTeX tables and charts.
"""

import threading
import tkinter as tk
from tkinter import filedialog, ttk

from backend import analysis, sorting
from backend.core import DynamicArray, parse_int, parse_number_list

from . import theme
from .widgets import LineChart, MessageLine, Table, explanation


class AnalysisTab(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent, padding=10)
        self.results = DynamicArray()
        self.running = False
        self.stop_requested = False
        self.progress_state = None

        top = ttk.Frame(self, style="Card.TFrame", padding=12)
        top.pack(fill="x")
        ttk.Label(top, text="Time complexity experiment", style="Title.TLabel").grid(row=0, column=0, columnspan=4, sticky="w")
        ttk.Label(top, text="Algorithms", style="Card.TLabel").grid(row=1, column=0, sticky="w", pady=4)
        self.algo_vars = {}
        col = 1
        for a in sorting.ALGORITHMS:
            v = tk.BooleanVar(value=True)
            ttk.Checkbutton(top, text=a.name, variable=v).grid(row=1, column=col, sticky="w", padx=4)
            self.algo_vars[a.key] = v
            col += 1
        ttk.Label(top, text="Inputs", style="Card.TLabel").grid(row=2, column=0, sticky="w", pady=4)
        self.kind_vars = {}
        col = 1
        for kind in analysis.INPUT_KINDS:
            v = tk.BooleanVar(value=True)
            ttk.Checkbutton(top, text=kind.capitalize() if kind != "reverse" else "Reverse sorted",
                            variable=v).grid(row=2, column=col, sticky="w", padx=4)
            self.kind_vars[kind] = v
            col += 1
        ttk.Label(top, text="Sizes n", style="Card.TLabel").grid(row=3, column=0, sticky="w", pady=4)
        self.sizes = ttk.Entry(top, width=44)
        self.sizes.insert(0, "100, 500, 1000, 2000")
        self.sizes.grid(row=3, column=1, columnspan=3, sticky="w", padx=4)
        ttk.Button(top, text="Use assignment sizes (up to 10,000)",
                   command=self.full_sizes).grid(row=3, column=4, columnspan=2, sticky="w")
        ttk.Label(top, text="Repeats", style="Card.TLabel").grid(row=4, column=0, sticky="w")
        self.repeats = ttk.Spinbox(top, from_=1, to=10, width=5)
        self.repeats.set("3")
        self.repeats.grid(row=4, column=1, sticky="w", padx=4)
        self.run_btn = ttk.Button(top, text="Run analysis", style="Accent.TButton", command=self.run)
        self.run_btn.grid(row=4, column=2, sticky="w", padx=4, pady=6)
        ttk.Button(top, text="Stop", command=self.stop).grid(row=4, column=3, sticky="w")
        ttk.Button(top, text="Export CSV…", command=self.export).grid(row=4, column=4, sticky="w")
        self.progress = ttk.Progressbar(top, length=300, mode="determinate")
        self.progress.grid(row=5, column=0, columnspan=3, sticky="we", pady=(4, 0))
        self.msg = MessageLine(top)
        self.msg.grid(row=5, column=3, columnspan=5, sticky="we", padx=8)
        self.msg.info("Larger sizes take longer: O(n²) sorts at n = 10,000 need tens of millions of steps in Python.")

        panes = ttk.PanedWindow(self, orient="vertical")
        panes.pack(fill="both", expand=True, pady=(8, 0))
        charts = ttk.Frame(panes, style="Card.TFrame", padding=10)
        panes.add(charts, weight=3)
        row = ttk.Frame(charts, style="Card.TFrame")
        row.pack(fill="x")
        ttk.Label(row, text="Show input", style="Card.TLabel").pack(side="left")
        self.show_kind = ttk.Combobox(row, values=analysis.INPUT_KINDS, width=10, state="readonly")
        self.show_kind.set("random")
        self.show_kind.pack(side="left", padx=6)
        self.show_kind.bind("<<ComboboxSelected>>", lambda e: self.refresh_charts())
        explanation(row, "   Hover over a point to see its value. If time / f(n) in the table stays roughly "
                         "constant as n grows, the measurements follow the theoretical Big-O.").pack(side="left")
        pair = ttk.Frame(charts, style="Card.TFrame")
        pair.pack(fill="both", expand=True)
        self.chart_quad = LineChart(pair, height=220)
        self.chart_quad.pack(side="left", fill="both", expand=True, padx=(0, 6))
        self.chart_nlogn = LineChart(pair, height=220)
        self.chart_nlogn.pack(side="left", fill="both", expand=True, padx=(6, 0))

        self.table = Table(panes, ("Algorithm", "Input", "n", "Avg time (ms)", "Comparisons", "Swaps / moves",
                                  "Theory f(n)", "time / f(n) (ns)"),
                           (190, 80, 80, 110, 120, 120, 90, 120), height=7)
        panes.add(self.table, weight=1)
        self.refresh_charts()

    def full_sizes(self):
        self.sizes.delete(0, "end")
        self.sizes.insert(0, "100, 500, 1000, 2000, 5000, 10000")
        self.msg.warn("Full sizes selected - with all algorithms this takes several minutes in Python.")

    def _checked(self, vars_dict, order):
        out = DynamicArray()
        i = 0
        while i < len(order):
            if vars_dict[order[i]].get():
                out.add(order[i])
            i += 1
        return out.to_fixed_array()

    def run(self):
        if self.running:
            return
        keys = self._checked(self.algo_vars, analysis.all_keys())
        kinds = self._checked(self.kind_vars, analysis.INPUT_KINDS)
        if len(keys) == 0 or len(kinds) == 0:
            self.msg.error("Choose at least one algorithm and one kind of input.")
            return
        sizes, error = parse_number_list(self.sizes.get(), 20)
        if error:
            self.msg.error("Sizes: " + error)
            return
        i = 0
        while i < len(sizes):
            if not isinstance(sizes[i], int) or sizes[i] < 2 or sizes[i] > 100000:
                self.msg.error("Every size must be a whole number between 2 and 100,000.")
                return
            i += 1
        repeats, error = parse_int(self.repeats.get(), "Repeats", 1, 10)
        if error:
            self.msg.error(error)
            return
        self.results = DynamicArray()
        self.table.clear()
        self.running = True
        self.stop_requested = False
        self.run_btn.configure(state="disabled")
        self.progress_state = [0, 1, False]       # done, total, finished
        self.progress["value"] = 0

        def progress(done, total, m):
            self.results.add(m)
            self.progress_state[0] = done
            self.progress_state[1] = total

        def work():
            try:
                analysis.run_experiment(keys, kinds, sizes, repeats, progress, lambda: self.stop_requested)
            finally:
                self.progress_state[2] = True
        threading.Thread(target=work, daemon=True).start()
        self.shown = 0
        self._poll()

    def _poll(self):
        done, total, finished = self.progress_state
        while self.shown < self.results.size():
            self._add_row(self.results.get(self.shown))
            self.shown += 1
        self.progress["value"] = 100.0 * done / max(total, 1)
        self.refresh_charts()
        if finished:
            self.running = False
            self.run_btn.configure(state="normal")
            if self.stop_requested:
                self.msg.warn("Stopped after %d of %d measurements." % (done, total))
            else:
                self.msg.ok("Finished %d measurements." % done)
            return
        self.msg.info("Running… %d of %d measurements done." % (done, total))
        self.after(250, self._poll)

    def stop(self):
        if self.running:
            self.stop_requested = True
            self.msg.warn("Stopping after the current measurement…")

    def _add_row(self, m):
        label, f = analysis.theoretical(m.key, m.kind, m.n)
        self.table.add((sorting.find_algorithm(m.key).name, m.kind, "{:,}".format(m.n), "%.3f" % m.avg_ms(),
                        "{:,.0f}".format(m.comparisons), "{:,.0f}".format(m.moves), label, "%.4f" % (m.avg_ns / f)))

    def _series(self, family, kind):
        out = []
        colour = 0
        for a in sorting.ALGORITHMS:
            if a.family != family:
                continue
            pts = []
            i = 0
            while i < self.results.size():
                m = self.results.get(i)
                if m.key == a.key and m.kind == kind:
                    pts += [(m.n, m.avg_ms())]          # results arrive in increasing n
                i += 1
            out += [(a.name, theme.SERIES[colour], pts)]
            colour += 1
        return out

    def refresh_charts(self):
        kind = self.show_kind.get()
        self.chart_quad.set_data("O(n²) sorts - %s input" % kind, "n", "time (ms)", self._series("quadratic", kind))
        self.chart_nlogn.set_data("O(n log n) sorts - %s input" % kind, "n", "time (ms)", self._series("nlogn", kind))

    def export(self):
        if self.results.size() == 0:
            self.msg.error("Nothing to export yet - run the analysis first.")
            return
        path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=(("CSV", "*.csv"),),
                                            initialfile="complexity_results.csv")
        if not path:
            return
        with open(path, "w", encoding="utf-8") as handle:
            handle.write("algorithm,input,n,repeats,avg_time_ms,comparisons,swaps_or_moves\n")
            i = 0
            while i < self.results.size():
                m = self.results.get(i)
                handle.write("%s,%s,%d,%d,%.4f,%.0f,%.0f\n" % (sorting.find_algorithm(m.key).name, m.kind, m.n,
                                                               m.repeats, m.avg_ms(), m.comparisons, m.moves))
                i += 1
        self.msg.ok("Saved %d rows to %s" % (self.results.size(), path))

