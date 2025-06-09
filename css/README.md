# CSS Architecture

This directory contains the refactored CSS for the Fairhaven Wealth website, organized following DRY and SRP principles.

## Structure

- **main.css** - Entry point that imports all other CSS files in the correct order
- **variables.css** - CSS custom properties and theme configuration
- **base.css** - Reset styles and base element styling
- **typography.css** - All typography-related styles (headings, paragraphs, lists)
- **utilities.css** - Utility classes (currently empty, reserved for future use)
- **responsive.css** - All media queries and responsive styles

### /layout
- **header.css** - Header-specific styles
- **footer.css** - Footer-specific styles
- **containers.css** - Container and layout structure styles

### /components
- **buttons.css** - Button styles
- **navigation.css** - Navigation menu styles
- **table-of-contents.css** - Table of contents component
- **expandable-sections.css** - Collapsible/expandable section styles
- **payment-table.css** - Payment table styles (About page)
- **glassmorphic.css** - Glass effect styles

### /pages
- **index.css** - Index page specific styles
- **about.css** - About page specific styles
- **testimonials.css** - Testimonials page specific styles (placeholder)

## Migration Notes

The original `styles.css` file (812 lines) has been split into these modular files. The old `styles.css` file in the root directory can now be deleted.

All HTML files have been updated to reference `css/main.css` instead of `styles.css`. 