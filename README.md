# COS30019 Assignment 2A — Route Finding Search

## Team Members
| Name | Student ID | Algorithms |
|------|------------|------------|
| Shania Serani | 102770855 | DFS, BFS, |
| Changhyeon AN | 102783073 | GBFS, A* CUS1, Testing|
| Kai Shuen | 104400549  |, CUS2 , Parser|


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
- To check how the graph is generate, type pip install matloblib in the terminal of the generate_graph.py

---

## How to Run
To run the tests in this project, execute the following command in a terminal from the project root directory (the file path)
Example: C:\Users\User\Documents\GitHub\COS30019_ASSIGNMENT_2A
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

### DFS (Depth-First Search)

Type: Uniformed
Strategy: Explores as deep as possible along a branch before backtracking
Data Structure: Stack (LIFO)
Evaluation: No cost or heuristic — purely structural traversal
Complete: Yes — if graph is finite and uses explored set
Optimal: No — may return a longer path than necessary
Space: O(b × m) — stores only current path and siblings (memory efficient)
Behavior: Can quickly find a solution in deep graphs but may get stuck exploring long incorrect paths first

### BFS (BReadth-First Search)
Type: Uninformed
Strategy: Explores all nodes at the current depth before moving deeper
Data Structure: Queue (FIFO)
Evaluation: No cost or heuristic — level-order traversal
Complete: Yes — will find a solution if one exists
Optimal: Yes — guarantees shortest path in terms of number of edges (unit cost)
Space: O(b^d) — stores all nodes at the current level (memory intensive)
Behavior: Always finds the shallowest goal first but can consume large memory for wide graphs
---

----

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
