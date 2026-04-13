"""
bfs.py — Breadth-First Search (BFS)

TO BE IMPLEMENTED BY TEAMMATE.

Tiebreaking (per spec):
    When multiple neighbours exist, expand in ascending node ID order.
    Among equal nodes on different branches, expand in chronological (insertion) order.

Args:
    graph       : dict { node_id: [(neighbour_id, edge_cost), ...] }
    coordinates : dict { node_id: (x, y) }
    origin      : int
    destinations: list of int

Returns:
    (goal_node, nodes_created, path_list)
    or (None, nodes_created, []) if no path found
"""


def bfs(graph, coordinates, origin, destinations):
    raise NotImplementedError("BFS is not yet implemented.")
