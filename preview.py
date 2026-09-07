#!/usr/bin/env python3
"""
Build the site, then serve _site/ locally for preview.

Single responsibility: run the build and hand the output directory to
Python's http.server. No file watcher -- rebuild-then-refresh is the loop.
"""

import argparse
import functools
import http.server
import logging
import sys
from pathlib import Path

from build.errors import BuildError
from build.orchestrator import configure_logging, run_build

logger = logging.getLogger(__name__)


def main() -> None:
    """
    CLI entry point: build the site, then serve _site/ on the given port.

    Args: None (reads sys.argv via argparse for --port, default 8000).
    Returns: None.
    """
    configure_logging()

    parser = argparse.ArgumentParser(description="Build and preview a site.")
    parser.add_argument("--port", type=int, default=8000, help="local preview port (default: 8000)")
    args = parser.parse_args()

    root = Path(__file__).parent
    out_dir = root / "_site"

    try:
        run_build(root, out_dir)
    except BuildError as exc:
        logger.error("Build failed: %s", exc)
        sys.exit(1)

    handler = functools.partial(http.server.SimpleHTTPRequestHandler, directory=str(out_dir))
    server = http.server.ThreadingHTTPServer(("127.0.0.1", args.port), handler)
    logger.info("Serving %s at http://127.0.0.1:%d/", out_dir, args.port)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        logger.info("Stopping preview server")
        server.shutdown()


if __name__ == "__main__":
    main()
