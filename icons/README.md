# Icons

Convention: devkit/aesthetics/icons-convention.md

The generator script (`generate_variants.py`) was copied from
`devkit/aesthetics/image-resizing/`. Re-copy occasionally to pick up
improvements.

Usage:
    python3 generate_variants.py --yes --targets web-favicon

Leave out og-image: og-image.png is the hand-made share card (lake photo,
seedling and name, from artifact/share-image-mockups.html option D), and the
generator's default set would overwrite it with a plain icon card.

icon-print.svg and icon-print-reversed.svg are black and white versions of
the same mark for print. They are reference files only: nothing links them
and the generator does not read them.
