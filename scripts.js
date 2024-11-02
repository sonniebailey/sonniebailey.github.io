document.addEventListener('DOMContentLoaded', function() {
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
    headings.forEach((heading, index) => {
        const listItem = document.createElement('li');
        const link = document.createElement('a');
        link.textContent = heading.textContent;
        link.href = `#heading-${index}`;
        listItem.appendChild(link);
        tocList.appendChild(listItem);

        // Add id to the heading
        heading.id = `heading-${index}`;
    });

    toc.appendChild(tocList);
    content.insertBefore(toc, content.firstChild);
}