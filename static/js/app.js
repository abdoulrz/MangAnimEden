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
        { quote: "Penser que tu ne vaux rien est la pire chose que tu puisses faire.", author: "Nobita Nobi", source: "Doraemon" },
        { quote: "Si tu ne prends pas de risques, tu ne pourras jamais créer ton avenir.", author: "Monkey D. Luffy", source: "One Piece" },
        { quote: "Un raté peut battre un génie par un travail acharné.", author: "Rock Lee", source: "Naruto" },
        { quote: "La peur n'est pas mauvaise. Elle te dit quelle est ta faiblesse. Et une fois que tu connais ta faiblesse, tu peux devenir plus fort et plus gentil.", author: "Gildarts Clive", source: "Fairy Tail" },
        { quote: "Le monde n'est pas parfait. Mais il est là pour nous, faisant de son mieux... c'est ce qui le rend si beau.", author: "Roy Mustang", source: "Fullmetal Alchemist" },
        { quote: "Si tu as le temps de penser à une belle fin, alors vis magnifiquement jusqu'à la fin.", author: "Sakata Gintoki", source: "Gintama" }
    ],
    'KR': [ // Korea (Manhwa)
        { quote: "Le pouvoir ne vient pas de la volonté de frapper, mais de la volonté de protéger.", author: "Goomoonryong", source: "The Breaker" },
        { quote: "Si je ne change pas, le monde ne changera pas.", author: "Jin Woo", source: "Solo Leveling" },
        { quote: "Il n'y a pas de repas gratuit. Si tu veux quelque chose, tu dois en payer le prix.", author: "Khun Aguero Agnis", source: "Tower of God" },
        { quote: "Un monstre ne naît pas, il est créé.", author: "Desir Arman", source: "A Returner's Magic Should Be Special" },
        { quote: "Ne fais confiance à personne, pas même à toi-même.", author: "Bam", source: "Tower of God" }
    ],
    'CN': [ // China (Manhua/Donghua)
        { quote: "Il n'y a pas de chemin vers les cieux, alors je marcherai sur le chemin des démons.", author: "Wei Wuxian", source: "Mo Dao Zu Shi" },
        { quote: "Dans ce monde, la force est respectée. Le raisonnement valable n'est que pour les forts.", author: "Proverbe Wuxia", source: "Martial World" },
        { quote: "Si les cieux veulent m'écraser, je briserai les cieux !", author: "Meng Hao", source: "I Shall Seal the Heavens" },
        { quote: "La patience est une lame qui garde le cœur.", author: "Inconnu", source: "Sagesse Ancienne" }
    ],
    'GLOBAL': [ // Western/General or Fallback
        { quote: "Un grand pouvoir implique de grandes responsabilités.", author: "Oncle Ben", source: "Spider-Man" },
        { quote: "Quoi qu'il arrive, cela arrive.", author: "Spike Spiegel", source: "Cowboy Bebop" }
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
});
