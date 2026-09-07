#!/usr/bin/env python3
"""
Local settings page for a site.

Serves a small form for editing the two files that describe the business and its
brand: content/site.json and the BRAND block at the top of css/variables.css.
Saving writes those files exactly as a hand edit would; nothing else in the site
knows this tool exists. It edits config and brand only, never page content --
page text lives in content/*.md and is edited directly.

Developer tool: never copied to _site/, never deployed.

Usage: python3 settings.py [--port 8001]
"""

import argparse
import json
import logging
import re
import sys
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path

ROOT = Path(__file__).parent
SITE_JSON = ROOT / "content" / "site.json"
VARIABLES_CSS = ROOT / "css" / "variables.css"
PAGE_HTML = ROOT / "settings.html"

BRAND_START = "/* ===== BRAND: edit these ===== */"
BRAND_END = "/* ===== END BRAND ===== */"
TOKEN_LINE = re.compile(r"^\s*(--[a-z0-9-]+)\s*:\s*(.+?)\s*;\s*$")

logger = logging.getLogger(__name__)


def read_brand_block(css_text: str) -> dict[str, str]:
    """
    Extract the brand tokens from variables.css.
    Args: css_text -- full text of css/variables.css
    Returns: ordered dict of token name -> value, e.g. {"--brand-primary": "#0f6b6b"}
    Raises ValueError if the BRAND markers are missing.
    """
    start = css_text.find(BRAND_START)
    end = css_text.find(BRAND_END)
    if start == -1 or end == -1 or end < start:
        raise ValueError("css/variables.css is missing the BRAND block markers")
    tokens: dict[str, str] = {}
    for line in css_text[start + len(BRAND_START):end].splitlines():
        match = TOKEN_LINE.match(line)
        if match:
            tokens[match.group(1)] = match.group(2)
    if not tokens:
        raise ValueError("No tokens found between the BRAND markers in css/variables.css")
    return tokens


def write_brand_block(css_text: str, tokens: dict[str, str]) -> str:
    """
    Replace token values inside the BRAND block, leaving every other line untouched.
    Args: css_text -- full text of css/variables.css; tokens -- name -> new value
    Returns: the updated CSS text
    Raises ValueError for a token name that is not already in the block (no new tokens
    are added here; add them in the file by hand).
    """
    start = css_text.find(BRAND_START) + len(BRAND_START)
    end = css_text.find(BRAND_END)
    block = css_text[start:end]
    existing = read_brand_block(css_text)
    unknown = set(tokens) - set(existing)
    if unknown:
        raise ValueError(f"Unknown brand token(s): {', '.join(sorted(unknown))}")
    new_lines = []
    for line in block.splitlines(keepends=True):
        match = TOKEN_LINE.match(line)
        if match and match.group(1) in tokens:
            indent = line[: len(line) - len(line.lstrip())]
            new_lines.append(f"{indent}{match.group(1)}: {tokens[match.group(1)]};\n")
        else:
            new_lines.append(line)
    return css_text[:start] + "".join(new_lines) + css_text[end:]


def load_state() -> dict:
    """
    Read both files for the page.
    Args: none
    Returns: {"site": site.json object, "brand": token dict}
    """
    site = json.loads(SITE_JSON.read_text(encoding="utf-8"))
    brand = read_brand_block(VARIABLES_CSS.read_text(encoding="utf-8"))
    return {"site": site, "brand": brand}


def save_state(state: dict) -> None:
    """
    Write site.json and the brand block from a page submission.
    Args: state -- {"site": object, "brand": token dict}
    Returns: None. Raises ValueError on a malformed submission.
    """
    if not isinstance(state.get("site"), dict) or not isinstance(state.get("brand"), dict):
        raise ValueError("Submission must contain 'site' (object) and 'brand' (object)")
    for name, value in state["brand"].items():
        if not isinstance(value, str) or ";" in value or "}" in value or "\n" in value:
            raise ValueError(f"Invalid value for {name}")
    SITE_JSON.write_text(json.dumps(state["site"], indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    css = VARIABLES_CSS.read_text(encoding="utf-8")
    VARIABLES_CSS.write_text(write_brand_block(css, state["brand"]), encoding="utf-8")


class SettingsHandler(BaseHTTPRequestHandler):
    """HTTP handler: GET / serves the page, GET /api/state returns JSON, POST /api/state saves."""

    def _send(self, status: int, body: bytes, content_type: str) -> None:
        """Write a response. Args: status code, body bytes, content type. Returns: None."""
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self) -> None:  # noqa: N802 (http.server naming)
        """Serve the settings page or the current state. Args: none. Returns: None."""
        if self.path == "/":
            self._send(200, PAGE_HTML.read_bytes(), "text/html; charset=utf-8")
        elif self.path == "/api/state":
            try:
                body = json.dumps(load_state()).encode("utf-8")
            except (ValueError, OSError, json.JSONDecodeError) as exc:
                self._send(500, json.dumps({"error": str(exc)}).encode(), "application/json")
                return
            self._send(200, body, "application/json")
        else:
            self._send(404, b"Not found", "text/plain")

    def do_POST(self) -> None:  # noqa: N802
        """Save a submission. Args: none. Returns: None."""
        if self.path != "/api/state":
            self._send(404, b"Not found", "text/plain")
            return
        length = int(self.headers.get("Content-Length", "0"))
        if length <= 0 or length > 200_000:
            self._send(400, json.dumps({"error": "Bad request body"}).encode(), "application/json")
            return
        try:
            state = json.loads(self.rfile.read(length).decode("utf-8"))
            save_state(state)
        except (ValueError, json.JSONDecodeError, OSError) as exc:
            self._send(400, json.dumps({"error": str(exc)}).encode(), "application/json")
            return
        logger.info("Saved content/site.json and the BRAND block in css/variables.css")
        self._send(200, json.dumps({"ok": True}).encode(), "application/json")

    def log_message(self, fmt: str, *args: object) -> None:
        """Route http.server request logs through logging. Args: format, values. Returns: None."""
        logger.debug(fmt, *args)


def main() -> int:
    """
    Parse args and serve the settings page on localhost.
    Args: none (reads sys.argv: --port)
    Returns: exit code
    """
    logging.basicConfig(level=logging.INFO, format="%(message)s")
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--port", type=int, default=8001)
    args = parser.parse_args()
    for path in (SITE_JSON, VARIABLES_CSS, PAGE_HTML):
        if not path.exists():
            logger.error("Missing %s", path.relative_to(ROOT))
            return 1
    server = HTTPServer(("127.0.0.1", args.port), SettingsHandler)
    logger.info("Settings page: http://127.0.0.1:%d/  (Ctrl+C to stop)", args.port)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    return 0


if __name__ == "__main__":
    sys.exit(main())
