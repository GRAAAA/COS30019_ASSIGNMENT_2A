import math
import heapq


def euclidean_distance(coord1, coord2):
    """Calculate Euclidean distance between two (x, y) coordinate tuples."""
    return math.sqrt((coord1[0] - coord2[0]) ** 2 + (coord1[1] - coord2[1]) ** 2)


def heuristic(node_id, destinations, coordinates):
    """
    Heuristic: minimum Euclidean distance from current node to any destination.
    Euclidean distance is admissible (never overestimates) so A* remains optimal.
    """
    node_coord = coordinates[node_id]
    return min(euclidean_distance(node_coord, coordinates[d]) for d in destinations)


def astar(graph, coordinates, origin, destinations):
    """
    A* Search (AS).

    Evaluation function: f(n) = g(n) + h(n)
        - g(n) = actual cumulative cost from origin to n
        - h(n) = Euclidean distance from n to the nearest destination (admissible heuristic)

    Because h(n) is admissible, A* is guaranteed to find the optimal (lowest-cost) path.

    Tiebreaking rules (per spec):
        1. Lower f(n) is always preferred.
        2. Equal f: smaller node ID expanded first.
        3. Equal f and node ID: earlier-inserted node expanded first (FIFO via counter).

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

    # g_cost tracks the best known cost to reach each node
    g_cost = {origin: 0}

    counter = 0  # insertion counter for FIFO tiebreaking
    start_h = heuristic(origin, destinations, coordinates)
    start_f = 0 + start_h  # f = g + h; g=0 at origin

    # heap entries: (f, node_id, insertion_order, g, path)
    heap = [(start_f, origin, counter, 0, [origin])]
    heapq.heapify(heap)

    visited = set()
    nodes_created = 1  # origin counts as created

    while heap:
        f_val, current, _, g_val, path = heapq.heappop(heap)

        # Skip if we already found a better path to this node
        if current in visited:
            continue
        visited.add(current)

        # Goal check — on pop, guarantees optimal path (A* property)
        if current in dest_set:
            return current, nodes_created, path

        # Expand neighbours — sorted ascending by node ID for tiebreak rule
        neighbours = sorted(graph.get(current, []), key=lambda x: x[0])

        for neighbour, edge_cost in neighbours:
            if neighbour not in visited:
                tentative_g = g_val + edge_cost

                # Only push if this is a better (or first) path to neighbour
                if neighbour not in g_cost or tentative_g < g_cost[neighbour]:
                    g_cost[neighbour] = tentative_g
                    counter += 1
                    nodes_created += 1
                    neighbour_h = heuristic(neighbour, destinations, coordinates)
                    neighbour_f = tentative_g + neighbour_h
                    heapq.heappush(
                        heap,
                        (neighbour_f, neighbour, counter, tentative_g, path + [neighbour])
                    )

    # No path found
    return None, nodes_created, []
