# SPEC-008: Regional Wisdom Feature

## 1. Context and Problem

Currently, the homepage displays a random anime quote fetched server-side from an external API (`animechan.xyz`). This introduces:

- **Latency**: The page load depends on the external API response.
- **Reliability**: If the API is down, the section is empty or falls back to a single hardcoded quote.
- **Lack of Control**: We cannot curate the quotes to match the "MangaAnimEden" tone or specific regions.

## 2. Goals

- Replace the server-side API call with a client-side JavaScript solution.
- Implement a **curated local database** of quotes (`REGIONAL_WISDOM`).
- Support "Regional" context to align with the "Manga" (Japan), "Manhwa" (Korea), "Manhua" (China) themes.
- Improve page load performance.

## 3. Technical Implementation

### 3.1 Data Structure (`static/js/app.js`)

We will create a `REGIONAL_WISDOM` object containing quotes categorized by region.

```javascript
const REGIONAL_WISDOM = {
    'JP': [ // Japan (Manga/Anime)
        { quote: "Thinking you're no-good and worthless is the worst thing you can do.", author: "Nobita Nobi", source: "Doraemon" },
        // ...
    ],
    'KR': [ // Korea (Manhwa)
        { quote: "Power is not the will to hit, but the will to protect.", author: "Unknown", source: "The Breaker" },
        // ...
    ],
    'CN': [ // China (Manhua/Donghua)
        { quote: "There is no path to the heavens, so I'll walk the path of demons.", author: "Wei Wuxian", source: "Mo Dao Zu Shi" },
        // ...
    ],
    'GLOBAL': [ // Western/General
        { quote: "With great power comes great responsibility.", author: "Uncle Ben", source: "Spider-Man" }
    ]
};
```

### 3.2 logic (`renderWisdom`)

A function `renderWisdom(region)` will:

1. Accept a region code (default to random or 'JP').
2. Select a random quote from that region's list.
3. Inject the HTML into the `.quote-container`.

### 3.3 Backend Cleanup

- Remove the `requests.get` call from `core/views.py`.
- Remove `quote` context variable from `home.html`.

### 3.4 Frontend Integration

- Add `<script src="{% static 'js/app.js' %}"></script>` to `base.html` (deferred).
- Ensure `home.html` has a target container with a unique ID (e.g., `#wisdom-container`).

## 4. UI/UX

- **Loading State**: Show a subtle skeleton or "Loading wisdom..." text (optional, since it's instant client-side).
- **Visuals**: Maintain existing Glassmorphism/Neumorphism style.
- **Regions**: Ideally, we could cycle through regions or pick based on user preference (future). For now, random region or weighted random.

## 5. Risks

- **Duplication**: Ensure we don't duplicate existing `reader.js` logic.
- **Cache**: Browser caching of `app.js` means updates to quotes require a file version bump or correct cache headers (handled by Django `static` tag usually).
