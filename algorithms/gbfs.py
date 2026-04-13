import math
import heapq


def euclidean_distance(coord1, coord2):
    """Calculate Euclidean distance between two (x, y) coordinate tuples."""
    return math.sqrt((coord1[0] - coord2[0]) ** 2 + (coord1[1] - coord2[1]) ** 2)


def heuristic(node_id, destinations, coordinates):
    """
    Heuristic: minimum Euclidean distance from current node to any destination.
    Used by both GBFS and A*.
    """
    node_coord = coordinates[node_id]
    return min(euclidean_distance(node_coord, coordinates[d]) for d in destinations)


def gbfs(graph, coordinates, origin, destinations):
    """
    Greedy Best-First Search (GBFS).

    Evaluation function: f(n) = h(n)
        - h(n) = Euclidean distance from n to the nearest destination node
        - Does NOT consider cost to reach n (g(n) is ignored)

    Tiebreaking rules (per spec):
        1. Smaller node ID is expanded first when h values are equal.
        2. Among nodes with the same h and same ID order, earlier-added nodes go first (FIFO).

    Args:
        graph       : dict { node_id: [(neighbour_id, edge_cost), ...] }
        coordinates : dict { node_id: (x, y) }
        origin      : int
        destinations: list of int

    Returns:
        (goal_node, nodes_created, path_list)
        or (None, nodes_created, []) if no path found
    """
    dest_set = set(destinations)

    # Priority queue entries: (h_value, insertion_order, node_id, path_so_far)
    # insertion_order ensures FIFO tiebreaking when h and node_id are equal.
    counter = 0  # monotonically increasing insertion counter

    start_h = heuristic(origin, destinations, coordinates)
    # heap: (h, node_id, insertion_order, path)
    # node_id as second key enforces ascending-node tiebreak before insertion order
    heap = [(start_h, origin, counter, [origin])]
    heapq.heapify(heap)

    visited = set()
    nodes_created = 1  # the start node counts

    while heap:
        h_val, current, _, path = heapq.heappop(heap)

        # Skip already-expanded nodes
        if current in visited:
            continue
        visited.add(current)

        # Goal check
        if current in dest_set:
            return current, nodes_created, path

        # Expand neighbours — sort by node ID ascending for deterministic ordering
        neighbours = sorted(graph.get(current, []), key=lambda x: x[0])

        for neighbour, _cost in neighbours:
            if neighbour not in visited:
                counter += 1
                nodes_created += 1
                neighbour_h = heuristic(neighbour, destinations, coordinates)
                heapq.heappush(heap, (neighbour_h, neighbour, counter, path + [neighbour]))

    # No path found
    return None, nodes_created, []
