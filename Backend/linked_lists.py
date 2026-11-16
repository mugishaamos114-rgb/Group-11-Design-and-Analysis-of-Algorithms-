"""
linked_lists.py - Module B(c): singly and doubly linked lists built from our
own Node objects with explicit `next` (and `prev`) references.

Both lists keep a `head`, a `tail` and a `count`.  "Before X" / "after X"
operations act on the FIRST node whose value equals X.
"""

from .core import DSError


class SinglyNode:
    """A node of a singly linked list: a value and a reference to the next node."""

    def __init__(self, value):
        self.value = value
        self.next = None


class DoublyNode:
    """A node of a doubly linked list: value, next and prev references."""

    def __init__(self, value):
        self.value = value
        self.next = None
        self.prev = None


# ===========================================================================
# Singly linked list
# ===========================================================================

class SinglyLinkedList:
    """Singly linked list with head and tail references."""

    def __init__(self):
        self.head = None
        self.tail = None
        self.count = 0

    # ---- helpers --------------------------------------------------------
    def _find_with_previous(self, target):
        """Walk the list looking for target.  Returns (previous, node);
        node is None if not found.  O(n)."""
        previous = None
        current = self.head
        while current is not None:
            if current.value == target:
                return previous, current
            previous = current
            current = current.next
        return None, None

    def _require(self, target):
        previous, node = self._find_with_previous(target)
        if node is None:
            raise DSError("Element %s not found in the list." % target)
        return previous, node

    # ---- insertion ------------------------------------------------------
    def insert_at_beginning(self, value):
        """New node becomes the head.  O(1)."""
        node = SinglyNode(value)
        node.next = self.head
        self.head = node
        if self.tail is None:          # list was empty
            self.tail = node
        self.count += 1

    def insert_at_end(self, value):
        """New node becomes the tail.  O(1) because we keep a tail reference."""
        node = SinglyNode(value)
        if self.tail is None:
            self.head = node
            self.tail = node
        else:
            self.tail.next = node
            self.tail = node
        self.count += 1

    def insert_after(self, target, value):
        """Insert value after the first node holding target.  O(n) search + O(1) link."""
        _, node = self._require(target)
        new_node = SinglyNode(value)
        new_node.next = node.next
        node.next = new_node
        if node is self.tail:
            self.tail = new_node
        self.count += 1

    def insert_before(self, target, value):
        """Insert value before the first node holding target.  O(n): a singly
        linked list must walk from the head to find the previous node."""
        previous, node = self._require(target)
        if previous is None:           # target is the head
            self.insert_at_beginning(value)
            return
        new_node = SinglyNode(value)
        new_node.next = node
        previous.next = new_node
        self.count += 1

    # ---- deletion -------------------------------------------------------
    def delete_at_beginning(self):
        """Remove the head.  O(1)."""
        if self.head is None:
            raise DSError("The list is empty, nothing to delete.")
        value = self.head.value
        self.head = self.head.next
        if self.head is None:
            self.tail = None
        self.count -= 1
        return value

    def delete_at_end(self):
        """Remove the tail.  O(n): we must find the node before the tail."""
        if self.head is None:
            raise DSError("The list is empty, nothing to delete.")
        if self.head is self.tail:
            return self.delete_at_beginning()
        current = self.head
        while current.next is not self.tail:
            current = current.next
        value = self.tail.value
        current.next = None
        self.tail = current
        self.count -= 1
        return value

    def delete_value(self, target):
        """Remove the first node holding target.  O(n)."""
        previous, node = self._require(target)
        if previous is None:
            return self.delete_at_beginning()
        previous.next = node.next
        if node is self.tail:
            self.tail = previous
        self.count -= 1
        return node.value

    def delete_after(self, target):
        """Remove the node right after the first node holding target.  O(n)."""
        _, node = self._require(target)
        if node.next is None:
            raise DSError("There is no element after %s (it is the last node)." % target)
        removed = node.next
        node.next = removed.next
        if removed is self.tail:
            self.tail = node
        self.count -= 1
        return removed.value

    def delete_before(self, target):
        """Remove the node right before the first node holding target.  O(n):
        we track the two nodes before the current one while walking."""
        _, node = self._require(target)
        if node is self.head:
            raise DSError("There is no element before %s (it is the first node)." % target)
        if self.head.next is node:     # the node before target is the head
            return self.delete_at_beginning()
        before_previous = self.head
        while before_previous.next.next is not node:
            before_previous = before_previous.next
        removed = before_previous.next
        before_previous.next = node
        self.count -= 1
        return removed.value

    # ---- queries --------------------------------------------------------
    def search(self, target):
        """Return the 0-based position of target, or -1.  O(n)."""
        position = 0
        current = self.head
        while current is not None:
            if current.value == target:
                return position
            current = current.next
            position += 1
        return -1

    def size(self):
        """O(1) - the count is kept up to date by every operation."""
        return self.count

    def is_empty(self):
        return self.count == 0

    def display_forward(self):
        """Values from head to tail as a new fixed array.  O(n)."""
        out = [None] * self.count
        i = 0
        current = self.head
        while current is not None:
            out[i] = current.value
            current = current.next
            i += 1
        return out


# ===========================================================================
# Doubly linked list
# ===========================================================================

class DoublyLinkedList:
    """Doubly linked list with head and tail references.  Because each node
    knows its predecessor, deleting at the end and inserting/deleting before
    a node need no extra walk once the node has been found."""

    def __init__(self):
        self.head = None
        self.tail = None
        self.count = 0

    def _find(self, target):
        """Return the first node holding target or None.  O(n)."""
        current = self.head
        while current is not None:
            if current.value == target:
                return current
            current = current.next
        return None

    def _require(self, target):
        node = self._find(target)
        if node is None:
            raise DSError("Element %s not found in the list." % target)
        return node

    def _unlink(self, node):
        """Remove a given node from the list.  O(1)."""
        if node.prev is None:
            self.head = node.next
        else:
            node.prev.next = node.next
        if node.next is None:
            self.tail = node.prev
        else:
            node.next.prev = node.prev
        node.next = None
        node.prev = None
        self.count -= 1
        return node.value

    # ---- insertion ------------------------------------------------------
    def insert_at_beginning(self, value):
        """O(1)."""
        node = DoublyNode(value)
        node.next = self.head
        if self.head is None:
            self.tail = node
        else:
            self.head.prev = node
        self.head = node
        self.count += 1

    def insert_at_end(self, value):
        """O(1)."""
        node = DoublyNode(value)
        node.prev = self.tail
        if self.tail is None:
            self.head = node
        else:
            self.tail.next = node
        self.tail = node
        self.count += 1

    def insert_after(self, target, value):
        """O(n) search + O(1) relinking."""
        node = self._require(target)
        if node is self.tail:
            self.insert_at_end(value)
            return
        new_node = DoublyNode(value)
        new_node.prev = node
        new_node.next = node.next
        node.next.prev = new_node
        node.next = new_node
        self.count += 1

    def insert_before(self, target, value):
        """O(n) search + O(1) relinking (uses the prev reference)."""
        node = self._require(target)
        if node is self.head:
            self.insert_at_beginning(value)
            return
        new_node = DoublyNode(value)
        new_node.next = node
        new_node.prev = node.prev
        node.prev.next = new_node
        node.prev = new_node
        self.count += 1

    # ---- deletion -------------------------------------------------------
    def delete_at_beginning(self):
        """O(1)."""
        if self.head is None:
            raise DSError("The list is empty, nothing to delete.")
        return self._unlink(self.head)

    def delete_at_end(self):
        """O(1) - the tail's prev reference gives the new tail directly."""
        if self.tail is None:
            raise DSError("The list is empty, nothing to delete.")
        return self._unlink(self.tail)

    def delete_value(self, target):
        """O(n)."""
        return self._unlink(self._require(target))

    def delete_after(self, target):
        """O(n)."""
        node = self._require(target)
        if node.next is None:
            raise DSError("There is no element after %s (it is the last node)." % target)
        return self._unlink(node.next)

    def delete_before(self, target):
        """O(n)."""
        node = self._require(target)
        if node.prev is None:
            raise DSError("There is no element before %s (it is the first node)." % target)
        return self._unlink(node.prev)

    # ---- queries --------------------------------------------------------
    def search(self, target):
        """0-based position of target or -1.  O(n)."""
        position = 0
        current = self.head
        while current is not None:
            if current.value == target:
                return position
            current = current.next
            position += 1
        return -1

    def size(self):
        return self.count

    def is_empty(self):
        return self.count == 0

    def display_forward(self):
        """Head to tail following next.  O(n)."""
        out = [None] * self.count
        i = 0
        current = self.head
        while current is not None:
            out[i] = current.value
            current = current.next
            i += 1
        return out

    def display_backward(self):
        """Tail to head following prev.  O(n)."""
        out = [None] * self.count
        i = 0
        current = self.tail
        while current is not None:
            out[i] = current.value
            current = current.prev
            i += 1
        return out
