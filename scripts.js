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
        })
        .catch(error => console.error('Error loading header:', error));
    
    // Load footer
    fetch('footer.html')
        .then(response => response.text())
        .then(data => {
            document.getElementById('footer-placeholder').innerHTML = data;
        })
        .catch(error => console.error('Error loading footer:', error));
        
    var video = document.getElementById('bgVideo');
    video.playbackRate = 0.5;

    // Pause video on scroll
    window.addEventListener('scroll', function() {
        if (!video.paused) {
            video.pause();
        }
    });

    // Generate table of contents for about page
    if (window.location.pathname.includes('about.html')) {
        generateTableOfContents();
    }

    // Add current page indicator
    const currentPage = window.location.pathname.split('/').pop() || 'index.html';
    document.querySelectorAll('.nav-links a').forEach(link => {
        if (link.getAttribute('href') === currentPage) {
            link.classList.add('current');
        }
    });

    // Add this before the fetch call
    marked.use({
        extensions: [{
            name: 'expand',
            level: 'block',
            start(src) {
                return src.match(/^\[expand\]/)?.index;
            },
            tokenizer(src) {
                const rule = /^\[expand\]([\s\S]*?)\[\/expand\]/;
                const match = rule.exec(src);
                if (match) {
                    return {
                        type: 'expand',
                        raw: match[0],
                        content: match[1].trim()
                    };
                }
            },
            renderer(token) {
                return `<div class="expandable-section">
                            <div class="expandable-header">
                                <h4>${token.content.split('\n')[0]}</h4>
                                <div class="expand-icon"></div>
                            </div>
                            <div class="expandable-content">
                                ${marked.parse(token.content.split('\n').slice(1).join('\n'))}
                            </div>
                        </div>`;
            }
        }]
    });

    // Update the existing fetch callback
    fetch('about-content.md')
        .then(response => response.text())
        .then(text => {
            const parsedContent = marked.parse(text);
            document.getElementById('content').innerHTML = parsedContent;
            generateTableOfContents();
            
            // Add click handlers for expandable sections
            document.querySelectorAll('.expandable-header').forEach(header => {
                header.addEventListener('click', () => {
                    header.parentElement.classList.toggle('expanded');
                    header.nextElementSibling.classList.toggle('expanded');
                });
            });
        });
});

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

function initializeExpandableSections() {
    const content = document.getElementById('content');
    const headers = content.querySelectorAll('h3, h4');
    
    headers.forEach(header => {
        // Skip headers in the table of contents
        if (header.closest('#table-of-contents')) return;
        
        // Create expandable section
        const section = document.createElement('div');
        section.className = 'expandable-section';
        
        // Create header with expand icon
        const headerDiv = document.createElement('div');
        headerDiv.className = 'expandable-header';
        headerDiv.innerHTML = `
            ${header.outerHTML}
            <div class="expand-icon"></div>
        `;
        
        // Gather content until next header or end
        const content = document.createElement('div');
        content.className = 'expandable-content';
        let nextEl = header.nextElementSibling;
        while (nextEl && !['H3', 'H4'].includes(nextEl.tagName)) {
            const clone = nextEl.cloneNode(true);
            content.appendChild(clone);
            nextEl = nextEl.nextElementSibling;
        }
        
        // Add click handler
        headerDiv.addEventListener('click', () => {
            section.classList.toggle('expanded');
            content.classList.toggle('expanded');
        });
        
        // Assemble and replace original content
        section.appendChild(headerDiv);
        section.appendChild(content);
        header.parentNode.insertBefore(section, header);
        
        // Remove original elements
        nextEl = header.nextElementSibling;
        while (nextEl && !['H3', 'H4'].includes(nextEl.tagName)) {
            const toRemove = nextEl;
            nextEl = nextEl.nextElementSibling;
            toRemove.remove();
        }
        header.remove();
    });
}