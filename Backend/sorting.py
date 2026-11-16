"""
sorting.py - Module C: Sorting Lab (back end).

Bubble, selection, insertion, merge sort and quicksort (first-element pivot
with the yellow/green partition, plus a randomised-pivot version), all
written on plain fixed-size arrays.

Every sort
  * works on a COPY of the input (the caller's array is never changed),
  * counts comparisons (element-vs-element) and swaps/moves,
  * can optionally record "frames" (a snapshot of the array plus colour tags)
    so the front end can show the array after every pass / merge / partition
    (level 1) or after every single comparison and swap (level 2).

Timing: run_sort() times a run WITHOUT recording (recording snapshots would
distort the time) and, if steps are wanted, does a second identical run that
records the frames.  The randomised quicksort uses a seeded generator so both
runs make exactly the same pivot choices.

Yellow/green partition (first-element pivot), used by both quicksorts:
    pivot = A[lo]
    i = lo                      # A[lo+1 .. i]   are  < pivot   (YELLOW region)
    for j = lo+1 .. hi:         # A[i+1 .. j-1]  are >= pivot   (GREEN region)
        if A[j] < pivot:
            i = i + 1
            swap A[i], A[j]     # grow the yellow region by one
    swap A[lo], A[i]            # put the pivot between yellow and green
    return i
"""

import random
import sys

from .core import DynamicArray, copy_array, now_ns

# Colour tags used in frames (the front end maps them to colours).
TAG_NORMAL = 0
TAG_COMPARE = 1   # elements being compared
TAG_SWAP = 2      # elements just swapped / written
TAG_PIVOT = 3     # quicksort pivot
TAG_SORTED = 4    # element in its final place
TAG_YELLOW = 5    # quicksort: < pivot
TAG_GREEN = 6     # quicksort: >= pivot
TAG_RANGE = 7     # sub-array currently being merged / partitioned

RECORD_OFF = 0
RECORD_PASSES = 1
RECORD_DETAILED = 2

MAX_FRAMES = 6000
MAX_RECORD_N_PASSES = 200     # step display limited to arrays this small
MAX_RECORD_N_DETAILED = 50


class Frame:
    """A snapshot of the array plus one colour tag per element and a caption."""

    def __init__(self, array, tags, text):
        self.array = array
        self.tags = tags
        self.text = text


class Recorder:
    """Collects frames.  `level` decides which calls actually record."""

    def __init__(self, level):
        self.level = level
        self.frames = DynamicArray(64)
        self.truncated = False

    def _add(self, a, text, sorted_lo, sorted_hi, range_lo, range_hi,
             compare, swap, pivot, yellow, green):
        if self.frames.size() >= MAX_FRAMES:
            self.truncated = True
            return
        n = len(a)
        tags = [TAG_NORMAL] * n
        k = range_lo
        while 0 <= k <= range_hi:
            tags[k] = TAG_RANGE
            k += 1
        k = sorted_lo
        while 0 <= k <= sorted_hi:
            tags[k] = TAG_SORTED
            k += 1
        if yellow is not None:
            k = yellow[0]
            while k <= yellow[1]:
                tags[k] = TAG_YELLOW
                k += 1
        if green is not None:
            k = green[0]
            while k <= green[1]:
                tags[k] = TAG_GREEN
                k += 1
        if pivot >= 0:
            tags[pivot] = TAG_PIVOT
        if compare is not None:
            tags[compare[0]] = TAG_COMPARE
            tags[compare[1]] = TAG_COMPARE
        if swap is not None:
            tags[swap[0]] = TAG_SWAP
            tags[swap[1]] = TAG_SWAP
        self.frames.add(Frame(copy_array(a), tags, text))

    def step(self, a, text, sorted_lo=-1, sorted_hi=-1, range_lo=-1, range_hi=-1,
             compare=None, swap=None, pivot=-1, yellow=None, green=None):
        """Record a pass-level frame (levels 1 and 2)."""
        if self.level >= RECORD_PASSES:
            self._add(a, text, sorted_lo, sorted_hi, range_lo, range_hi,
                      compare, swap, pivot, yellow, green)

    def detail(self, a, text, sorted_lo=-1, sorted_hi=-1, range_lo=-1, range_hi=-1,
               compare=None, swap=None, pivot=-1, yellow=None, green=None):
        """Record a comparison/swap-level frame (level 2 only)."""
        if self.level >= RECORD_DETAILED:
            self._add(a, text, sorted_lo, sorted_hi, range_lo, range_hi,
                      compare, swap, pivot, yellow, green)


class SortResult:
    """What a sort returns to the front end."""

    def __init__(self, key, name, array, comparisons, moves, moves_label, time_ns=0,
                 frames=None, truncated=False):
        self.key = key
        self.name = name
        self.array = array
        self.comparisons = comparisons
        self.moves = moves
        self.moves_label = moves_label
        self.time_ns = time_ns
        self.frames = frames
        self.truncated = truncated


# ===========================================================================
# Bubble sort
# ===========================================================================

def bubble_sort(data, rec):
    """Repeatedly swap adjacent out-of-order pairs; after pass i the i largest
    values are in place.  Stops early if a pass makes no swap.
    Time: best O(n) (already sorted), average/worst O(n^2).  Space O(1).  Stable."""
    a = copy_array(data)
    steps = rec.level >= RECORD_PASSES        # record pass-level frames?
    detailed = rec.level >= RECORD_DETAILED   # record every comparison/swap?
    n = len(a)
    comparisons = 0
    swaps = 0
    if steps: rec.step(a, "Initial array")
    i = 0
    while i < n - 1:
        swapped = False
        j = 0
        while j < n - 1 - i:
            comparisons += 1
            if detailed: rec.detail(a, "Pass %d: compare %s and %s" % (i + 1, a[j], a[j + 1]),
                       sorted_lo=n - i, sorted_hi=n - 1, compare=(j, j + 1))
            if a[j] > a[j + 1]:
                a[j], a[j + 1] = a[j + 1], a[j]
                swaps += 1
                swapped = True
                if detailed: rec.detail(a, "Pass %d: swap -> %s, %s" % (i + 1, a[j], a[j + 1]),
                           sorted_lo=n - i, sorted_hi=n - 1, swap=(j, j + 1))
            j += 1
        if steps: rec.step(a, "After pass %d: %s is in its final place%s"
                 % (i + 1, a[n - 1 - i], "" if swapped else " (no swaps - array is sorted, stop early)"),
                 sorted_lo=n - 1 - i, sorted_hi=n - 1)
        if not swapped:
            break
        i += 1
    if steps: rec.step(a, "Sorted", sorted_lo=0, sorted_hi=n - 1)
    return a, comparisons, swaps


# ===========================================================================
# Selection sort
# ===========================================================================

def selection_sort(data, rec):
    """Find the smallest element of the unsorted part and swap it to the
    front of that part.  Always n(n-1)/2 comparisons.
    Time: O(n^2) in every case.  Space O(1).  Not stable."""
    a = copy_array(data)
    steps = rec.level >= RECORD_PASSES        # record pass-level frames?
    detailed = rec.level >= RECORD_DETAILED   # record every comparison/swap?
    n = len(a)
    comparisons = 0
    swaps = 0
    if steps: rec.step(a, "Initial array")
    i = 0
    while i < n - 1:
        smallest = i
        j = i + 1
        while j < n:
            comparisons += 1
            if detailed: rec.detail(a, "Pass %d: compare %s with current minimum %s" % (i + 1, a[j], a[smallest]),
                       sorted_lo=0, sorted_hi=i - 1, compare=(smallest, j))
            if a[j] < a[smallest]:
                smallest = j
            j += 1
        if smallest != i:
            a[i], a[smallest] = a[smallest], a[i]
            swaps += 1
            if detailed: rec.detail(a, "Pass %d: swap minimum %s into position %d" % (i + 1, a[i], i),
                       sorted_lo=0, sorted_hi=i - 1, swap=(i, smallest))
        if steps: rec.step(a, "After pass %d: minimum %s placed at index %d" % (i + 1, a[i], i),
                 sorted_lo=0, sorted_hi=i)
        i += 1
    if steps: rec.step(a, "Sorted", sorted_lo=0, sorted_hi=n - 1)
    return a, comparisons, swaps


# ===========================================================================
# Insertion sort
# ===========================================================================

def insertion_sort(data, rec):
    """Take each element in turn and shift larger elements of the sorted
    prefix one place right until its position is found.
    Time: best O(n) (sorted input: one comparison per element), average and
    worst O(n^2).  Space O(1).  Stable.  'Moves' counts element writes."""
    a = copy_array(data)
    steps = rec.level >= RECORD_PASSES        # record pass-level frames?
    detailed = rec.level >= RECORD_DETAILED   # record every comparison/swap?
    n = len(a)
    comparisons = 0
    moves = 0
    if steps: rec.step(a, "Initial array", sorted_lo=0, sorted_hi=0 if n > 0 else -1)
    i = 1
    while i < n:
        key = a[i]
        j = i - 1
        while j >= 0:
            comparisons += 1
            if detailed: rec.detail(a, "Insert %s: compare with %s" % (key, a[j]),
                       sorted_lo=0, sorted_hi=i - 1, compare=(j, j + 1))
            if a[j] > key:
                a[j + 1] = a[j]            # shift right
                moves += 1
                a[j] = key                 # (only so the picture shows the key travelling)
                if detailed: rec.detail(a, "Insert %s: shift %s right" % (key, a[j + 1]),
                           sorted_lo=0, sorted_hi=i, swap=(j, j + 1))
                j -= 1
            else:
                break
        if j + 1 != i:
            a[j + 1] = key
            moves += 1
        if steps: rec.step(a, "After pass %d: inserted %s at index %d" % (i, key, j + 1),
                 sorted_lo=0, sorted_hi=i)
        i += 1
    if steps: rec.step(a, "Sorted", sorted_lo=0, sorted_hi=n - 1)
    return a, comparisons, moves


# ===========================================================================
# Merge sort
# ===========================================================================

def merge_sort(data, rec):
    """Divide the array in half, sort each half recursively, then merge the
    two sorted halves using an auxiliary array.
    Time: O(n log n) in every case.  Space O(n) for the auxiliary array plus
    O(log n) recursion depth.  Stable (ties are taken from the left half).
    'Moves' counts element writes (copy to the auxiliary array + write back)."""
    a = copy_array(data)
    steps = rec.level >= RECORD_PASSES        # record pass-level frames?
    detailed = rec.level >= RECORD_DETAILED   # record every comparison/swap?
    n = len(a)
    aux = [None] * n
    counts = [0, 0]                        # counts[0] = comparisons, counts[1] = moves
    if steps: rec.step(a, "Initial array")

    def merge(lo, mid, hi):
        k = lo
        while k <= hi:                     # copy a[lo..hi] into aux
            aux[k] = a[k]
            counts[1] += 1
            k += 1
        i, j, k = lo, mid + 1, lo
        while i <= mid and j <= hi:
            counts[0] += 1
            if detailed: rec.detail(a, "Merge [%d..%d]: compare %s and %s" % (lo, hi, aux[i], aux[j]),
                       range_lo=lo, range_hi=hi, compare=(i, j))
            if aux[i] <= aux[j]:           # <= keeps equal elements in order (stable)
                a[k] = aux[i]
                i += 1
            else:
                a[k] = aux[j]
                j += 1
            counts[1] += 1
            k += 1
        while i <= mid:                    # copy what is left of the left half
            a[k] = aux[i]
            counts[1] += 1
            i += 1
            k += 1
        while j <= hi:                     # copy what is left of the right half
            a[k] = aux[j]
            counts[1] += 1
            j += 1
            k += 1
        if steps: rec.step(a, "Merged [%d..%d] and [%d..%d]" % (lo, mid, mid + 1, hi),
                 range_lo=lo, range_hi=hi)

    def sort(lo, hi):
        if lo >= hi:                       # 0 or 1 element: already sorted
            return
        mid = (lo + hi) // 2
        sort(lo, mid)
        sort(mid + 1, hi)
        merge(lo, mid, hi)

    sort(0, n - 1)
    if steps: rec.step(a, "Sorted", sorted_lo=0, sorted_hi=n - 1)
    return a, counts[0], counts[1]


# ===========================================================================
# Quicksort (first-element pivot and randomised pivot)
# ===========================================================================

def _quick_sort(data, rec, rng):
    """Shared quicksort.  rng is None for the first-element pivot, or a
    random.Random for the randomised pivot (a random element is swapped
    into position lo before partitioning).

    Time: best/average O(n log n); worst O(n^2) - with the first-element
    pivot the worst case happens on already sorted or reverse-sorted input,
    because every partition is as unbalanced as possible.  Space: O(log n)
    average recursion depth.  Not stable."""
    a = copy_array(data)
    steps = rec.level >= RECORD_PASSES        # record pass-level frames?
    detailed = rec.level >= RECORD_DETAILED   # record every comparison/swap?
    n = len(a)
    counts = [0, 0]                        # comparisons, swaps
    if sys.getrecursionlimit() < n + 500:  # worst case can recurse deeply
        sys.setrecursionlimit(n + 500)
    if steps: rec.step(a, "Initial array")

    def swap(x, y):
        a[x], a[y] = a[y], a[x]
        counts[1] += 1

    def partition(lo, hi):
        if rng is not None:
            r = rng.randint(lo, hi)        # randomised pivot: move it to the front
            if r != lo:
                swap(lo, r)
                if detailed: rec.detail(a, "Random pivot %s moved to index %d" % (a[lo], lo),
                           range_lo=lo, range_hi=hi, swap=(lo, r))
        pivot = a[lo]
        i = lo                             # end of the yellow (< pivot) region
        j = lo + 1
        while j <= hi:
            counts[0] += 1
            if detailed: rec.detail(a, "Pivot %s: compare with %s" % (pivot, a[j]), range_lo=lo, range_hi=hi,
                       pivot=lo, compare=(lo, j),
                       yellow=(lo + 1, i) if i > lo else None,
                       green=(i + 1, j - 1) if j - 1 > i else None)
            if a[j] < pivot:
                i += 1
                if i != j:
                    swap(i, j)
                    if detailed: rec.detail(a, "%s < pivot: swap into the yellow region" % a[i],
                               range_lo=lo, range_hi=hi, pivot=lo, swap=(i, j),
                               yellow=(lo + 1, i), green=(i + 1, j) if j > i else None)
            j += 1
        if i != lo:
            swap(lo, i)                    # pivot goes between yellow and green
        return i

    def quick(lo, hi):
        # Recurse on the left part; the right part is handled by the loop
        # (tail-call elimination) so sorted input does not recurse n deep.
        while lo < hi:
            p = partition(lo, hi)
            if steps: rec.step(a, "Partition [%d..%d] around pivot %s (now at index %d)" % (lo, hi, a[p], p),
                     range_lo=lo, range_hi=hi, pivot=p,
                     yellow=(lo, p - 1) if p > lo else None,
                     green=(p + 1, hi) if hi > p else None)
            quick(lo, p - 1)
            lo = p + 1

    quick(0, n - 1)
    if steps: rec.step(a, "Sorted", sorted_lo=0, sorted_hi=n - 1)
    return a, counts[0], counts[1]


def quick_sort_first(data, rec, seed=None):
    """Quicksort with the first element as pivot (yellow/green partition)."""
    return _quick_sort(data, rec, None)


def quick_sort_random(data, rec, seed=None):
    """Quicksort with a randomly chosen pivot (expected O(n log n) on any input)."""
    return _quick_sort(data, rec, random.Random(seed))


# ===========================================================================
# Registry and runners
# ===========================================================================

class SortInfo:
    """Description of one algorithm for menus and the complexity help panel."""

    def __init__(self, key, name, func, moves_label, best, average, worst, space, stable, family):
        self.key = key
        self.name = name
        self.func = func
        self.moves_label = moves_label
        self.best = best
        self.average = average
        self.worst = worst
        self.space = space
        self.stable = stable
        self.family = family                # "quadratic" or "nlogn" (for the charts)


def _wrap(f):
    def run(data, rec, seed=None):
        return f(data, rec)
    return run


ALGORITHMS = [
    SortInfo("bubble", "Bubble sort", _wrap(bubble_sort), "swaps",
             "O(n)", "O(n²)", "O(n²)", "O(1)", "Yes", "quadratic"),
    SortInfo("selection", "Selection sort", _wrap(selection_sort), "swaps",
             "O(n²)", "O(n²)", "O(n²)", "O(1)", "No", "quadratic"),
    SortInfo("insertion", "Insertion sort", _wrap(insertion_sort), "moves",
             "O(n)", "O(n²)", "O(n²)", "O(1)", "Yes", "quadratic"),
    SortInfo("merge", "Merge sort", _wrap(merge_sort), "moves",
             "O(n log n)", "O(n log n)", "O(n log n)", "O(n)", "Yes", "nlogn"),
    SortInfo("quick_first", "Quicksort (first pivot)", quick_sort_first, "swaps",
             "O(n log n)", "O(n log n)", "O(n²)", "O(log n)*", "No", "nlogn"),
    SortInfo("quick_random", "Quicksort (random pivot)", quick_sort_random, "swaps",
             "O(n log n)", "O(n log n)", "O(n²)**", "O(log n)*", "No", "nlogn"),
]

COMPLEXITY_NOTES = (
    "* Average recursion depth; O(n) in the worst case.\n"
    "** The worst case needs consistently bad random pivots, which has a "
    "vanishingly small probability, so the expected time is O(n log n) on every input."
)


def find_algorithm(key):
    """Look up a SortInfo by key with a simple linear scan.  O(number of algorithms)."""
    i = 0
    while i < len(ALGORITHMS):
        if ALGORITHMS[i].key == key:
            return ALGORITHMS[i]
        i += 1
    raise KeyError("Unknown sorting algorithm: " + str(key))


def run_sort(key, data, record_level=RECORD_OFF, seed=12345):
    """Sort a copy of data with the chosen algorithm.

    The reported time comes from a run with recording OFF.  If record_level
    is not OFF a second, identical run collects the frames."""
    if record_level not in (RECORD_OFF, RECORD_PASSES, RECORD_DETAILED):
        raise ValueError("record_level must be RECORD_OFF, RECORD_PASSES or RECORD_DETAILED.")
    info = find_algorithm(key)
    quiet = Recorder(RECORD_OFF)       # built BEFORE the clock starts, so setting it up is not timed
    start = now_ns()
    result, comparisons, moves = info.func(data, quiet, seed)
    elapsed = now_ns() - start
    frames = None
    truncated = False
    if record_level != RECORD_OFF:
        rec = Recorder(record_level)
        info.func(data, rec, seed)
        frames = rec.frames
        truncated = rec.truncated
    return SortResult(key, info.name, result, comparisons, moves, info.moves_label,
                      elapsed, frames, truncated)


def compare_all(data, seed=12345):
    """Run every algorithm on the same input (no recording).  Returns a fixed
    array of SortResult in the order of ALGORITHMS."""
    out = [None] * len(ALGORITHMS)
    i = 0
    while i < len(ALGORITHMS):
        out[i] = run_sort(ALGORITHMS[i].key, data, RECORD_OFF, seed)
        i += 1
    return out


def is_sorted(a):
    """True if a is in non-decreasing order.  O(n)."""
    i = 1
    while i < len(a):
        if a[i - 1] > a[i]:
            return False
        i += 1
    return True
