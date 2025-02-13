function enableImagePairs(document) {
    const imagePairs = document.querySelectorAll('.image-pair');

    imagePairs.forEach(pair => {
        const images = pair.querySelectorAll('.image-comparison');
        const titles = pair.querySelectorAll('.image-title');
        let activeState = 'source';

        function applyActiveState(newState) {
            images.forEach(img => {
                img.style.display = (img.dataset.state === newState) ? 'block' : 'none';
            });

            titles.forEach(title => {
                title.style.fontWeight = (title.dataset.state === newState) ? 'bold' : 'normal';
            });

            if (newState === 'golden') {
                pair.classList.add("image-pair-golden");
            } else {
                pair.classList.remove("image-pair-golden");
            }

            activeState = newState;
        }

        function swapImagesAndTitles() {
            const newState = activeState === 'source' ? 'golden' : 'source';
            applyActiveState(newState);
        }

        applyActiveState(activeState);
        images.forEach(img => {
            img.addEventListener('click', swapImagesAndTitles);
        });
    });
}

function enableViewLinks(document) {
    const viewLinks = document.querySelectorAll('.view-link');

    viewLinks.forEach(link => {

        const container = link.closest('.titled-image-container');
        if (container) {
            const hiddenImage = container.querySelector('.hidden-image');
            if (hiddenImage) {

                link.addEventListener('click', (event) => {
                    event.preventDefault();
                    hiddenImage.style.display = 'block';
                    link.style.display = 'none';
                });

                hiddenImage.addEventListener('click', () => {
                    hiddenImage.style.display = 'none';
                    link.style.display = 'block';
                });
            }
        }
    });
}

function enableAnchorCopying(document) {
    function addClickHandler(element) {
        if (element.id) {
            element.addEventListener('click', () => {
                const currentURL = window.location.href.split('#');
                const anchor = element.id;
                const urlWithAnchor = `${currentURL}#${anchor}`;

                navigator.clipboard.writeText(urlWithAnchor)
            });
        }
    }

    const h2Elements = document.querySelectorAll('h2');
    h2Elements.forEach(addClickHandler);
    const h3Elements = document.querySelectorAll('h3');
    h3Elements.forEach(addClickHandler);
}

document.addEventListener('DOMContentLoaded', () => {
    enableViewLinks(document);
    enableImagePairs(document);
    enableAnchorCopying(document);
});

document.addEventListener('DOMContentLoaded', () => {
    enableViewLinks(document);
    enableImagePairs(document);
    enableAnchorCopying(document);
});