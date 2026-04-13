"""
search.py — Main entry point for the Route Finding search program.

Usage:
    python search.py <filename> <method>

Supported methods:
    DFS   — Depth-First Search          (uninformed)
    BFS   — Breadth-First Search        (uninformed)
    GBFS  — Greedy Best-First Search    (informed)
    AS    — A* Search                   (informed)
    CUS1  — Iterative Deepening DFS     (uninformed, custom)
    CUS2  — Custom informed search      (informed, custom)

Output format (goal found):
    <filename> <method>
    <goal> <number_of_nodes>
    <path>

Output format (no path):
    <filename> <method>
    No path found
"""

import sys
import os

from parser import parse_file

from algorithms.dfs import dfs
from algorithms.bfs import bfs
from algorithms.gbfs import gbfs
from algorithms.astar import astar
from algorithms.cus1 import cus1
from algorithms.cus2 import cus2


SUPPORTED_METHODS = {
    'DFS':  dfs,
    'BFS':  bfs,
    'GBFS': gbfs,
    'AS':   astar,
    'CUS1': cus1,
    'CUS2': cus2,
}


def format_path(path):
    """Convert a list of node IDs to the required arrow-separated string."""
    return ' -> '.join(str(n) for n in path)


def main():
    if len(sys.argv) != 3:
        print("Usage: python search.py <filename> <method>")
        print(f"Methods: {', '.join(SUPPORTED_METHODS.keys())}")
        sys.exit(1)

    filepath = sys.argv[1]
    method = sys.argv[2].upper()

    if not os.path.isfile(filepath):
        print(f"Error: File '{filepath}' not found.")
        sys.exit(1)

    if method not in SUPPORTED_METHODS:
        print(f"Error: Unknown method '{method}'.")
        print(f"Supported methods: {', '.join(SUPPORTED_METHODS.keys())}")
        sys.exit(1)

    graph, coordinates, origin, destinations = parse_file(filepath)

    search_fn = SUPPORTED_METHODS[method]

    try:
        goal, nodes_created, path = search_fn(graph, coordinates, origin, destinations)
    except NotImplementedError:
        print(f"Error: {method} has not been implemented yet.")
        sys.exit(1)

    filename = os.path.basename(filepath)
    print(f"{filename} {method}")

    if goal is not None:
        print(f"{goal} {nodes_created}")
        print(format_path(path))
    else:
        print("No path found")


if __name__ == '__main__':
    main()
