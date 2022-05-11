#!/usr/bin/env python3

import os
import re
import sys

RESULT_RE = re.compile(r"(PASS|FAIL):\s+(\S+)")


def _parse_suite_test(output):
    suite = os.path.basename(os.path.dirname(output))
    test = os.path.basename(output)
    test, _ = os.path.splitext(test)
    return suite, test


def _process(logfile):

    results = {}

    for line in logfile:
        match = RESULT_RE.match(line)
        if not match:
            continue

        result = match.group(1)
        output = match.group(2)
        suite, test = _parse_suite_test(output)

        if suite not in results:
            results[suite] = {
                "PASS": [],
                "FAIL": [],
            }

        suite_results = results[suite]
        suite_results[result].append((test, output))
    return results


def main(log_file):
    with open(log_file) as infile:
        processed_results = _process(infile)

    passed_suites = []
    failed_suites = []

    for suite, results in processed_results.items():
        num_passes = len(results["PASS"])
        num_fails = len(results["FAIL"])

        if not num_fails:
            passed_suites.append(f"Suite {suite} passed all {num_passes} tests.")
            continue

        failed_suites.append(f"X Suite {suite} passed {num_passes} failed {num_fails}.")

    for line in sorted(passed_suites):
        print(line)

    print()
    for line in sorted(failed_suites):
        print(line)

    return 0


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print(f"Usage: {sys.argv[0]} <compare_script_log_output>")
        exit(1)

    main(sys.argv[1])
    exit(0)
