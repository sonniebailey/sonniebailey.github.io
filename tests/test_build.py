"""
Tests for the build modules.

Each test builds a minimal fake site tree under pytest's tmp_path fixture
(its own content/, images/, templates/) rather than depending on the real
project content/ or templates/, which are owned by a concurrent build.
"""

import json

import pytest

from build.errors import BuildError
from build.faq_transform import to_details
from build.markdown_render import render_body
from build.output import copy_assets
from build.page_loader import load_pages
from build.root_relative import rootify
from build.site_config import load_site_config
from build.checks import check_output
from build.sitemap_writer import write_robots, write_sitemap


def _write_site_json(root, overrides=None):
    """Write a minimal valid content/site.json under root, with optional overrides."""
    config = {
        "name": "Example Co",
        "tagline": "Doing the thing",
        "domain": "https://example.co.nz",
        "phone": {"display": "03 123 4567", "tel": "+6431234567"},
        "email": "hello@example.co.nz",
        "address": {"lines": ["1 Test St"], "single_line": "1 Test St"},
        "hours": [],
        "nav": [{"label": "About", "href": "about.html"}],
        "logo": "images/logo.png",
        "favicon": "images/favicon.png",
        "social_image": "images/social-card.png",
        "fonts": {
            "heading": "Fraunces",
            "body": "Inter",
            "google_css": "https://fonts.googleapis.com/css2?family=Fraunces",
        },
    }
    if overrides:
        config.update(overrides)
    content_dir = root / "content"
    content_dir.mkdir(exist_ok=True)
    (content_dir / "site.json").write_text(json.dumps(config), encoding="utf-8")
    return config


def _write_page(root, filename, frontmatter_lines, body):
    """Write a content/*.md page under root with the given frontmatter and body."""
    content_dir = root / "content"
    content_dir.mkdir(exist_ok=True)
    text = "---\n" + "\n".join(frontmatter_lines) + "\n---\n" + body
    (content_dir / filename).write_text(text, encoding="utf-8")


def _touch_image(root, relative_path):
    """Create an empty placeholder image file at the given repo-relative path."""
    path = root / relative_path
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(b"")


# ---------------------------------------------------------------------------
# site_config
# ---------------------------------------------------------------------------

def test_site_config_missing_key_raises(tmp_path):
    """A site.json missing a required top-level key raises BuildError naming it."""
    config = _write_site_json(tmp_path)
    del config["email"]
    (tmp_path / "content" / "site.json").write_text(json.dumps(config), encoding="utf-8")

    with pytest.raises(BuildError, match="email"):
        load_site_config(tmp_path)


def test_site_config_valid_loads(tmp_path):
    """A fully valid site.json loads and returns the expected name."""
    _write_site_json(tmp_path)
    config = load_site_config(tmp_path)
    assert config["name"] == "Example Co"


def test_site_config_footer_link_missing_href_raises(tmp_path):
    """A footer_links item without an href raises BuildError naming the item."""
    _write_site_json(tmp_path, {"footer_links": [{"label": "Privacy"}]})
    with pytest.raises(BuildError, match=r"footer_links\[0\]"):
        load_site_config(tmp_path)


# ---------------------------------------------------------------------------
# output
# ---------------------------------------------------------------------------

def test_copy_assets_publishes_root_pdfs_at_site_root(tmp_path):
    """A PDF at the repo root is copied to the output root, keeping its address."""
    (tmp_path / "disclosure.pdf").write_bytes(b"%PDF-")
    out_dir = tmp_path / "_site"
    out_dir.mkdir()
    copy_assets(tmp_path, out_dir)
    assert (out_dir / "disclosure.pdf").read_bytes() == b"%PDF-"


def test_copy_assets_publishes_favicon_at_site_root(tmp_path):
    """icons/favicon.ico is also copied to the output root for blind /favicon.ico requests."""
    (tmp_path / "icons").mkdir()
    (tmp_path / "icons" / "favicon.ico").write_bytes(b"ICO")
    out_dir = tmp_path / "_site"
    out_dir.mkdir()
    copy_assets(tmp_path, out_dir)
    assert (out_dir / "icons" / "favicon.ico").read_bytes() == b"ICO"
    assert (out_dir / "favicon.ico").read_bytes() == b"ICO"


# ---------------------------------------------------------------------------
# page_loader
# ---------------------------------------------------------------------------

def test_page_missing_field_raises(tmp_path):
    """A page missing a required frontmatter field raises BuildError naming file and field."""
    _touch_image(tmp_path, "images/hero.jpg")
    _write_page(
        tmp_path,
        "about.md",
        ['title: "About"', 'layout: page'],  # missing description
        "# About us\n\nSome text.\n",
    )
    with pytest.raises(BuildError, match="about.md.*description"):
        load_pages(tmp_path)


def test_page_unknown_layout_raises(tmp_path):
    """A page with a layout not in {page, home, faq} raises BuildError."""
    _touch_image(tmp_path, "images/hero.jpg")
    _write_page(
        tmp_path,
        "about.md",
        ['title: "About"', 'description: "d"', 'layout: banana'],
        "# About us\n\nSome text.\n",
    )
    with pytest.raises(BuildError, match="layout"):
        load_pages(tmp_path)


def test_page_missing_hero_image_raises(tmp_path):
    """A page whose hero_image does not exist on disk raises BuildError."""
    _write_page(
        tmp_path,
        "about.md",
        ['title: "About"', 'description: "d"', 'layout: page', 'hero_image: images/missing.jpg'],
        "# About us\n\nSome text.\n",
    )
    with pytest.raises(BuildError, match="missing.jpg"):
        load_pages(tmp_path)


def test_page_valid_loads_with_defaults(tmp_path):
    """A minimal valid page loads with the default hero_image and noindex False."""
    _touch_image(tmp_path, "images/hero.jpg")
    _write_page(
        tmp_path,
        "about.md",
        ['title: "About"', 'description: "d"', 'layout: page'],
        "# About us\n\nSome text.\n",
    )
    pages = load_pages(tmp_path)
    assert len(pages) == 1
    assert pages[0]["hero_image"] == "images/hero.jpg"
    assert pages[0]["noindex"] is False
    assert pages[0]["url"] == "about.html"


# ---------------------------------------------------------------------------
# markdown_render
# ---------------------------------------------------------------------------

def test_render_body_lifts_h1():
    """render_body extracts the first H1 as hero_title and removes it from the HTML."""
    hero_title, html = render_body("# Welcome\n\nSome *text*.\n", "index.md")
    assert hero_title == "Welcome"
    assert "Welcome" not in html
    assert "<em>text</em>" in html


def test_render_body_no_h1_raises():
    """render_body raises BuildError naming the file when no H1 is present."""
    with pytest.raises(BuildError, match="index.md"):
        render_body("Just a paragraph, no heading.\n", "index.md")


# ---------------------------------------------------------------------------
# faq_transform
# ---------------------------------------------------------------------------

def test_faq_transform_wraps_sections():
    """to_details wraps each H2 section in a <details><summary> element."""
    html = "<h2>Q1</h2><p>A1</p><h2>Q2</h2><p>A2</p>"
    result = to_details(html, "faq.md")
    assert result.count("<details") == 2
    assert "<summary>Q1</summary>" in result
    assert "<summary>Q2</summary>" in result
    assert "<p>A1</p>" in result
    assert "<p>A2</p>" in result


def test_faq_transform_emits_styling_hooks():
    """
    to_details emits the class names the CSS targets.

    Regression guard: an earlier version emitted bare <details> elements
    while every FAQ rule in css/components.css targeted .faq-item, so none
    of the FAQ styling applied to the built page and the accordions fell
    back to browser defaults. The build still passed, because nothing
    checks that a class the stylesheet expects is actually present.
    """
    html = "<h2>Q1</h2><p>A1</p><h2>Q2</h2><p>A2</p>"
    result = to_details(html, "faq.md")
    assert result.count('<details class="faq-item">') == 2
    assert result.count('<div class="faq-answer">') == 2
    # The single wrapper is what js/faq.js scopes its expand-all control to.
    assert result.count('<div class="faq-list">') == 1
    assert result.startswith('<div class="faq-list">')
    assert result.endswith("</div>")


def test_faq_transform_keeps_preamble_outside_list():
    """Content before the first H2 stays outside the accordion wrapper."""
    html = "<p>Intro</p><h2>Q1</h2><p>A1</p>"
    result = to_details(html, "faq.md")
    assert result.startswith("<p>Intro</p>")
    assert result.index("<p>Intro</p>") < result.index('<div class="faq-list">')


def test_faq_transform_no_h2_raises():
    """to_details raises BuildError naming the file when there is no H2 heading."""
    with pytest.raises(BuildError, match="faq.md"):
        to_details("<p>No headings here.</p>", "faq.md")


# ---------------------------------------------------------------------------
# root_relative
# ---------------------------------------------------------------------------

def test_rootify_prefixes_relative_references():
    """rootify prefixes document-relative href/src/url() and leaves absolute ones alone."""
    html = (
        '<a href="about.html">About</a>'
        '<img src="images/hero.jpg">'
        '<style>body { background: url(images/bg.png); }</style>'
        '<a href="https://example.com">External</a>'
        '<a href="#section">Anchor</a>'
    )
    result = rootify(html)
    assert 'href="/about.html"' in result
    assert 'src="/images/hero.jpg"' in result
    assert "url(/images/bg.png)" in result
    assert 'href="https://example.com"' in result
    assert 'href="#section"' in result


# ---------------------------------------------------------------------------
# sitemap_writer
# ---------------------------------------------------------------------------

def test_sitemap_excludes_404_and_noindex(tmp_path):
    """write_sitemap excludes the 404 page and any noindex page."""
    out_dir = tmp_path / "_site"
    out_dir.mkdir()
    site = {"domain": "https://example.co.nz"}
    pages = [
        {"url": "index.html", "canonical": "https://example.co.nz/", "noindex": False},
        {"url": "404.html", "canonical": "https://example.co.nz/404.html", "noindex": True},
        {"url": "secret.html", "canonical": "https://example.co.nz/secret.html", "noindex": True},
    ]
    write_sitemap(out_dir, site, pages)
    text = (out_dir / "sitemap.xml").read_text(encoding="utf-8")
    assert "example.co.nz/</loc>" in text
    assert "404.html" not in text
    assert "secret.html" not in text


def test_search_visible_defaults_to_false(tmp_path):
    """A site.json with no search_visible key loads as hidden from search."""
    _write_site_json(tmp_path)

    config = load_site_config(tmp_path)

    assert config["search_visible"] is False


def test_search_visible_rejects_non_boolean(tmp_path):
    """A non-boolean search_visible raises BuildError naming the key."""
    _write_site_json(tmp_path, {"search_visible": "yes"})

    with pytest.raises(BuildError, match="search_visible"):
        load_site_config(tmp_path)


def test_robots_disallows_all_when_hidden(tmp_path):
    """write_robots refuses all crawlers and names no sitemap on a hidden site."""
    out_dir = tmp_path / "_site"
    out_dir.mkdir()

    write_robots(out_dir, {"domain": "https://example.co.nz", "search_visible": False})

    text = (out_dir / "robots.txt").read_text(encoding="utf-8")
    assert "Disallow: /" in text
    assert "Sitemap:" not in text


def test_robots_allows_all_when_visible(tmp_path):
    """write_robots allows all crawlers and names the sitemap on a visible site."""
    out_dir = tmp_path / "_site"
    out_dir.mkdir()

    write_robots(out_dir, {"domain": "https://example.co.nz", "search_visible": True})

    text = (out_dir / "robots.txt").read_text(encoding="utf-8")
    assert "Allow: /" in text
    assert "Sitemap: https://example.co.nz/sitemap.xml" in text


# ---------------------------------------------------------------------------
# checks
# ---------------------------------------------------------------------------

def test_check_output_detects_leftover_template_syntax(tmp_path):
    """check_output raises BuildError when a page still contains '{{' template syntax."""
    out_dir = tmp_path / "_site"
    out_dir.mkdir()
    (out_dir / "about.html").write_text(
        '<html><body><header></header><main class="hero">{{ page.title }}</main>'
        '<footer></footer></body></html>',
        encoding="utf-8",
    )
    (out_dir / "404.html").write_text("<html><body>Not found</body></html>", encoding="utf-8")
    (out_dir / "sitemap.xml").write_text("<urlset></urlset>", encoding="utf-8")
    (out_dir / "robots.txt").write_text("User-agent: *\n", encoding="utf-8")

    pages = [{"url": "about.html", "layout": "page"}]
    with pytest.raises(BuildError, match=r"\{\{"):
        check_output(out_dir, pages)
