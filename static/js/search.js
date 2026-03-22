/**
 * Live Search Logic
 * Context-aware: searches GROUPS on forum pages, MANGA on all other pages.
 */

document.addEventListener('DOMContentLoaded', () => {
    const initSearch = (inputId, panelId, apiUrl, context) => {
        const input = document.getElementById(inputId);
        const panel = document.getElementById(panelId);

        if (!input || !panel) return;

        // If a data-api attribute exists on the input, override the apiUrl
        const resolvedApi = input.dataset.api || apiUrl;
        const resolvedContext = input.dataset.context || context;

        let debounceTimer;

        input.addEventListener('input', () => {
            clearTimeout(debounceTimer);
            const query = input.value.trim();

            if (query.length < 2) {
                panel.innerHTML = '';
                panel.classList.add('hidden');
                return;
            }

            debounceTimer = setTimeout(() => {
                fetchSearchResults(query, panel, resolvedApi, resolvedContext);
            }, 300);
        });

        document.addEventListener('mousedown', (e) => {
            if (!input.contains(e.target) && !panel.contains(e.target)) {
                panel.classList.add('hidden');
            }
        });

        input.addEventListener('focus', () => {
            if (input.value.trim().length >= 2 && panel.innerHTML.trim() !== '') {
                panel.classList.remove('hidden');
            }
        });
    };

    // Navbar search: reads data-api/data-context from the input element itself
    initSearch('navbarSearchInput', 'searchResultsPanel', '/catalogue/search/api/', 'manga');

    // Catalog page search: always manga
    initSearch('catalogSearchInput', 'catalogSearchResultsPanel', '/catalogue/search/api/', 'manga');

    async function fetchSearchResults(query, resultsPanel, apiUrl, context) {
        try {
            const response = await fetch(`${apiUrl}?q=${encodeURIComponent(query)}`);
            if (!response.ok) throw new Error('Search failed');
            const data = await response.json();
            renderResults(data.results, resultsPanel, query, context);
        } catch (error) {
            console.error('Search error:', error);
            resultsPanel.classList.add('hidden');
        }
    }

    function renderResults(results, resultsPanel, query, context) {
        if (results.length === 0) {
            const label = context === 'groups' ? 'Aucun groupe trouvé' : 'Aucun scan trouvé';
            resultsPanel.innerHTML = `<div class="search-result-empty">${label}</div>`;
        } else if (context === 'groups') {
            // Render group results
            let html = '<div class="search-results-list d-flex flex-column gap-1">';
            results.forEach(item => {
                const icon = item.icon
                    ? `<img src="${item.icon}" alt="${item.name}" class="search-result-thumb">`
                    : `<div class="search-result-thumb search-result-thumb-placeholder">👥</div>`;
                html += `
                    <a href="${item.url}" class="search-result-item d-flex align-items-center gap-3">
                        ${icon}
                        <div class="search-result-info d-flex flex-column overflow-hidden">
                            <span class="search-result-title">${item.name}</span>
                            <span class="search-result-meta">Groupe</span>
                        </div>
                    </a>
                `;
            });
            html += '</div>';
            resultsPanel.innerHTML = html;
        } else {
            // Render manga results
            let html = '<div class="search-results-list d-flex flex-column gap-1">';
            results.forEach(item => {
                html += `
                    <a href="${item.url}" class="search-result-item d-flex align-items-center gap-3">
                        <img src="${item.cover}" alt="${item.title}" class="search-result-thumb">
                        <div class="search-result-info d-flex flex-column overflow-hidden">
                            <span class="search-result-title">${item.title}</span>
                            <span class="search-result-meta">${item.type}</span>
                        </div>
                    </a>
                `;
            });
            html += '</div>';
            html += `<a href="/catalogue/?q=${encodeURIComponent(query)}" class="search-result-view-all">Voir tout le catalogue →</a>`;
            resultsPanel.innerHTML = html;
        }
        resultsPanel.classList.remove('hidden');
    }
});
