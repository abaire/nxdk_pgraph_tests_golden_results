#!/usr/bin/env python3

# ruff: noqa: S701: By default, jinja2 sets `autoescape` to `False`.

from __future__ import annotations

import argparse
import glob
import json
import logging
import os
import sys
from collections import defaultdict
from dataclasses import dataclass
from typing import Any, Collection

from jinja2 import Environment, FileSystemLoader

logger = logging.getLogger(__name__)

RESULTS_SUBDIR = "results"
RESULTS_NO_ALPHA_SUBDIR = "results-noalpha"


@dataclass
class TestSuiteDescriptor:
    """Describes one of the nxdk_pgraph_tests test suites."""

    suite_name: str
    class_name: str
    description: list[str]
    source_file: str
    source_file_line: int
    test_descriptions: dict[str, str]

    @classmethod
    def from_obj(cls, obj: dict[str, Any]) -> TestSuiteDescriptor:
        return cls(
            suite_name=obj.get("suite", "").replace(" ", "_"),
            class_name=obj.get("class", ""),
            description=obj.get("description", []),
            source_file=obj.get("source_file", ""),
            source_file_line=obj.get("source_file_line", -1),
            test_descriptions=obj.get("test_descriptions", {}),
        )


class TestSuiteDescriptorLoader:
    """Loads test suite descriptors from the nxdk_pgraph_tests project."""

    def __init__(self, registry_url: str):
        self.registry_url = registry_url

    def _load_registry(self) -> dict[str, Any] | None:
        import requests

        try:
            response = requests.get(self.registry_url, timeout=30)
            response.raise_for_status()
            return json.loads(response.content)
        except requests.exceptions.RequestException:
            logger.exception("Failed to load descriptor from '%s'", self.registry_url)
            return None

    def process(self) -> dict[str, TestSuiteDescriptor]:
        """Loads the test suite descriptors from the nxdk_pgraph_tests project."""

        registry = self._load_registry()
        if not registry:
            return {}

        return {
            descriptor.suite_name: descriptor
            for descriptor in [TestSuiteDescriptor.from_obj(item) for item in registry.get("test_suites", [])]
        }


def _fuzzy_lookup_suite_descriptor(
    descriptors: dict[str, TestSuiteDescriptor], suite_name: str
) -> TestSuiteDescriptor | None:
    """Attempts a permissive lookup of the given suite_name in the given set of `TestSuiteDescriptor`s"""

    # Check for a perfect match.
    ret = descriptors.get(suite_name)
    if ret:
        return ret

    # Descriptor keys are generally of the form TestSuiteTests whereas the suite names tend to be "Test_suite".
    camel_cased = "".join(element.title() for element in suite_name.split("_"))
    ret = descriptors.get(camel_cased)
    if ret:
        return ret

    return descriptors.get(f"{camel_cased}Tests")


@dataclass
class TestResult:
    """Contains information about the results of a specific test within a suite."""

    name: str
    artifact_url: str
    no_alpha_artifact_url: str


@dataclass
class SuiteResults:
    """Contains information about the results of a specific suite within a run."""

    name: str
    test_results: Collection[TestResult]
    descriptor: TestSuiteDescriptor | None


class ResultsScanner:
    """Scans and categorizes test results."""

    def __init__(
        self,
        results_dir: str,
        output_dir: str,
        base_url: str,
        base_url_no_alpha: str,
        test_suite_descriptors: dict[str, TestSuiteDescriptor],
    ) -> None:
        self.results_dir = results_dir
        self.output_dir = output_dir
        self.base_url = base_url
        self.base_url_no_alpha = base_url_no_alpha
        self.test_suite_descriptors = test_suite_descriptors

    def _get_suite_descriptor(self, suite_name: str) -> TestSuiteDescriptor | None:
        return _fuzzy_lookup_suite_descriptor(self.test_suite_descriptors, suite_name)

    def _process_suite(self, suite_name: str, images: list[str]) -> SuiteResults | None:
        suite_base_url = f"{self.base_url}/{RESULTS_SUBDIR}/{suite_name}"
        suite_no_alpha_base_url = f"{self.base_url_no_alpha}/{RESULTS_NO_ALPHA_SUBDIR}/{suite_name}"
        test_results = [
            TestResult(name=os.path.splitext(image)[0], artifact_url=f"{suite_base_url}/{image}", no_alpha_artifact_url=f"{suite_no_alpha_base_url}/{image}") for image in images
        ]

        return SuiteResults(
            name=suite_name,
            test_results=test_results,
            descriptor=self._get_suite_descriptor(suite_name),
        )

    def _find_result_images(self) -> dict[str, list[str]]:
        """Discovers png images within the results directory."""
        results_files = glob.glob("**/*.png", root_dir=self.results_dir, recursive=True)

        suite_to_results: dict[str, list[str]] = defaultdict(list)

        for image in results_files:
            suite_to_results[os.path.dirname(image)].append(os.path.basename(image))

        return suite_to_results

    def process(self) -> dict[str, SuiteResults]:
        """Processes the results directory into {run_identifier: ResultsInfo}."""

        suite_results = self._find_result_images()

        return {
            suite_name: self._process_suite(suite_name, image_files)
            for suite_name, image_files in suite_results.items()
        }


class PagesWriter:
    """Generates HTML output suitable for GitHub pages."""

    def __init__(
        self,
        results: dict[str, SuiteResults],
        env: Environment,
        output_dir: str,
        result_images_base_url: str,
        test_source_base_url: str,
    ) -> None:
        self.results = results
        self.env = env
        self.output_dir = output_dir.rstrip("/")
        self.css_output_dir = output_dir.rstrip("/")
        self.js_output_dir = output_dir.rstrip("/")
        self.images_base_url = result_images_base_url.rstrip("/")
        self.test_source_base_url = test_source_base_url.rstrip("/")

    def _home_url(self, output_dir) -> str:
        return f"{os.path.relpath(self.output_dir, output_dir)}/index.html"

    @staticmethod
    def _suite_result_url(suite_name: str) -> str:
        return f"{RESULTS_SUBDIR}/{suite_name}/index.html"

    def _suite_source_url(self, source_file_path: str, source_line: int) -> str:
        if self.test_source_base_url and source_file_path:
            if source_line >= 0:
                return f"{self.test_source_base_url}/{source_file_path}#L{source_line}"
            return f"{self.test_source_base_url}/{source_file_path}"
        return ""

    def _pack_descriptor(self, descriptor: TestSuiteDescriptor | None) -> dict[str, Any] | None:
        if not descriptor:
            return None
        return {
            "description": descriptor.description,
            "source_file": descriptor.source_file,
            "source_url": self._suite_source_url(descriptor.source_file, descriptor.source_file_line),
            "test_descriptions": descriptor.test_descriptions,
        }

    def _write_test_suite_results_page(self, suite: SuiteResults) -> None:
        """Generates a page for all the test case results within a single test suite."""
        index_template = self.env.get_template("test_suite_results.html.j2")
        output_subdir = os.path.join(RESULTS_SUBDIR, suite.name)
        output_dir = os.path.join(self.output_dir, output_subdir)
        os.makedirs(output_dir, exist_ok=True)

        result_infos: dict[str, dict[str, str]] = {}
        for result in suite.test_results:
            result_infos[result.name] = {"url": result.artifact_url, "no_alpha_url": result.no_alpha_artifact_url}

        with open(os.path.join(output_dir, "index.html"), "w") as outfile:
            outfile.write(
                index_template.render(
                    suite_name=suite.name,
                    results=result_infos,
                    css_dir=os.path.relpath(self.css_output_dir, output_dir),
                    js_dir=os.path.relpath(self.js_output_dir, output_dir),
                    descriptor=self._pack_descriptor(suite.descriptor),
                    home_url=self._home_url(output_dir),
                )
            )

    def _write_top_level_index(self) -> None:
        index_template = self.env.get_template("index.html.j2")
        output_dir = self.output_dir

        with open(os.path.join(output_dir, "index.html"), "w") as outfile:
            outfile.write(
                index_template.render(
                    results={suite_name: self._suite_result_url(suite_name) for suite_name in self.results},
                    css_dir=os.path.relpath(self.css_output_dir, output_dir),
                    js_dir=os.path.relpath(self.js_output_dir, output_dir),
                )
            )

    def _write_css(self) -> None:
        css_template = self.env.get_template("site.css.j2")
        with open(os.path.join(self.css_output_dir, "site.css"), "w") as outfile:
            outfile.write(
                css_template.render(
                    comparison_golden_outline_size=6,
                    title_bar_height=40,
                )
            )

    def _write_js(self) -> None:
        css_template = self.env.get_template("script.js.j2")
        with open(os.path.join(self.js_output_dir, "script.js"), "w") as outfile:
            outfile.write(css_template.render())

    def write(self) -> int:
        os.makedirs(self.output_dir, exist_ok=True)
        self._write_css()
        self._write_js()
        self._write_top_level_index()
        for suite_results in self.results.values():
            self._write_test_suite_results_page(suite_results)

        return 0


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--verbose",
        "-v",
        help="Enables verbose logging information",
        action="store_true",
    )
    parser.add_argument(
        "results_dir",
        help="Directory including test outputs that will be processed",
    )
    parser.add_argument(
        "output_dir",
        help="Directory into which HTML files will be generated",
    )
    parser.add_argument(
        "--base-url",
        default="https://raw.githubusercontent.com/abaire/nxdk_pgraph_tests_golden_results/main",
        help="Base URL at which the contents of the golden images from Xbox hardware may be publicly accessed.",
    )
    parser.add_argument(
        "--no-alpha-base-url",
        default="https://raw.githubusercontent.com/abaire/nxdk_pgraph_tests_golden_results/pages_deploy",
        help="Base URL at which the golden images from Xbox hardware with alpha ignored may be publicly accessed.",
    )
    parser.add_argument(
        "--templates-dir",
        help="Directory containing the templates used to render the site.",
    )
    parser.add_argument(
        "--test-descriptor-registry-url",
        default="https://raw.githubusercontent.com/abaire/nxdk_pgraph_tests/pages_doxygen/xml/nxdk_pgraph_tests_registry.json",
        help="URL at which the JSON test suite registry for nxdk_pgraph_tests may be publicly accessed.",
    )
    parser.add_argument(
        "--test-source-browser-base-url",
        default="https://github.com/abaire/nxdk_pgraph_tests/blob/pages_doxygen",
        help="Base URL from which the test suite source files may be publicly accessed.",
    )

    args = parser.parse_args()

    log_level = logging.DEBUG if args.verbose else logging.INFO
    logging.basicConfig(level=log_level)

    os.makedirs(args.output_dir, exist_ok=True)

    test_suite_descriptors = (
        TestSuiteDescriptorLoader(args.test_descriptor_registry_url).process()
        if args.test_descriptor_registry_url
        else {}
    )

    results = ResultsScanner(
        args.results_dir,
        args.output_dir,
        args.base_url,
        args.no_alpha_base_url,
        test_suite_descriptors,
    ).process()

    if not args.templates_dir:
        args.templates_dir = os.path.join(os.path.dirname(__file__), "site-templates")

    jinja_env = Environment(loader=FileSystemLoader(args.templates_dir))
    jinja_env.globals["sidenav_width"] = 48
    jinja_env.globals["sidenav_icon_width"] = 32

    return PagesWriter(results, jinja_env, args.output_dir, args.base_url, args.test_source_browser_base_url).write()


if __name__ == "__main__":
    sys.exit(main())
