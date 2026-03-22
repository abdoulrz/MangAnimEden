/**
 * MangaAnimEden Main Application Logic
 * Handles global interactions and the "Regional Wisdom" feature.
 */

let wisdomCache = null;
let shownIndices = new Set(); // Tracks shown quotes for this session (in-memory, no localStorage race)
let isRendering = false;      // Prevents concurrent async calls

/**
 * Renders a wisdom quote into #wisdom-container.
 * - forceNew=false: respects 24h cooldown, shows cached quote
 * - forceNew=true: always picks a new, non-repeated quote
 *
 * Uses an in-memory Set to guarantee no repeats until all quotes are exhausted.
 */
async function renderWisdom(forceNew = false) {
    const container = document.getElementById('wisdom-container');
    if (!container) return;

    // Guard: prevent multiple concurrent renders on rapid clicks
    if (isRendering) return;
    isRendering = true;

    try {
        // 1. 24h cooldown check (only when not forced)
        if (!forceNew) {
            const lastShown = parseInt(localStorage.getItem('wisdom_last_shown') || '0', 10);
            const cachedStr = localStorage.getItem('wisdom_current_quote');
            if (Date.now() - lastShown < 86_400_000 && cachedStr) {
                try {
                    _displayQuote(container, JSON.parse(cachedStr));
                    return;
                } catch(e) { /* corrupted cache, fall through */ }
            }
        }

        // 2. Load quotes if not yet cached
        if (!wisdomCache) {
            const cbVersion = window.APP_STATIC_VERSION || new Date().getTime();
            const response = await fetch('/static/data/wisdom.json?cb=' + cbVersion);
            if (!response.ok) throw new Error('Failed to load wisdom');
            wisdomCache = await response.json();
        }

        // 3. Detect language — strip region code (e.g. 'fr-fr' → 'fr')
        const rawLang = (document.documentElement.lang || 'fr').split('-')[0].toLowerCase();
        const quotes = wisdomCache[rawLang] || wisdomCache['fr'] || wisdomCache['en'];
        if (!quotes || quotes.length === 0) return;

        // 4. Reset the shown-set when all quotes have been displayed
        if (shownIndices.size >= quotes.length) {
            shownIndices.clear();
        }

        // 5. Pick a random index not yet shown this session
        let idx;
        let attempts = 0;
        const maxAttempts = quotes.length * 3;
        do {
            idx = Math.floor(Math.random() * quotes.length);
            attempts++;
        } while (shownIndices.has(idx) && attempts < maxAttempts);

        shownIndices.add(idx);

        // 6. Persist for 24h cooldown
        localStorage.setItem('wisdom_last_shown', Date.now().toString());
        localStorage.setItem('wisdom_current_quote', JSON.stringify(quotes[idx]));

        _displayQuote(container, quotes[idx]);

    } catch (error) {
        console.error('Wisdom Error:', error);
        container.innerHTML = '<p class="footer-quote-text">"La sagesse est le fruit de l\'expérience."</p>';
    } finally {
        isRendering = false;
    }
}

function _displayQuote(container, quote) {
    container.style.opacity = '0';
    setTimeout(() => {
        container.innerHTML = `
            <p class="footer-quote-text">"${quote.quote}"</p>
            <span class="footer-quote-author">— ${quote.author} (${quote.source})</span>
        `;
        container.style.opacity = '1';
    }, 200);
}

// ==========================================================================
// INITIALIZATION
// ==========================================================================
document.addEventListener('DOMContentLoaded', () => {
    const wisdomContainer = document.getElementById('wisdom-container');
    if (wisdomContainer) {
        renderWisdom(false); // Respects 24h cooldown on page load
        wisdomContainer.addEventListener('click', () => renderWisdom(true)); // Click forces new quote
        wisdomContainer.style.cursor = 'pointer';
        wisdomContainer.title = 'Cliquer pour une nouvelle citation';
    }

    // Mobile Menu Toggle
    const mobileMenuToggle = document.getElementById('mobileMenuToggle');
    const navbarMenu = document.querySelector('.navbar-menu');

    if (mobileMenuToggle && navbarMenu) {
        const barsIcon = `<svg xmlns="http://www.w3.org/2000/svg" width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="3" y1="12" x2="21" y2="12"></line><line x1="3" y1="6" x2="21" y2="6"></line><line x1="3" y1="18" x2="21" y2="18"></line></svg>`;
        const xIcon = `<svg xmlns="http://www.w3.org/2000/svg" width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="18" y1="6" x2="6" y2="18"></line><line x1="6" y1="6" x2="18" y2="18"></line></svg>`;

        mobileMenuToggle.addEventListener('click', (e) => {
            e.stopPropagation();
            navbarMenu.classList.toggle('active');
            mobileMenuToggle.innerHTML = navbarMenu.classList.contains('active') ? xIcon : barsIcon;
        });

        document.addEventListener('click', (e) => {
            if (navbarMenu.classList.contains('active') && !navbarMenu.contains(e.target) && !mobileMenuToggle.contains(e.target)) {
                navbarMenu.classList.remove('active');
                mobileMenuToggle.innerHTML = barsIcon;
            }
        });
    }
});
