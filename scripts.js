document.addEventListener('DOMContentLoaded', function() {
    // Load header elements into head section
    fetch('header-elements.html')
        .then(response => response.text())
        .then(data => {
            document.head.insertAdjacentHTML('beforeend', data);
        })
        .catch(error => console.error('Error loading header elements:', error));

    // Load header
    fetch('header.html')
        .then(response => response.text())
        .then(data => {
            document.getElementById('header-placeholder').innerHTML = data;

            // Add current page indicator after header is loaded
            const currentPage = window.location.pathname.split('/').pop() || 'index.html';
            document.querySelectorAll('.nav-links a').forEach(link => {
                if (link.getAttribute('href') === currentPage) {
                    link.classList.add('current');
                }
            });
        })
        .catch(error => console.error('Error loading header:', error));
    
    // Load footer
    fetch('footer.html')
        .then(response => response.text())
        .then(data => {
            document.getElementById('footer-placeholder').innerHTML = data;
        })
        .catch(error => console.error('Error loading footer:', error));

});

/**
 * Load and parse markdown content with optional features.
 *
 * Args:
 *   file: Path to markdown file
 *   containerId: ID of element to insert parsed content
 *   options: Configuration object
 *     - generateTOC: Generate table of contents (default: false)
 *     - enableExpandable: Enable expandable sections (default: true)
 *     - onLoad: Callback function after content loaded
 *
 * Returns:
 *   Promise that resolves when content is loaded
 *
 * LLM Note: Expandable extension handles both [expand] tags and h4 headers.
 * Always sets up click handlers if expandable sections exist.
 */
function loadMarkdownContent(file, containerId, options = {}) {
    const config = {
        generateTOC: options.generateTOC || false,
        enableExpandable: options.enableExpandable !== false, // default true
        onLoad: options.onLoad || null
    };

    // Configure marked.js with expandable extension
    if (config.enableExpandable) {
        marked.use({
            extensions: [{
                name: 'expand',
                level: 'block',
                start(src) {
                    return src.match(/^\[expand\]|\n####\s/)?.index;
                },
                tokenizer(src) {
                    // Check for [expand] tags first
                    const expandRule = /^\[expand\]([\s\S]*?)\[\/expand\]/;
                    const expandMatch = expandRule.exec(src);
                    if (expandMatch) {
                        return {
                            type: 'expand',
                            raw: expandMatch[0],
                            content: expandMatch[1].trim()
                        };
                    }

                    // Check for h4 headers
                    const h4Rule = /^####\s+(.+?)(?:\n([\s\S]*?)(?=\n#{1,4}\s|$)|\n*$)/;
                    const h4Match = h4Rule.exec(src);
                    if (h4Match) {
                        return {
                            type: 'expand',
                            raw: h4Match[0],
                            title: h4Match[1],
                            content: h4Match[2] || ''
                        };
                    }
                },
                renderer(token) {
                    const title = token.title || token.content.split('\n')[0];
                    const content = token.title ? token.content : token.content.split('\n').slice(1).join('\n');

                    return `<div class="expandable-section glass glass--strong">
                        <div class="expandable-header">
                            <h4>${title}</h4>
                            <div class="expand-icon"></div>
                        </div>
                        <div class="expandable-content">
                            ${marked.parse(content)}
                        </div>
                    </div>`;
                }
            }]
        });
    }

    // Fetch and parse markdown content
    return fetch(file)
        .then(response => response.text())
        .then(text => {
            const parsedContent = marked.parse(text);
            document.getElementById(containerId).innerHTML = parsedContent;

            // Generate TOC if requested
            if (config.generateTOC) {
                generateTableOfContents();
            }

            // Add click handlers for expandable sections
            if (config.enableExpandable) {
                document.querySelectorAll('.expandable-header').forEach(header => {
                    header.addEventListener('click', () => {
                        header.parentElement.classList.toggle('expanded');
                        header.nextElementSibling.classList.toggle('expanded');
                    });
                });
            }

            // Call callback if provided
            if (config.onLoad) {
                config.onLoad();
            }
        })
        .catch(error => console.error(`Error loading ${file}:`, error));
}

function generateTableOfContents() {
    const content = document.querySelector('#content');
    const headings = content.querySelectorAll('h2'); // Changed from 'h2, h3'
    const toc = document.createElement('div');
    toc.id = 'table-of-contents';
    toc.className = 'glass';
    
    const tocTitle = document.createElement('h2');
    tocTitle.textContent = 'Table of Contents';
    toc.appendChild(tocTitle);

    const tocList = document.createElement('ul');
    let currentList = tocList;
    let previousLevel = 2;

    headings.forEach((heading, index) => {
        const level = parseInt(heading.tagName.charAt(1));
        const listItem = document.createElement('li');
        const link = document.createElement('a');
        link.textContent = heading.textContent;
        link.href = `#heading-${index}`;
        listItem.appendChild(link);

        if (level > previousLevel) {
            const subList = document.createElement('ul');
            currentList.lastElementChild.appendChild(subList);
            currentList = subList;
        } else if (level < previousLevel) {
            currentList = tocList;
        }

        currentList.appendChild(listItem);
        previousLevel = level;

        // Add id to the heading
        heading.id = `heading-${index}`;
    });

    toc.appendChild(tocList);

    // Find the first h2 element
    const firstH2 = content.querySelector('h2');

    // Insert the table of contents before the first h2 element
    if (firstH2) {
        firstH2.parentNode.insertBefore(toc, firstH2);
    } else {
        // If there's no h2, append it to the end of the content
        content.appendChild(toc);
    }
}