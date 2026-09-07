#!/usr/bin/env python3
"""
Build a site: content/*.md + templates/ -> _site/.

Thin CLI entry point. All orchestration logic lives in build/orchestrator.py
(kept out of this file because a root-level build.py cannot itself be
imported as a module named "build" alongside the build/ package -- Python
resolves "build" to the package, not this script). This file just parses
args, calls run_build, and turns a BuildError into a clean exit 1.
"""

import argparse
import logging
import sys
from pathlib import Path

from build.errors import BuildError
from build.orchestrator import configure_logging, run_build

logger = logging.getLogger(__name__)


def main() -> None:
    """
    CLI entry point: parse args, run the build, exit 1 on BuildError.

    Args: None (reads sys.argv via argparse).
    Returns: None.
    """
    configure_logging()

    parser = argparse.ArgumentParser(description="Build a site.")
    parser.add_argument(
        "--out", default="_site", help="output directory, relative to repo root (default: _site)"
    )
    args = parser.parse_args()

    root = Path(__file__).parent
    out_dir = root / args.out

    try:
        run_build(root, out_dir)
    except BuildError as exc:
        logger.error("Build failed: %s", exc)
        sys.exit(1)


if __name__ == "__main__":
    main()
