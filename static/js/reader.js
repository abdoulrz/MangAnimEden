/**
 * LE LECTEUR (READER)
 * Gère l'expérience de lecture : Modes (Vertical/Paged), Navigation, Paramètres.
 */

const MangaReader = (function () {
    // Configuration
    const config = {
        lazyLoadThreshold: 0.5,
        zoomStep: 0.1,
        maxZoom: 3.0
    };

    // État local
    let state = {
        currentPage: 1, // 1-based index
        totalPages: 0,
        readingMode: localStorage.getItem('reader_mode') || 'vertical', // 'vertical', 'webtoon', 'paged'
        direction: localStorage.getItem('reader_direction') || 'ltr', // 'ltr', 'rtl' (manga)
        gapless: localStorage.getItem('reader_gapless') === 'true',
        zoomLevel: 1.0,
        isMenuOpen: false
    };

    // Éléments du DOM
    const elements = {
        container: document.getElementById('reader-container'),
        pages: Array.from(document.querySelectorAll('.reader-page')), // Convert NodeList to Array
        settingsBtn: document.getElementById('settingsBtn'),
        settingsMenu: document.getElementById('settingsMenu'),
        clickZoneLeft: document.getElementById('clickZoneLeft'),
        clickZoneRight: document.getElementById('clickZoneRight'),
        gaplessToggle: document.getElementById('gaplessToggle'),
        modeBtns: document.querySelectorAll('.mode-btn'),
        dirBtns: document.querySelectorAll('.dir-btn')
    };

    // --- Méthodes Privées ---

    const _applySettings = () => {
        // Reset classes
        elements.container.classList.remove('mode-vertical', 'mode-webtoon', 'mode-paged', 'gapless');

        // Apply Mode
        elements.container.classList.add(`mode-${state.readingMode}`);

        // Apply Gapless
        if (state.gapless && state.readingMode === 'webtoon') {
            elements.container.classList.add('gapless');
        }

        // Show/Hide Direction controls (only for Paged)
        const pagedControls = document.querySelector('.paged-only');
        const verticalControls = document.querySelector('.vertical-only');

        if (state.readingMode === 'paged') {
            if (pagedControls) pagedControls.classList.remove('hidden');
            if (verticalControls) verticalControls.classList.add('hidden');
            _updatePagedView();
            _setupClickZones();
        } else {
            if (pagedControls) pagedControls.classList.add('hidden');
            if (verticalControls) verticalControls.classList.remove('hidden');
            // Show all pages in vertical modes
            elements.pages.forEach(p => p.classList.add('active'));
            elements.clickZoneLeft.classList.add('hidden');
            elements.clickZoneRight.classList.add('hidden');
            document.body.style.overflow = 'auto'; // Re-enable scroll
        }

        // Update UI state (buttons)
        elements.modeBtns.forEach(btn => {
            btn.classList.toggle('active', btn.dataset.mode === state.readingMode);
        });
        elements.dirBtns.forEach(btn => {
            btn.classList.toggle('active', btn.dataset.dir === state.direction);
        });
        if (elements.gaplessToggle) elements.gaplessToggle.checked = state.gapless;

        // Save to LocalStorage
        localStorage.setItem('reader_mode', state.readingMode);
        localStorage.setItem('reader_direction', state.direction);
        localStorage.setItem('reader_gapless', state.gapless);
    };

    const _updatePagedView = () => {
        // Hide all pages
        elements.pages.forEach(p => p.classList.remove('active'));

        // Show current page
        const currentIndex = state.currentPage - 1;
        if (elements.pages[currentIndex]) {
            elements.pages[currentIndex].classList.add('active');

            // Force load current image if lazy
            const img = elements.pages[currentIndex];
            if (img.dataset.src) {
                img.src = img.dataset.src;
                img.classList.remove('lazy');
                img.removeAttribute('data-src'); // Prevent re-loading
            }

            // Preload next image
            const nextIndex = currentIndex + 1;
            if (elements.pages[nextIndex] && elements.pages[nextIndex].dataset.src) {
                elements.pages[nextIndex].src = elements.pages[nextIndex].dataset.src;
                elements.pages[nextIndex].classList.remove('lazy');
                elements.pages[nextIndex].removeAttribute('data-src');
            }
        }

        // Scroll to top to ensure visibility
        window.scrollTo(0, 0);
        document.body.style.overflow = 'hidden'; // Disable page scroll in paged mode
    }

    const _setupClickZones = () => {
        elements.clickZoneLeft.classList.remove('hidden');
        elements.clickZoneRight.classList.remove('hidden');

        // Direction logic: 
        // LTR (Standard): Left = Prev, Right = Next
        // RTL (Manga): Left = Next, Right = Prev

        if (state.direction === 'ltr') {
            elements.clickZoneLeft.title = "Précédent";
            elements.clickZoneRight.title = "Suivant";
        } else {
            elements.clickZoneLeft.title = "Suivant";
            elements.clickZoneRight.title = "Précédent";
        }
    };

    const _navigatePage = (direction) => {
        // direction: 1 (Next), -1 (Prev)
        const newPage = state.currentPage + direction;

        if (newPage >= 1 && newPage <= state.totalPages) {
            state.currentPage = newPage;
            _updatePagedView();
            _updateProgress(state.currentPage);
        } else {
            // End of chapter logic (could prompt "Next Chapter")
            console.log("End of chapter/start reached");
        }
    };

    const _handleZoneClick = (side) => {
        // side: 'left' or 'right'
        if (state.direction === 'ltr') {
            if (side === 'left') _navigatePage(-1); // Prev
            if (side === 'right') _navigatePage(1); // Next
        } else {
            // RTL
            if (side === 'left') _navigatePage(1); // Next
            if (side === 'right') _navigatePage(-1); // Prev
        }
    };

    const _initEventListeners = () => {
        // Settings Toggle
        if (elements.settingsBtn) {
            elements.settingsBtn.addEventListener('click', (e) => {
                e.stopPropagation();
                state.isMenuOpen = !state.isMenuOpen;
                elements.settingsMenu.classList.toggle('hidden', !state.isMenuOpen);
            });

            // Close menu clicking outside
            document.addEventListener('click', (e) => {
                if (state.isMenuOpen && !elements.settingsMenu.contains(e.target) && e.target !== elements.settingsBtn) {
                    state.isMenuOpen = false;
                    elements.settingsMenu.classList.add('hidden');
                }
            });
        }

        // Mode Switching
        elements.modeBtns.forEach(btn => {
            btn.addEventListener('click', () => {
                state.readingMode = btn.dataset.mode;
                _applySettings();
            });
        });

        // Direction Switching
        elements.dirBtns.forEach(btn => {
            btn.addEventListener('click', () => {
                state.direction = btn.dataset.dir;
                _applySettings();
            });
        });

        // Gapless Toggle
        if (elements.gaplessToggle) {
            elements.gaplessToggle.addEventListener('change', (e) => {
                state.gapless = e.target.checked;
                _applySettings();
            });
        }

        // Click Zones
        if (elements.clickZoneLeft) {
            elements.clickZoneLeft.addEventListener('click', () => _handleZoneClick('left'));
        }
        if (elements.clickZoneRight) {
            elements.clickZoneRight.addEventListener('click', () => _handleZoneClick('right'));
        }

        // Keyboard Navigation
        document.addEventListener('keydown', (e) => {
            if (state.readingMode === 'paged') {
                if (e.key === 'ArrowRight' || e.key === 'ArrowDown') _handleZoneClick('right');
                if (e.key === 'ArrowLeft' || e.key === 'ArrowUp') _handleZoneClick('left');
            }
        });

        // Swipe Gestures (Touch)
        let touchStartX = 0;
        let touchEndX = 0;

        document.addEventListener('touchstart', (e) => {
            touchStartX = e.changedTouches[0].screenX;
        }, { passive: true });

        document.addEventListener('touchend', (e) => {
            if (state.readingMode !== 'paged') return;

            touchEndX = e.changedTouches[0].screenX;
            handleSwipe();
        }, { passive: true });

        const handleSwipe = () => {
            const SWIPE_THRESHOLD = 50;
            if (touchEndX < touchStartX - SWIPE_THRESHOLD) _handleZoneClick('right'); // Swipe Left -> Next (visually moving right)
            if (touchEndX > touchStartX + SWIPE_THRESHOLD) _handleZoneClick('left'); // Swipe Right -> Prev
        };
    };

    const _initLazyLoading = () => {
        if ('IntersectionObserver' in window) {
            const imageObserver = new IntersectionObserver((entries, observer) => {
                entries.forEach(entry => {
                    if (entry.isIntersecting) {
                        const img = entry.target;
                        if (img.dataset.src) {
                            img.src = img.dataset.src;
                            img.classList.remove('lazy');
                            img.removeAttribute('data-src');
                            observer.unobserve(img);
                        }
                    }
                });
            }, { threshold: config.lazyLoadThreshold, rootMargin: "500px" });

            elements.pages.forEach(img => {
                if (img.dataset.src) imageObserver.observe(img);
            });
        }
    };

    const _updateProgress = (page) => {
        // Send progress to server (Debounced or simple fire-and-forget)
        // const url = `/api/reader/progress/${page}/`;
        // fetch(url, { method: 'POST' });
        console.log(`Progress: Page ${page}`);
    };

    // --- Méthodes Publiques ---

    const init = (total) => {
        state.totalPages = parseInt(total) || 1;
        _initEventListeners();
        _applySettings(); // Applies initial mode and styles
        _initLazyLoading();
        console.log(`MangaReader initialized. Mode: ${state.readingMode}, Total Pages: ${state.totalPages}`);
    };

    return {
        init: init
    };

})();

// Initialisation via le template
// (Le code d'initialisation reste dans demo.html ou ici si on préfère,
// mais demo.html l'appelle déjà via MangaReader.init())
