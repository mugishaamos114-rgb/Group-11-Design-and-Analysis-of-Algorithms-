"""
queues.py - Module B(b): linear queue and circular queue on fixed-size arrays.

Linear queue
    front starts at 0 and only ever moves right; rear starts at -1 and only
    ever moves right.  Once rear reaches the last slot the queue reports
    "full" even if dequeues have freed slots at the start of the array.
    This is the "false full" problem.

Circular queue
    The same array, but front and rear wrap around with the modulo operator:
    rear = (rear + 1) % capacity.  Freed slots at the start are reused, so the
    queue is only full when it really holds `capacity` elements.
"""

from .core import DSError


def _check_capacity(capacity):
    """Capacity must be a whole number of at least 1 (rejects 0, negatives,
    floats and text, which would otherwise crash with a confusing error)."""
    if not isinstance(capacity, int) or isinstance(capacity, bool) or capacity < 1:
        raise DSError("Capacity must be a whole number of at least 1.")


class LinearQueue:
    """FIFO queue on a fixed array, no wrap-around.
    enqueue, dequeue, front, size, is_empty, is_full are all O(1);
    display is O(n); clear is O(capacity)."""

    def __init__(self, capacity):
        _check_capacity(capacity)
        self._data = [None] * capacity
        self._capacity = capacity
        self._front = 0                # index of the first element
        self._rear = -1                # index of the last element

    def enqueue(self, value):
        """Add value at the rear.  O(1)."""
        if self.is_full():
            if self._front > 0:
                raise DSError(
                    "Queue is full (rear is at the last index %d) - but %d slot(s) at the "
                    "front are actually free. This is the 'false full' problem of the "
                    "linear queue; a circular queue would reuse them."
                    % (self._capacity - 1, self._front))
            raise DSError("Queue is full (capacity %d), cannot enqueue %s." % (self._capacity, value))
        self._rear += 1
        self._data[self._rear] = value

    def dequeue(self):
        """Remove and return the front element.  O(1) - we just move `front`."""
        if self.is_empty():
            raise DSError("Queue is empty, nothing to dequeue.")
        value = self._data[self._front]
        self._data[self._front] = None
        self._front += 1
        return value

    def front(self):
        """Return the front element without removing it.  O(1)."""
        if self.is_empty():
            raise DSError("Queue is empty, there is no front element.")
        return self._data[self._front]

    def size(self):
        """Number of elements.  O(1)."""
        return self._rear - self._front + 1

    def is_empty(self):
        """O(1)."""
        return self.size() == 0

    def is_full(self):
        """'Full' means rear has reached the last index (even if front > 0).  O(1)."""
        return self._rear == self._capacity - 1

    def is_false_full(self):
        """True when the queue says full but there are free slots in front.  O(1)."""
        return self.is_full() and self._front > 0

    def clear(self):
        """Remove every element and put front/rear back to their start
        positions.  This also cures the 'false full' state.  O(capacity)."""
        i = 0
        while i < self._capacity:
            self._data[i] = None
            i += 1
        self._front = 0
        self._rear = -1

    def capacity(self):
        return self._capacity

    def front_index(self):
        return self._front

    def rear_index(self):
        return self._rear

    def slots(self):
        """Copy of the raw array (None = free slot) for drawing.  O(capacity)."""
        out = [None] * self._capacity
        i = 0
        while i < self._capacity:
            out[i] = self._data[i]
            i += 1
        return out

    def display(self):
        """Elements from front to rear as a new fixed array.  O(n)."""
        n = self.size()
        out = [None] * n
        i = 0
        while i < n:
            out[i] = self._data[self._front + i]
            i += 1
        return out


class CircularQueue:
    """FIFO queue on a fixed array with wrap-around.
    All operations O(1) except display O(n) and clear O(capacity)."""

    def __init__(self, capacity):
        _check_capacity(capacity)
        self._data = [None] * capacity
        self._capacity = capacity
        self._front = 0
        self._rear = capacity - 1      # so that the first enqueue puts rear at 0
        self._count = 0

    def enqueue(self, value):
        """Add value at the rear, wrapping round to index 0 if needed.  O(1)."""
        if self.is_full():
            raise DSError("Circular queue is full (all %d slots are in use), cannot enqueue %s."
                          % (self._capacity, value))
        self._rear = (self._rear + 1) % self._capacity
        self._data[self._rear] = value
        self._count += 1

    def dequeue(self):
        """Remove and return the front element.  O(1)."""
        if self.is_empty():
            raise DSError("Circular queue is empty, nothing to dequeue.")
        value = self._data[self._front]
        self._data[self._front] = None
        self._front = (self._front + 1) % self._capacity
        self._count -= 1
        return value

    def front(self):
        """O(1)."""
        if self.is_empty():
            raise DSError("Circular queue is empty, there is no front element.")
        return self._data[self._front]

    def size(self):
        return self._count

    def is_empty(self):
        return self._count == 0

    def is_full(self):
        return self._count == self._capacity

    def clear(self):
        """Remove every element and reset front/rear.  O(capacity)."""
        i = 0
        while i < self._capacity:
            self._data[i] = None
            i += 1
        self._front = 0
        self._rear = self._capacity - 1
        self._count = 0

    def capacity(self):
        return self._capacity

    def front_index(self):
        return self._front

    def rear_index(self):
        return self._rear

    def slots(self):
        """Copy of the raw array for drawing.  O(capacity)."""
        out = [None] * self._capacity
        i = 0
        while i < self._capacity:
            out[i] = self._data[i]
            i += 1
        return out

    def display(self):
        """Elements from front to rear (following the wrap-around).  O(n)."""
        out = [None] * self._count
        i = 0
        while i < self._count:
            out[i] = self._data[(self._front + i) % self._capacity]
            i += 1
        return out
