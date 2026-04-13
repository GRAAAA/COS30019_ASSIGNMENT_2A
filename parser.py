"""
parser.py — Parses the route-finding problem text file format.

Expected file format:
    Nodes:
    1: (4,1)
    ...
    Edges:
    (2,1): 4
    ...
    Origin:
    2
    Destinations:
    5; 4
"""

import re


def parse_file(filepath):
    """
    Parse a problem file and return graph components.

    Returns:
        graph       : dict { node_id (int): [(neighbour_id (int), cost (int/float)), ...] }
        coordinates : dict { node_id (int): (x (int), y (int)) }
        origin      : int
        destinations: list of int
    """
    with open(filepath, 'r') as f:
        content = f.read()

    # Split into sections by keywords
    sections = re.split(r'\b(Nodes|Edges|Origin|Destinations)\s*:', content)

    # Build a dict of section_name -> raw text
    section_map = {}
    for i in range(1, len(sections), 2):
        section_map[sections[i].strip()] = sections[i + 1].strip()

    # --- Parse Nodes ---
    coordinates = {}
    for line in section_map['Nodes'].splitlines():
        line = line.strip()
        if not line:
            continue
        # Format: "1: (4,1)"
        match = re.match(r'(\d+)\s*:\s*\((\d+)\s*,\s*(\d+)\)', line)
        if match:
            node_id = int(match.group(1))
            x = int(match.group(2))
            y = int(match.group(3))
            coordinates[node_id] = (x, y)

    # --- Parse Edges ---
    # Initialise adjacency list for every known node
    graph = {node_id: [] for node_id in coordinates}

    for line in section_map['Edges'].splitlines():
        line = line.strip()
        if not line:
            continue
        # Format: "(2,1): 4"  means directed edge from 2 -> 1 with cost 4
        match = re.match(r'\((\d+)\s*,\s*(\d+)\)\s*:\s*(\d+(?:\.\d+)?)', line)
        if match:
            from_node = int(match.group(1))
            to_node = int(match.group(2))
            cost = float(match.group(3))
            # Use int cost if it's a whole number (cleaner output)
            cost = int(cost) if cost == int(cost) else cost
            graph[from_node].append((to_node, cost))

    # --- Parse Origin ---
    origin = int(section_map['Origin'].strip())

    # --- Parse Destinations ---
    dest_raw = section_map['Destinations'].strip()
    destinations = [int(d.strip()) for d in dest_raw.split(';') if d.strip()]

    return graph, coordinates, origin, destinations
