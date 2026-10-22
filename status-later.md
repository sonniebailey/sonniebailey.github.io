# Status later

Deliberately parked work, not actively pursued. Items move back to status.md when they become active.

## After launch

Parked until the rebuild has replaced the live site (decided). The single-page design points every copy's canonical at index.html, so it changes how the site appears in search; launching first with three separate pages keeps the live site's search standing unchanged.

- DECISION: add an end-to-end build test before the single-page build.
  Recommended, not chosen. tests/test_build.py tests modules one at a time;
  nothing runs run_build on a tiny fixture site and checks the output files,
  titles, 404 root-relativity, sitemap and robots. Written now it survives the
  restructure with only its assertions adjusted.

- Build the single-page site: scoped and decided, see technical.md, Single
  page. Panes side by side sliding in a loop, same document written per pane,
  history per slide, canonical to index.html, nav plus swipe plus arrow keys,
  no-JS copies each show their own pane. Known breakage to work through, all
  implementation not decisions: body padding for the fixed header and footer
  moves to the panes (base.css); menu.js's overflow lock and focus return must
  not fight the slide's focus move; reveal.js needs the pane as its observer
  root; faq.js loops panes with unique ids; orchestrator renders all panes once
  and writes per copy; checks.py current-marker rule rewritten; 404 excluded
  from the pane set; tests rewritten; sonnie.png lazy-loaded; in-prose links to
  pane files and fragment links inside a pane intercepted; sticker button
  disabled mid-slide. Then readme.md (Add a page, Redirects) and technical.md
  (Build steps, Trial layout, JavaScript) updated to the built reality and the
  "not yet built" line removed from the Single page section. Afterwards,
  DECISION: whether to add a Playwright smoke test for the slide (load the
  preview, click each nav item, check the address and visible pane); a new
  kind of test for this project.

