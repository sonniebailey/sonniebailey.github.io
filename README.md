# Fairhaven Wealth Website

Code for Fairhaven Wealth's website, hosted at www.fairhavenwealth.co.nz.

---

## Current State

This is a **working 3-page website** with:
- Clean, modular CSS structure (7 files, ~1,400 lines)
- Markdown-based content loading
- Glassmorphic design with responsive layout
- Consolidated architecture (reduced from 17 CSS files)

**Project health:** ⚠️ **Good for production, needs work for template use**

---

## Using as a Template for Future Sites

This codebase can serve as a starter for similar 3-10 page information websites, but **requires improvements first**.

### ✅ What's Already Good

**Structure & Organization:**
- Modular CSS: variables → base → components → responsive
- Centralized markdown loading with options
- Documented architecture (see `css/README.md`)
- No dead code or unused files
- 17 CSS variables for easy theming

**Patterns Established:**
- Glass morphic effects (`.glass` pattern)
- Page-specific styles (`[data-page]` attribute)
- Responsive breakpoints (tablet 768px, mobile 480px)
- Component-based organization

### ❌ What Needs Fixing for Template Use

**Priority order for template readiness:**

#### 1. **Accessibility** ⚠️ MEDIUM PRIORITY
- [ ] Add keyboard support to expandable sections (tabindex, Enter/Space keys)
- [ ] Add skip link for keyboard navigation
- [ ] Add ARIA landmarks (role="banner", role="main", etc.)

**Why:** New sites should be accessible from day one, not retrofitted later

---

#### 2. **JavaScript Modernization** 🟡 LOW PRIORITY
- [ ] Refactor promise chains to async/await
- [ ] Implement module pattern (remove global scope pollution)
- [ ] Add proper error handling

**Why:** Should teach modern patterns, not outdated 2015 code

---

#### 3. **Security Hardening** 🟡 LOW PRIORITY
- [ ] Add Subresource Integrity (SRI) to external scripts
- [ ] Implement Content Security Policy (CSP)
- [ ] Document security considerations for future sites

**Why:** Security best practices should be built-in, not added later

---

#### 4. **Optional: Container Simplification** 🔵 OPTIONAL
- [ ] Consolidate 4 container patterns to 2 (see `css/README.md` Phase 3)
- [ ] Update all HTML files if pursued

**Why:** Simpler mental model, but breaking change

---

## Template Readiness Checklist

### ✅ Ready to Use NOW (85% template-ready)
- Clean file structure
- Good documentation
- Reusable patterns
- Theme variables
- Clean CSS (no !important, proper specificity)

### 🎯 Complete for "Professional Template" (100% ready)
- Add basic accessibility (skip link, ARIA, keyboard support)
- Modern JavaScript patterns (async/await, modules)
- Security hardening (CSP, SRI)
- Optional: Container pattern simplification

---

## Key Files & Documentation

- **`css/README.md`** - Comprehensive CSS documentation and refactoring plan
- **`css/main.css`** - Import order and structure
- **`scripts.js`** - Centralized markdown loader and site functionality
- **`css/variables.css`** - Theme configuration (colors, spacing, effects)

---

## Quick Start for New Project

**To use this as a template:**

1. **Clone and rename**
   ```bash
   cp -r sonniebailey.github.io new-project-name
   cd new-project-name
   ```

2. **Update theme** (edit `css/variables.css`)
   - Colors: `--link-color`, `--text-color`
   - Spacing: Use existing `--space-*` scale
   - Effects: `--overlay-*`, `--shadow-standard`

3. **Replace content**
   - Update `index-content.md`, `about-content.md`, etc.
   - Modify `header.html` and `footer.html`
   - Update `<title>` tags in HTML files

4. **Consider adding** (from checklist above):
   - Basic accessibility (items 1.1-1.3)
   - Security hardening if handling sensitive data

---

## Known Issues / Technical Debt

**See `css/README.md` "Technical Debt & Refactoring Plan" for detailed breakdown.**

**Summary:**
1. ✅ ~~Magic numbers~~ → Resolved (converted to CSS variables)
2. ✅ ~~51 !important declarations~~ → Resolved (proper specificity)
3. ⏳ Container pattern complexity → Optional (see `css/README.md` Phase 2)
4. ⏳ No accessibility baseline → Items 1.1-1.3 above
5. ⏳ No security hardening → Items 3.1-3.2 above

---

## Development Notes

- **No build process** - Plain HTML/CSS/JS (consider adding Vite for production template)
- **No dependencies** - Only external CDN scripts (marked.js, plausible.io)
- **GitHub Pages ready** - Static site, works out of the box
- **WSL/Windows compatible** - Tested in WSL2 environment

---

## Lessons Learned (For Future Templates)

**Do from the start:**
- CSS variables for ALL repeated values (not just some)
- Accessibility markup (ARIA, roles, tabindex)
- Module pattern for JavaScript
- Security headers (CSP, SRI)
- Avoid high specificity selectors (prevents !important need)

**Architecture that worked well:**
- Flat CSS structure (no deep nesting of folders)
- Page-specific data attributes (`[data-page="name"]`)
- Markdown for content (non-technical editing)
- Single centralized loader function with options

**What would change:**
- Start with async/await (not promise chains)
- Build accessibility in from day 1 (not retrofit)
- Add basic build process for minification/optimization
- Document as you go (not retrospectively)

---

## Support & Updates

For questions or improvements, see commit history or `css/README.md` for detailed refactoring guidance.

**Last major refactor:** CSS consolidation (17 files → 7 files) + variable standardization
