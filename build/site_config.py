"""
Load and validate content/site.json.

Single responsibility: read site.json, check every key the contract
requires (including nested ones), apply the documented defaults, and raise
BuildError naming the exact missing key on any gap. Nothing downstream
re-validates site config.
"""

import json
import logging
from pathlib import Path

from build.errors import BuildError

logger = logging.getLogger(__name__)

# Top-level keys that must be present regardless of type. "logo" is
# deliberately absent: the header falls back to the site name set as a text
# wordmark, which is the better default for a business without a logo file
# and is the only version that recolours correctly in dark mode.
_REQUIRED_TOP_LEVEL = (
    "name",
    "tagline",
    "domain",
    "phone",
    "email",
    "address",
    "hours",
    "nav",
    "favicon",
    "social_image",
    "fonts",
)


def _require(container: dict, key: str, context: str) -> object:
    """
    Fetch a required key from a dict, raising BuildError naming it if absent.

    Args:
        container: the dict to look the key up in
        key: the key expected to be present
        context: human-readable location, used in the error message

    Returns:
        The value stored at that key.

    Raises:
        BuildError: if the key is missing from container.
    """
    if key not in container:
        raise BuildError(f"content/site.json: missing required key '{key}' in {context}")
    return container[key]


def load_site_config(root: Path) -> dict:
    """
    Load content/site.json and validate it against the build contract.

    Args:
        root: repository root Path; content/site.json is read from beneath it.

    Returns:
        The parsed site config dict, with 'search_visible' defaulted to False
        when absent. No other key is altered.

    Raises:
        BuildError: if the file is missing, is not valid JSON, is missing any
            required key (top-level or nested) named in the contract, or sets
            'search_visible' to something other than true or false.
    """
    config_path = root / "content" / "site.json"
    if not config_path.exists():
        raise BuildError(f"content/site.json: file not found at {config_path}")

    try:
        text = config_path.read_text(encoding="utf-8")
    except OSError as exc:
        raise BuildError(f"content/site.json: could not read file: {exc}") from exc

    try:
        config = json.loads(text)
    except json.JSONDecodeError as exc:
        raise BuildError(f"content/site.json: invalid JSON: {exc}") from exc

    for key in _REQUIRED_TOP_LEVEL:
        _require(config, key, "site.json")

    # Nested: phone.display / phone.tel
    phone = config["phone"]
    if not isinstance(phone, dict):
        raise BuildError("content/site.json: 'phone' must be an object")
    _require(phone, "display", "site.json phone")
    _require(phone, "tel", "site.json phone")

    # Nested: address.lines / address.single_line
    address = config["address"]
    if not isinstance(address, dict):
        raise BuildError("content/site.json: 'address' must be an object")
    _require(address, "lines", "site.json address")
    _require(address, "single_line", "site.json address")

    # Nested: fonts.heading / fonts.body / fonts.google_css
    fonts = config["fonts"]
    if not isinstance(fonts, dict):
        raise BuildError("content/site.json: 'fonts' must be an object")
    _require(fonts, "heading", "site.json fonts")
    _require(fonts, "body", "site.json fonts")
    _require(fonts, "google_css", "site.json fonts")

    # Nested: nav items each need label / href
    nav = config["nav"]
    if not isinstance(nav, list):
        raise BuildError("content/site.json: 'nav' must be a list")
    for index, item in enumerate(nav):
        if not isinstance(item, dict):
            raise BuildError(f"content/site.json: nav[{index}] must be an object")
        _require(item, "label", f"site.json nav[{index}]")
        _require(item, "href", f"site.json nav[{index}]")

    # Nested: map, optional -- only validated when present and not null.
    map_config = config.get("map")
    if map_config is not None:
        if not isinstance(map_config, dict):
            raise BuildError("content/site.json: 'map' must be an object or null")
        _require(map_config, "embed_url", "site.json map")
        _require(map_config, "link_url", "site.json map")

    # search_visible, optional, default False. Absent means hidden: a site
    # that has not said it is ready to be found should not be found. The
    # default is deliberately the safe direction, because the cost of a
    # forgotten key is an unlisted site (fixable in one commit) rather than a
    # client's unfinished draft appearing in Google.
    search_visible = config.get("search_visible", False)
    if not isinstance(search_visible, bool):
        raise BuildError(
            "content/site.json: 'search_visible' must be true or false, "
            f"not {type(search_visible).__name__}"
        )
    config["search_visible"] = search_visible

    logger.info("Loaded and validated content/site.json")
    return config
