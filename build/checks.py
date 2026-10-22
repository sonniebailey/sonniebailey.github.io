"""
Post-build smoke checks against the rendered _site/ output.

Single responsibility: assert the finished output looks correct -- required
markup present, no leftover template syntax, correct current-page marker
count, 404.html present and fully root-relative, sitemap/robots present,
faq pages contain <details>, and every asset reference resolves on disk.
Collects all failures and raises one BuildError listing them.
"""

import logging
import re
from pathlib import Path

from build.errors import BuildError

logger = logging.getLogger(__name__)

_ASSET_REF_PATTERN = re.compile(r'\b(?:href|src)="([^"]+)"')


def _check_page(out_dir: Path, page: dict, failures: list[str]) -> str | None:
    """
    Run the per-page structural checks for one page and append any failures.

    Args:
        out_dir: build output directory (_site/).
        page: page dict with at least 'url' and 'layout'.
        failures: list to append human-readable failure messages to.

    Returns:
        The page's HTML text if the file exists and could be read, else None.
    """
    path = out_dir / page["url"]
    if not path.exists():
        failures.append(f"{page['url']}: output file does not exist")
        return None

    html = path.read_text(encoding="utf-8")

    for required in ("<header", "<footer", "<main"):
        if required not in html:
            failures.append(f"{page['url']}: missing '{required}'")

    if "{{" in html or "{%" in html:
        failures.append(f"{page['url']}: leftover template syntax ('{{{{' or '{{%')")

    # The header partial renders the nav twice (desktop nav and mobile menu), so a
    # page listed in site.nav carries exactly two markers; a page not in the nav
    # (404) carries none. Index carries one, on the header's home button, which
    # is not part of either nav block. Any other count means the marker logic is broken.
    is_current_count = html.count('aria-current="page"')
    if page["url"] == "index.html":
        if is_current_count != 1:
            failures.append(
                f"{page['url']}: expected 1 current-page marker on index (home button), found {is_current_count}"
            )
    elif is_current_count not in (0, 2):
        failures.append(
            f"{page['url']}: expected 0 or 2 current-page markers (one per nav block), found {is_current_count}"
        )

    if page["layout"] == "faq" and "<details" not in html:
        failures.append(f"{page['url']}: faq page missing '<details'")

    return html


def _check_asset_references(out_dir: Path, url: str, html: str, failures: list[str]) -> None:
    """
    Verify every href/src reference to css/js/images resolves under out_dir.

    Args:
        out_dir: build output directory (_site/).
        url: the page's url, used in failure messages.
        html: the page's rendered HTML.
        failures: list to append human-readable failure messages to.

    Returns:
        None.
    """
    for match in _ASSET_REF_PATTERN.finditer(html):
        value = match.group(1)
        if not any(value.startswith(f"{prefix}/") or value.startswith(f"/{prefix}/") for prefix in ("css", "js", "images")):
            continue
        relative = value.lstrip("/")
        if not (out_dir / relative).exists():
            failures.append(f"{url}: referenced asset '{value}' does not exist in output")


def check_output(out_dir: Path, pages: list[dict]) -> None:
    """
    Run all post-build smoke checks and raise BuildError if any fail.

    Args:
        out_dir: build output directory (_site/).
        pages: list of page dicts as produced by build.py (with 'url', 'layout').

    Returns:
        None.

    Raises:
        BuildError: listing every failure found, if any.
    """
    failures: list[str] = []

    for page in pages:
        html = _check_page(out_dir, page, failures)
        if html is not None:
            _check_asset_references(out_dir, page["url"], html, failures)

    not_found_path = out_dir / "404.html"
    if not not_found_path.exists():
        failures.append("404.html: does not exist at output root")
    else:
        not_found_html = not_found_path.read_text(encoding="utf-8")
        for match in re.finditer(r'(?:href|src)="([^"]+)"', not_found_html):
            value = match.group(1)
            stripped = value.strip()
            if stripped.startswith(("/", "#", "http://", "https://", "//", "tel:", "mailto:", "data:")):
                continue
            failures.append(f"404.html: non-root-relative reference '{value}'")

    if not (out_dir / "sitemap.xml").exists():
        failures.append("sitemap.xml: does not exist")
    if not (out_dir / "robots.txt").exists():
        failures.append("robots.txt: does not exist")

    if failures:
        raise BuildError("Post-build checks failed:\n  " + "\n  ".join(failures))

    logger.info("All %d page(s) passed post-build checks", len(pages))
