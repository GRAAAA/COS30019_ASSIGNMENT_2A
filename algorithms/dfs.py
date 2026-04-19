"""
dfs.py — Depth-First Search (DFS)



Goal:
    Find a path from the origin node to ANY one of the destination nodes.

Core Idea:
    Always go as deep as possible along one branch before backtracking.

Data Structure:
    Stack (LIFO — Last In, First Out)

Step-by-step:
    1. Push the origin node onto the stack.
    2. Repeat until stack is empty:
        a. Pop the top node (current node).
        b. If already explored → skip (lazy deletion).
        c. Mark node as explored.
        d. If node is a destination → return result.
        e. Expand neighbours:
            - Sort neighbours in DESCENDING order
            - Push them onto the stack
              (this ensures ASCENDING expansion order when popped)

Important Rules from Spec:
    - Directed graph → only follow given edges
    - Goal test happens when node is POPPED (expanded)
    - Count nodes when PUSHED to stack
    - Expand nodes in ASCENDING node ID order

Why reverse sorting?
    Stack pops last-added node first → reversing ensures smallest node expands first.

Complexity:
    Time  : O(b^m)
    Space : O(b*m)


"""

# ── Main algorithm 

def dfs(graph, coordinates, origin, destinations):
    dest_set = set(destinations)

    # Early exit
    if origin in dest_set:
        return origin, 1, [origin]

    # Stack (LIFO)
    stack = [(origin, [origin])]

    explored = set()
    nodes_created = 1

    while stack:
        current, path = stack.pop()

        if current in explored:
            continue

        explored.add(current)

        # Goal test on expansion
        if current in dest_set:
            return current, nodes_created, path

        # Sort DESC → ensures ASC order when popping
        neighbours = sorted(
            graph.get(current, []),
            key=lambda edge: edge[0],
            reverse=True
        )

        for neighbour_id, _ in neighbours:
            if neighbour_id not in explored:
                nodes_created += 1
                stack.append((neighbour_id, path + [neighbour_id]))

    return None, nodes_created, []
