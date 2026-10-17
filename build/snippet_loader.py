"""
Load content/snippets/*.md: blocks of wording shown inside templates rather
than as pages of their own (eg the Limited capacity popup).

Single responsibility: read each snippet file and render it to a title and
HTML through build/markdown_render.py. Snippets carry no frontmatter and are
not pages: they get no URL, canonical or sitemap entry. load_pages globs
content/*.md non-recursively, so files in this subfolder never become pages.
"""

import logging
from pathlib import Path

from markupsafe import Markup

from build.markdown_render import render_body

logger = logging.getLogger(__name__)


def load_snippets(root: Path) -> dict:
    """
    Load and render every content/snippets/*.md file.

    Args:
        root: repository root Path; content/snippets/ is read from beneath it.

    Returns:
        A dict keyed by file stem (capacity.md -> "capacity"), each value a
        dict with 'title' (the file's H1 text) and 'html' (the rest of the
        body rendered, marked safe for Jinja autoescaping).

    Raises:
        BuildError: if a snippet has no H1 heading (from render_body).

    LLM Note: templates read these as snippets.<stem>.title / .html via a
    Jinja global set in build/orchestrator.py. A missing file surfaces as a
    StrictUndefined template failure on the first page that uses it.
    """
    snippets: dict = {}
    for path in sorted((root / "content" / "snippets").glob("*.md")):
        label = f"snippets/{path.name}"
        title, html = render_body(path.read_text(encoding="utf-8"), label)
        snippets[path.stem] = {"title": title, "html": Markup(html)}

    logger.info("Loaded %d snippet(s) from content/snippets/", len(snippets))
    return snippets
