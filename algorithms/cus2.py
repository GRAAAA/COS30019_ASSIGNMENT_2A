"""
cus2.py — Custom Informed Search Strategy 2 (CUS2)

TO BE IMPLEMENTED BY TEAMMATE.

Requirements (per spec):
    - Must be an *informed* method.
    - Must find a shortest path (with least moves / lowest cost) to the goal.
    - Must use some form of heuristic to guide the search.

Suggestions: Bidirectional A*, Weighted A* (f = g + w*h, w > 1), or IDA*.

Tiebreaking (per spec):
    When multiple neighbours have equal priority, expand in ascending node ID order.
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


def cus2(graph, coordinates, origin, destinations):
    raise NotImplementedError("CUS2 is not yet implemented.")
