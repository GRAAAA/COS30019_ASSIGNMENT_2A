
"""
bfs.py — Breadth-First Search (BFS)



Goal:
    Find a path from the origin node to ANY one of the destination nodes.

Core Idea:
    Explore all nodes level by level (closest nodes first).

Data Structure:
    Queue (FIFO — First In, First Out)

Step-by-step:
    1. Enqueue the origin node.
    2. Repeat until queue is empty:
        a. Dequeue the front node (current node).
        b. If already explored → skip.
        c. Mark node as explored.
        d. If node is a destination → return result.
        e. Expand neighbours:
            - Sort neighbours in ASCENDING order
            - Enqueue them

Important Rules from Spec:
    - Directed graph → only follow given edges
    - Goal test happens when node is DEQUEUED (expanded)
    - Count nodes when ENQUEUED
    - Expand nodes in ASCENDING node ID order
    - Maintain chronological order → queue naturally does this

Why BFS is optimal (in steps)?
    It explores all nodes at depth d before going to depth d+1,
    so the first goal found is the shortest path (in number of edges).

    

Complexity:
    Time  : O(b^d)
    Space : O(b^d)


"""

from collections import deque

# ── Main algorithm 

def bfs(graph, coordinates, origin, destinations):
    dest_set = set(destinations)

    # Early exit
    if origin in dest_set:
        return origin, 1, [origin]

    # Queue (FIFO)
    queue = deque([(origin, [origin])])

    explored = set()
    nodes_created = 1

    while queue:
        current, path = queue.popleft()

        if current in explored:
            continue

        explored.add(current)

        # Goal test on expansion
        if current in dest_set:
            return current, nodes_created, path

        # Sort ASC → ensures correct expansion order
        neighbours = sorted(
            graph.get(current, []),
            key=lambda edge: edge[0]
        )

        for neighbour_id, _ in neighbours:
            if neighbour_id not in explored:
                nodes_created += 1
                queue.append((neighbour_id, path + [neighbour_id]))

    return None, nodes_created, []

