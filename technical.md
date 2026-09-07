# Technical notes

How the site is built, for whoever maintains it. readme.md covers day-to-day editing; this covers the machinery.

## Stack

- Python 3.12 build script: Jinja2 templates, python-markdown (extensions extra and smarty), PyYAML for page settings. Pinned in requirements.txt.
- Output is plain HTML, CSS and four small vanilla JavaScript files. No framework, no bundler.
- Hosted on Netlify, connected to the GitHub repository. netlify.toml gives Netlify the build command and the folder to publish.
- Pillow is used only by utils/optimise_images.py, not by the build.

## Folder layout

- content/ - one markdown file per page, plus site.json
- templates/ - Jinja2 templates: base.html (page shell and head), page.html, home.html, faq.html, partials/header.html, partials/footer.html, partials/logo.html, partials/theme-preload.html, partials/theme-toggle.html, partials/icons.html
- css/ - main.css imports variables.css, base.css, prose.css, components.css, responsive.css in that order
- js/ - theme.js (light/dark switch), menu.js (mobile menu), reveal.js (scroll-in animation), faq.js (expand/collapse all)
- images/ - images as published; the build copies this folder unchanged
- build.py and build/ - the build; build/orchestrator.py runs the steps in order
- preview.py - build then serve _site/ locally
- settings.py and settings.html - local editor for site.json and the brand block; never published
- utils/optimise_images.py - photo resizer
- tests/ - pytest tests for the build modules
- _redirects - Netlify redirect rules, copied to the output
- _site/ - build output, ignored by git, recreated on every build

## Build steps

build/orchestrator.py run_build, in order:

1. site_config.load_site_config reads content/site.json and checks every required key (name, tagline, domain, phone.display, phone.tel, email, address.lines, address.single_line, hours, nav, favicon, social_image, fonts.heading, fonts.body, fonts.google_css; logo is optional; map is optional and, if present, needs embed_url and link_url).
2. page_loader.load_pages reads every content/*.md, splits the YAML front matter, checks title, description and layout (page, home or faq), applies defaults (hero_image images/hero.jpg, noindex false, show_map false), checks the hero image exists, checks the shape of cta and features, and derives the URL from the file name.
3. output.prepare_output empties _site/ (retrying briefly if a sync client such as Dropbox holds a lock).
4. For each page: markdown_render.render_body lifts the first H1 out as the hero title and renders the rest to HTML; faq_transform.to_details wraps each H2 section in a details.faq-item (answer inside a div.faq-answer), collected into a single div.faq-list, for faq pages; page_renderer.render_page renders the template named after the layout; root_relative.rootify rewrites 404.html's links to start with / so it works from any path.
5. output.copy_assets copies css/, js/, images/ and _redirects.
6. sitemap_writer writes sitemap.xml (every page except 404 and noindex pages) and robots.txt.
7. checks.check_output reads the output back and fails the build if any page is missing its header, footer, hero or main, still contains template syntax, links to a css/js/image file that does not exist, has the wrong number of current-page markers, or if 404.html, sitemap.xml or robots.txt is missing.

Any problem raises BuildError with the file and field named, build.py prints it and exits 1. There are no fallbacks: a broken page is never published.

## Template context

Every template receives: site (the site.json object), page (title, description, url, canonical, hero_image, cta, features, noindex, show_map, layout), hero_title, content (rendered body HTML), build (year). Templates run with StrictUndefined, so referring to a value that does not exist fails the build rather than rendering blank.

The header shows site.name as a text wordmark in the heading font. Setting logo in site.json to an image path swaps in that image instead. The wordmark is the default because a bitmap logo cannot recolour for dark mode, so it has to be legible on both a light and a dark header or shipped twice; a business with a real logo should supply an SVG that inherits currentColor.

The header marks the current page by comparing page.url with each nav item's href, adding class is-current and aria-current on the desktop nav and again on the mobile menu.

## Head and SEO

base.html sets the title (site name and tagline on the home page, page title and site name elsewhere), meta description, canonical link built from site.json domain, Open Graph tags with site.json social_image as the default image, a Twitter card tag, the favicon, the Google Fonts stylesheet from site.json fonts.google_css and css/main.css. A page with noindex true also gets a robots noindex meta tag and is left out of the sitemap.

Search visibility is a whole-site setting, separate from the per-page noindex flag. site.json search_visible is optional and defaults to false, applied by site_config.load_site_config so the value is always present downstream. False puts `<meta name="robots" content="noindex, nofollow">` in every page head and makes sitemap_writer.write_robots emit a `Disallow: /` robots.txt with no Sitemap line; true restores the allow-all robots.txt naming the sitemap, and the per-page noindex flag applies as before. The sitemap itself is written either way, so the post-build check for its presence needs no special case. The orchestrator logs which state every build is in, in both directions, so the state is readable in the Netlify deploy log.

The default is false rather than true because the two mistakes are not equal: a forgotten key leaves a finished site unlisted, which one commit fixes, whereas the reverse would put a client's unfinished draft in front of Google. A new site is therefore hidden from its first build, and going live is a single deliberate edit. Treat that edit as one-way: once a site is live, deploying a hidden build would remove it from search results.

## CSS

css/variables.css is the only file that contains literal colours, sizes and font names. Everything else references them as var(--token). The BRAND block at the top holds the eight values a new site changes (primary, primary dark, accent, background, text, heading font, body font, corner radius); all other tokens derive from those, mostly through color-mix, so changing the brand moves the tints, scrims, shadows and dark palette with it. Breakpoint numbers in responsive.css are the one exception, because media queries cannot use variables.

Derived tokens are grouped by what they are for: a four-step brand tint ramp for hovers, rules and fills; surface colours where raised surfaces are translucent rather than solid, so the ground texture shows through and cards brighten on hover; brand-tinted shadows, because flat black shadows read as grey smudges on a warm background; motion tokens (easing curves and durations); per-area rhythm tokens (hero, section, card, feature gap, content inset) that responsive.css restages at each breakpoint; and a type scale with semantic prose tiers layered on top, so components reference the tier rather than a raw size.

A derivation is a default, not a constraint. Where a particular brand needs a hand-tuned value, overwrite the derived token directly; nothing depends on it having been computed.

The layers have distinct jobs and rules do not cross between them. base.css owns the reset, the heading system and the page furniture (header, hero, footer). prose.css owns running text inside main: the vertical rhythm between blocks, lists, quotes, rules, tables, code and captions. components.css owns discrete components (nav, wordmark, cards, FAQ, theme toggle, map). responsive.css restages tokens at each breakpoint.

Spacing between a page's main blocks has one owner. main > .container in base.css is a grid whose gap is --section-gap, with --section-padding-block as its top padding and --section-gap at the bottom; the footer's own top padding, also --section-gap, closes the page. The two tokens are deliberately different sizes: --section-padding-block is the air either side of a change of register, below the hero and above the footer, while --section-gap is the smaller join between two pieces of ordinary content within the page. The gap before the footer is deliberately shared between the two sides of that join rather than sitting wholly inside the footer. The footer paints its own background, so the join is a visible colour boundary, and padding added inside the footer sits below that line: it separates the footer's text from the boundary but does nothing to stop the page's last block touching the edge of its own section. Using one value for both put a full hero gap between the home page's text and its feature cards, which read as a hole rather than as breathing room. The FAQ page takes --section-gap for its top padding too, via a :has() rule, because it opens on a small right-aligned control rather than a body of text. The blocks it lays out (.prose, .features, .faq-page, .map-embed) carry no vertical padding or margin of their own, so a new block added to a template is spaced correctly without being told to be. This replaced an arrangement where each block padded both its top and its bottom with a full --section-padding-block, which rendered a doubled gap at every join between two of them: text to feature cards, text to map, map to footer, and text to footer on a page with no map. The rule is scoped to main because the header and footer share the .container class and keep owning their own padding. main > .container > * sets min-width: 0, since a grid item does not shrink below its content by default and a wide table or code block in .prose would otherwise stretch the page.

Type is defined by role, not by level. variables.css holds the raw scale, then names tiers on top of it (--font-size-heading-section, -sub, -minor, -card for headings; --font-size-lead, -prose, -secondary, -caption for running text). base.css maps each heading level to a tier once; everything else references the tier. responsive.css steps the tiers down together at each breakpoint, so the intervals between levels stay proportional rather than the largest heading collapsing onto the others.

Font weights are tokens (--weight-body, -medium, -semibold, -heading) and only weights actually listed in the Google Fonts URL in site.json may be given values. Asking for a weight that was not loaded makes the browser synthesise a fake bold, which is a common and hard-to-place cause of type looking inconsistent from one component to the next. Changing the fonts means checking the weights in that URL against these four tokens.

Vertical rhythm is tokenised as --flow-gap (between paragraphs), --flow-gap-heading-top and -top-minor (above a heading), --flow-gap-heading-bottom (below one) and --flow-gap-block (around quotes, images, tables). The asymmetry is deliberate: a heading is given more space above than below so it binds to the text it introduces. Equal margins are what make a page read as evenly but arbitrarily spaced.

prose.css works off elements alone, never classes, because an author writing markdown cannot add one. Every element markdown can emit is styled, including ones a brochure site is unlikely to use (code, tables), since an unstyled element falls back to browser defaults that visibly do not belong to the rest of the page.

--ground-texture paints a faint tinted pattern under the page and header via body::before, so surfaces read as a material rather than flat colour. Set it to a url() of a tileable image for a real texture, or to none to switch it off.

The hero is two layers over the photograph: --hero-wash, a diagonal brand gradient that pulls the image towards the site's colour, and --hero-scrim, which holds a plateau of darkness behind the heading before falling away, so the text is legible without dimming the whole image evenly.

Hero height is a vh value paired with a px floor: --hero-min-height (home) and --hero-min-height-interior (every other page, applied by the hero--interior class). responsive.css also lowers these under max-height queries, so landscape phones and short laptop screens do not get a banner that fills the viewport.

settings.py edits only the lines between the BRAND markers, so keep one token per line in the form `--name: value;`. Everything added below the markers is invisible to it.

## Light and dark mode

The theme is a data-theme attribute on the html element. variables.css defines the light palette on :root and overrides only the colour tokens under [data-theme="dark"]; spacing, type and motion are shared between the two.

templates/partials/theme-preload.html is an inline script in the head, ahead of the stylesheet. It resolves the theme in this order: the visitor's saved choice in localStorage under the key site-theme, then their operating system setting via prefers-color-scheme, then light. Because it runs before first paint, the page never flashes the wrong theme. It is deliberately self-contained and must not be made to depend on js/theme.js, which loads later.

There is no prefers-color-scheme media query in the CSS. The preload script resolves the OS setting into the attribute, so the attribute is the single source of truth and a visitor's explicit choice always wins.

templates/partials/theme-toggle.html is the sun/moon button, included twice (header and mobile menu). Both icons are always in the markup; components.css shows the one matching the current theme. js/theme.js handles clicks and keeps aria-label and aria-pressed accurate on every toggle on the page.

Dark surfaces derive from the brand text colour rather than pure black, so the dark theme keeps the brand's temperature. Link and accent colours are lifted towards white in dark mode, because fully saturated brand colours vibrate against dark backgrounds.

## Responsive

responsive.css restages the token values at each breakpoint rather than only resizing individual components, so the page recomposes at each size instead of shrinking uniformly. Each block redefines the per-area rhythm tokens, the hero wrap width and the type sizes; component rules are limited to what a token cannot express, such as swapping the desktop nav for the burger or collapsing the feature grid to one column.

Breakpoints: 768px (tablet), 480px (mobile), and two max-height queries (749px and 520px). The height queries exist because a hero sized in vh fills the screen on landscape phones and short laptops, which no width breakpoint catches. Both queries lower the vh share as well as the px floor: raising the share is self-defeating, because on a short screen a larger share is also a larger banner in absolute terms.

## JavaScript

Each file is self-contained, has JSDoc comments and starts with `// @ts-check`. Each runs on DOMContentLoaded and does nothing if its markup is absent, so removing a feature from the templates needs no JS change.

- theme.js: switches the theme and keeps the toggle's aria-label and aria-pressed accurate. See Light and dark mode below.
- faq.js: reveals the .faq-toggle-all button and wires it to open or close every question at once, re-syncing its label when a visitor opens one by hand. The accordions themselves are native details elements and work without it.
- menu.js: toggles the mobile menu (button.menu-toggle and nav#mobile-menu), closes on Escape, returns focus.
- reveal.js: adds is-visible to elements with class reveal as they scroll into view. Does nothing when the visitor prefers reduced motion or the browser lacks IntersectionObserver; the CSS keeps those elements visible.

## Tests

    python3 -m pytest tests

Covers front matter validation, site.json validation, H1 lifting, the FAQ transform (including the class names the stylesheet targets), root-relative rewriting, sitemap contents and the leftover-syntax check. Tests build their own tiny site in a temporary folder and do not depend on the real content.

## Deploy

netlify.toml: build command `pip install -r requirements.txt && python3 build.py`, publish folder _site. .python-version pins Python 3.12 for Netlify's build image. A failed build leaves the previous deploy live.

Netlify reads _redirects natively and serves a root 404.html for unknown paths automatically.

## Known limitations

- No file watcher in preview.py; rerun it after edits.
- A page with show_map set loads a Google Maps iframe on view, so Google is contacted on that page whether or not the visitor looks at the map. This replaced a click-to-load facade, which avoided the request but put a control between the visitor and the one thing a contact page exists to show. The embed stays opt-in per page to keep the cost off pages that do not need it.
- Nothing checks that a class the stylesheet targets is actually present in the built page. faq_transform.py once emitted bare details elements while every FAQ rule targeted .faq-item, so the accordion fell back to browser defaults and the build still passed. A unit test now guards that specific contract, but the general gap remains: the markup hooks documented as contracts in components.css are enforced only by whichever tests happen to assert them.
- Feature card icons come from a fixed set in templates/partials/icons.html, named from a page's frontmatter. Adding an icon means editing that template, which is a step a non-technical owner will not take unaided.
- Fonts load from Google Fonts. Self-hosting would remove the external request; it is a per-site choice.
