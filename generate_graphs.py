"""
generate_graphs.py — Renders graph diagrams for all 15 test cases.

For each test case, produces one PNG per algorithm showing:
  - Nodes at their (x, y) coordinates
  - All directed edges (grey arrows)
  - The solution path highlighted in colour per algorithm
  - Origin node (green), destination nodes (red/orange), path nodes (blue)

Output: tests/graph_images/TCxx_METHOD.png
"""

import os, math
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyArrowPatch

OUT_DIR = 'tests/graph_images'
os.makedirs(OUT_DIR, exist_ok=True)

# ── Colour scheme per method ──────────────────────────────────────────────────
METHOD_COLOR = {
    'DFS':  '#E74C3C',
    'BFS':  '#2980B9',
    'GBFS': '#8E44AD',
    'AS':   '#27AE60',
    'CUS1': '#D35400',
    'CUS2': '#16A085',
}

# ── Test case definitions ─────────────────────────────────────────────────────
TESTS = {
'TC01': {
    'title': 'TC01: Original Sample',
    'nodes': {1:(4,1),2:(2,2),3:(4,4),4:(6,3),5:(5,6),6:(7,5)},
    'edges': [(2,1,4),(3,1,5),(1,3,5),(2,3,4),(3,2,5),(4,1,6),(1,4,6),
              (4,3,5),(3,5,6),(5,3,6),(4,5,7),(5,4,8),(6,3,7),(3,6,7)],
    'origin': 2, 'destinations': [5,4],
    'paths': {
        'DFS': [2,1,3,5], 'BFS': [2,1,4], 'GBFS': [2,3,5],
        'AS':  [2,1,4],   'CUS1':[2,1,4], 'CUS2': [2,1,4],
    },
},
'TC02': {
    'title': 'TC02: Origin Is Destination',
    'nodes': {1:(1,1),2:(5,5),3:(8,2)},
    'edges': [(1,2,7),(2,3,5)],
    'origin': 1, 'destinations': [1],
    'paths': {m:[1] for m in ['DFS','BFS','GBFS','AS','CUS1','CUS2']},
},
'TC03': {
    'title': 'TC03: No Path Exists',
    'nodes': {1:(1,1),2:(3,3),3:(7,7),4:(9,9)},
    'edges': [(3,4,3)],
    'origin': 1, 'destinations': [4],
    'paths': {m:[] for m in ['DFS','BFS','GBFS','AS','CUS1','CUS2']},
},
'TC04': {
    'title': 'TC04: Two-Node Direct',
    'nodes': {1:(0,0),2:(3,4)},
    'edges': [(1,2,5)],
    'origin': 1, 'destinations': [2],
    'paths': {m:[1,2] for m in ['DFS','BFS','GBFS','AS','CUS1','CUS2']},
},
'TC05': {
    'title': 'TC05: GBFS vs A*',
    'nodes': {1:(0,0),2:(1,0),3:(0,1),4:(1,1)},
    'edges': [(1,2,1),(2,4,10),(1,3,1),(3,4,1)],
    'origin': 1, 'destinations': [4],
    'paths': {
        'DFS': [1,2,4], 'BFS': [1,2,4], 'GBFS': [1,2,4],
        'AS':  [1,3,4], 'CUS1':[1,2,4], 'CUS2': [1,3,4],
    },
},
'TC06': {
    'title': 'TC06: Multiple Destinations',
    'nodes': {1:(5,5),2:(1,1),3:(9,1),4:(5,9),5:(2,5),6:(8,5)},
    'edges': [(1,2,6),(1,3,6),(1,4,5),(1,5,4),(1,6,4),(5,2,2),(6,3,2)],
    'origin': 1, 'destinations': [2,3,4],
    'paths': {
        'DFS': [1,2], 'BFS': [1,2], 'GBFS': [1,2],
        'AS':  [1,4], 'CUS1':[1,2], 'CUS2': [1,4],
    },
},
'TC07': {
    'title': 'TC07: Linear Chain',
    'nodes': {1:(0,0),2:(2,0),3:(4,0),4:(6,0),5:(8,0)},
    'edges': [(1,2,2),(2,3,2),(3,4,2),(4,5,2)],
    'origin': 1, 'destinations': [5],
    'paths': {m:[1,2,3,4,5] for m in ['DFS','BFS','GBFS','AS','CUS1','CUS2']},
},
'TC08': {
    'title': 'TC08: Directed Trap',
    'nodes': {1:(0,5),2:(3,5),3:(6,5),4:(3,2),5:(6,2)},
    'edges': [(1,2,3),(2,3,3),(2,4,4),(4,5,3),(3,5,3)],
    'origin': 1, 'destinations': [5],
    'paths': {m:[1,2,3,5] for m in ['DFS','BFS','GBFS','AS','CUS1','CUS2']},
},
'TC09': {
    'title': 'TC09: Dense Graph',
    'nodes': {1:(3,3),2:(1,5),3:(5,5),4:(1,1),5:(5,1),6:(3,7)},
    'edges': [(1,2,3),(1,3,3),(1,4,3),(1,5,3),(2,3,4),(2,4,3),(2,6,3),
              (3,5,3),(3,6,3),(4,5,4),(5,6,5)],
    'origin': 1, 'destinations': [6],
    'paths': {
        'DFS': [1,2,3,5,6], 'BFS': [1,2,6], 'GBFS': [1,2,6],
        'AS':  [1,2,6],     'CUS1':[1,2,6], 'CUS2': [1,2,6],
    },
},
'TC10': {
    'title': 'TC10: Large Graph',
    'nodes': {1:(0,0),2:(2,3),3:(4,1),4:(6,4),5:(8,2),6:(3,6),
              7:(7,6),8:(5,8),9:(1,8),10:(9,8)},
    'edges': [(1,2,4),(1,3,4),(2,4,4),(2,6,6),(3,4,4),(3,5,5),
              (4,6,4),(4,7,4),(5,7,5),(6,8,4),(6,9,5),(7,8,4),(7,10,4),(8,10,4)],
    'origin': 1, 'destinations': [10],
    'paths': {
        'DFS': [1,2,4,6,8,10], 'BFS': [1,2,4,7,10], 'GBFS': [1,2,4,7,10],
        'AS':  [1,2,4,7,10],   'CUS1':[1,2,4,7,10], 'CUS2': [1,2,4,7,10],
    },
},
'TC11': {
    'title': 'TC11: Star Topology',
    'nodes': {1:(5,5),2:(5,9),3:(9,5),4:(5,1),5:(1,5),6:(8,8)},
    'edges': [(1,2,4),(1,3,4),(1,4,4),(1,5,4),(1,6,5)],
    'origin': 1, 'destinations': [6],
    'paths': {m:[1,6] for m in ['DFS','BFS','GBFS','AS','CUS1','CUS2']},
},
'TC12': {
    'title': 'TC12: Deep Goal',
    'nodes': {1:(0,0),2:(2,1),3:(4,0),4:(2,3),5:(4,4),6:(6,3),7:(8,4),8:(6,6),9:(8,8)},
    'edges': [(1,2,3),(1,3,4),(2,4,4),(3,4,3),(3,6,5),(4,5,3),(5,6,3),(5,8,5),
              (6,7,3),(7,8,3),(7,9,4),(8,9,3)],
    'origin': 1, 'destinations': [9],
    'paths': {
        'DFS': [1,2,4,5,6,7,8,9], 'BFS': [1,3,6,7,9], 'GBFS': [1,3,6,7,9],
        'AS':  [1,3,6,7,9],       'CUS1':[1,3,6,7,9], 'CUS2': [1,3,6,7,9],
    },
},
'TC13': {
    'title': 'TC13: Tiebreaking',
    'nodes': {1:(0,0),2:(4,0),3:(4,4),4:(0,4),5:(2,2)},
    'edges': [(1,2,4),(1,4,4),(2,5,3),(4,5,3),(2,3,4),(4,3,4)],
    'origin': 1, 'destinations': [5],
    'paths': {m:[1,2,5] for m in ['DFS','BFS','GBFS','AS','CUS1','CUS2']},
},
'TC14': {
    'title': 'TC14: Hop vs Cost',
    'nodes': {1:(0,0),2:(10,0),3:(3,0),4:(6,0)},
    'edges': [(1,2,2),(1,3,3),(3,4,3),(4,2,3)],
    'origin': 1, 'destinations': [2],
    'paths': {m:[1,2] for m in ['DFS','BFS','GBFS','AS','CUS1','CUS2']},
},
'TC15': {
    'title': 'TC15: Partial Reachability',
    'nodes': {1:(0,0),2:(4,2),3:(8,0),4:(0,8),5:(8,8)},
    'edges': [(1,2,4),(2,3,4),(2,5,8)],
    'origin': 1, 'destinations': [3,4,5],
    'paths': {m:[1,2,3] for m in ['DFS','BFS','GBFS','AS','CUS1','CUS2']},
},
}

METHODS = ['DFS','BFS','GBFS','AS','CUS1','CUS2']


def draw_graph(tc_id, method, ax):
    tc = TESTS[tc_id]
    nodes = tc['nodes']
    edges = tc['edges']
    origin = tc['origin']
    dests = set(tc['destinations'])
    path = tc['paths'].get(method, [])
    path_set = set(zip(path, path[1:])) if len(path) > 1 else set()
    path_nodes = set(path)
    color = METHOD_COLOR[method]

    # Auto-scale coords to fit nicely
    xs = [v[0] for v in nodes.values()]
    ys = [v[1] for v in nodes.values()]
    xmin, xmax = min(xs), max(xs)
    ymin, ymax = min(ys), max(ys)
    xr = max(xmax - xmin, 1)
    yr = max(ymax - ymin, 1)

    def nx(x): return (x - xmin) / xr
    def ny(y): return (y - ymin) / yr

    pos = {n: (nx(x), ny(y)) for n, (x, y) in nodes.items()}

    ax.set_xlim(-0.15, 1.15)
    ax.set_ylim(-0.15, 1.15)
    ax.set_aspect('equal')
    ax.axis('off')

    # Draw edges
    for (frm, to, cost) in edges:
        x0, y0 = pos[frm]
        x1, y1 = pos[to]
        on_path = (frm, to) in path_set
        ec = color if on_path else '#CCCCCC'
        lw = 2.5 if on_path else 1.0
        alpha = 1.0 if on_path else 0.6
        ax.annotate('', xy=(x1, y1), xytext=(x0, y0),
                    arrowprops=dict(arrowstyle='->', color=ec, lw=lw,
                                   connectionstyle='arc3,rad=0.05'),
                    alpha=alpha)
        # Edge cost label (only on path edges)
        if on_path:
            mx, my = (x0+x1)/2, (y0+y1)/2
            ax.text(mx, my, str(cost), fontsize=6, ha='center', va='center',
                    color=color, fontweight='bold',
                    bbox=dict(boxstyle='round,pad=0.1', fc='white', ec='none', alpha=0.8))

    # Draw nodes
    for n, (x, y) in pos.items():
        if n == origin and n in dests:
            fc = '#F39C12'  # orange: both origin and destination
        elif n == origin:
            fc = '#2ECC71'  # green: origin
        elif n in dests:
            fc = '#E74C3C'  # red: destination
        elif n in path_nodes:
            fc = color
        else:
            fc = '#BDC3C7'  # grey: unvisited

        circle = plt.Circle((x, y), 0.06, color=fc, zorder=3)
        ax.add_patch(circle)
        ax.text(x, y, str(n), ha='center', va='center', fontsize=8,
                fontweight='bold', color='white', zorder=4)

    # Path label
    if path:
        pstr = ' -> '.join(str(n) for n in path)
        ax.set_title(f'{method}: {pstr}', fontsize=7, pad=4, color=color)
    else:
        ax.set_title(f'{method}: No path found', fontsize=7, pad=4, color='#999999')


def generate_combined(tc_id):
    """One image per test case with 6 subplots (one per method)."""
    tc = TESTS[tc_id]
    fig, axes = plt.subplots(2, 3, figsize=(10, 7))
    fig.suptitle(tc['title'], fontsize=11, fontweight='bold', y=1.01)
    axes_flat = axes.flatten()
    for i, method in enumerate(METHODS):
        draw_graph(tc_id, method, axes_flat[i])
    plt.tight_layout()
    out = os.path.join(OUT_DIR, f'{tc_id}_all.png')
    plt.savefig(out, dpi=110, bbox_inches='tight')
    plt.close()
    print(f'  Saved {out}')


def generate_single(tc_id, method):
    """One small image per (tc, method) pair."""
    fig, ax = plt.subplots(figsize=(3.2, 2.8))
    draw_graph(tc_id, method, ax)
    plt.tight_layout()
    out = os.path.join(OUT_DIR, f'{tc_id}_{method}.png')
    plt.savefig(out, dpi=110, bbox_inches='tight')
    plt.close()


if __name__ == '__main__':
    for tc_id in TESTS:
        print(f'Generating {tc_id}...')
        generate_combined(tc_id)
        for m in METHODS:
            generate_single(tc_id, m)
    print('Done.')
