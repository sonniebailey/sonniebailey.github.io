"""
Write sitemap.xml and robots.txt to the build output.

Single responsibility: generate these two small discovery files from the
already-loaded pages and site config. Nothing else in the build touches them.
"""

import logging
import xml.etree.ElementTree as ET
from pathlib import Path

logger = logging.getLogger(__name__)

_SITEMAP_NAMESPACE = "http://www.sitemaps.org/schemas/sitemap/0.9"


def write_sitemap(out_dir: Path, site: dict, pages: list[dict]) -> None:
    """
    Write sitemap.xml listing every page except 404 and noindex pages.

    Args:
        out_dir: build output directory (_site/).
        site: validated site config dict; provides 'domain'.
        pages: list of page dicts, each with 'url', 'canonical', 'noindex'.

    Returns:
        None. Writes out_dir/sitemap.xml.
    """
    urlset = ET.Element("urlset", xmlns=_SITEMAP_NAMESPACE)
    included = 0
    for page in pages:
        if page["url"] == "404.html" or page["noindex"]:
            continue
        url_el = ET.SubElement(urlset, "url")
        loc_el = ET.SubElement(url_el, "loc")
        loc_el.text = page["canonical"]
        included += 1

    tree = ET.ElementTree(urlset)
    ET.indent(tree, space="  ")
    output_path = out_dir / "sitemap.xml"
    tree.write(output_path, xml_declaration=True, encoding="UTF-8")
    logger.info("Wrote sitemap.xml with %d url(s)", included)


def write_robots(out_dir: Path, site: dict) -> None:
    """
    Write robots.txt, allowing or refusing crawlers per site search visibility.

    Args:
        out_dir: build output directory (_site/).
        site: validated site config dict; provides 'domain' and
            'search_visible' (defaulted by site_config, so always present).

    Returns:
        None. Writes out_dir/robots.txt.

    LLM Note: robots.txt is a request, not an instruction -- the noindex meta
    tag in base.html is what actually keeps a hidden site out of results. Both
    are driven by the same site.search_visible value; do not set one without
    the other.
    """
    if site["search_visible"]:
        content = (
            "User-agent: *\n"
            "Allow: /\n"
            f"Sitemap: {site['domain']}/sitemap.xml\n"
        )
    else:
        # No Sitemap line on a hidden site: pointing crawlers at a list of
        # every page while asking them not to crawl is working against itself.
        content = (
            "User-agent: *\n"
            "Disallow: /\n"
        )
    (out_dir / "robots.txt").write_text(content, encoding="utf-8")
    logger.info("Wrote robots.txt")
