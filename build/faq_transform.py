"""
Transform FAQ page HTML into native <details>/<summary> accordions.

Single responsibility: given already-rendered HTML for a faq-layout page,
wrap each H2 and the markup up to the next H2 in a <details><summary>
element. Content before the first H2 (if any) is left untouched.
"""

import logging
import re

from build.errors import BuildError

logger = logging.getLogger(__name__)

# Splits on each <h2 ...>...</h2> heading, keeping the heading text and the
# tail of the document after it as separate capture groups.
_H2_PATTERN = re.compile(r"<h2[^>]*>(.*?)</h2>", re.IGNORECASE | re.DOTALL)


def _strip_tags(text: str) -> str:
    """
    Remove any HTML tags from a heading's inner text, for use as a summary.

    Args:
        text: raw inner HTML of an <h2> element.

    Returns:
        Plain text with tags removed.
    """
    return re.sub(r"<[^>]+>", "", text).strip()


def to_details(html: str, filename: str) -> str:
    """
    Wrap each H2 section of rendered HTML in a <details><summary> element.

    Args:
        html: rendered HTML body of a faq-layout page.
        filename: source filename, used only in the BuildError message.

    Returns:
        HTML with content before the first H2 left as-is, and every H2
        heading plus its following content (up to the next H2) wrapped in
        <details class="faq-item"><summary>heading text</summary>
        <div class="faq-answer">...content...</div></details>. The details
        elements are collected into a single <div class="faq-list">, which
        js/faq.js uses as the scope for its expand/collapse-all control.

    Raises:
        BuildError: if the HTML contains no H2 heading.
    """
    matches = list(_H2_PATTERN.finditer(html))
    if not matches:
        raise BuildError(f"{filename}: faq layout requires at least one H2 heading")

    preamble = html[: matches[0].start()]
    parts = [preamble] if preamble.strip() else []

    for index, match in enumerate(matches):
        summary_text = _strip_tags(match.group(1))
        section_start = match.end()
        section_end = matches[index + 1].start() if index + 1 < len(matches) else len(html)
        section_body = html[section_start:section_end]
        parts.append(
            f'<details class="faq-item">'
            f"<summary>{summary_text}</summary>"
            f'<div class="faq-answer">{section_body}</div>'
            f"</details>"
        )

    logger.info("Transformed %d FAQ sections for %s", len(matches), filename)
    preamble_html = parts[0] if preamble.strip() else ""
    items = parts[1:] if preamble.strip() else parts
    return preamble_html + '<div class="faq-list">' + "".join(items) + "</div>"
