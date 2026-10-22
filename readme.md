# Website

This folder is the complete source of a small static website. It builds a handful of pages from plain text files and publishes them to GitHub Pages. There is no database, no server-side code and no admin login.

If you are new here, whether a person or an AI assistant, read this file and then technical.md before changing anything.

## How the site works

- Page text lives in content/ as markdown files, one per page. Edit them in any text editor.
- Business details (name, legal name, tagline, phone, address, email, opening hours, navigation links, the banner and the footer note) live in content/site.json and appear wherever the templates use them. Legal name is optional and not currently shown on the site. The footer is pinned to the bottom of the screen on every page: footer_note if set and each of footer_links one per line on the left, and any opening hours, the email and the phone number one per line on the right. It shows no address or copyright line. On phones the footer is hidden and its contents (any opening hours, the email, footer_note and footer_links) appear at the bottom of the menu instead, with the phone number above the email, followed by an email icon and a large gold call button. The menu also starts with a Home link. footer_links is an optional list of small links, each with a label and an href, in the same shape as the nav list. It currently links the disclosure statement and privacy policy.
- The disclosure statement and privacy policy are disclosure.pdf and privacy.pdf in the top folder. To update one, replace the file and keep its name. Any PDF in the top folder is published at the top level of the site, eg fairhavenwealth.co.nz/disclosure.pdf.
- The banner is an optional notice under the menu on every page. It is the banner value in content/site.json, currently null, so no banner shows. Put wording there to bring it back.
- The home page shows the gold seedling from the site icon at the right of its heading on tablets and desktops, not on phones. It is the same image as the small seedling in the header.
- The home page shows a gold "Limited capacity" sticker as its main button under the text; the popup it opens ends with the home page's cta link. Other pages do not show the sticker. Clicking it opens a popup explaining how few clients the business takes on. The popup's wording is in content/snippets/capacity.md, edited like any page: the `# ` line is not shown (the sticker across the popup's top edge acts as its heading) but names the popup for screen readers, and the paragraphs below it are its text. It has no settings block at the top. The words on the sticker itself are fixed in templates/partials/capacity_dialog.html.
- The business name appears in the top left as text, in the site's heading font. If you have a logo image, add `"logo": "images/logo.svg"` to content/site.json and it is used instead. Make sure it reads against the dark header, which sits over the background photograph.
- Colours and fonts live in the block at the top of css/variables.css marked BRAND. Most of the site is worked out from those eight values, so changing them changes the whole site. The dark surface colours are the exception: they are set by hand rather than derived, so this site matches the rest of the estate.
- The site is dark only. There is no light version and no sun/moon switch, so there is one set of colours to maintain.
- Running build.py turns all of that into ordinary HTML files in _site/. That folder is what visitors see.
- GitHub builds the site itself. Every push to the default branch (main) runs the workflow in .github/workflows/pages.yml, which rebuilds the site and publishes it to GitHub Pages. Nothing is uploaded by hand.

## What you need installed

- Python 3.12 (the version is pinned in .python-version)
- The three packages in requirements.txt: `pip install -r requirements.txt`
- For the photo optimiser only: `pip install pillow`

## Preview locally

    python3 preview.py

Builds the site and serves it at http://127.0.0.1:8000/. After editing a file, stop the server (Ctrl+C) and run it again, then refresh the browser. There is no automatic reload.

## Edit a page

Open the page's file in content/ (for example content/about.md). The block between the two `---` lines at the top is the page's settings; below it is the page text in markdown. The first line beginning with `# ` becomes the page's big heading, at the top of the page. To hide a paragraph on phones, put `{: .hide-on-phone }` on the line directly below it.

## Add a page

1. Copy an existing file in content/, for example content/about.md to content/services.md. The file name becomes the address: services.md is published as services.html.
2. Change title, description and the text.
3. To show it in the menu, add a line to the nav list in content/site.json: `{ "label": "Services", "href": "services.html" }`.
4. Run preview.py and check it.

Page settings, all in the block at the top of the file:

- title and description: required. Used in the browser tab, search results and link previews.
- layout: required. `page` for a normal page, `faq` for a page where every `##` heading becomes a click-to-expand question, `home` for the home page only.
- hero_image: optional. Path to the page's photograph (a .jpg); defaults to images/hero.jpg. It fills the screen behind the page, darkened and blurred. A .webp copy with the same name must sit beside it, since browsers load the WebP and fall back to the JPG; without it the page shows no photograph.
- cta: optional. A gold button: on the home page it sits at the bottom of the Limited capacity popup (and under the text for visitors without JavaScript), on other pages beside the heading. For example `cta: { label: "Book now", href: "contact.html" }`.
- intro: optional. A line of text shown under the page heading (page and faq layouts). For example `intro: Some kind words from clients are below.`
- show_map: optional. `true` shows the map (from site.json) at the bottom of the page. Only set it on pages where the map earns its place: the map is a Google embed, so those pages contact Google when they load.
- noindex: optional. `true` keeps the page out of search engines (used by the 404 page).

## Frequently asked questions page

On a page with `layout: faq`, every `##` heading becomes a question that opens when clicked, and the text under it is the answer. An expand-all button appears above the list automatically, at the right; on phones it is half the width of the row. You do not need to add anything for it.

Text above the first `##` heading is not part of the list: it stays on show, sits above the expand-all button, and is not opened or closed by it. The About page uses this for its opening paragraphs. A single short line that belongs with the heading is better set as `intro` instead.

## Add a photo

Do not copy photos straight from a phone into images/: they are far too large and make the site slow. Run the optimiser first:

    python3 utils/optimise_images.py path/to/photo.jpg

It writes a resized, compressed copy into images/. Use `--max-width 800` for smaller card images. Then refer to the file from a page (`![Description](images/photo.jpg)`) or set it as hero_image.

## Change business details, colours or fonts

Either edit content/site.json and the BRAND block in css/variables.css directly, or run the settings page:

    python3 settings.py

and open http://127.0.0.1:8001/. It edits exactly those two files and nothing else. Rebuild afterwards to see the change. Saving rewrites site.json in a standard layout, so its spacing may change; the values do not.

## Publish

Commit and push to the default branch (main) on GitHub. GitHub builds and publishes within a minute or two; progress and any errors are under the repository's Actions tab. If the build fails (for example a page is missing its title), the previous version stays live; fix the file and push again. Run preview.py before pushing to catch problems locally: the build stops with a message naming the file and the field.

The repository's Pages setting (Settings, Pages, Build and deployment) must be "GitHub Actions". The same page holds the custom domain.

## Redirects

GitHub Pages has no redirect rules. If a page is renamed, keep a small page at the old address that sends the visitor on: a file whose head contains `<meta http-equiv="refresh" content="0; url=/new-page.html">` and a link to the new page. The page and PDF names match the previous site, so none is needed today.

## Search engines

Search visibility is one setting, `search_visible` in content/site.json. It is true: pages carry no noindex tag, robots.txt allows all crawlers and names the sitemap. Every build says which state it is in, so you can confirm it in the build log under the Actions tab.

Set it to false only for a site that is being built and reviewed and must not turn up in Google: every page then carries a noindex tag and robots.txt refuses all crawlers, while the site still works for anyone you give the address to.

Leave it true from then on. Deploying a hidden build after the site is live would take it out of Google, and getting back in takes time.

## Domain

The site's address for links, sitemap and search engines is the domain value in content/site.json. Change it if the site moves. It is the bare domain, fairhavenwealth.co.nz, matching the custom domain in the repository's Pages settings; the www form is not served. The domain's DNS lives at the registrar and is not touched by anything in this folder. The registrar is Crazy Domains (which took over Domains4Less), and the zone is on its Free DNS Service. The zone holds four A records pointing the bare domain at GitHub Pages, a www CNAME to the bare domain, Google Workspace MX records for email, a Mailchimp DKIM CNAME and an SPF TXT record. The domain is delegated to ns1 and ns2.crazydomains.com; it was left on the retired Domains4Less nameservers until October 2026, which took the site and inbound email down for a morning. Any change to where the site or email lives is made in that zone. The full record of the zone, the outage and the registrar account (including the lapsed Domain Guard) is in the infrastructure project at infrastructure/technical/domains.md.
