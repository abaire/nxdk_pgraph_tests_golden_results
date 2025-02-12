#!/usr/bin/env python3

from __future__ import annotations

import argparse
import glob
import logging
import os
import sys
from collections import defaultdict
from typing import Collection
from urllib.parse import quote

logger = logging.getLogger(__name__)

RAW_BASE_URL = "https://raw.githubusercontent.com/abaire/nxdk_pgraph_tests_golden_results/main"


def _find_artifacts(results_dir: str) -> dict[str, list[str]]:
    artifacts = glob.glob("**/*.png", root_dir=results_dir, recursive=True)

    results_by_suite: dict[str, list[str]] = defaultdict(list)

    for result in artifacts:
        suite_name, test_case = result.split("/", 1)
        results_by_suite[suite_name].append(test_case)

    return results_by_suite


def _write_top_level_page(output_dir: str, suite_names: Collection[str]) -> None:
    with open(os.path.join(output_dir, "Home.md"), "w") as outfile:
        outfile.writelines(
            [
                "Results\n",
                "---\n",
                *[f"- [[{suite_name}|Results-{suite_name}]]\n" for suite_name in sorted(suite_names)],
            ]
        )


def _write_suite_results_page(results_dir: str, output_dir: str, suite_name: str, artifacts: Collection[str]) -> None:
    # GitHub's wiki does not seem to support pages in subdirs, so they are only used for
    # image content. Test suites should all have unique names so this should not cause
    # issues.
    with open(os.path.join(output_dir, f"Results-{suite_name}.md"), "w") as outfile:
        outfile.writelines(
            [
                f"{suite_name}\n",
                "---\n",
            ]
        )

        for artifact in sorted(artifacts):
            image_path = os.path.join(os.path.basename(results_dir), suite_name, artifact)
            urlsafe_image_path = quote(image_path)
            image_url = f"{RAW_BASE_URL}/{urlsafe_image_path}"
            outfile.writelines(
                [
                    f"## {artifact}\n",
                    f"![{artifact}]({image_url})\n",
                ]
            )


def _clean_output_dir(output_dir: str) -> None:
    markdown_pages = glob.glob("*.md", root_dir=output_dir)
    for page in markdown_pages:
        os.unlink(os.path.join(output_dir, page))


def process_results(results_dir: str, output_dir: str) -> int:
    logger.debug(
        "Generating wiki markdown in '%s' using artifacts in '%s'",
        os.path.abspath(output_dir),
        os.path.abspath(results_dir),
    )
    results_by_suite = _find_artifacts(results_dir)
    logger.debug("Found %d suites", len(results_by_suite))

    os.makedirs(output_dir, exist_ok=True)
    _clean_output_dir(output_dir)

    _write_top_level_page(output_dir, results_by_suite.keys())
    for suite_name, artifacts in results_by_suite.items():
        _write_suite_results_page(results_dir, output_dir, suite_name, artifacts)

    return 0


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--verbose",
        "-v",
        help="Enables verbose logging information",
        action="store_true",
    )
    parser.add_argument(
        "results",
        help="Path to the directory containing the results of running the test suites.",
    )
    parser.add_argument(
        "output",
        help="Path to the directory into which GitHub wiki markdown should be written.",
    )

    args = parser.parse_args()
    log_level = logging.DEBUG if args.verbose else logging.INFO
    logging.basicConfig(level=log_level)

    return process_results(args.results, args.output)


if __name__ == "__main__":
    sys.exit(main())
