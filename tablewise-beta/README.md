# Tablewise — Beta v0.7 (recipe sources, Kroger regional flyers, shared ingredient breakdowns)

Tablewise is a standalone dinner planner and shopping list web app with local browser storage. Default household preferences: ZIP **48864**, four people, five dinners, $150 budget, Meijer/ALDI/Kroger, 3% cushion on *illustrative* prices. Preferences are editable in the app.

## What changed in v0.7

- Expanded from 31 to **42** selectable dinners. New directly linked original recipes from widely used, established publishers: **Allrecipes**, **Delish**, **Simply Recipes**, **RecipeTin Eats**, and **The Pioneer Woman**. Existing Food Network and Budget Bytes entries are retained. Cuisine diversity includes soups, quick skillets, enchiladas, creamy chicken, and shawarma.
- Every recipe is a planning card; original cooking directions remain on the publisher's site. **Ingredients and quantities in Tablewise are independently estimated**, not copied verbatim or guaranteed to equal the original recipe.
- Every recipe card has a photo. The new entries use *illustrative local dish photos* (from a bundled collage, which may not match the exact dish); some existing Budget Bytes cards display remotely hosted publisher photos with fallbacks.
- Shopping list now shows each selected dinner, weekday, estimated required quantity of each shared ingredient, and its contribution to the aggregated planned quantity. A **Double this recipe ×2** button doubles that day's servings and recalculates **all** its ingredients, the purchase-unit rounding, store allocation, estimated spend and budget. The other recipes' quantities remain unchanged. Press the button again to restore the original quantity. The one-week change persists in this browser. Swapping or regenerating a meal clears that slot's serving multiplier.
- Expands the Kroger weekly-ad section to the **current dated regional editions** on https://www.weeklyads2.com/kroger/. As checked October 26, 2026, there are **nine editions across MI, OH, IN, TN, GA and TX**, including multiple editions for OH/GA/TX. The app suggests a state from a ZIP *prefix* where possible, lets users choose any available region or view all, and provides a direct link to WeeklyAds2's exact-ZIP selector. This is only a state-level hint; ZIP assignment to a precise Kroger market cannot be guaranteed without the retailer's own store-aware data.
- The GitHub Actions Wednesday job now checks available public Kroger and Meijer flyer index links and dates when robots.txt permits access, with regression tests. It stores link/date/state metadata, **never advert photos or scraped flyer prices**, and never treats regional flyers as verified store prices. Future dated or expired flyers aren't shown as current. A live run of this workflow has not yet been independently verified.
- Mobile shopping list cards no longer widen the page beyond the device viewport when displaying multi-recipe attribution; fixed navigation remains visible on narrow screens.

## Quick start

Open `Tablewise_Beta_Play.html` in a desktop or mobile modern browser. It is standalone (all CSS, JavaScript and illustrative photos bundled). Alternatively serve the source directory with `python -m http.server` and open `index.html` (the unbundled source references individual JS/CSS modules).

## Tests

The local test suite runs:

```sh
node test_app.js
node test_recipe_library.js
python test_meijer_weeklyads2.py
python test_kroger_weeklyads2.py
python test_v04_browser.py
python test_v05_buffer.py
python test_v07.py
```

Browser tests require Playwright and Chromium. Current local desktop and mobile tests passed, including quantity isolation on a shared ingredient, restoration after doubling, current regional flyers, local calculation, popup controls, pantry and one-store/cart switching.

## Price limitations

The model prices are **illustrative**, not live Meijer, Kroger, or ALDI checkout totals. A configurable 3% estimate cushion applies only to modeled prices. Manually entered prices have priority. ALDI third-party advertised prices can provisionally replace an exact ingredient+unit match only while valid; they're **not ZIP-verified**. Kroger and Meijer flyer pages are referenced only for region/date discovery and do **not** enter the price model. Verify quantities, packages, loyalty conditions, tax and final prices directly in the selected retailer storefront.

## Safeguards

WeeklyAds2's [Terms of Use](https://www.weeklyads2.com/terms-of-use/) restrict copying and republication. The refresh job limits itself to public metadata and refuses to fetch when robots.txt disallows it; it never copies flyer images or product descriptions. The original recipe publisher pages are linked. Tablewise does not reproduce copyrighted recipe instructions.

## Build and storage

Run `python build.py` in this folder to regenerate `tablewise-test.html` then copy to `Tablewise_Beta_Play.html`. The app stores household settings, meal multipliers, pantry selections and favorites in browser localStorage. No account or syncing yet.
## v0.8 — Manual price synchronization

In split-store mode each grocery row displays the selected lowest cost and a breakdown of all selected store prices. Only changed fields in the edit-price dialog are persisted as manual overrides; other stores retain their modeled prices. The assigned store, item cost, store comparison, receipt, and budget recalculate after every edit. In one-store mode, item costs use the selected store only. Browser-based regression checks cover cheaper and more expensive overrides at desktop and mobile widths.
