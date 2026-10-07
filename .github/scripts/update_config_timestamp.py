#!/usr/bin/env python3
"""Updates the timestamp field in the repository config file."""

from __future__ import annotations

import argparse
import json
import os
import sys
from datetime import datetime, timezone


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Update the timestamp in a config file.",
    )
    parser.add_argument(
        "config_file",
        nargs="?",
        default="config.json",
        help="Path to the config file (default: config.json).",
    )
    parser.add_argument(
        "--timestamp",
        help="Custom timestamp string to set (default: current UTC ISO-8601 string).",
    )
    return parser.parse_args()


def update_timestamp(config_path: str, timestamp: str | None = None) -> None:
    if not os.path.isfile(config_path):
        print(f"Error: Config file not found: {config_path}", file=sys.stderr)
        sys.exit(1)

    with open(config_path, encoding="utf-8") as f:
        data = json.load(f)

    if timestamp is None:
        timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    data["timestamp"] = timestamp

    with open(config_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, sort_keys=True)
        f.write("\n")

    print(f"Updated timestamp in {config_path} to {timestamp}")


def main() -> None:
    args = parse_args()
    update_timestamp(args.config_file, args.timestamp)


if __name__ == "__main__":
    main()
