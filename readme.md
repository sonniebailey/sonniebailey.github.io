# Website

This folder is the complete source of a small static website. It builds a handful of pages from plain text files and publishes them to Netlify. There is no database, no server-side code and no admin login.

If you are new here, whether a person or an AI assistant, read this file and then technical.md before changing anything.

## How the site works

- Page text lives in content/ as markdown files, one per page. Edit them in any text editor.
- Business details (name, legal name, tagline, phone, address, email, opening hours, navigation links, the banner and the footer note) live in content/site.json and appear wherever the templates use them. Legal name is used in the copyright line and falls back to the business name if left out; footer_note is an optional line of small print above it; both are optional.
- The banner is the notice sitting under the menu on every page, currently that the business is not taking new clients. It is the banner value in content/site.json. Change the wording there, or remove the line to remove the strip entirely.
- The business name appears in the top left as text, in the site's heading font. If you have a logo image, add `"logo": "images/logo.svg"` to content/site.json and it is used instead. Make sure it reads against the dark header and against the hero photograph, since the header sits over the photograph rather than above it.
- Colours and fonts live in the block at the top of css/variables.css marked BRAND. Most of the site is worked out from those eight values, so changing them changes the whole site. The dark surface colours are the exception: they are set by hand rather than derived, so this site matches the rest of the estate.
- The site is dark only. There is no light version and no sun/moon switch, so there is one set of colours to maintain.
- Running build.py turns all of that into ordinary HTML files in _site/. That folder is what visitors see.
- Netlify watches the GitHub repository. Every push to the default branch (master) rebuilds and publishes the site automatically. Nothing is uploaded by hand.

## What you need installed

- Python 3.12 (the version is pinned in .python-version)
- The three packages in requirements.txt: `pip install -r requirements.txt`
- For the photo optimiser only: `pip install pillow`

## Preview locally

    python3 preview.py

Builds the site and serves it at http://127.0.0.1:8000/. After editing a file, stop the server (Ctrl+C) and run it again, then refresh the browser. There is no automatic reload.

## Edit a page

Open the page's file in content/ (for example content/about.md). The block between the two `---` lines at the top is the page's settings; below it is the page text in markdown. The first line beginning with `# ` becomes the big heading in the hero banner.

## Add a page

1. Copy an existing file in content/, for example content/about.md to content/services.md. The file name becomes the address: services.md is published as services.html.
2. Change title, description and the text.
3. To show it in the menu, add a line to the nav list in content/site.json: `{ "label": "Services", "href": "services.html" }`.
4. Run preview.py and check it.

Page settings, all in the block at the top of the file:

- title and description: required. Used in the browser tab, search results and link previews.
- layout: required. `page` for a normal page, `faq` for a page where every `##` heading becomes a click-to-expand question, `home` for the home page only.
- hero_image: optional. Path to the banner image; defaults to images/hero.jpg. The home page gets a taller banner than the other pages automatically.
- cta: optional. A button in the hero, for example `cta: { label: "Book now", href: "contact.html" }`.
- show_map: optional. `true` shows the map (from site.json) at the bottom of the page. Only set it on pages where the map earns its place: the map is a Google embed, so those pages contact Google when they load.
- noindex: optional. `true` keeps the page out of search engines.

## Home page feature cards

The home page can show a row of cards under its text. They are set up in the block at the top of content/index.md, under `features`. Each card needs a title, a line of text and an icon:

    features:
      - title: Same-week appointments
        text: Most people get seen within a few days, not weeks.
        icon: calendar

The icon is a name, not a picture file. Available names: calendar, clock, users, activity, phone, pin, check, shield, star. An unrecognised name shows a plain dot rather than breaking the page. Do not use emoji here; they are drawn differently by every phone and computer and will not match the rest of the site.

## Frequently asked questions page

On a page with `layout: faq`, every `##` heading becomes a question that opens when clicked, and the text under it is the answer. An expand-all button appears above the list automatically. You do not need to add anything for it.

## Add a photo

Do not copy photos straight from a phone into images/: they are far too large and make the site slow. Run the optimiser first:

    python3 utils/optimise_images.py path/to/photo.jpg

It writes a resized, compressed copy into images/. Use `--max-width 800` for smaller card images. Then refer to the file from a page (`![Description](images/photo.jpg)`) or set it as hero_image.

## Change business details, colours or fonts

Either edit content/site.json and the BRAND block in css/variables.css directly, or run the settings page:

    python3 settings.py

and open http://127.0.0.1:8001/. It edits exactly those two files and nothing else. Rebuild afterwards to see the change. Saving rewrites site.json in a standard layout, so its spacing may change; the values do not.

## Publish

Commit and push to the default branch (master) on GitHub. Netlify builds and publishes within a minute or two. If the build fails (for example a page is missing its title), Netlify keeps the previous version live and shows the error in its deploy log; fix the file and push again. Run preview.py before pushing to catch problems locally: the build stops with a message naming the file and the field.

## Who can see the site

Netlify has its own control over who may view a project, separate from anything in this folder. A newly imported project can start private, which serves a "This site is private" sign-in page instead of the site, even though the build succeeded. It is changed in the project's access and security settings in the Netlify dashboard, and takes effect immediately with no redeploy.

That setting and the search engines setting below do different jobs, and a site being reviewed needs both: visitor access public, so anyone with the address can open it, and search visibility off, so it does not turn up in Google.

## Redirects

If a page is renamed, add a line to _redirects so old links keep working: `/old-page  /new-page.html  301`.

## Search engines

A new site is hidden from search engines. Every page carries a noindex tag and robots.txt refuses all crawlers, so the site works normally for anyone you give the address to but does not turn up in Google. This is what you want while the site is being built and reviewed.

To go live, set `"search_visible": true` in content/site.json and push. Every build says which state it is in, so you can confirm it in Netlify's deploy log.

Leave it true from then on. Deploying a hidden build after the site is live would take it out of Google, and getting back in takes time.

## Domain

The site's address for links, sitemap and search engines is the domain value in content/site.json. Change it if the site moves. Connecting a custom domain to Netlify is done in the Netlify dashboard (Domain management); it needs one A record and one CNAME at the domain's registrar and does not touch email records.
