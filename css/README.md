# CSS Architecture

Consolidated CSS structure for small sites (3-10 pages).

## File Structure

```
css/
├── main.css                  # Import manager - loads all CSS in correct order
├── variables.css             # Theme variables and CSS custom properties
├── base.css                  # Reset, typography, layout (header/footer/containers)
├── components-core.css       # Global components (buttons, glass, navigation)
├── components-content.css    # Content components (expandables, TOC, tables)
├── page-modifiers.css        # Page-specific style overrides
└── responsive.css            # All media queries (must be last)
```

**Total: 7 CSS files, ~1,400 lines**

## Import Order (in main.css)

1. **variables.css** - Define all CSS custom properties first
2. **base.css** - Reset and foundational styles
3. **components-core.css** - Components used on every page
4. **components-content.css** - Components used in content areas
5. **page-modifiers.css** - Page-specific overrides
6. **responsive.css** - Media queries (must be last for proper cascade)

## File Details

### variables.css (~42 lines)
- Color scheme (links, text, borders)
- Glassmorphic effect variables
- Spacing scale (space-1 through space-10)
- Semantic spacing aliases
- Breakpoint definitions

### base.css (~372 lines)
**Reset & Base:**
- HTML/body reset
- Link styles
- Main content structure

**Typography:**
- Heading styles (h1-h6)
- Paragraph and list styles
- Scroll margin for fixed header

**Layout: Containers:**
- Base container
- Hero container
- Background image/overlay

**Layout: Header:**
- Fixed header with glassmorphic effect
- Container adjustments

**Layout: Footer:**
- Fixed footer with glassmorphic effect
- Footer content and icons

### components-core.css (~253 lines)
Components used on every page:

**Buttons:**
- `.button` - Primary call-to-action
- `.button-container` - Button grouping

**Glassmorphic:**
- `.glass` - Base glass effect
- `.glass--strong` - Stronger variant for nested elements
- `.glass--subtle` - Subtle variant
- `.glass-container` - Legacy support

**Navigation:**
- Logo and nav link styles
- Current page indicator
- Phone/mail icons
- Responsive navigation patterns

### components-content.css (~362 lines)
Components used in content areas:

**Disclosure:**
- Base expand/collapse pattern
- `.disclosure__header`, `.disclosure__content`
- `.disclosure__icon` - Plus/minus indicator

**Expandable Sections:**
- `.expandable-section` - Section container
- `.expandable-header`, `.expandable-content`
- `.expand-icon` - Expand indicator
- Glass container variants

**Table of Contents:**
- `#table-of-contents` - Auto-generated TOC
- Nested list styling
- Glass variant for containers

**Payment Table:**
- `.payment-table` - Pricing/payment table
- Opacity rows for visual hierarchy
- Responsive table container

### page-modifiers.css (~46 lines)
Page-specific style overrides using `[data-page]` attribute:

- `[data-page="index"]` - Index page layout adjustments
- `[data-page="about"]` - About page h2 positioning
- `[data-page="testimonials"]` - Placeholder for future styles

### responsive.css (~299 lines)
All media queries organized by breakpoint:

**Tablet (max-width: 768px):**
- Spacing adjustments
- Typography scaling
- Container patterns
- Navigation/footer responsive

**Mobile (max-width: 480px):**
- Further spacing reduction
- Typography adjustments
- Index page redesign
- Payment table horizontal scroll

## Adding New Styles

**New global component?** → Add to `components-core.css`

**New content feature?** → Add to `components-content.css`

**Page-specific style?** → Add to `page-modifiers.css` with `[data-page="pagename"]`

**New color/spacing?** → Add to `variables.css`

**Responsive adjustment?** → Add to `responsive.css` in appropriate breakpoint

## Migration History

**Previous structure:** 17 files across multiple folders (components/, layout/, pages/)

**Consolidated:** 7 files, flat structure (except main.css which imports others)

**Merged into base.css:**
- Old base.css (reset/base)
- typography.css (all typography)
- layout/header.css (header layout)
- layout/footer.css (footer layout)
- layout/containers.css (container layouts)

**Merged into components-core.css:**
- components/buttons.css
- components/glassmorphic.css
- components/navigation.css

**Merged into components-content.css:**
- components/disclosure.css
- components/expandable-sections.css
- components/table-of-contents.css
- components/payment-table.css

**Merged into page-modifiers.css:**
- pages/about.css (deleted - was redundant)

## Notes

- All pages reference `css/main.css` which imports everything in the correct order
- Responsive styles use CSS custom properties from variables.css for consistency
- Glass effects are centralized in components-core.css with modifiers
- Current known issue: responsive.css contains 51 `!important` declarations (tech debt)
