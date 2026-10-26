# Tablewise — Dinner planner and grocery beta v0.5

An install-free web app for planning meals and estimating grocery carts across ALDI, Kroger and Meijer. Built for testing with defaults of ZIP 48864, household of four, $150 weekly dinner budget and five dinners. Every setting can be changed in the app.

## Open

Open `Tablewise_Beta_Play.html` directly in a modern browser, or open the published `tablewise-beta/index.html` from the GitHub repository. Data is stored in browser localStorage, without an account.

## Available in v0.5

- Choose and swap among 31 dinner recipes, with finished-dish images, favorites, source links and ingredient mappings.
- Build a grocery cart from the recipes currently selected for the week and scale for household size.
- **Weekly pantry review**: show every ingredient called for by the week's actual recipes, grouped by category. Tap ingredients you already have; the shopping list, estimates and remaining budget update automatically. Other spices and staples are available under a separate expandable section.
- Correctly recompute and display **one-store versus split-store** shopping scenarios; the one-store option assigns every item to the same chosen retailer.
- Dialog controls: outside click, Escape, close X, Done checking, form save and finish actions; pantry scroll location preserved after selection.
- **Adjustable price-estimate cushion** (3% by default, editable 0–20% in Preferences). The buffer applies only to illustrative modeled unit prices, and affects budget planning, one-store, split-store and exported totals consistently. Manually checked/edited prices, dated ALDI weekly offers and manually added grocery items are not inflated.
- Links from the store comparison page to each retailer’s online shop (not yet synchronized into this app).
- Mobile-friendly pantry button positioned above the bottom-navigation overlay.
- Optional custom grocery items, editable sample prices, list checkboxes, text export, and printable view.
- Dated independent ALDI weekly-ad references and links to Meijer/Kroger ad sources.

## Price limitations and online shopping

Sample everyday prices are **illustrative estimates**, not live shelf or checkout prices. Publicly advertised ALDI prices are independent offers and **not verified for the user's local store**. Weekly ad data may be unavailable or stale. Customers can view their real shopping prices on retailer websites, but the app needs an authorized product pricing feed or retailer-compatible store-scoped data access to import those prices automatically. Instacart partner API access and the Kroger developer API are potential integration paths, not yet connected. Retailer pickup/delivery prices can differ from in-store prices, and discounts/fees can depend on checkout context. Store totals reflect approximate planning quantities rather than optimized package sizing and do not include tax or applicable coupons.

## Files

- `Tablewise_Beta_Play.html`: complete stand-alone app, with bundled photo sprite, recipes, JavaScript and CSS.
- `index.html` and `styles.css`, `data.js`, `app.js`, `ads-module.js`, `ads-data.js`: editable source (run `python build.py` to compile).
- `refresh_ads.py`, `.github/workflows/refresh-tablewise-ads.yml`: attempted limited source update workflow; automatic live operation is **not verified**.
- `test_v04_browser.py`: desktop/mobile browser interaction suite.
- `test_v05_buffer.py`: desktop/mobile price-buffer and provenance regression suite.
- `test_app.js`, `test_recipe_library.js`, `test_aldi.py`: component and source checks.

## Important recipe note

Cooking directions and ingredient measurements must be reviewed on the linked publisher pages. The app's ingredient quantities are independent planning approximations and do not replace the original recipes.