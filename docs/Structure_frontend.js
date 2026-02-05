/**
 * LE LECTEUR (READER)
 * Ce fichier gère l'expérience de lecture.
 * Il suit le principe de "Progressive Enhancement".
 */

const MangaReader = (function() {
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
                        img.src = img.dataset.src; // Chargement réel
                        img.classList.remove('lazy');
                        observer.unobserve(img);
                    }
                });
            });

            elements.pages.forEach(img => imageObserver.observe(img));
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
        state.totalPages = total;
        _initLazyLoading();
        console.log('MangaReader initialisé en mode ' + state.readingMode);
    };

    const toggleControls = () => {
        elements.uiControls.classList.toggle('hidden');
    };

    return {
        init: init,
        toggleUI: toggleControls
    };

})();

// Initialisation au chargement
document.addEventListener('DOMContentLoaded', () => {
    // Supposons que le template Django injecte le total des pages
    const totalPages = document.getElementById('reader-data').dataset.total;
    MangaReader.init(totalPages);
});