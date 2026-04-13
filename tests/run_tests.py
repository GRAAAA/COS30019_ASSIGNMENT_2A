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
    ('PathFinder-test-1.txt', 'GBFS'): ('5', '2 -> 3 -> 5'),
    ('PathFinder-test-1.txt', 'AS'):   ('4', '2 -> 1 -> 4'),
    ('PathFinder-test-1.txt', 'CUS1'): ('4', '2 -> 1 -> 4'),
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
