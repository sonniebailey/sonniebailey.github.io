"""
Orchestrate the full build: content/*.md + templates/ -> _site/.

Single responsibility: sequence the build steps, each delegated to its own
module under build/. Order: load and validate site.json; load and validate
every content page; prepare a clean output directory; render each page
(markdown -> optional FAQ transform -> Jinja2 template -> root-relative
rewrite for 404.html); copy static assets; write sitemap.xml and
robots.txt; run post-build smoke checks.

Lives in the build package (rather than root build.py) so both build.py
and preview.py can import run_build without a module/package name clash
between root-level build.py and this build/ package.
"""

import logging
import sys
from datetime import date
from pathlib import Path

from build.checks import check_output
from build.faq_transform import to_details
from build.markdown_render import render_body
from build.output import copy_assets, prepare_output
from build.page_loader import compute_canonical, load_pages
from build.page_renderer import create_env, render_page
from build.root_relative import rootify
from build.site_config import load_site_config
from build.sitemap_writer import write_robots, write_sitemap

logger = logging.getLogger(__name__)


def configure_logging() -> None:
    """
    Configure a simple stdout logging handler for the whole build.

    Args: None.
    Returns: None.
    """
    logging.basicConfig(
        level=logging.INFO,
        format="%(levelname)s %(name)s: %(message)s",
        stream=sys.stdout,
    )


def run_build(root: Path, out_dir: Path) -> None:
    """
    Run the full build.

    Args:
        root: repository root Path.
        out_dir: build output directory to write into.

    Returns:
        None.

    Raises:
        BuildError: on any invalid input or failed post-build check.
    """
    site = load_site_config(root)
    pages = load_pages(root)

    for page in pages:
        page["canonical"] = compute_canonical(site["domain"], page["url"])

    prepare_output(out_dir)

    env = create_env(root)
    build_info = {"year": date.today().year}

    for page in pages:
        hero_title, content_html = render_body(page["body"], page["filename"])
        if page["layout"] == "faq":
            content_html = to_details(content_html, page["filename"])

        html = render_page(env, page, site, hero_title, content_html, build_info)

        if page["url"] == "404.html":
            html = rootify(html)

        (out_dir / page["url"]).write_text(html, encoding="utf-8")
        logger.info("Wrote %s", page["url"])

    copy_assets(root, out_dir)
    write_sitemap(out_dir, site, pages)
    write_robots(out_dir, site)

    # Announced on every build, in both directions, so the state is visible in
    # the Netlify deploy log as well as locally. The launch flip is a one-way
    # door in practice: once a site is live, a hidden deploy would remove it
    # from search results.
    if site["search_visible"]:
        logger.info("SEARCH VISIBLE: this build is public and may be indexed")
    else:
        logger.info(
            "HIDDEN FROM SEARCH: this build carries noindex on every page and a "
            "Disallow robots.txt. Set search_visible true in content/site.json "
            "to publish."
        )

    check_output(out_dir, pages)
    logger.info("Build complete: %d page(s) written to %s", len(pages), out_dir)
