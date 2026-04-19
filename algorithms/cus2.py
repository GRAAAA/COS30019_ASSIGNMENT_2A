# cus2.py — IDA* (CUS2)

def heuristic(node, goal, coords):
    # Compute Euclidean distance between current node and goal
    x1, y1 = coords[node]
    x2, y2 = coords[goal]
    dx = x1 - x2
    dy = y1 - y2
    return (dx * dx + dy * dy) ** 0.5


def _h_min(node, destinations, coords):
    # Return the minimum heuristic value to any destination
    return min(heuristic(node, d, coords) for d in destinations)


def cus2(graph, coordinates, origin, destinations):
    """
    IDA* search (CUS2)

    Returns:
        goal node, number of nodes generated, and the path
    """

    # Initial threshold based on heuristic from start node
    threshold = _h_min(origin, destinations, coordinates)

    total_nodes_generated = 0

    while True:
        path = [origin]

        # Perform depth-limited search with current threshold
        result, next_threshold, nodes_generated, final_path = _search(
            path, 0, threshold, destinations, graph, coordinates
        )

        # Accumulate generated nodes across iterations
        total_nodes_generated += nodes_generated

        # Goal found
        if result == "FOUND":
            return final_path[-1], total_nodes_generated, final_path

        # No solution exists
        if next_threshold == float("inf"):
            return None, total_nodes_generated, []

        # Increase threshold for next iteration
        threshold = next_threshold


def _search(path, g, threshold, destinations, graph, coords):
    node = path[-1]

    # Compute f = g + h
    h = _h_min(node, destinations, coords)
    f = g + h

    # Prune if f exceeds current threshold
    if f > threshold:
        return "NOT_FOUND", f, 0, None

    # Goal test
    if node in destinations:
        return "FOUND", f, 0, path.copy()

    min_threshold = float("inf")
    nodes_generated = 0

    # Expand neighbors in ascending order (NOTE 2 requirement)
    neighbors = sorted(graph.get(node, []), key=lambda x: x[0])

    for neighbor, cost in neighbors:
        if neighbor not in path:  # Avoid cycles
            new_path = path + [neighbor]

            result, temp, count, final_path = _search(
                new_path,
                g + cost,
                threshold,
                destinations,
                graph,
                coords
            )

            # Count generated nodes
            nodes_generated += count + 1

            if result == "FOUND":
                return "FOUND", temp, nodes_generated, final_path

            # Track smallest f that exceeded threshold
            if temp < min_threshold:
                min_threshold = temp

    return "NOT_FOUND", min_threshold, nodes_generated, None




