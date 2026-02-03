/**
 * LE LECTEUR (READER)
 * Ce fichier gère l'expérience de lecture.
 * Il suit le principe de "Progressive Enhancement".
 */

const MangaReader = (function () {
    // Configuration (Design Tokens récupérés depuis le CSS si possible)
    const config = {
        lazyLoadThreshold: 0.5, // Charger l'image quand 50% visible
        zoomStep: 0.1,
        maxZoom: 2.0
    };

    // État local
    let state = {
        currentPage: 1,
        totalPages: 0,
        zoomLevel: 1.0,
        readingMode: 'vertical' // ou 'webtoon' (scroll infini)
    };

    // Éléments du DOM
    const elements = {
        container: document.getElementById('reader-container'),
        pages: document.querySelectorAll('.manga-page'),
        uiControls: document.getElementById('reader-controls')
    };

    // --- Méthodes Privées ---

    const _initLazyLoading = () => {
        // Utilisation de l'IntersectionObserver pour la perf (Recommandé par MDN)
        if ('IntersectionObserver' in window) {
            const imageObserver = new IntersectionObserver((entries, observer) => {
                entries.forEach(entry => {
                    if (entry.isIntersecting) {
                        const img = entry.target;
                        const imageSrc = img.dataset.src;
                        if (imageSrc) {
                            img.src = imageSrc; // Chargement réel
                            img.classList.remove('lazy');
                            observer.unobserve(img);
                        }
                    }
                });
            }, {
                threshold: config.lazyLoadThreshold
            });

            elements.pages.forEach(img => {
                if (img.dataset.src) {
                    imageObserver.observe(img);
                }
            });
        } else {
            // Fallback pour anciens navigateurs
            elements.pages.forEach(img => {
                if (img.dataset.src) {
                    img.src = img.dataset.src;
                    img.classList.remove('lazy');
                }
            });
        }
    };

    const _updateProgress = () => {
        // Envoi asynchrone à Django pour sauvegarder la progression
        // Utilisation de fetch API
        const url = `/api/reader/progress/${state.currentPage}/`;
        // fetch(url, { method: 'POST', ... }) 
        console.log(`Page ${state.currentPage} lue.`);
    };

    // --- Méthodes Publiques ---

    const init = (total) => {
        state.totalPages = parseInt(total) || 1;
        _initLazyLoading();
        console.log('MangaReader initialisé en mode ' + state.readingMode);
        console.log('Total pages: ' + state.totalPages);
    };

    const toggleControls = () => {
        if (elements.uiControls) {
            elements.uiControls.classList.toggle('hidden');
        }
    };

    return {
        init: init,
        toggleUI: toggleControls
    };

})();

// Initialisation au chargement
document.addEventListener('DOMContentLoaded', () => {
    // Supposons que le template Django injecte le total des pages
    const readerData = document.getElementById('reader-data');
    if (readerData) {
        const totalPages = readerData.dataset.total || '1';
        MangaReader.init(totalPages);
    } else {
        console.warn('reader-data element not found');
    }
});
