"""
Create the Jinja2 environment and render a page through its layout template.

Single responsibility: Jinja2 setup and per-page rendering. Does not know
about markdown, frontmatter validation, or the FAQ transform -- it receives
already-rendered content HTML and a page dict.
"""

import logging
from pathlib import Path

from jinja2 import Environment, FileSystemLoader, StrictUndefined, TemplateError, select_autoescape
from markupsafe import Markup

from build.errors import BuildError

logger = logging.getLogger(__name__)


def create_env(root: Path) -> Environment:
    """
    Create a Jinja2 Environment configured for the site templates.

    Args:
        root: repository root Path; templates are loaded from templates/ beneath it.

    Returns:
        A configured jinja2.Environment with FileSystemLoader, StrictUndefined
        (any missing template variable fails the build), and autoescaping for
        html/xml templates.
    """
    env = Environment(
        loader=FileSystemLoader(str(root / "templates")),
        autoescape=select_autoescape(["html", "xml"]),
        undefined=StrictUndefined,
    )
    logger.info("Jinja environment initialised from %s", root / "templates")
    return env


def render_page(
    env: Environment,
    page: dict,
    site: dict,
    hero_title: str,
    content_html: str,
    build_info: dict,
) -> str:
    """
    Render one page through its layout template.

    Args:
        env: Jinja2 Environment from create_env.
        page: page dict from build/page_loader.py, plus 'canonical' set.
        site: validated site config dict from build/site_config.py.
        hero_title: the H1 text lifted from the page body.
        content_html: rendered (and, for faq pages, transformed) body HTML.
        build_info: dict with build-time context, e.g. {"year": 2026}.

    Returns:
        The fully rendered HTML document as a string.
    """
    template_name = f"{page['layout']}.html"
    try:
        template = env.get_template(template_name)
        html = template.render(
            site=site,
            page=page,
            hero_title=hero_title,
            content=Markup(content_html),
            build=build_info,
        )
    except TemplateError as exc:
        # StrictUndefined and template syntax problems surface here; name the
        # page and template so the fix is obvious rather than a bare traceback.
        raise BuildError(f"{page['filename']}: template {template_name} failed: {exc}") from exc
    logger.info("Rendered %s with template %s.html", page["url"], page["layout"])
    return html
