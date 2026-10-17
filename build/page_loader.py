"""
Load and validate every content/*.md page.

Single responsibility: split frontmatter from body for each markdown file,
validate required and optional-with-default fields per the build contract,
compute url/canonical, and check that referenced files (hero_image) exist.
Does not render markdown to HTML -- that is build/markdown_render.py.
"""

import logging
from pathlib import Path

import yaml

from build.errors import BuildError

logger = logging.getLogger(__name__)

_VALID_LAYOUTS = {"page", "home", "faq"}
_DEFAULT_HERO_IMAGE = "images/hero.jpg"
_REQUIRED_FIELDS = ("title", "description", "layout")


def _split_frontmatter(text: str, filename: str) -> tuple[dict, str]:
    """
    Split a markdown file's leading "---" delimited YAML frontmatter from its body.

    Args:
        text: full raw content of the markdown file.
        filename: source filename, used only in the BuildError message.

    Returns:
        A (frontmatter, body) tuple: frontmatter is the parsed YAML dict,
        body is the remaining markdown text.

    Raises:
        BuildError: if the file does not start with a "---" delimited block,
            or the YAML block does not parse to a dict.
    """
    if not text.startswith("---"):
        raise BuildError(f"{filename}: missing YAML frontmatter (must start with '---')")

    parts = text.split("---", 2)
    if len(parts) < 3:
        raise BuildError(f"{filename}: malformed frontmatter (need opening and closing '---')")

    try:
        frontmatter = yaml.safe_load(parts[1])
    except yaml.YAMLError as exc:
        raise BuildError(f"{filename}: invalid YAML frontmatter: {exc}") from exc

    if not isinstance(frontmatter, dict):
        raise BuildError(f"{filename}: frontmatter must be a YAML mapping")

    body = parts[2]
    return frontmatter, body


def _validate_features(features: object, filename: str) -> None:
    """
    Validate the shape of a home page's optional 'features' field.

    Args:
        features: the raw value of the frontmatter 'features' key (or None).
        filename: source filename, used only in the BuildError message.

    Returns:
        None.

    Raises:
        BuildError: if features is present but not a list of objects each
            containing title, text and icon.
    """
    if features is None:
        return
    if not isinstance(features, list):
        raise BuildError(f"{filename}: 'features' must be a list")
    for index, feature in enumerate(features):
        if not isinstance(feature, dict):
            raise BuildError(f"{filename}: features[{index}] must be an object")
        for key in ("title", "text", "icon"):
            if key not in feature:
                raise BuildError(f"{filename}: features[{index}] missing required key '{key}'")


def load_pages(root: Path) -> list[dict]:
    """
    Load, validate and normalise every content/*.md page.

    Args:
        root: repository root Path; content/*.md is read from beneath it.

    Returns:
        A list of page dicts, each with keys: filename, title, description,
        layout, hero_image, cta, intro, features, noindex, show_map, url,
        canonical, body
        (raw markdown body, frontmatter removed).

    Raises:
        BuildError: on missing/unknown required fields, an unknown layout,
            a missing hero_image file on disk, or a malformed 'features'
            list on a home page. Named by file and field throughout.
    """
    content_dir = root / "content"
    site_config_path = content_dir / "site.json"

    md_files = sorted(
        path for path in content_dir.glob("*.md") if path != site_config_path
    )
    if not md_files:
        raise BuildError(f"content/: no markdown pages found in {content_dir}")

    # Domain is validated separately via site_config; here we only need it
    # for canonical URLs, so re-read the minimal bit lazily via caller instead.
    pages: list[dict] = []
    for path in md_files:
        filename = path.name
        text = path.read_text(encoding="utf-8")
        frontmatter, body = _split_frontmatter(text, filename)

        for field in _REQUIRED_FIELDS:
            if field not in frontmatter:
                raise BuildError(f"{filename}: missing required frontmatter field '{field}'")

        layout = frontmatter["layout"]
        if layout not in _VALID_LAYOUTS:
            raise BuildError(
                f"{filename}: unknown layout '{layout}' (must be one of {sorted(_VALID_LAYOUTS)})"
            )

        hero_image = frontmatter.get("hero_image", _DEFAULT_HERO_IMAGE)
        hero_image_path = root / hero_image
        if not hero_image_path.exists():
            raise BuildError(f"{filename}: hero_image '{hero_image}' does not exist")

        cta = frontmatter.get("cta")
        if cta is not None:
            if not isinstance(cta, dict) or "label" not in cta or "href" not in cta:
                raise BuildError(f"{filename}: 'cta' must be an object with 'label' and 'href'")

        intro = frontmatter.get("intro")
        if intro is not None and not isinstance(intro, str):
            raise BuildError(f"{filename}: 'intro' must be text")

        features = frontmatter.get("features")
        if layout == "home":
            _validate_features(features, filename)

        noindex = frontmatter.get("noindex", False)
        if not isinstance(noindex, bool):
            raise BuildError(f"{filename}: 'noindex' must be a boolean")

        show_map = frontmatter.get("show_map", False)
        if not isinstance(show_map, bool):
            raise BuildError(f"{filename}: 'show_map' must be a boolean")

        url = filename[:-3] + ".html"

        pages.append(
            {
                "filename": filename,
                "title": frontmatter["title"],
                "description": frontmatter["description"],
                "layout": layout,
                "hero_image": hero_image,
                "cta": cta,
                "intro": intro,
                "features": features,
                "noindex": bool(noindex),
                "show_map": bool(show_map),
                "url": url,
                "body": body,
            }
        )

    logger.info("Loaded %d page(s) from content/", len(pages))
    return pages


def compute_canonical(domain: str, url: str) -> str:
    """
    Compute a page's canonical URL from the site domain and page url.

    Args:
        domain: canonical origin, no trailing slash (e.g. "https://example.co.nz").
        url: page url as produced by load_pages (e.g. "about.html" or "index.html").

    Returns:
        domain + "/" for index.html, otherwise domain + "/" + url.
    """
    if url == "index.html":
        return f"{domain}/"
    return f"{domain}/{url}"
