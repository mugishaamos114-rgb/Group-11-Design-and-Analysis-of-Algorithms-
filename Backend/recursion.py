"""
recursion.py - Module A: Recursion Lab (back end).

Fibonacci (naive, memoized, bottom-up), factorial (recursive, iterative)
and the Tower of Hanoi.  Every function returns the result together with the
number of calls / iterations and the time taken, measured with
time.perf_counter_ns.
"""

import sys

from .core import AlgoResult, DynamicArray, now_ns

# Limits that keep the application responsive and inside Python's recursion
# limit (default 1000 frames).
FIB_NAIVE_MAX = 30       # naive Fibonacci makes ~1.6^n calls: n=30 -> 2.7 million
FIB_MEMO_MAX = 900       # memoized recursion goes n levels deep
FIB_BOTTOM_UP_MAX = 10_000
FACT_REC_MAX = 900       # recursive factorial goes n levels deep
FACT_ITER_MAX = 5_000
HANOI_MAX_DISKS = 8

FIB_NAIVE_EXPLANATION = (
    "Naive recursion recomputes the same sub-problems again and again: "
    "fib(n) calls fib(n-1) and fib(n-2), and each of those calls two more. "
    "The number of calls grows like 1.6^n (it equals 2*fib(n+1) - 1), so "
    "n = 30 already needs 2,692,537 calls and n = 40 would need over 330 million. "
    "That is why the naive version is limited to n <= 30. Memoization stores each "
    "fib(k) the first time it is computed, so only n+1 distinct values are ever "
    "calculated - O(n) instead of O(1.6^n)."
)


def _ensure_recursion_depth(depth):
    """Make sure Python allows at least `depth` nested calls."""
    if sys.getrecursionlimit() < depth + 200:
        sys.setrecursionlimit(depth + 200)


def _check_fib_input(n):
    """Fibonacci is only defined here for n >= 0.  Without this check a
    negative n would silently return n itself (the base case k < 2)."""
    if n < 0:
        raise ValueError("Fibonacci is not defined for negative numbers.")


# ---------------------------------------------------------------------------
# Fibonacci
# ---------------------------------------------------------------------------

def fib_naive(n):
    """n-th Fibonacci number by plain recursion.
    Time O(phi^n) ~ O(1.618^n) (exponential), space O(n) for the call stack.
    Rejects negative n."""
    _check_fib_input(n)
    calls = 0

    def fib(k):
        nonlocal calls
        calls += 1
        if k < 2:                      # base cases fib(0)=0, fib(1)=1
            return k
        return fib(k - 1) + fib(k - 2)

    start = now_ns()
    value = fib(n)
    elapsed = now_ns() - start
    return AlgoResult("Naive recursion", value, calls, "function calls", elapsed)


def fib_memo(n):
    """n-th Fibonacci number by recursion with memoization (top-down DP).
    Time O(n) - each fib(k) is computed once; space O(n) for the memo array
    plus O(n) for the call stack.  Rejects negative n."""
    _check_fib_input(n)
    _ensure_recursion_depth(n)
    memo = [None] * (n + 1)            # fixed-size memo table, memo[k] = fib(k)
    calls = 0

    def fib(k):
        nonlocal calls
        calls += 1
        if k < 2:
            return k
        if memo[k] is not None:        # already computed: reuse it
            return memo[k]
        memo[k] = fib(k - 1) + fib(k - 2)
        return memo[k]

    start = now_ns()
    value = fib(n)
    elapsed = now_ns() - start
    return AlgoResult("Memoized recursion", value, calls, "function calls", elapsed)


def fib_bottom_up(n):
    """n-th Fibonacci number by bottom-up dynamic programming.
    Time O(n) loop iterations, space O(1) (we only keep the last two values).
    Rejects negative n."""
    _check_fib_input(n)
    start = now_ns()
    iterations = 0
    if n < 2:
        value = n
    else:
        previous, current = 0, 1       # fib(0), fib(1)
        k = 2
        while k <= n:
            previous, current = current, previous + current
            iterations += 1
            k += 1
        value = current
    elapsed = now_ns() - start
    return AlgoResult("Bottom-up DP", value, iterations, "loop iterations", elapsed)


# ---------------------------------------------------------------------------
# Factorial
# ---------------------------------------------------------------------------

def factorial_recursive(n):
    """n! recursively: n! = n * (n-1)!, 0! = 1.
    Time O(n) calls, space O(n) call stack.  Rejects negative n."""
    if n < 0:
        raise ValueError("Factorial is not defined for negative numbers.")
    _ensure_recursion_depth(n)
    calls = 0

    def fact(k):
        nonlocal calls
        calls += 1
        if k == 0:                     # base case 0! = 1
            return 1
        return k * fact(k - 1)

    start = now_ns()
    value = fact(n)
    elapsed = now_ns() - start
    return AlgoResult("Recursive", value, calls, "function calls", elapsed)


def factorial_iterative(n):
    """n! with a loop.  Time O(n) iterations, space O(1)."""
    if n < 0:
        raise ValueError("Factorial is not defined for negative numbers.")
    start = now_ns()
    result = 1
    iterations = 0
    k = 2
    while k <= n:
        result *= k
        iterations += 1
        k += 1
    elapsed = now_ns() - start
    return AlgoResult("Iterative", result, iterations, "loop iterations", elapsed)


# ---------------------------------------------------------------------------
# Tower of Hanoi
# ---------------------------------------------------------------------------

class HanoiMove:
    """One move: disk number `disk` goes from peg `source` to peg `target`."""

    def __init__(self, number, disk, source, target):
        self.number = number
        self.disk = disk
        self.source = source
        self.target = target

    def __str__(self):
        return "Move disk %d from %s to %s" % (self.disk, self.source, self.target)


def hanoi(n, source, destination, auxiliary):
    """Solve the Tower of Hanoi recursively for n disks.

    To move n disks from S to D using A:
        1. move n-1 disks from S to A (using D),
        2. move disk n from S to D,
        3. move n-1 disks from A to D (using S).
    T(n) = 2T(n-1) + 1 = 2^n - 1 moves, so time O(2^n); recursion depth O(n).

    Returns an AlgoResult whose value is a DynamicArray of HanoiMove and whose
    `extra` is the number of recursive calls.
    """
    if n < 1:
        raise ValueError("The number of disks must be at least 1.")
    if source == destination or source == auxiliary or destination == auxiliary:
        raise ValueError("Source, destination and auxiliary must be three different pegs.")

    moves = DynamicArray(16)
    calls = 0

    def solve(k, s, d, a):
        nonlocal calls
        calls += 1
        if k == 0:
            return
        solve(k - 1, s, a, d)
        moves.add(HanoiMove(moves.size() + 1, k, s, d))
        solve(k - 1, a, d, s)

    start = now_ns()
    solve(n, source, destination, auxiliary)
    elapsed = now_ns() - start
    return AlgoResult("Tower of Hanoi", moves, moves.size(), "moves", elapsed, extra=calls)
