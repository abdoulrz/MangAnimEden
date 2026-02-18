/**
 * MangaAnimEden Main Application Logic
 * Handles global interactions and the "Regional Wisdom" feature.
 */

// ==========================================================================
// REGIONAL WISDOM DATABASE
// Quotes curated by region to match Manga (JP), Manhwa (KR), Manhua (CN)
// ==========================================================================
const REGIONAL_WISDOM = {
    'JP': [ // Japan (Manga/Anime)
        { quote: "Si tu ne prends pas de risques, tu ne pourras jamais créer ton avenir.", author: "Monkey D. Luffy", source: "One Piece" },
        { quote: "Je ne reviens jamais sur ma parole, c'est ça mon nindô !", author: "Naruto Uzumaki", source: "Naruto" },
        { quote: "Si tu gagnes, tu vis. Si tu perds, tu meurs. Si tu ne te bats pas, tu ne peux pas gagner !", author: "Eren Jaeger", source: "L'Attaque des Titans" },
        { quote: "Les gens ne cessent de mourir. C'est pour ça que je veux au moins qu'ils aient une mort correcte.", author: "Yuji Itadori", source: "Jujutsu Kaisen" },
        { quote: "Le monde n'est pas parfait. Mais il est là pour nous, faisant de son mieux... c'est ce qui le rend si beau.", author: "Roy Mustang", source: "Fullmetal Alchemist" },
        { quote: "Tu ne peux pas changer le monde sans te salir les mains.", author: "Lelouch Lamperouge", source: "Code Geass" },
        { quote: "Un grand pouvoir implique de grandes responsabilités... Attends, mauvais univers.", author: "Sakata Gintoki", source: "Gintama" }
    ],
    'KR': [ // Korea (Manhwa)
        { quote: "Les faibles n'ont pas le droit de choisir leur façon de mourir.", author: "Trafalgar Law (Invité)", source: "Réf. Culturelle" },
        { quote: "Je ne protège pas le monde. Je protège les gens qui sont à ma portée.", author: "Sung Jin-Woo", source: "Solo Leveling" },
        { quote: "Il n'y a pas de repas gratuit. Si tu veux quelque chose, tu dois en payer le prix.", author: "Khun Aguero Agnis", source: "Tower of God" },
        { quote: "La vie est injuste, c'est pourquoi elle est amusante.", author: "Desir Arman", source: "A Returner's Magic Should Be Special" },
        { quote: "Même si le ciel s'effondre, il y aura toujours un trou pour s'échapper.", author: "Proverbe Coréen", source: "Sagesse Manhwa" }
    ],
    'CN': [ // China (Manhua/Donghua)
        { quote: "Qui se soucie de la voie royale glorieuse ? Je préfère traverser la passerelle de bois jusqu'à ce qu'il fasse sombre.", author: "Wei Wuxian", source: "Mo Dao Zu Shi" },
        { quote: "Si je deviens un Bouddha, il n'y a pas de démons. Si je deviens un démon, il n'y a pas de Bouddha !", author: "Sun Wukong", source: "La Légende du Roi Singe" },
        { quote: "Dans ce monde, la force est la seule vérité.", author: "Fang Yuan", source: "Reverend Insanity" },
        { quote: "Trente ans à l'est du fleuve, trente ans à l'ouest... Ne jamais intimider un jeune homme pauvre !", author: "Xiao Yan", source: "Battle Through the Heavens" }
    ],
    'GLOBAL': [ // Western/General or Fallback
        { quote: "Un grand pouvoir implique de grandes responsabilités.", author: "Oncle Ben", source: "Spider-Man" },
        { quote: "Quoi qu'il arrive, cela arrive.", author: "Spike Spiegel", source: "Cowboy Bebop" },
        { quote: "La seule chose dont nous devons avoir peur, c'est de la peur elle-même.", author: "Franklin D. Roosevelt", source: "Histoire" }
    ]
};

/**
 * Renders a random wisdom quote into the DOM.
 * @param {string} region - Optional region code ('JP', 'KR', 'CN', 'GLOBAL'). If null, picks random.
 */
function renderWisdom(region = null) {
    const container = document.getElementById('wisdom-container');
    if (!container) return;

    // 1. Determine Region
    const regions = Object.keys(REGIONAL_WISDOM);
    const selectedRegion = region && regions.includes(region)
        ? region
        : regions[Math.floor(Math.random() * regions.length)];

    // 2. Select Random Quote
    const quotes = REGIONAL_WISDOM[selectedRegion];
    const randomQuote = quotes[Math.floor(Math.random() * quotes.length)];

    // 3. Render HTML
    // Using a fade effect for smoothness
    container.style.opacity = '0';

    setTimeout(() => {
        container.innerHTML = `
            <p class="quote-text">"${randomQuote.quote}"</p>
            <span class="quote-author">
                — ${randomQuote.author}
                <br><small>${randomQuote.source} <span class="badge-region">${selectedRegion}</span></small>
            </span>
        `;
        container.style.opacity = '1';
    }, 200);
}

// ==========================================================================
// INITIALIZATION
// ==========================================================================
document.addEventListener('DOMContentLoaded', () => {
    // Render Wisdom on Home Page
    if (document.getElementById('wisdom-container')) {
        renderWisdom();

        // Optional: Cycle wisdom on click (Easter Egg)
        document.getElementById('wisdom-container').addEventListener('click', () => renderWisdom());
    }

    // Mobile Menu Toggle logic
    const mobileMenuToggle = document.getElementById('mobileMenuToggle');
    const navbarMenu = document.querySelector('.navbar-menu');

    if (mobileMenuToggle && navbarMenu) {
        mobileMenuToggle.addEventListener('click', (e) => {
            e.stopPropagation();
            navbarMenu.classList.toggle('active');

            // Toggle Icon SVG
            if (navbarMenu.classList.contains('active')) {
                // Switch to X icon
                mobileMenuToggle.innerHTML = `
                    <svg xmlns="http://www.w3.org/2000/svg" width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                        <line x1="18" y1="6" x2="6" y2="18"></line>
                        <line x1="6" y1="6" x2="18" y2="18"></line>
                    </svg>
                `;
            } else {
                // Switch back to Bars icon
                mobileMenuToggle.innerHTML = `
                    <svg xmlns="http://www.w3.org/2000/svg" width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                        <line x1="3" y1="12" x2="21" y2="12"></line>
                        <line x1="3" y1="6" x2="21" y2="6"></line>
                        <line x1="3" y1="18" x2="21" y2="18"></line>
                    </svg>
                `;
            }
        });

        // Close sidebar when clicking outside
        document.addEventListener('click', (e) => {
            if (navbarMenu.classList.contains('active') && !navbarMenu.contains(e.target) && !mobileMenuToggle.contains(e.target)) {
                navbarMenu.classList.remove('active');
                // Reset to Bars icon
                mobileMenuToggle.innerHTML = `
                    <svg xmlns="http://www.w3.org/2000/svg" width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                        <line x1="3" y1="12" x2="21" y2="12"></line>
                        <line x1="3" y1="6" x2="21" y2="6"></line>
                        <line x1="3" y1="18" x2="21" y2="18"></line>
                    </svg>
                `;
            }
        });
    }
});
