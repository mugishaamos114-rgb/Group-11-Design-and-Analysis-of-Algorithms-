"""
analysis.py - Module D: Time Complexity Analysis (back end).

Times every sorting algorithm on random, sorted and reverse-sorted inputs of
increasing size, repeats each run and reports the average.  Used both by the
"Complexity Analysis" tab of the application and by benchmark/run_benchmark.py,
which produces the tables and charts for the report.
"""

import math

from .core import DynamicArray, make_input, now_ns
from .sorting import ALGORITHMS, Recorder, RECORD_OFF, find_algorithm, is_sorted

STANDARD_SIZES = [100, 500, 1000, 2000, 5000, 10000]
LARGE_SIZES = [50000, 100000]          # only for merge sort and quicksort
INPUT_KINDS = ["random", "sorted", "reverse"]


class Measurement:
    """Average results of `repeats` runs of one algorithm on one input."""

    def __init__(self, key, kind, n, repeats, avg_ns, comparisons, moves):
        self.key = key
        self.kind = kind
        self.n = n
        self.repeats = repeats
        self.avg_ns = avg_ns
        self.comparisons = comparisons
        self.moves = moves

    def avg_ms(self):
        return self.avg_ns / 1_000_000


def theoretical(key, kind, n):
    """Return (label, f(n)) for the expected growth of this algorithm on this
    kind of input, used to compute time / f(n) (which should stay roughly
    constant if the measurements match the theory)."""
    log_n = math.log2(n) if n > 1 else 1
    if key == "bubble" and kind == "sorted":
        return "n", n
    if key == "insertion" and kind == "sorted":
        return "n", n
    if key == "quick_first" and kind != "random":
        return "n²", n * n
    if key == "merge" or key == "quick_first" or key == "quick_random":
        return "n log n", n * log_n
    return "n²", n * n


def is_skipped(key, kind, n):
    """Large sizes are only run for the O(n log n) algorithms, and not for
    first-pivot quicksort on sorted/reverse input (that would be O(n^2) on
    100,000 elements = 5 billion comparisons)."""
    if n <= 10000:
        return False
    if key == "merge" or key == "quick_random":
        return False
    if key == "quick_first" and kind == "random":
        return False
    return True


def time_one(key, kind, n, repeats=3, base_seed=2026):
    """Run one algorithm `repeats` times on fresh inputs of the given kind and
    size, check the output really is sorted, and return a Measurement with the
    average time and the average operation counts."""
    info = find_algorithm(key)
    total_ns = 0
    total_comparisons = 0
    total_moves = 0
    r = 0
    while r < repeats:
        data = make_input(kind, n, seed=base_seed + 1000 * r + n)
        start = now_ns()
        result, comparisons, moves = info.func(data, Recorder(RECORD_OFF), base_seed + r)
        total_ns += now_ns() - start
        if not is_sorted(result):
            raise AssertionError(info.name + " produced an unsorted result")
        total_comparisons += comparisons
        total_moves += moves
        r += 1
    return Measurement(key, kind, n, repeats, total_ns / repeats,
                       total_comparisons / repeats, total_moves / repeats)


def run_experiment(keys, kinds, sizes, repeats=3, progress=None, should_stop=None):
    """Run time_one for every (algorithm, kind, size) combination.

    keys, kinds, sizes : fixed arrays
    progress(done, total, measurement) : optional callback after each cell
    should_stop() : optional callback; return True to cancel
    Returns a DynamicArray of Measurement."""
    total = 0
    a = 0
    while a < len(keys):
        k = 0
        while k < len(kinds):
            s = 0
            while s < len(sizes):
                if not is_skipped(keys[a], kinds[k], sizes[s]):
                    total += 1
                s += 1
            k += 1
        a += 1

    results = DynamicArray(64)
    done = 0
    s = 0
    while s < len(sizes):                  # small sizes first, so partial results are useful
        a = 0
        while a < len(keys):
            k = 0
            while k < len(kinds):
                if should_stop is not None and should_stop():
                    return results
                if not is_skipped(keys[a], kinds[k], sizes[s]):
                    m = time_one(keys[a], kinds[k], sizes[s], repeats)
                    results.add(m)
                    done += 1
                    if progress is not None:
                        progress(done, total, m)
                k += 1
            a += 1
        s += 1
    return results


def all_keys():
    """Fixed array of every algorithm key."""
    out = [None] * len(ALGORITHMS)
    i = 0
    while i < len(ALGORITHMS):
        out[i] = ALGORITHMS[i].key
        i += 1
    return out
