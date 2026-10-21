"""
CSC2107: Design & Analysis of Algorithms
Assignment 5.1: Naive vs. Memoized Fibonacci
Group 11 - Uganda Christian University (UCU)
"""

import time
import sys
from matplotlib import pyplot as plt

# Global call counters
calls_a = 0
calls_b = 0

# -------------------------------------------------------------
# Part 1: Algorithm A & Algorithm B Implementation
# -------------------------------------------------------------

def fib_a(n):
    """Algorithm A: Plain Recursion"""
    global calls_a
    calls_a += 1
    if n == 0 or n == 1:
        return n
    else:
        return fib_a(n - 1) + fib_a(n - 2)

def fib_b(n, fibtable=None):
    """Algorithm B: Recursion with Memoization (Fixed truthiness check)"""
    global calls_b
    calls_b += 1
    if fibtable is None:
        fibtable = {}
    
    if n in fibtable:
        return fibtable[n]
    
    if n == 0 or n == 1:
        value = n
    else:
        value = fib_b(n - 1, fibtable) + fib_b(n - 2, fibtable)
    
    fibtable[n] = value
    return value

# Verification for n = 0 to 20
def verify_correctness():
    print("Verifying Algorithm A and B correctness for n = 0 to 20:")
    for n in range(21):
        global calls_a, calls_b
        calls_a = 0
        calls_b = 0
        val_a = fib_a(n)
        val_b = fib_b(n, {})
        assert val_a == val_b, f"Mismatch at n={n}"
        print(f"n={n:2d} | fib(n)={val_a:<10d} | Calls A={calls_a:<8d} | Calls B={calls_b:<4d}")
    print("-> Verification Passed! Both algorithms yield identical values.\n")

# -------------------------------------------------------------
# Part 2: Experiments
# -------------------------------------------------------------

def run_experiments():
    print("--- Algorithm A Experiments ---")
    results_a = []
    for n in [5, 10, 15, 20, 25, 30, 35]:
        global calls_a
        calls_a = 0
        start = time.perf_counter()
        val = fib_a(n)
        elapsed = time.perf_counter() - start
        results_a.append((n, calls_a, elapsed))
        print(f"n = {n:2d} | Calls = {calls_a:10d} | Time = {elapsed:.6f}s")
        if elapsed > 60:
            print("Run took longer than 60 seconds. Stopping Algorithm A.")
            break

    print("\n--- Algorithm B Experiments ---")
    results_b = []
    # Set higher recursion limit for B up to 1000
    sys.setrecursionlimit(3000)
    for n in [10, 50, 100, 200, 500, 1000]:
        global calls_b
        calls_b = 0
        fibtable = {}
        start = time.perf_counter()
        val = fib_b(n, fibtable)
        elapsed = time.perf_counter() - start
        results_b.append((n, calls_b, elapsed))
        print(f"n = {n:4d} | Calls = {calls_b:10d} | Time = {elapsed:.6f}s")

    return results_a, results_b

# -------------------------------------------------------------
# Part 4: Fixes for Recursion Limit & Iterative Fibonacci
# -------------------------------------------------------------

def fib_b_iterative(n):
    """Fix 2: Iterative Bottom-Up Approach (O(n) time, O(1) space)"""
    if n == 0 or n == 1:
        return n
    prev2, prev1 = 0, 1
    for _ in range(2, n + 1):
        curr = prev1 + prev2
        prev2, prev1 = prev1, curr
    return prev1

if __name__ == "__main__":
    verify_correctness()
    run_experiments()
