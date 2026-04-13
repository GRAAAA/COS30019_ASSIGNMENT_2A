"""
CUS1 — Iterative Deepening Depth-First Search (IDDFS)

Why IDDFS for CUS1?
--------------------
The spec requires CUS1 to be an *uninformed* method. IDDFS is a classic
uninformed algorithm that combines the space efficiency of DFS with the
completeness (and level-order optimality in terms of fewest edges) of BFS.

Properties:
    - Complete      : Yes — will always find a solution if one exists
    - Optimal       : Yes in terms of number of edges (fewest hops), not edge cost
    - Time          : O(b^d) where b = branching factor, d = depth of shallowest goal
    - Space         : O(b*d) — much better than BFS which uses O(b^d) space

How it works:
    1. Run DFS with a depth limit of 0, then 1, then 2, ... increasing each time.
    2. If DFS finds the goal within limit, return it.
    3. If DFS exhausts the limit without finding goal, increase limit and retry.
    4. Because we restart each iteration, we explore shallower solutions first,
       guaranteeing the first solution found has the fewest hops from origin.

Tiebreaking (per spec):
    When multiple neighbours exist, expand in ascending node ID order.
    Within the same depth-limited DFS pass, this naturally follows insertion order.
"""


def _depth_limited_dfs(graph, current, dest_set, depth_limit, path, visited, nodes_created_ref):
    """
    Recursive depth-limited DFS helper.

    Args:
        graph             : adjacency dict
        current           : current node being explored
        dest_set          : set of destination node IDs
        depth_limit       : max depth allowed from this point
        path              : path taken so far (list of node IDs)
        visited           : set of nodes already on the current path (cycle prevention)
        nodes_created_ref : list of length 1 used as mutable int counter

    Returns:
        (goal_node, path_list) if found, else (None, [])
    """
    # Goal check
    if current in dest_set:
        return current, path

    # Depth exhausted
    if depth_limit == 0:
        return None, []

    # Expand neighbours in ascending node ID order (tiebreak rule)
    neighbours = sorted(graph.get(current, []), key=lambda x: x[0])

    for neighbour, _cost in neighbours:
        if neighbour not in visited:
            nodes_created_ref[0] += 1
            visited.add(neighbour)
            result, result_path = _depth_limited_dfs(
                graph, neighbour, dest_set,
                depth_limit - 1,
                path + [neighbour],
                visited,
                nodes_created_ref
            )
            if result is not None:
                return result, result_path
            visited.remove(neighbour)  # backtrack

    return None, []


def cus1(graph, coordinates, origin, destinations):
    """
    CUS1: Iterative Deepening Depth-First Search (IDDFS).

    Uninformed search — uses no heuristic, only graph structure and edge existence.

    Args:
        graph       : dict { node_id: [(neighbour_id, edge_cost), ...] }
        coordinates : dict { node_id: (x, y) }  (not used — uninformed)
        origin      : int
        destinations: list of int

    Returns:
        (goal_node, nodes_created, path_list)
        or (None, nodes_created, []) if no path found
    """
    dest_set = set(destinations)

    # Edge case: origin is already a destination
    if origin in dest_set:
        return origin, 1, [origin]

    # Max depth to try = number of nodes (any deeper must contain a cycle, no new paths)
    max_depth = len(graph)

    # nodes_created_ref: mutable counter shared across recursive calls
    # We use a list so the recursive helper can modify it
    nodes_created_ref = [1]  # origin counts as 1

    for depth_limit in range(1, max_depth + 1):
        visited = {origin}
        goal, path = _depth_limited_dfs(
            graph, origin, dest_set,
            depth_limit,
            [origin],
            visited,
            nodes_created_ref
        )
        if goal is not None:
            return goal, nodes_created_ref[0], path

    # No path found within max depth
    return None, nodes_created_ref[0], []
