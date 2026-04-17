"""
run_tests.py — Automated test runner for all search algorithms.

Usage:
    python tests/run_tests.py

Runs every .txt file in tests/test_cases/ against all 6 methods and
prints a pass/fail summary table.

Add expected outputs to the EXPECTED dict below to enable assertion checking.
If no expected output is set for a case, the result is printed but not asserted.
"""

import subprocess
import os
import sys

# Directory containing test case .txt files
TEST_DIR = os.path.join(os.path.dirname(__file__), 'test_cases')
SEARCH_SCRIPT = os.path.join(os.path.dirname(__file__), '..', 'search.py')

METHODS = ['DFS', 'BFS', 'GBFS', 'AS', 'CUS1', 'CUS2']

# Optional: define expected outputs for specific (filename, method) pairs.
# Format: { ('test_file.txt', 'METHOD'): ('goal', 'path') }
# Leave empty to just print results without asserting.
EXPECTED = {
    # TC01 — original sample (6-node directed graph, 2 destinations)
    ('PathFinder-test-1.txt', 'DFS'):  ('5', '2 -> 1 -> 3 -> 5'),
    ('PathFinder-test-1.txt', 'BFS'):  ('4', '2 -> 1 -> 4'),
    ('PathFinder-test-1.txt', 'GBFS'): ('5', '2 -> 3 -> 5'),
    ('PathFinder-test-1.txt', 'AS'):   ('4', '2 -> 1 -> 4'),
    ('PathFinder-test-1.txt', 'CUS1'): ('4', '2 -> 1 -> 4'),
    ('PathFinder-test-1.txt', 'CUS2'): ('4', '2 -> 1 -> 4'),

    # TC02 — origin is already a destination (trivial early exit)
    ('TC02_origin_is_destination.txt', 'DFS'):  ('1', '1'),
    ('TC02_origin_is_destination.txt', 'BFS'):  ('1', '1'),
    ('TC02_origin_is_destination.txt', 'GBFS'): ('1', '1'),
    ('TC02_origin_is_destination.txt', 'AS'):   ('1', '1'),
    ('TC02_origin_is_destination.txt', 'CUS1'): ('1', '1'),
    ('TC02_origin_is_destination.txt', 'CUS2'): ('1', '1'),

    # TC03 — no path exists (disconnected: origin has no outgoing edges to destination area)
    ('TC03_no_path.txt', 'DFS'):  ('No path found', ''),
    ('TC03_no_path.txt', 'BFS'):  ('No path found', ''),
    ('TC03_no_path.txt', 'GBFS'): ('No path found', ''),
    ('TC03_no_path.txt', 'AS'):   ('No path found', ''),
    ('TC03_no_path.txt', 'CUS1'): ('No path found', ''),
    ('TC03_no_path.txt', 'CUS2'): ('No path found', ''),

    # TC04 — two nodes, single direct edge (simplest possible path)
    ('TC04_two_node_direct.txt', 'DFS'):  ('2', '1 -> 2'),
    ('TC04_two_node_direct.txt', 'BFS'):  ('2', '1 -> 2'),
    ('TC04_two_node_direct.txt', 'GBFS'): ('2', '1 -> 2'),
    ('TC04_two_node_direct.txt', 'AS'):   ('2', '1 -> 2'),
    ('TC04_two_node_direct.txt', 'CUS1'): ('2', '1 -> 2'),
    ('TC04_two_node_direct.txt', 'CUS2'): ('2', '1 -> 2'),

    # TC05 — two paths with very different costs; GBFS picks wrong (non-optimal) path,
    #         A* and CUS2 find optimal; demonstrates GBFS vs A* trade-off
    ('TC05_gbfs_vs_astar.txt', 'DFS'):  ('4', '1 -> 2 -> 4'),
    ('TC05_gbfs_vs_astar.txt', 'BFS'):  ('4', '1 -> 2 -> 4'),
    ('TC05_gbfs_vs_astar.txt', 'GBFS'): ('4', '1 -> 2 -> 4'),
    ('TC05_gbfs_vs_astar.txt', 'AS'):   ('4', '1 -> 3 -> 4'),
    ('TC05_gbfs_vs_astar.txt', 'CUS1'): ('4', '1 -> 2 -> 4'),
    ('TC05_gbfs_vs_astar.txt', 'CUS2'): ('4', '1 -> 3 -> 4'),

    # TC06 — multiple destinations; different algorithms reach different goals
    ('TC06_multiple_destinations.txt', 'DFS'):  ('2', '1 -> 2'),
    ('TC06_multiple_destinations.txt', 'BFS'):  ('2', '1 -> 2'),
    ('TC06_multiple_destinations.txt', 'GBFS'): ('2', '1 -> 2'),
    ('TC06_multiple_destinations.txt', 'AS'):   ('4', '1 -> 4'),
    ('TC06_multiple_destinations.txt', 'CUS1'): ('2', '1 -> 2'),
    ('TC06_multiple_destinations.txt', 'CUS2'): ('4', '1 -> 4'),

    # TC07 — linear chain (only one possible path; all algorithms agree)
    ('TC07_linear_chain.txt', 'DFS'):  ('5', '1 -> 2 -> 3 -> 4 -> 5'),
    ('TC07_linear_chain.txt', 'BFS'):  ('5', '1 -> 2 -> 3 -> 4 -> 5'),
    ('TC07_linear_chain.txt', 'GBFS'): ('5', '1 -> 2 -> 3 -> 4 -> 5'),
    ('TC07_linear_chain.txt', 'AS'):   ('5', '1 -> 2 -> 3 -> 4 -> 5'),
    ('TC07_linear_chain.txt', 'CUS1'): ('5', '1 -> 2 -> 3 -> 4 -> 5'),
    ('TC07_linear_chain.txt', 'CUS2'): ('5', '1 -> 2 -> 3 -> 4 -> 5'),

    # TC08 — directed graph where one branch looks closer but costs more
    ('TC08_directed_trap.txt', 'DFS'):  ('5', '1 -> 2 -> 3 -> 5'),
    ('TC08_directed_trap.txt', 'BFS'):  ('5', '1 -> 2 -> 3 -> 5'),
    ('TC08_directed_trap.txt', 'GBFS'): ('5', '1 -> 2 -> 3 -> 5'),
    ('TC08_directed_trap.txt', 'AS'):   ('5', '1 -> 2 -> 3 -> 5'),
    ('TC08_directed_trap.txt', 'CUS1'): ('5', '1 -> 2 -> 3 -> 5'),
    ('TC08_directed_trap.txt', 'CUS2'): ('5', '1 -> 2 -> 3 -> 5'),

    # TC09 — dense graph (many edges); BFS/AS find shortest, DFS goes deep first
    ('TC09_dense_graph.txt', 'DFS'):  ('6', '1 -> 2 -> 3 -> 5 -> 6'),
    ('TC09_dense_graph.txt', 'BFS'):  ('6', '1 -> 2 -> 6'),
    ('TC09_dense_graph.txt', 'GBFS'): ('6', '1 -> 2 -> 6'),
    ('TC09_dense_graph.txt', 'AS'):   ('6', '1 -> 2 -> 6'),
    ('TC09_dense_graph.txt', 'CUS1'): ('6', '1 -> 2 -> 6'),
    ('TC09_dense_graph.txt', 'CUS2'): ('6', '1 -> 2 -> 6'),

    # TC10 — large 10-node graph (tests scalability)
    ('TC10_large_graph.txt', 'DFS'):  ('10', '1 -> 2 -> 4 -> 6 -> 8 -> 10'),
    ('TC10_large_graph.txt', 'BFS'):  ('10', '1 -> 2 -> 4 -> 7 -> 10'),
    ('TC10_large_graph.txt', 'GBFS'): ('10', '1 -> 2 -> 4 -> 7 -> 10'),
    ('TC10_large_graph.txt', 'AS'):   ('10', '1 -> 2 -> 4 -> 7 -> 10'),
    ('TC10_large_graph.txt', 'CUS1'): ('10', '1 -> 2 -> 4 -> 7 -> 10'),
    ('TC10_large_graph.txt', 'CUS2'): ('10', '1 -> 2 -> 4 -> 7 -> 10'),

    # TC11 — star topology (hub with direct edges to all nodes including goal)
    ('TC11_star_topology.txt', 'DFS'):  ('6', '1 -> 6'),
    ('TC11_star_topology.txt', 'BFS'):  ('6', '1 -> 6'),
    ('TC11_star_topology.txt', 'GBFS'): ('6', '1 -> 6'),
    ('TC11_star_topology.txt', 'AS'):   ('6', '1 -> 6'),
    ('TC11_star_topology.txt', 'CUS1'): ('6', '1 -> 6'),
    ('TC11_star_topology.txt', 'CUS2'): ('6', '1 -> 6'),

    # TC12 — goal is deep in the graph; DFS explores a longer branch first
    ('TC12_deep_goal.txt', 'DFS'):  ('9', '1 -> 2 -> 4 -> 5 -> 6 -> 7 -> 8 -> 9'),
    ('TC12_deep_goal.txt', 'BFS'):  ('9', '1 -> 3 -> 6 -> 7 -> 9'),
    ('TC12_deep_goal.txt', 'GBFS'): ('9', '1 -> 3 -> 6 -> 7 -> 9'),
    ('TC12_deep_goal.txt', 'AS'):   ('9', '1 -> 3 -> 6 -> 7 -> 9'),
    ('TC12_deep_goal.txt', 'CUS1'): ('9', '1 -> 3 -> 6 -> 7 -> 9'),
    ('TC12_deep_goal.txt', 'CUS2'): ('9', '1 -> 3 -> 6 -> 7 -> 9'),

    # TC13 — equal-cost symmetric paths; validates ascending node-ID tiebreaking
    ('TC13_tiebreak.txt', 'DFS'):  ('5', '1 -> 2 -> 5'),
    ('TC13_tiebreak.txt', 'BFS'):  ('5', '1 -> 2 -> 5'),
    ('TC13_tiebreak.txt', 'GBFS'): ('5', '1 -> 2 -> 5'),
    ('TC13_tiebreak.txt', 'AS'):   ('5', '1 -> 2 -> 5'),
    ('TC13_tiebreak.txt', 'CUS1'): ('5', '1 -> 2 -> 5'),
    ('TC13_tiebreak.txt', 'CUS2'): ('5', '1 -> 2 -> 5'),

    # TC14 — 1-hop high-cost path vs 3-hop low-cost path; BFS/DFS/CUS1 prefer fewer hops,
    #         A*/CUS2 find lowest cost; both happen to be 1 hop here (cost 2 direct edge)
    ('TC14_short_hop_vs_low_cost.txt', 'DFS'):  ('2', '1 -> 2'),
    ('TC14_short_hop_vs_low_cost.txt', 'BFS'):  ('2', '1 -> 2'),
    ('TC14_short_hop_vs_low_cost.txt', 'GBFS'): ('2', '1 -> 2'),
    ('TC14_short_hop_vs_low_cost.txt', 'AS'):   ('2', '1 -> 2'),
    ('TC14_short_hop_vs_low_cost.txt', 'CUS1'): ('2', '1 -> 2'),
    ('TC14_short_hop_vs_low_cost.txt', 'CUS2'): ('2', '1 -> 2'),

    # TC15 — 3 destinations; only 2 are reachable; 1 is completely unreachable (node 4)
    ('TC15_partial_reachability.txt', 'DFS'):  ('3', '1 -> 2 -> 3'),
    ('TC15_partial_reachability.txt', 'BFS'):  ('3', '1 -> 2 -> 3'),
    ('TC15_partial_reachability.txt', 'GBFS'): ('3', '1 -> 2 -> 3'),
    ('TC15_partial_reachability.txt', 'AS'):   ('3', '1 -> 2 -> 3'),
    ('TC15_partial_reachability.txt', 'CUS1'): ('3', '1 -> 2 -> 3'),
    ('TC15_partial_reachability.txt', 'CUS2'): ('3', '1 -> 2 -> 3'),
}

GREEN = '\033[92m'
RED   = '\033[91m'
RESET = '\033[0m'
GREY  = '\033[90m'


def run_test(test_file, method):
    """Run search.py on a test file with the given method. Returns output lines."""
    result = subprocess.run(
        [sys.executable, SEARCH_SCRIPT, test_file, method],
        capture_output=True, text=True
    )
    return result.stdout.strip().splitlines(), result.returncode


def main():
    test_files = sorted(f for f in os.listdir(TEST_DIR) if f.endswith('.txt'))

    if not test_files:
        print("No test files found in tests/test_cases/")
        sys.exit(1)

    total = 0
    passed = 0
    failed = 0
    skipped = 0

    print(f"\n{'='*70}")
    print(f"  Route Finder — Automated Test Runner")
    print(f"{'='*70}\n")

    for test_file in test_files:
        filepath = os.path.join(TEST_DIR, test_file)
        print(f"  📄 {test_file}")

        for method in METHODS:
            total += 1
            lines, returncode = run_test(filepath, method)

            if returncode != 0 or not lines:
                print(f"    {RED}[ERROR]{RESET}  {method:<6} — crashed or no output")
                failed += 1
                continue

            # Parse output
            # Line 0: "filename method"
            # Line 1: "goal nodes" or "No path found"
            # Line 2: path (if found)
            goal_line = lines[1] if len(lines) > 1 else ''
            path_line = lines[2] if len(lines) > 2 else ''

            if 'No path found' in goal_line:
                goal_val = 'No path found'
                path_val = ''
            else:
                parts = goal_line.split()
                goal_val = parts[0] if parts else '?'
                path_val = path_line

            key = (test_file, method)
            if key in EXPECTED:
                exp_goal, exp_path = EXPECTED[key]
                if goal_val == exp_goal and path_val == exp_path:
                    print(f"    {GREEN}[PASS]{RESET}   {method:<6} → goal={goal_val}, path={path_val}")
                    passed += 1
                else:
                    print(f"    {RED}[FAIL]{RESET}   {method:<6} → got goal={goal_val} path={path_val}")
                    print(f"             expected goal={exp_goal} path={exp_path}")
                    failed += 1
            else:
                print(f"    {GREY}[RUN]{RESET}    {method:<6} → goal={goal_val}, path={path_val}")
                skipped += 1

        print()

    print(f"{'='*70}")
    print(f"  Results: {passed} passed | {failed} failed | {skipped} unverified | {total} total")
    print(f"{'='*70}\n")

    if failed > 0:
        sys.exit(1)


if __name__ == '__main__':
    main()
