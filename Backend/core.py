"""
core.py - shared building blocks for the back end.

Everything here is written from first principles so that the rest of the
back end can obey the CSC2107 "strict Python rules":

  * Python lists are only ever used as FIXED-SIZE arrays, created with
    [None] * capacity and accessed by index.  We never call append, insert,
    pop(i), sort, reverse, index, min, max, never use `del`, slicing or list
    concatenation, and never use `in` to search a list.
  * When we need something that can grow (for example the list of moves of
    the Tower of Hanoi, or the frames of a sorting animation) we use our own
    DynamicArray below, which grows by allocating a bigger fixed array and
    copying the elements across one by one.
"""

import time
import random


class DSError(Exception):
    """Raised by our data structures for user-level errors such as
    'Stack overflow', 'Queue is empty' or 'Element 7 not found'.
    The front end catches it and shows the message to the user."""


# ---------------------------------------------------------------------------
# Timing
# ---------------------------------------------------------------------------

def now_ns():
    """Return a high-resolution timestamp in nanoseconds.  O(1).
    time.perf_counter_ns is the highest-resolution monotonic timer in Python."""
    return time.perf_counter_ns()


def format_ns(ns):
    """Format a duration in nanoseconds as a readable string.  O(1)."""
    if ns < 1_000:
        return str(ns) + " ns"
    if ns < 1_000_000:
        return "%.2f µs" % (ns / 1_000)
    if ns < 1_000_000_000:
        return "%.3f ms" % (ns / 1_000_000)
    return "%.3f s" % (ns / 1_000_000_000)


# ---------------------------------------------------------------------------
# DynamicArray: our own growable array (used instead of list.append)
# ---------------------------------------------------------------------------

class DynamicArray:
    """A growable array built on top of a fixed-size Python list.

    add()  : amortised O(1) - when the array is full we allocate a new array
             of twice the capacity and copy every element (O(n)), but this
             happens rarely enough that the average cost per add is O(1).
    get()  : O(1)
    set()  : O(1)
    """

    def __init__(self, capacity=8):
        if capacity < 1:
            capacity = 1
        self._data = [None] * capacity
        self._size = 0

    def add(self, item):
        """Add item at the end.  Amortised O(1)."""
        if self._size == len(self._data):
            self._grow()
        self._data[self._size] = item
        self._size += 1

    def _grow(self):
        """Double the capacity by copying into a new fixed array.  O(n)."""
        bigger = [None] * (2 * len(self._data))
        i = 0
        while i < self._size:
            bigger[i] = self._data[i]
            i += 1
        self._data = bigger

    def get(self, i):
        """Return the element at position i.  O(1)."""
        if i < 0 or i >= self._size:
            raise IndexError("DynamicArray index out of range")
        return self._data[i]

    def set(self, i, item):
        """Overwrite the element at position i.  O(1)."""
        if i < 0 or i >= self._size:
            raise IndexError("DynamicArray index out of range")
        self._data[i] = item

    def size(self):
        """Number of elements stored.  O(1)."""
        return self._size

    def __len__(self):
        return self._size

    def __getitem__(self, i):
        # Only integer indexing is supported - deliberately no slicing.
        if not isinstance(i, int):
            raise TypeError("DynamicArray supports integer indexes only")
        return self.get(i)

    def to_fixed_array(self):
        """Return a new fixed-size list holding exactly the elements.  O(n)."""
        out = [None] * self._size
        i = 0
        while i < self._size:
            out[i] = self._data[i]
            i += 1
        return out


# ---------------------------------------------------------------------------
# Array helpers
# ---------------------------------------------------------------------------

def copy_array(a):
    """Return an element-by-element copy of a fixed array.  O(n)."""
    n = len(a)
    out = [None] * n
    i = 0
    while i < n:
        out[i] = a[i]
        i += 1
    return out


def array_to_text(a, limit=60):
    """Return '[3, 1, 2]' for a fixed array, shortening very long arrays.
    O(min(n, limit))."""
    n = len(a)
    text = "["
    i = 0
    while i < n and i < limit:
        if i > 0:
            text += ", "
        text += format_number(a[i])
        i += 1
    if n > limit:
        text += ", ... (" + str(n) + " values)"
    return text + "]"


def format_number(x):
    """Show 5.0 as '5' and 2.5 as '2.5'.  O(1)."""
    if isinstance(x, float) and x == int(x):
        return str(int(x))
    return str(x)


def random_array(n, low=1, high=1000, seed=None):
    """Fixed array of n random integers in [low, high].  O(n)."""
    rng = random.Random(seed)
    a = [None] * n
    i = 0
    while i < n:
        a[i] = rng.randint(low, high)
        i += 1
    return a


def sorted_array(n):
    """Fixed array 1, 2, ..., n (already sorted input).  O(n)."""
    a = [None] * n
    i = 0
    while i < n:
        a[i] = i + 1
        i += 1
    return a


def reversed_array(n):
    """Fixed array n, n-1, ..., 1 (reverse-sorted input).  O(n)."""
    a = [None] * n
    i = 0
    while i < n:
        a[i] = n - i
        i += 1
    return a


def make_input(kind, n, seed=None):
    """Build a test input of the given kind: 'random', 'sorted' or 'reverse'."""
    if kind == "sorted":
        return sorted_array(n)
    if kind == "reverse":
        return reversed_array(n)
    return random_array(n, 1, 10 * n if n > 100 else 1000, seed)


# ---------------------------------------------------------------------------
# Input validation / parsing (no str.split - we scan character by character)
# ---------------------------------------------------------------------------

def _is_separator(ch):
    return ch == " " or ch == "," or ch == ";" or ch == "\n" or ch == "\t" or ch == "\r"


def parse_number(token):
    """Convert one token to int (preferred) or float.  Raises ValueError."""
    try:
        return int(token)
    except ValueError:
        value = float(token)          # may raise ValueError again
        if value != value or value == float("inf") or value == float("-inf"):
            raise ValueError("not a finite number")
        return value


def parse_number_list(text, max_count=100_000):
    """Parse '5, 3 9;1' into a fixed array [5, 3, 9, 1].

    Returns (array, None) on success or (None, error_message) on failure.
    O(len(text)).
    """
    if text is None or text.strip() == "":
        return None, "Please enter at least one number (e.g. 5, 3, 9, 1)."
    values = DynamicArray()
    token = ""
    pos = 0
    length = len(text)
    while pos <= length:
        ch = text[pos] if pos < length else " "   # sentinel separator at the end
        if _is_separator(ch):
            if token != "":
                try:
                    values.add(parse_number(token))
                except ValueError:
                    return None, "'" + token + "' is not a number. Use numbers separated by commas or spaces."
                if values.size() > max_count:
                    return None, "Too many values: the limit is " + str(max_count) + "."
                token = ""
        else:
            token += ch
        pos += 1
    if values.size() == 0:
        return None, "Please enter at least one number."
    return values.to_fixed_array(), None


def parse_int(text, name, low, high):
    """Validate that text is a whole number between low and high.

    Returns (value, None) or (None, error_message).  O(len(text)).
    """
    if text is None or text.strip() == "":
        return None, "Please enter a value for " + name + "."
    try:
        value = int(text.strip())
    except ValueError:
        return None, name + " must be a whole number, not '" + text.strip() + "'."
    if value < low or value > high:
        return None, name + " must be between " + str(low) + " and " + str(high) + "."
    return value, None


class AlgoResult:
    """Bundle returned by the recursion algorithms so the UI can show the
    result, the number of operations and the time taken."""

    def __init__(self, name, value, operations, operation_label, time_ns, extra=None):
        self.name = name
        self.value = value
        self.operations = operations
        self.operation_label = operation_label
        self.time_ns = time_ns
        self.extra = extra

