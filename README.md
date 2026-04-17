# COS30019 Assignment 2A — Route Finding Search

## Team Members
| Name | Student ID | Algorithms |
|------|------------|------------|
| [Shania Serani] | [102770855] | DFS, BFS, Parser |
| [Member B] | [ID] | GBFS, A* (AS) |
| [Member C] | [ID] | CUS1 (IDDFS), CUS2 |
| [Member D] | [ID] | Tests, Report, Integration |

> Give tutor/lecturer **read-only** access to this repository.

---

## Project Structure

```
search-assignment/
├── search.py                  ← Main entry point (run this)
├── parser.py                  ← Problem file parser
├── algorithms/
│   ├── __init__.py
│   ├── dfs.py                 ← Depth-First Search
│   ├── bfs.py                 ← Breadth-First Search
│   ├── gbfs.py                ← Greedy Best-First Search  ✅
│   ├── astar.py               ← A* Search                 ✅
│   ├── cus1.py                ← IDDFS (Custom uninformed) ✅
│   └── cus2.py                ← Custom informed (stub)
├── tests/
│   ├── run_tests.py           ← Automated test runner
│   └── test_cases/
│       ├── PathFinder-test-1.txt
│       └── ...                ← Add more test files here
└── report/
    └── TeamID.pdf             ← Final report (to be added)
```

---

## Requirements

- Python 3.8+
- No external libraries required for Part A

---

## How to Run

```
python search.py <filename> <method>
```

**Methods:** `DFS`, `BFS`, `GBFS`, `AS`, `CUS1`, `CUS2`

**Example:**
```
python search.py tests/test_cases/PathFinder-test-1.txt GBFS
python search.py tests/test_cases/PathFinder-test-1.txt AS
python search.py tests/test_cases/PathFinder-test-1.txt CUS1
```

**Expected output format:**
```
PathFinder-test-1.txt GBFS
5 6
2 -> 3 -> 5
```

If no path exists:
```
PathFinder-test-1.txt DFS
No path found
```

---

## Running All Tests

```
python tests/run_tests.py
```

---

## Algorithm Notes

### GBFS (Greedy Best-First Search)
- **Type:** Informed
- **Heuristic:** Euclidean distance to nearest destination
- **Evaluation:** `f(n) = h(n)` only — ignores path cost
- **Not guaranteed** to find optimal path

### A\* (AS)
- **Type:** Informed
- **Heuristic:** Euclidean distance to nearest destination (admissible)
- **Evaluation:** `f(n) = g(n) + h(n)`
- **Guaranteed optimal** because heuristic never overestimates

### CUS1 — Iterative Deepening DFS (IDDFS)
- **Type:** Uninformed
- **Strategy:** Repeatedly runs depth-limited DFS with increasing limits
- **Complete:** Yes — finds a solution if one exists
- **Optimal:** Yes in terms of fewest hops (edges traversed)
- **Space:** O(b × d) — far more memory-efficient than BFS

### Tiebreaking (all algorithms)
Per spec: when evaluation scores are equal, nodes are expanded in **ascending node ID order**, and among nodes added at the same time, in **chronological (insertion) order**. This is implemented via a `(f_value, node_id, insertion_counter)` heap key.

---

## GitHub Workflow

```
main
├── feature/dfs-bfs        ← Member A's branch
├── feature/gbfs-astar     ← Member B's branch
├── feature/cus1-cus2      ← Member C's branch
└── feature/tests-report   ← Member D's branch
```

1. Work on your feature branch
2. Open a Pull Request → `main` when done
3. At least one other member reviews before merging
4. Never commit directly to `main`
