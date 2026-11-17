"""
ds_tab.py - Module B screens: stack, linear/circular queues, singly/doubly
linked lists and the bracket checker.  Every operation calls the back-end
class and then redraws the structure.
"""

import random
import tkinter as tk
from tkinter import ttk

from backend.brackets import check_brackets
from backend.core import DSError, format_number, parse_int, parse_number
from backend.linked_lists import DoublyLinkedList, SinglyLinkedList
from backend.queues import CircularQueue, LinearQueue
from backend.stack import ArrayStack

from . import theme
from .widgets import MessageLine, ScrollCanvas, Table, card, explanation, labelled_entry

BOX_FILL = "#e8eef9"
BOX_LINE = "#5b7fc4"
HIGHLIGHT = "#fde7b0"
EMPTY_FILL = "#f4f3ef"


def read_value(entry, msg, name="Value"):
    """Read and validate a number from an Entry; shows an error and returns None if invalid."""
    text = entry.get().strip()
    if text == "":
        msg.error("Please type a %s first." % name.lower())
        return None
    try:
        return parse_number(text)
    except ValueError:
        msg.error("%s must be a number, not '%s'." % (name, text))
        return None


def join_values(values, separator=", "):
    """'3, 5, 9' from a fixed array."""
    text = ""
    i = 0
    while i < len(values):
        if i > 0:
            text += separator
        text += format_number(values[i])
        i += 1
    return text


def button_row(parent, title, buttons):
    """LabelFrame with a row of buttons: buttons = ((text, command), ...)."""
    frame = ttk.LabelFrame(parent, text=title, padding=(8, 4))
    for text, command in buttons:
        ttk.Button(frame, text=text, command=command).pack(side="left", padx=2, pady=2)
    return frame


class DataStructuresTab(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent, padding=10)
        book = ttk.Notebook(self, style="Sub.TNotebook")
        book.pack(fill="both", expand=True)
        book.add(StackPanel(book), text="Stack")
        book.add(QueuePanel(book), text="Queues")
        book.add(LinkedListPanel(book), text="Linked lists")
        book.add(BracketPanel(book), text="Bracket checker (stack application)")


# ===========================================================================
class StackPanel(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent, style="Card.TFrame", padding=14)
        self.stack = ArrayStack(6)
        self.highlight = -1
        ttk.Label(self, text="Array-based stack (LIFO)", style="Title.TLabel").pack(anchor="w")
        explanation(self, "A fixed-size array plus a 'top' index. push and pop work only at the top, so every "
                          "operation is O(1). Pushing onto a full stack is an overflow; popping an empty stack "
                          "is an underflow.").pack(anchor="w", pady=(2, 8))
        row = ttk.Frame(self, style="Card.TFrame")
        row.pack(fill="x")
        self.cap = labelled_entry(row, "Capacity", 5, "6")
        self.cap.pack(side="left")
        ttk.Button(row, text="Create new stack", command=self.create).pack(side="left", padx=(6, 20))
        self.value = labelled_entry(row, "Value", 8, "42")
        self.value.pack(side="left")
        self.value.entry.bind("<Return>", lambda e: self.push())
        ops = ttk.Frame(self, style="Card.TFrame")
        ops.pack(fill="x", pady=8)
        button_row(ops, "Operations", (("Push", self.push), ("Pop", self.pop), ("Peek", self.peek),
                                       ("Size", self.size), ("Is empty?", self.is_empty),
                                       ("Is full?", self.is_full), ("Display", self.display))).pack(side="left")
        self.msg = MessageLine(self)
        self.msg.pack(fill="x", pady=(0, 6))
        body = ttk.Frame(self, style="Card.TFrame")
        body.pack(fill="both", expand=True)
        self.canvas = tk.Canvas(body, bg="#fbfbf9", highlightthickness=1, highlightbackground=theme.LINE)
        self.canvas.pack(side="left", fill="both", expand=True)
        self.canvas.bind("<Configure>", lambda e: self.draw())
        log_frame = ttk.Frame(body, style="Card.TFrame", padding=(10, 0, 0, 0))
        log_frame.pack(side="right", fill="y")
        ttk.Label(log_frame, text="History", style="Card.TLabel").pack(anchor="w")
        self.log = tk.Listbox(log_frame, width=34, font=theme.mono(9), relief="flat",
                              highlightthickness=1, highlightbackground=theme.LINE)
        self.log.pack(fill="both", expand=True)

    def note(self, text, ok=True):
        (self.msg.ok if ok else self.msg.error)(text)
        self.log.insert(0, ("  " if ok else "✖ ") + text)
        self.draw()

    def create(self):
        cap, error = parse_int(self.cap.entry.get(), "Capacity", 1, 20)
        if error:
            self.msg.error(error)
            return
        self.stack = ArrayStack(cap)
        self.highlight = -1
        self.log.delete(0, "end")
        self.note("Created an empty stack with capacity %d" % cap)

    def push(self):
        v = read_value(self.value.entry, self.msg)
        if v is None:
            return
        try:
            self.stack.push(v)
            self.highlight = self.stack.top_index()
            self.note("Pushed %s" % format_number(v))
            self.value.entry.delete(0, "end")
            self.value.entry.insert(0, str(random.randint(1, 99)))
        except DSError as e:
            self.note(str(e), False)

    def pop(self):
        try:
            v = self.stack.pop()
            self.highlight = -1
            self.note("Popped %s" % format_number(v))
        except DSError as e:
            self.note(str(e), False)

    def peek(self):
        try:
            v = self.stack.peek()
            self.highlight = self.stack.top_index()
            self.note("Top element is %s (not removed)" % format_number(v))
        except DSError as e:
            self.note(str(e), False)

    def size(self):
        self.note("Size = %d (capacity %d)" % (self.stack.size(), self.stack.capacity()))

    def is_empty(self):
        self.note("is_empty() → %s" % self.stack.is_empty())

    def is_full(self):
        self.note("is_full() → %s" % self.stack.is_full())

    def display(self):
        items = self.stack.display()
        self.note("Bottom → top: [%s]" % join_values(items) if len(items) else "Stack is empty: []")

    def draw(self):
        c = self.canvas
        c.delete("all")
        w = max(c.winfo_width(), 200)
        h = max(c.winfo_height(), 200)
        cap = self.stack.capacity()
        box_h = min(42, (h - 60) / cap)
        box_w = 140
        x = w / 2 - box_w / 2
        top = self.stack.top_index()
        items = self.stack.display()
        i = 0
        while i < cap:
            y2 = h - 24 - i * box_h
            y1 = y2 - box_h
            filled = i <= top
            fill = HIGHLIGHT if i == self.highlight else (BOX_FILL if filled else EMPTY_FILL)
            c.create_rectangle(x, y1, x + box_w, y2, fill=fill, outline=BOX_LINE if filled else theme.LINE,
                               width=2 if filled else 1)
            c.create_text(x - 14, (y1 + y2) / 2, text="[%d]" % i, fill=theme.MUTED, font=theme.font(8), anchor="e")
            if filled:
                c.create_text(x + box_w / 2, (y1 + y2) / 2, text=format_number(items[i]),
                              fill=theme.INK, font=theme.font(11, "bold"))
            if i == top:
                c.create_text(x + box_w + 14, (y1 + y2) / 2, text="← TOP (index %d)" % top, anchor="w",
                              fill=theme.ACCENT, font=theme.font(10, "bold"))
            i += 1
        if top == -1:
            c.create_text(x + box_w + 14, h - 24 - box_h / 2, text="TOP = -1 (empty)", anchor="w",
                          fill=theme.MUTED, font=theme.font(10, "bold"))
        c.create_text(x + box_w / 2, h - 10, text="size %d / capacity %d" % (self.stack.size(), cap),
                      fill=theme.MUTED, font=theme.font(9))


# ===========================================================================
class QueuePanel(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent, style="Card.TFrame", padding=14)
        self.linear = LinearQueue(5)
        self.circular = CircularQueue(5)
        self.demo_steps = None
        ttk.Label(self, text="Linear queue and circular queue (FIFO)", style="Title.TLabel").pack(anchor="w")
        explanation(self, "Both queues use a fixed array. Operations are applied to the queue(s) chosen under "
                          "'Apply to' - try 'Both' to compare them side by side. Try the 'false full' demo.").pack(anchor="w", pady=(2, 8))
        row = ttk.Frame(self, style="Card.TFrame")
        row.pack(fill="x")
        self.cap = labelled_entry(row, "Capacity", 5, "5")
        self.cap.pack(side="left")
        ttk.Button(row, text="Create new queues", command=self.create).pack(side="left", padx=(6, 18))
        self.value = labelled_entry(row, "Value", 8, "10")
        self.value.pack(side="left")
        self.value.entry.bind("<Return>", lambda e: self.enqueue())
        ttk.Label(row, text="Apply to", style="Card.TLabel").pack(side="left", padx=(18, 4))
        self.target = tk.StringVar(value="both")
        for text, val in (("Both", "both"), ("Linear", "linear"), ("Circular", "circular")):
            ttk.Radiobutton(row, text=text, value=val, variable=self.target).pack(side="left")
        ops = ttk.Frame(self, style="Card.TFrame")
        ops.pack(fill="x", pady=8)
        button_row(ops, "Operations", (("Enqueue", self.enqueue), ("Dequeue", self.dequeue), ("Front", self.front),
                                       ("Size", self.size), ("Is empty?", self.is_empty), ("Is full?", self.is_full),
                                       ("Display", self.display))).pack(side="left")
        ttk.Button(ops, text="▶ Demo: false full", style="Accent.TButton",
                   command=self.demo).pack(side="left", padx=12)
        self.msg = MessageLine(self)
        self.msg.pack(fill="x")
        self.msg2 = MessageLine(self)
        self.msg2.pack(fill="x", pady=(0, 6))
        self.canvas = tk.Canvas(self, bg="#fbfbf9", highlightthickness=1, highlightbackground=theme.LINE, height=300)
        self.canvas.pack(fill="both", expand=True)
        self.canvas.bind("<Configure>", lambda e: self.draw())
        box = card(self, 10)
        box.pack(fill="x", pady=(8, 0))
        explanation(box.inner,
                    "The 'false full' problem: in a linear queue, dequeue only moves FRONT forward, so the freed "
                    "slots at the start of the array can never be used again. Once REAR reaches the last index the "
                    "queue reports full even though it holds fewer than 'capacity' elements. The circular queue "
                    "fixes this by wrapping the indices round with rear = (rear + 1) mod capacity (and the same for "
                    "front), so the next element goes into slot 0 if it is free. It is only full when "
                    "count == capacity.").pack(anchor="w")

    def _targets(self):
        t = self.target.get()
        out = []
        if t == "both" or t == "linear":
            out += [("Linear", self.linear)]
        if t == "both" or t == "circular":
            out += [("Circular", self.circular)]
        return out

    def _apply(self, action):
        """Run action(queue) on the chosen queue(s) and show one message per queue."""
        lines = [self.msg, self.msg2]
        self.msg2.configure(text="")
        i = 0
        for name, q in self._targets():
            try:
                lines[i].ok("%s queue: %s" % (name, action(q)))
            except DSError as e:
                lines[i].error("%s queue: %s" % (name, e))
            i += 1
        self.draw()

    def create(self):
        cap, error = parse_int(self.cap.entry.get(), "Capacity", 1, 12)
        if error:
            self.msg.error(error)
            return
        self.linear = LinearQueue(cap)
        self.circular = CircularQueue(cap)
        self.msg.ok("Created an empty linear queue and circular queue, capacity %d." % cap)
        self.msg2.configure(text="")
        self.draw()

    def enqueue(self):
        v = read_value(self.value.entry, self.msg)
        if v is None:
            return

        def act(q):
            q.enqueue(v)
            return "enqueued %s at index %d" % (format_number(v), q.rear_index())
        self._apply(act)
        self.value.entry.delete(0, "end")
        self.value.entry.insert(0, str(random.randint(1, 99)))

    def dequeue(self):
        self._apply(lambda q: "dequeued %s" % format_number(q.dequeue()))

    def front(self):
        self._apply(lambda q: "front element is %s" % format_number(q.front()))

    def size(self):
        self._apply(lambda q: "size = %d" % q.size())

    def is_empty(self):
        self._apply(lambda q: "is_empty() → %s" % q.is_empty())

    def is_full(self):
        def act(q):
            text = "is_full() → %s" % q.is_full()
            if isinstance(q, LinearQueue) and q.is_false_full():
                text += "  (FALSE FULL: only %d of %d slots used!)" % (q.size(), q.capacity())
            return text
        self._apply(act)

    def display(self):
        self._apply(lambda q: "front → rear: [%s]" % join_values(q.display()))

    def demo(self):
        """Automatic demonstration of the false-full problem."""
        self.target.set("both")
        self.cap.entry.delete(0, "end")
        self.cap.entry.insert(0, "5")
        self.create()
        steps = [("enqueue", 10), ("enqueue", 20), ("enqueue", 30), ("enqueue", 40), ("enqueue", 50),
                 ("dequeue", None), ("dequeue", None), ("enqueue", 60), ("enqueue", 70)]
        self.demo_steps = steps
        self._demo_step(0)

    def _demo_step(self, i):
        if i >= len(self.demo_steps):
            self.msg.warn("Linear queue: rear is stuck at index 4, so 60 and 70 were rejected although "
                          "slots 0 and 1 are free ('false full').")
            self.msg2.ok("Circular queue: rear wrapped round to index 0 and then 1, reusing the freed slots.")
            return
        op, v = self.demo_steps[i]
        if op == "enqueue":
            self.value.entry.delete(0, "end")
            self.value.entry.insert(0, str(v))
            self.enqueue()
        else:
            self.dequeue()
        self.after(900, lambda: self._demo_step(i + 1))

    def _draw_queue(self, q, title, y, circular):
        c = self.canvas
        w = max(c.winfo_width(), 300)
        cap = q.capacity()
        box = min(70, (w - 140) / cap)
        x0 = 110
        slots = q.slots()
        c.create_text(14, y + box / 2, text=title, anchor="w", fill=theme.ACCENT_DARK, font=theme.font(10, "bold"))
        false_full = (not circular) and q.is_false_full()
        i = 0
        while i < cap:
            x = x0 + i * box
            used = slots[i] is not None
            fill = BOX_FILL if used else ("#fde2e1" if false_full else EMPTY_FILL)
            c.create_rectangle(x, y, x + box, y + box * 0.8, fill=fill,
                               outline=BOX_LINE if used else theme.LINE, width=2 if used else 1)
            if used:
                c.create_text(x + box / 2, y + box * 0.4, text=format_number(slots[i]),
                              fill=theme.INK, font=theme.font(11, "bold"))
            c.create_text(x + box / 2, y + box * 0.8 + 10, text=str(i), fill=theme.MUTED, font=theme.font(8))
            i += 1
        f, r = q.front_index(), q.rear_index()
        if not q.is_empty() or not circular:
            fx = x0 + f * box + box / 2 if f < cap else x0 + cap * box + 12
            c.create_text(fx, y + box * 0.8 + 28, text="▲ FRONT", fill=theme.OK, font=theme.font(8, "bold"))
            rx = x0 + r * box + box / 2 if r >= 0 else x0 - 26
            c.create_text(rx, y - 10, text="REAR ▼", fill=theme.ERROR, font=theme.font(8, "bold"))
        info = "front = %d, rear = %d, size = %d / %d" % (f, r, q.size(), cap)
        if false_full:
            info += "   ⚠ FALSE FULL"
        if circular and q.is_empty():
            info += "   (empty)"
        c.create_text(x0 + cap * box + 24, y + box * 0.4, text=info, anchor="w",
                      fill=theme.ERROR if false_full else theme.MUTED, font=theme.font(9, "bold"))

    def draw(self):
        self.canvas.delete("all")
        self._draw_queue(self.linear, "Linear\nqueue", 34, False)
        self._draw_queue(self.circular, "Circular\nqueue", 170, True)


# ===========================================================================
class LinkedListPanel(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent, style="Card.TFrame", padding=14)
        self.singly = SinglyLinkedList()
        self.doubly = DoublyLinkedList()
        for v in (10, 20, 30):
            self.singly.insert_at_end(v)
            self.doubly.insert_at_end(v)
        self.highlight = -1
        ttk.Label(self, text="Singly and doubly linked lists", style="Title.TLabel").pack(anchor="w")
        explanation(self, "Lists built from our own Node objects with explicit next (and prev) references. "
                          "'Before' and 'after' operations use the first node whose value equals Target.").pack(anchor="w", pady=(2, 8))
        row = ttk.Frame(self, style="Card.TFrame")
        row.pack(fill="x")
        ttk.Label(row, text="List", style="Card.TLabel").pack(side="left", padx=(0, 4))
        self.kind = tk.StringVar(value="singly")
        ttk.Radiobutton(row, text="Singly linked", value="singly", variable=self.kind,
                        command=self.switch).pack(side="left")
        ttk.Radiobutton(row, text="Doubly linked", value="doubly", variable=self.kind,
                        command=self.switch).pack(side="left", padx=(0, 18))
        self.value = labelled_entry(row, "Value", 7, "5")
        self.value.pack(side="left", padx=(0, 12))
        self.target = labelled_entry(row, "Target", 7, "20")
        self.target.pack(side="left")
        ttk.Button(row, text="Clear list", command=self.clear).pack(side="left", padx=(18, 2))
        ttk.Button(row, text="Add 5 random", command=self.add_random).pack(side="left", padx=2)

        grid = ttk.Frame(self, style="Card.TFrame")
        grid.pack(fill="x", pady=8)
        button_row(grid, "Insert value", (("At beginning", lambda: self.insert("begin")),
                                          ("At end", lambda: self.insert("end")),
                                          ("Before target", lambda: self.insert("before")),
                                          ("After target", lambda: self.insert("after")))).grid(row=0, column=0, sticky="w")
        button_row(grid, "Delete", (("At beginning", lambda: self.delete("begin")),
                                    ("At end", lambda: self.delete("end")),
                                    ("Before target", lambda: self.delete("before")),
                                    ("After target", lambda: self.delete("after")),
                                    ("Target itself", lambda: self.delete("value")))).grid(row=0, column=1, sticky="w", padx=8)
        button_row(grid, "Query", (("Search target", self.search), ("Size", self.size),
                                   ("Display forward", self.forward),
                                   ("Display backward", self.backward))).grid(row=1, column=0, columnspan=2, sticky="w", pady=(6, 0))
        self.msg = MessageLine(self)
        self.msg.pack(fill="x", pady=(0, 6))
        self.view = ScrollCanvas(self, height=220)
        self.view.pack(fill="both", expand=True)
        self.draw()

    def current(self):
        return self.singly if self.kind.get() == "singly" else self.doubly

    def switch(self):
        self.highlight = -1
        self.msg.info("Now working on the %s linked list." % self.kind.get())
        self.draw()

    def clear(self):
        if self.kind.get() == "singly":
            self.singly = SinglyLinkedList()
        else:
            self.doubly = DoublyLinkedList()
        self.highlight = -1
        self.msg.ok("List cleared.")
        self.draw()

    def add_random(self):
        lst = self.current()
        i = 0
        while i < 5:
            lst.insert_at_end(random.randint(1, 99))
            i += 1
        self.msg.ok("Added 5 random values at the end.")
        self.draw()

    def insert(self, where):
        lst = self.current()
        v = read_value(self.value.entry, self.msg)
        if v is None:
            return
        try:
            if where == "begin":
                lst.insert_at_beginning(v)
                self.highlight = 0
                text = "Inserted %s at the beginning" % format_number(v)
            elif where == "end":
                lst.insert_at_end(v)
                self.highlight = lst.size() - 1
                text = "Inserted %s at the end" % format_number(v)
            else:
                t = read_value(self.target.entry, self.msg, "Target")
                if t is None:
                    return
                if where == "before":
                    lst.insert_before(t, v)
                    self.highlight = lst.search(t) - 1
                    text = "Inserted %s before %s" % (format_number(v), format_number(t))
                else:
                    lst.insert_after(t, v)
                    self.highlight = lst.search(t) + 1
                    text = "Inserted %s after %s" % (format_number(v), format_number(t))
            self.msg.ok(text)
        except DSError as e:
            self.msg.error(str(e))
        self.draw()

    def delete(self, where):
        lst = self.current()
        self.highlight = -1
        try:
            if where == "begin":
                text = "Deleted %s from the beginning" % format_number(lst.delete_at_beginning())
            elif where == "end":
                text = "Deleted %s from the end" % format_number(lst.delete_at_end())
            else:
                t = read_value(self.target.entry, self.msg, "Target")
                if t is None:
                    return
                if where == "before":
                    text = "Deleted %s (it was before %s)" % (format_number(lst.delete_before(t)), format_number(t))
                elif where == "after":
                    text = "Deleted %s (it was after %s)" % (format_number(lst.delete_after(t)), format_number(t))
                else:
                    text = "Deleted %s" % format_number(lst.delete_value(t))
            self.msg.ok(text)
        except DSError as e:
            self.msg.error(str(e))
        self.draw()

    def search(self):
        t = read_value(self.target.entry, self.msg, "Target")
        if t is None:
            return
        pos = self.current().search(t)
        self.highlight = pos
        if pos >= 0:
            self.msg.ok("Found %s at position %d (counting from 0 at the head) after visiting %d node(s)."
                        % (format_number(t), pos, pos + 1))
        else:
            self.msg.error("%s is not in the list (visited all %d nodes)." % (format_number(t), self.current().size()))
        self.draw()

    def size(self):
        self.msg.ok("Size = %d node(s)." % self.current().size())

    def forward(self):
        items = self.current().display_forward()
        arrow = " → " if self.kind.get() == "singly" else " ⇄ "
        self.msg.ok("Forward (head → tail): " + (join_values(items, arrow) + arrow + "NULL" if len(items) else "empty"))

    def backward(self):
        if self.kind.get() == "singly":
            self.msg.error("A singly linked list has no prev references, so it cannot be traversed backward. "
                           "Switch to the doubly linked list.")
            return
        items = self.doubly.display_backward()
        self.msg.ok("Backward (tail → head): " + (join_values(items, " ⇄ ") + " ⇄ NULL" if len(items) else "empty"))

    def draw(self):
        c = self.view.canvas
        c.delete("all")
        lst = self.current()
        doubly = self.kind.get() == "doubly"
        values = lst.display_forward()
        n = len(values)
        y = 90
        node_w = 96 if doubly else 80
        gap = 46
        x = 70
        c.create_text(30, y, text="HEAD", fill=theme.ACCENT, font=theme.font(9, "bold"))
        if n == 0:
            c.create_text(x + 30, y, text="NULL  (empty list)", anchor="w", fill=theme.MUTED, font=theme.font(10, "bold"))
            self.view.fit()
            return
        c.create_line(48, y, x, y, arrow="last", fill=theme.ACCENT, width=2)
        i = 0
        while i < n:
            fill = HIGHLIGHT if i == self.highlight else BOX_FILL
            c.create_rectangle(x, y - 22, x + node_w, y + 22, fill=fill, outline=BOX_LINE, width=2)
            if doubly:
                c.create_line(x + 22, y - 22, x + 22, y + 22, fill=BOX_LINE)
                c.create_line(x + node_w - 22, y - 22, x + node_w - 22, y + 22, fill=BOX_LINE)
                c.create_text(x + 11, y, text="•", fill=BOX_LINE)
                c.create_text(x + node_w / 2, y, text=format_number(values[i]), font=theme.font(11, "bold"))
            else:
                c.create_line(x + node_w - 22, y - 22, x + node_w - 22, y + 22, fill=BOX_LINE)
                c.create_text(x + (node_w - 22) / 2, y, text=format_number(values[i]), font=theme.font(11, "bold"))
            c.create_text(x + node_w - 11, y, text="•", fill=BOX_LINE)
            c.create_text(x + node_w / 2, y + 36, text="[%d]" % i, fill=theme.MUTED, font=theme.font(8))
            nx = x + node_w + gap
            if i < n - 1:
                c.create_line(x + node_w - 11, y - 6 if doubly else y, nx, y - 6 if doubly else y,
                              arrow="last", fill="#33415c", width=2)
                if doubly:
                    c.create_line(nx + 11, y + 6, x + node_w, y + 6, arrow="last", fill="#b0573a", width=2)
            else:
                c.create_line(x + node_w - 11, y, nx, y, arrow="last", fill="#33415c", width=2)
                c.create_text(nx + 4, y, text="NULL", anchor="w", fill=theme.MUTED, font=theme.font(9, "bold"))
            if i == 0 and doubly:
                c.create_line(x + 11, y + 22, x + 11, y + 44, arrow="last", fill="#b0573a", width=2)
                c.create_text(x + 11, y + 54, text="NULL", fill=theme.MUTED, font=theme.font(8, "bold"))
            if i == n - 1:
                c.create_text(x + node_w / 2, y - 40, text="TAIL ▼", fill=theme.ACCENT, font=theme.font(9, "bold"))
            x = nx
            i += 1
        legend = "next →  (dark)      ← prev  (orange)" if doubly else "each node: [ value | next ]"
        c.create_text(20, 170, text=legend, anchor="w", fill=theme.MUTED, font=theme.font(9))
        c.create_text(20, 190, text="size = %d" % n, anchor="w", fill=theme.MUTED, font=theme.font(9))
        self.view.fit()


# ===========================================================================
class BracketPanel(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent, style="Card.TFrame", padding=14)
        ttk.Label(self, text="Balanced brackets - a stack application", style="Title.TLabel").pack(anchor="w")
        explanation(self, "Read the expression left to right: push every opening bracket; for every closing "
                          "bracket pop the top and check it matches. The expression is balanced if every pop "
                          "matches and the stack is empty at the end. O(n) time, O(n) space.").pack(anchor="w", pady=(2, 8))
        row = ttk.Frame(self, style="Card.TFrame")
        row.pack(fill="x")
        self.expr = labelled_entry(row, "Expression", 40, "{ ( [ ] ) }")
        self.expr.pack(side="left")
        self.expr.entry.bind("<Return>", lambda e: self.run())
        ttk.Button(row, text="Check", style="Accent.TButton", command=self.run).pack(side="left", padx=10)
        for example in ("{ ( [ ] ) }", "{ ( [ ) ] }", "((a+b)*[c-d])", "(()"):
            ttk.Button(row, text=example, command=lambda e=example: self._example(e)).pack(side="left", padx=2)
        self.result = tk.Label(self, text="", bg=theme.CARD, font=theme.font(13, "bold"), anchor="w")
        self.result.pack(fill="x", pady=8)
        self.table = Table(self, ("Step", "Symbol", "Action", "Stack after (bottom → top)"),
                           (60, 70, 280, 360), height=12, anchors=("center", "center", "w", "w"))
        self.table.pack(fill="both", expand=True)
        self.run()

    def _example(self, text):
        self.expr.entry.delete(0, "end")
        self.expr.entry.insert(0, text)
        self.run()

    def run(self):
        balanced, message, steps = check_brackets(self.expr.entry.get())
        self.result.configure(text=("✔  " if balanced else "✖  ") + message,
                              fg=theme.OK if balanced else theme.ERROR)
        self.table.clear()
        i = 0
        while i < steps.size():
            s = steps.get(i)
            self.table.add((i + 1, s.symbol, s.action, "  ".join(s.stack_after) if len(s.stack_after) else "(empty)"))
            i += 1

