"""
brackets.py - stack application: check whether a bracket expression such as
{ ( [ ] ) } is balanced, recording the stack after every symbol.

Algorithm (O(n) time, O(n) space):
    for each character c:
        if c is an opening bracket: push c
        if c is a closing bracket:
            if the stack is empty -> unbalanced (nothing to match)
            pop the top; if it is not the matching opener -> unbalanced
    at the end the expression is balanced only if the stack is empty.
"""

from .core import DynamicArray
from .stack import ArrayStack


def _is_opening(ch):
    return ch == "(" or ch == "[" or ch == "{"


def _is_closing(ch):
    return ch == ")" or ch == "]" or ch == "}"


def _matches(opening, closing):
    return ((opening == "(" and closing == ")") or
            (opening == "[" and closing == "]") or
            (opening == "{" and closing == "}"))


class BracketStep:
    """One row of the trace: the symbol read, what was done and the stack after."""

    def __init__(self, position, symbol, action, stack_after):
        self.position = position
        self.symbol = symbol
        self.action = action
        self.stack_after = stack_after          # fixed array, bottom -> top


def check_brackets(expression):
    """Return (balanced: bool, message: str, steps: DynamicArray of BracketStep).
    Characters that are not brackets (letters, digits, spaces) are skipped."""
    if expression is None or expression.strip() == "":
        return False, "Please enter an expression such as { ( [ ] ) }.", DynamicArray()

    stack = ArrayStack(len(expression))         # can never hold more than n symbols
    steps = DynamicArray()
    position = 0
    while position < len(expression):
        ch = expression[position]
        if _is_opening(ch):
            stack.push(ch)
            steps.add(BracketStep(position, ch, "push " + ch, stack.display()))
        elif _is_closing(ch):
            if stack.is_empty():
                steps.add(BracketStep(position, ch, "stack empty - nothing matches " + ch,
                                      stack.display()))
                return False, ("Not balanced: '%s' at position %d has no matching opening bracket."
                               % (ch, position + 1)), steps
            top = stack.pop()
            if not _matches(top, ch):
                steps.add(BracketStep(position, ch, "pop " + top + " - does NOT match " + ch,
                                      stack.display()))
                return False, ("Not balanced: '%s' at position %d closes '%s'."
                               % (ch, position + 1, top)), steps
            steps.add(BracketStep(position, ch, "pop " + top + " - matches " + ch, stack.display()))
        position += 1

    if not stack.is_empty():
        return False, ("Not balanced: %d opening bracket(s) were never closed (top of stack: '%s')."
                       % (stack.size(), stack.peek())), steps
    if steps.size() == 0:
        return False, "The expression contains no brackets.", steps
    return True, "Balanced: every opening bracket is closed in the right order.", steps
