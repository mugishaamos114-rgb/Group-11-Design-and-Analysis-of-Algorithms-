# Algorithm Explorer — Group 11


## Team
ROCKDIT MINYIEL AYUAK //
ANYANG JAMES GAI //
MUGISHA AMOS ISRAEL //
WANI SAMSON WILSON //
ESILU BRIAN JOEL //
MUSASIZI JIMMY ERNEST //
ONGAR SOLOMON //

An interactive desktop application for **CSC2107 Design and Analysis of Algorithms**. A user enters their own input, the
algorithm runs in the back end, and the interface shows the result, the steps taken, the
number of operations and the running time.

**Language:** Python 3 (3.8 or newer, 3.11+ recommended) · **Interface:** Tkinter (built into Python)

| Module | What it does |
|---|---|
| A · Recursion Lab | Fibonacci (naive, memoized, bottom-up), factorial (recursive, iterative), animated Tower of Hanoi with user-chosen source/destination/auxiliary pegs, Start / Pause / Step / Reset and speed control |
| B · Data Structures Lab | Array stack, linear and circular queue (with a "false full" demo), singly and doubly linked lists (insert/delete at beginning, end, before, after; search; forward/backward display), balanced-bracket checker |
| C · Sorting Lab | Bubble, selection, insertion, merge sort, quicksort (first-element pivot, yellow/green partition) and randomised quicksort; step-by-step and auto-play display, comparison/swap counts, execution time, "Compare all", complexity help |
| D · Complexity Analysis | Times every sort on random, sorted and reverse-sorted input of increasing size, plots time vs n and compares with Big-O |


The benchmark writes `results/results.csv`, LaTeX tables to `report/tables/` and charts to
`report/figures/`. `python tools/take_screenshots.py` regenerates the screenshots in `report/screenshots/`.

## Project structure

```
main.py                  start the application
backend/                 algorithms and data structures (no Tkinter - testable on their own)
  core.py                DynamicArray, timer, input validation, DSError
  recursion.py           Module A
  stack.py, queues.py, linked_lists.py, brackets.py   Module B
  sorting.py             Module C
  analysis.py            Module D
frontend/                Tkinter screens (one file per module) + theme and widgets
tests/test_backend.py    unit tests
benchmark/run_benchmark.py   Module D experiment for the report
tools/check_rules.py     strict-rule checker
report/                  Overleaf report (main.tex, tables, figures, screenshots)
```

## Strict Python rules

All algorithms and data structures are written from first principles. In `backend/`:

- Python lists are only used as fixed-size arrays (`[None] * capacity`) accessed by index.
- No `sort()`, `sorted()`, `min()`, `max()`, `bisect`, `heapq`, `collections.deque`, `queue.Queue`,
  `list.index()`, `in` for searching, `list.insert()`, `list.pop(i)`, `del`, `list.reverse()`,
  slicing or list concatenation.
- Growable sequences use our own `DynamicArray`; linked lists use our own `SinglyNode` / `DoublyNode`
  objects with explicit `next` / `prev` references.

`tools/check_rules.py` checks this automatically.



CSC2107 Group 11.
