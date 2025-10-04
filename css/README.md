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

---

# Technical Debt & Refactoring Plan

## Current Issues Summary

**Total identified issues:** 3 major categories
**Estimated complexity reduction:** ~100 lines of CSS, 51 !important removals, 6+ new variables

### Issue 1: !important Overuse (51 instances)
**Location:** responsive.css lines 91-96, 157-236
**Root cause:** Index page mobile layout uses `all: unset !important` because base CSS specificity is too high

### Issue 2: Magic Numbers (Not Variables)
**Problem:** Repeated hardcoded values that should be CSS variables
- `rgba(0, 0, 0, 0.1)` - used 6 times (dark overlay - light)
- `rgba(0, 0, 0, 0.2)` - used 3 times (dark overlay - medium)
- `rgba(0, 0, 0, 0.3)` - used 2 times (dark overlay - strong)
- `border-radius: 10px` - used 7 times
- `box-shadow: 0 4px 30px rgba(0, 0, 0, 0.1)` - used 4 times

### Issue 3: Container Pattern Complexity
**Problem:** 4 different container patterns doing similar things
- `.container` - base container
- `.glass-container` - container with glass effect
- `header .container` - header-specific overrides
- `footer .container` - footer-specific overrides

---

## Refactoring Strategy

### Phase 1: Add Missing Variables (No Breaking Changes)
**Goal:** Eliminate magic numbers by adding variables

**Add to variables.css:**
```css
/* Overlay/Shadow Variables */
--overlay-light: rgba(0, 0, 0, 0.1);
--overlay-medium: rgba(0, 0, 0, 0.2);
--overlay-strong: rgba(0, 0, 0, 0.3);
--shadow-standard: 0 4px 30px rgba(0, 0, 0, 0.1);
--border-radius-standard: 10px;
--border-radius-small: 4px;
```

**Replace throughout codebase:**
- Search: `rgba(0, 0, 0, 0.1)` → Replace with: `var(--overlay-light)`
- Search: `rgba(0, 0, 0, 0.2)` → Replace with: `var(--overlay-medium)`
- Search: `rgba(0, 0, 0, 0.3)` → Replace with: `var(--overlay-strong)`
- Search: `border-radius: 10px` → Replace with: `border-radius: var(--border-radius-standard)`
- Search: `border-radius: 4px` → Replace with: `border-radius: var(--border-radius-small)`
- Search: `0 4px 30px rgba(0, 0, 0, 0.1)` → Replace with: `var(--shadow-standard)`

**Effort:** 15 minutes
**Files affected:** components-content.css, components-core.css, base.css, responsive.css
**Risk:** None (purely additive)

---

### Phase 2: Fix Index Page Mobile Layout (!important removal)
**Goal:** Remove all 51 !important declarations

**Problem Analysis:**
Current approach (responsive.css lines 169-199):
- Uses `all: unset !important` to reset main/container
- Manually rewrites all glass effects with !important
- Fights against base.css specificity

**Better approach:**
1. Move index page mobile styles to higher specificity selector
2. Use existing `.glass` classes instead of duplicating properties
3. Restructure to work WITH cascade, not against it

**Step-by-step:**

**Step 2.1: Reduce base.css specificity**
- Change `header .container` → `header > .container` (direct child only)
- Change `footer .container` → `footer > .container` (direct child only)
- Prevents these from affecting index page deeply nested containers

**Step 2.2: Rewrite index mobile without !important**
Replace responsive.css lines 169-199 with:
```css
@media (max-width: 768px) {
    body[data-page="index"] main {
        /* Higher specificity - no !important needed */
        all: unset;
        display: block;
        position: relative;
        width: 100%;
        height: 100vh;
        pointer-events: none;
    }

    body[data-page="index"] main .glass-container {
        /* Use existing glass class */
        all: unset;
        position: fixed;
        top: 50%;
        left: 50%;
        transform: translate(-50%, -50%);
        /* ... rest without !important */
    }
}
```

**Step 2.3: Use utility classes for glass effects**
Instead of duplicating backdrop-filter/background-color, add class in HTML:
```html
<div class="container glass-container">
```
CSS naturally applies glass effect, no !important needed.

**Step 2.4: Fix table-of-contents overrides (lines 91-96)**
Replace:
```css
#table-of-contents {
    padding: 0 !important;
    background: none !important;
    /* ... more !important */
}
```

With higher specificity:
```css
@media (max-width: 768px) {
    .glass-container #table-of-contents.glass {
        padding: 0;
        background: none;
        /* ... no !important */
    }
}
```

**Effort:** 1-2 hours
**Files affected:** base.css, responsive.css
**Risk:** Medium (test index page thoroughly on mobile/tablet)

---

### Phase 3: Simplify Container System (Optional)
**Goal:** Reduce from 4 container patterns to 2

**Current complexity:**
- `.container` - max-width 800px, padding
- `.glass-container` - adds glass effect
- `header .container` - special overrides
- `footer .container` - special overrides

**Proposed simplification:**

**Option A: Merge glass into container (recommended)**
- Make `.container` always have max-width/padding
- Add `.glass` class separately when needed: `<div class="container glass">`
- Delete `.glass-container` entirely
- Update all HTML: `class="glass-container"` → `class="container glass"`

**Option B: Keep current (if uncertain)**
- Keep both `.container` and `.glass-container`
- Just better documentation of when to use which

**Effort:** 30 minutes (Option A), 5 minutes (Option B)
**Files affected:** All CSS files, all HTML files (if Option A)
**Risk:** High if Option A (breaking change), None if Option B

**Recommendation:** Start with Phase 1 & 2, defer Phase 3 until site is stable

---

## Implementation Checklist

### Phase 1: Variables (Safe, Quick Win)
- [ ] Add overlay/shadow/radius variables to variables.css
- [ ] Replace `rgba(0, 0, 0, 0.1)` → `var(--overlay-light)` (6 instances)
- [ ] Replace `rgba(0, 0, 0, 0.2)` → `var(--overlay-medium)` (3 instances)
- [ ] Replace `rgba(0, 0, 0, 0.3)` → `var(--overlay-strong)` (2 instances)
- [ ] Replace `border-radius: 10px` → `var(--border-radius-standard)` (7 instances)
- [ ] Replace `border-radius: 4px` → `var(--border-radius-small)` (instances)
- [ ] Replace shadow values with `var(--shadow-standard)` (4 instances)
- [ ] Test: Visual regression check (should look identical)

### Phase 2: !important Removal (Medium Risk)
- [ ] Update base.css: Change `header .container` → `header > .container`
- [ ] Update base.css: Change `footer .container` → `footer > .container`
- [ ] Rewrite responsive.css lines 169-199 with `body[data-page="index"]` higher specificity
- [ ] Remove all !important from index page mobile styles
- [ ] Fix TOC overrides (lines 91-96) with higher specificity
- [ ] Test: Index page mobile (< 768px) - glass card centered correctly
- [ ] Test: Index page tablet (768px) - glass card centered correctly
- [ ] Test: About/Testimonials pages mobile - no regressions
- [ ] Count: Verify 0 !important in responsive.css (was 51)

### Phase 3: Container Simplification (Optional, High Risk)
- [ ] Decision: Option A (merge) or Option B (keep current)
- [ ] If Option A: Update all HTML files (3 pages)
- [ ] If Option A: Remove `.glass-container` from CSS
- [ ] If Option A: Update this documentation
- [ ] Test: All pages, all breakpoints

---

## Testing Strategy

**After each phase:**

**Visual Regression:**
1. Screenshot all pages at: 1920px, 768px, 480px, 375px widths
2. Compare before/after screenshots
3. Check: glass effects, spacing, alignment

**Specificity Check:**
```bash
# After Phase 2, verify no !important
grep -c "!important" css/responsive.css
# Should output: 0
```

**Variable Usage Check:**
```bash
# After Phase 1, find any remaining magic numbers
grep -E "rgba\(0, 0, 0, 0\.[123]\)" css/*.css
grep "border-radius: [0-9]" css/*.css
# Should output: nothing
```

---

## Success Metrics

**Before refactoring:**
- !important count: 51
- Magic number instances: ~20
- CSS variables: 11
- Total CSS lines: ~1,400

**After refactoring (target):**
- !important count: 0 ✓
- Magic number instances: 0 ✓
- CSS variables: 17+ ✓
- Total CSS lines: ~1,300 (reduction via deduplication) ✓

**Maintainability improvement:**
- Single source of truth for colors/spacing/shadows
- Easier to override responsive styles
- Clearer cascade hierarchy
- Better alignment with CSS best practices

---

## Rollback Plan

If issues arise during Phase 2:

1. **Git workflow (if using version control):**
   ```bash
   git checkout -- css/base.css css/responsive.css
   ```

2. **Manual rollback:**
   - Keep backup of base.css and responsive.css before starting Phase 2
   - Name backups: `base.css.backup`, `responsive.css.backup`
   - Restore if needed

3. **Partial rollback:**
   - Phase 1 is safe, keep those changes
   - Only rollback Phase 2 changes
   - Document which specific change caused issue

---

## Notes & Warnings

**⚠️ Critical:**
- Always test index page mobile after changes - it's the most fragile
- Never remove !important without increasing specificity elsewhere
- Test on actual mobile devices, not just browser DevTools

**💡 Tips:**
- Do Phase 1 first - it's safe and gives quick wins
- Phase 2 requires careful testing but biggest improvement
- Phase 3 is optional - only if you want perfect cleanliness

**📝 After completion:**
- Update this section with "COMPLETED" dates
- Remove from "Current Issues Summary" at top
- Add lessons learned for future projects
