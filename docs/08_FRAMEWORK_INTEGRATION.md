# Bootstrap Integration Strategy & Reference Guide

This document serves as our step-by-step manual for replacing manual CSS layouts with Bootstrap's Grid and Utility classes. Our goal is to **reduce CSS bloat** while **keeping 100% of the premium design**.

## Core Philosophy: The "Soft Integration"
We will ONLY use Bootstrap's **Grid** (for columns and rows) and **Utilities** (for spacing, text alignment, flexbox). We will **NOT** use Bootstrap's components (like `.card`, `.btn`, `.navbar`), relying instead on our existing premium components.

### Token Mapping Strategy
To ensure Bootstrap fits our premium design, we will map Bootstrap's CSS variables to our `tokens.css` variables in a new file (e.g., `bootstrap-overrides.css`):
- `--bs-primary` mapped to `var(--color-purple-primary)`
- `--bs-secondary` mapped to `var(--color-pink-primary)`
- `--bs-body-font-family` mapped to `var(--font-ui)`
- Bootstrap breakpoints synchronized with our custom media queries.

---

## Step-by-Step Migration Plan per Section

To avoid getting overwhelmed, we will migrate the project one module at a time. The process for each file is always the same:
1. Open the HTML template.
2. Replace custom wrapper classes (e.g., `<div class="profile-layout-container">`) with Bootstrap grid classes (`<div class="container"><div class="row">`).
3. Replace custom margin/padding classes with utilities (`mt-4`, `p-3`).
4. Go to the corresponding `.css` file and **delete** the no-longer-needed layout rules.
5. Verify on Desktop and Mobile.

### Phase 1: The Proof of Concept (Profile Page)
* **Goal:** Prove the system works without breaking the Otaku Card or custom panels.
* **Target:** `templates/users/profile.html` and `profile.css`
* **Focus:** 
  - Convert `profile-layout-container` to a Bootstrap `.row`.
  - Convert the sidebar to `.col-lg-3`.
  - Convert the main content to `.col-lg-9`.
  - Remove complex media queries for row/column flipping in `profile.css`.

### Phase 2: The Core Components
* **Goal:** Standardize the global wrappers.
* **Target:** `base.html`, `navbar.html`, `footer.html`.
* **Focus:**
  - Wrap the main `<main>` content in standard container classes.
  - Simplify navbar flexbox alignments using Bootstrap's `d-flex justify-content-between align-items-center`.

### Phase 3: The Social Pages (Forum / Chat)
* **Goal:** Resolve recurring layout bugs in complex interaction pages.
* **Target:** `chat.css`, `forum.html`, `chat.html`.
* **Focus:**
  - The chat interface is heavily reliant on tricky fixed heights and flex layouts. We will use Bootstrap's utility classes to manage `h-100` (height 100%) and overflow areas.
  - Standardize the spacing between forum posts using `mb-3` or `gap-3`.

### Phase 4: The Catalog (Manga / Anime Lists)
* **Goal:** Perfect the responsive grid of posters.
* **Target:** `catalog/index.html`, `catalog.css`.
* **Focus:**
  - Replace manual CSS Grid setups with Bootstrap's `row-cols-2 row-cols-sm-3 row-cols-md-4 row-cols-lg-5`.
  - This instantly provides perfect responsiveness for item cards across all device sizes with zero custom CSS.

### Phase 5: Authentication & Forms
* **Goal:** Clean up form spacing.
* **Target:** `login.html`, `register.html`, `forms.css`.
* **Focus:**
  - Use Bootstrap form spacing for inputs, drastically reducing the need for custom wrappers around labels and input fields.
