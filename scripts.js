document.addEventListener('DOMContentLoaded', function() {
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
});

function generateTableOfContents() {
    const content = document.querySelector('#content');
    const headings = content.querySelectorAll('h2, h3');
    const toc = document.createElement('div');
    toc.id = 'table-of-contents';
    
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