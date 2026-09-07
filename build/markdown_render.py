"""
Render a page's markdown body and lift its H1 into a hero title.

Single responsibility: turn raw markdown body text into (hero_title, html).
Does not know about frontmatter, templates, or the FAQ transform.
"""

import logging
import re

import markdown

from build.errors import BuildError

logger = logging.getLogger(__name__)

# Matches a line that is exactly a level-1 ATX heading, e.g. "# About us".
_H1_LINE_PATTERN = re.compile(r"^# (.+)$", re.MULTILINE)

_MARKDOWN_EXTENSIONS = ["extra", "smarty"]


def render_body(markdown_text: str, filename: str) -> tuple[str, str]:
    """
    Lift the first H1 out of a markdown body and render the remainder to HTML.

    Args:
        markdown_text: the raw markdown body (frontmatter already stripped).
        filename: source filename, used only in the BuildError message.

    Returns:
        A (hero_title, html) tuple: hero_title is the plain text of the first
        H1 line; html is the body rendered with the "extra" and "smarty"
        extensions, with that H1 line removed.

    Raises:
        BuildError: if the body contains no top-level "# " heading.
    """
    match = _H1_LINE_PATTERN.search(markdown_text)
    if match is None:
        raise BuildError(f"{filename}: body has no H1 ('# ...') heading to use as hero title")

    hero_title = match.group(1).strip()
    remaining = markdown_text[: match.start()] + markdown_text[match.end():]

    html = markdown.markdown(remaining, extensions=_MARKDOWN_EXTENSIONS)
    logger.info("Rendered body for %s (hero: %s)", filename, hero_title)
    return hero_title, html
