# Tablewise beta v0.3 — Dinner, sorted.

Static dinner planner with 31 curated dinners (up from 15), finished-dish images, search by ingredient, saved recipes, third-party ALDI weekly advertised prices, a public store-ad link board, and an optional narrowly scoped weekly refresh. This is a beta, not a real-time retailer API. Price estimates are fictitious demonstrations. ALDI offers are sourced from the independent, unaffiliated aldiweekly.com website; they are NOT verified Okemos shelf prices. Exact matched ALDI ingredient/unit ad prices override prototype estimates while active, unless the user entered a price. All unrelated prices remain demonstrations. All sources and expiration dates should be reviewed before a purchase.

Default onboarding: ZIP 48864, Meijer/ALDI/Kroger, 4 servings, $150 dinner budget, 5 dinners, balanced meals. Settings remain editable. Data saves in browser localStorage; no personal information is sent to Tablewise.

## Run
Open index.html in a recent browser, or run `python -m http.server 8000` here and open `http://localhost:8000`. HTML/JS/CSS only; no build or dependencies. Downloading files together is sufficient to run the planner.

## Weekly ad sources
- Meijer Okemos: https://www.meijer.com/shopping/weekly-ad?storeId=25 (page-based flyer, no reliably extracted item prices)
- ALDI: https://aldiweekly.com/ (independent weekly ad summary, October 21–27 listings initially captured; prices not ZIP-specific or official)
- Kroger Michigan: https://www.weeklyad.io/kroger (regional circular, not store-specific shelf prices)

Optional scheduled automation: `refresh_ads.py` checks the ALDI independent public ad summary once a week, subject to robots.txt access, and emits `ads-data.js` / `ads.json` only from dated, legible grocery offer rows. It leaves Meijer and Kroger as direct source links. Unparseable/blocked listings remain clickable ad links, not made-up prices; expired prices are discarded. The workflow must be enabled in a suitable GitHub repository for automatic refresh; a static download will not self-update.

## Recipes and imagery
- 31 recipes, with 16 newly linked and verified Budget Bytes articles plus the existing 15 Budget Bytes/Food Network entries. Cards show finished-dish photos, category, cooking time, publisher, favorites, and add-to-week actions.
- The 15 original cards use a **locally bundled, generated collage of illustrative dish photographs**. They do not claim to be the publisher’s exact dish photos. The 16 new cards show credited, directly linked images from Budget Bytes, which may fail to load offline or if the source blocks embedding. In that case, emoji placeholders display automatically.
- The entire original recipe remains with the publisher. Meal ingredients are **rough shopping-planning quantities**, not the authoritative recipe card. Prices are estimates unless clearly attributed to active ad offers.
- AI-generated photography is bundled as an optimized WebP data URL in `styles.css`, keeping the standalone HTML beta functional without image hosting or paid APIs.
- Recipe filters include meal type, quick dinners, favorites, and ingredient search. The existing menu generator selects from all 31 recipes. Browser storage persists saved favorites.

## Known limitations
* Prices for Meijer, ALDI, Kroger are not reliable live store-by-store prices. Store comparison uses clearly labeled illustrative values; a few exact ALDI ingredient/unit matches can use unconfirmed third-party advertised offers for ZIP 48864. The user can change prices.
* Recipe ingredients and package quantities are approximate prototypes and should be checked against the publisher's recipe.
* ZIP 48864 is the only pre-mapped local store group. Other ZIP codes require selecting the correct retailer location using provided links. No claim of automatic store discovery for arbitrary ZIP codes.
* Generated shopping plan does not guarantee the lowest possible real-world total. Sale offers can impose sizes/coupons/minimum quantities.
* No user accounts or cross-device sync yet. Data resides only in one browser's local storage.

## Implementation and tests
Run `node test_app.js`, `node test_recipe_library.js`, and `python test_aldi.py` from this directory. The initial October 21–27 prices were manually checked against aldiweekly.com on October 25, 2026. The auto-refresh workflow has not yet been proven against the live website from GitHub Actions; if robots or hosting blocks automation it will provide the source link and no new prices, rather than circumvent access controls.