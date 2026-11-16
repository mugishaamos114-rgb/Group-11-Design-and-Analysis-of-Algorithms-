"""
stack.py - Module B(a): array-based stack with a fixed capacity.

The elements live in a fixed-size Python list created once with
[None] * capacity.  `top` is the index of the top element (-1 when empty).
"""

from .core import DSError


class ArrayStack:
    """LIFO stack on a fixed-size array.  Every operation is O(1) except
    display(), which is O(n)."""

    def __init__(self, capacity):
        if capacity < 1:
            raise DSError("Capacity must be at least 1.")
        self._data = [None] * capacity
        self._capacity = capacity
        self._top = -1                 # index of the top element

    def push(self, value):
        """Put value on top.  O(1).  Raises DSError on overflow."""
        if self.is_full():
            raise DSError("Stack overflow: the stack is full (capacity %d), cannot push %s."
                          % (self._capacity, value))
        self._top += 1
        self._data[self._top] = value

    def pop(self):
        """Remove and return the top element.  O(1).  Raises DSError on underflow."""
        if self.is_empty():
            raise DSError("Stack underflow: the stack is empty, nothing to pop.")
        value = self._data[self._top]
        self._data[self._top] = None   # clear the slot so the drawing shows it as free
        self._top -= 1
        return value

    def peek(self):
        """Return the top element without removing it.  O(1)."""
        if self.is_empty():
            raise DSError("The stack is empty, there is no top element.")
        return self._data[self._top]

    def size(self):
        """Number of elements.  O(1)."""
        return self._top + 1

    def is_empty(self):
        """True if there are no elements.  O(1)."""
        return self._top == -1

    def is_full(self):
        """True if size == capacity.  O(1)."""
        return self._top == self._capacity - 1

    def capacity(self):
        """Maximum number of elements.  O(1)."""
        return self._capacity

    def top_index(self):
        """Index of the top element (-1 if empty).  O(1)."""
        return self._top

    def display(self):
        """Return a new fixed array of the elements from bottom to top.  O(n)."""
        out = [None] * (self._top + 1)
        i = 0
        while i <= self._top:
            out[i] = self._data[i]
            i += 1
        return out
