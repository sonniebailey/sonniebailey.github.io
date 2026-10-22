"""
Rewrite document-relative URLs in baked HTML to root-relative ones.

Single responsibility: prefix href/src attribute values and CSS url()
targets with "/" wherever they are document-relative. Used only for
404.html, which GitHub Pages serves for any unmatched path, so
document-relative references (css/main.css, about.html) must be pinned to
the site root instead of resolving against whatever path the visitor hit.

Ported from chch ortho's deploy/root_relative.py.
"""

import re

# Attribute values and CSS url() targets that must NOT be prefixed: anything
# already absolute, already rooted, a bare fragment, or a non-http scheme.
_SKIP_PREFIXES = ("/", "#", "http://", "https://", "//", "tel:", "mailto:", "data:")

_ATTR_PATTERN = re.compile(r'\b(href|src)="([^"]*)"')
_CSS_URL_PATTERN = re.compile(r"url\((['\"]?)([^'\")]+)\1\)")


def _needs_root(value: str) -> bool:
    """
    Report whether a URL is document-relative and so needs a leading slash.

    Args:
        value: the raw attribute or url() value as authored.

    Returns:
        True if the value should be prefixed with "/", False to leave it alone.
    """
    stripped = value.strip()
    if not stripped:
        return False
    return not stripped.startswith(_SKIP_PREFIXES)


def rootify(html: str) -> str:
    """
    Return html with every document-relative href/src/url() made root-relative.

    Args:
        html: a fully baked page's HTML.

    Returns:
        The same HTML with relative references prefixed by "/".
    """
    def _attr(match: re.Match) -> str:
        attr, value = match.group(1), match.group(2)
        if not _needs_root(value):
            return match.group(0)
        return f'{attr}="/{value.strip()}"'

    def _css(match: re.Match) -> str:
        quote, value = match.group(1), match.group(2)
        if not _needs_root(value):
            return match.group(0)
        return f"url({quote}/{value.strip()}{quote})"

    return _CSS_URL_PATTERN.sub(_css, _ATTR_PATTERN.sub(_attr, html))
