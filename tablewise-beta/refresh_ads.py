#!/usr/bin/env python3
"""Refresh public weekly grocery-ad metadata for Tablewise.

ALDI uses aldiweekly.com, an INDEPENDENT third-party summary, not an official
ALDI localized catalog. Respect robots.txt, parse only limited, explicitly priced
list entries in current grocery categories, expire them at the ad end date,
and never label them locally verified. No image copying, login, browser bypass,
private APIs, OCR, or misleading prices.
"""
import argparse
import datetime as dt
import json
import pathlib
import re
import time
from urllib.parse import urlparse, urljoin
from urllib.request import Request, urlopen
from urllib.robotparser import RobotFileParser
from bs4 import BeautifulSoup
from bs4.element import Tag

BASE = pathlib.Path(__file__).parent
AGENT = 'TablewiseBetaAdCheck/0.2 (+personal grocery planner; weekly public-page access)'
SOURCES = {
    'Meijer': {'url': 'https://www.weeklyads2.com/meijer/',
               'officialUrl': 'https://www.meijer.com/shopping/weekly-ad?storeId=25',
               'name': 'Meijer Okemos', 'address': '2055 W Grand River, Okemos, MI 48864',
               'detail': 'WeeklyAds2 is an independent MI/OH/IN regional flyer index, NOT ZIP-specific pricing. Its flyers are mostly images; only dated links are indexed. Verify exact prices, packages and mPerks at Meijer.'},
    'ALDI': {'url': 'https://aldiweekly.com/',
             'name': 'ALDI Okemos', 'address': '5165 Marsh Rd, Okemos, MI 48864',
             'detail': 'Independent ad summary (not affiliated with ALDI); prices and availability may vary by location. Check your local store.'},
    'Kroger': {'url': 'https://www.weeklyad.io/kroger',
               'name': 'Kroger Okemos', 'address': '4884 Marsh Rd, Okemos, MI 48864',
               'detail': 'Michigan regional circular; local prices/coupon eligibility require confirmation.'}
}
MONTH = r'(?:Jan(?:uary)?|Feb(?:ruary)?|Mar(?:ch)?|Apr(?:il)?|May|Jun(?:e)?|Jul(?:y)?|Aug(?:ust)?|Sep(?:tember)?|Oct(?:ober)?|Nov(?:ember)?|Dec(?:ember)?)'
DATE_WINDOW = re.compile(rf'\b({MONTH})\s+(\d{{1,2}})\s*[-–—]\s*(?:({MONTH})\s+)?(\d{{1,2}})\s*,?\s*(20\d{{2}})\b', re.I)
PRICE_ROW = re.compile(r'^(.+?)\s*[:：–]\s*\$([0-9]{1,3}(?:\.[0-9]{2})?)(?:\s*/\s*|\s+)?(lb|each|oz|kg)?\s*$', re.I)
SECTIONS = {'fresh produce deals': 'Produce', 'meat and poultry deals': 'Meat', 'seafood deals': 'Seafood'}


def allowed(url):
    parsed = urlparse(url)
    robots = RobotFileParser()
    robots.set_url(f'{parsed.scheme}://{parsed.netloc}/robots.txt')
    try:
        robots.read()
        # If robots.txt cannot be retrieved, RobotFileParser normally has no
        # entries and denies access. Fail closed on any exception.
        return robots.can_fetch(AGENT, url)
    except Exception:
        return False


def public_html(url):
    if not allowed(url):
        raise RuntimeError('robots.txt blocked or inaccessible')
    request = Request(url, headers={
        'User-Agent': AGENT, 'Accept': 'text/html', 'Accept-Language': 'en-US,en;q=0.8'
    })
    with urlopen(request, timeout=14) as response:
        if 'text/html' not in response.headers.get('Content-Type', ''):
            raise ValueError('response is not HTML')
        contents = response.read(2_000_001)
        if len(contents) > 2_000_000:
            raise ValueError('page exceeds safety size limit')
        return contents.decode('utf-8', 'replace')


def date_range(page_text):
    # Use only the introductory current-week section, never 'next week' text.
    lead = page_text[:3500]
    match = DATE_WINDOW.search(lead)
    if not match:
        return None
    m1, d1, m2, d2, year = match.groups()
    def parse_date(month, day):
        m = month[:3].title()
        return dt.datetime.strptime(f'{m} {day} {year}', '%b %d %Y').date()
    try:
        start = parse_date(m1, d1)
        end = parse_date(m2 or m1, d2)
        # A weekly circular can cross a calendar year, e.g., Dec 30-Jan 5.
        if end < start and m2 and start.month == 12 and end.month == 1:
            end = end.replace(year=end.year + 1)
        if not (0 <= (end - start).days <= 14):
            return None
        return start, end
    except (ValueError, OverflowError):
        return None


def item_unit(name, denominator):
    if denominator:
        return 'lb' if denominator.lower() == 'lb' else denominator.lower()
    pkg = re.search(r'\(([^)]{1,36})\)', name)
    if pkg:
        return pkg.group(1).strip()
    return 'each' if re.search(r'\b(avocados?|kiwi)\b', name, re.I) else 'item'


def grocery_mapping(name, unit):
    norm = name.lower()
    # Exact corresponding ingredient and units, no cross-item guesses.
    if unit == 'lb':
        if 'chicken breast' in norm and 'boneless' not in norm:
            return 'chicken'
        if 'chicken thigh' in norm:
            return 'thighs'
    if unit == 'each' and norm.strip() in ('avocado', 'avocados'):
        return 'avocado'
    return None


def parse_aldiweekly(html, seen):
    soup = BeautifulSoup(html, 'html.parser')
    heading = soup.find(['h1', 'h2'], string=re.compile('ALDI Weekly Ad This Week', re.I))
    intro = soup.get_text(' ', strip=True)[:3500]
    dates = date_range(intro)
    today = dt.date.fromisoformat(seen)
    if dates is None or not (dates[0] <= today <= dates[1]):
        return [], 'no-current-dated-ad'
    start, end = dates
    if len(soup.find_all(['h2', 'h3', 'h4'])) > 140:
        return [], 'page-structure-unrecognized'
    found = []
    keys = set()
    within_this_week = False
    for header in soup.find_all(['h2', 'h3', 'h4']):
        section_name = header.get_text(' ', strip=True).strip().lower()
        if header.name == 'h2':
            within_this_week = 'aldi weekly ad this week' in section_name
        if not within_this_week or section_name not in SECTIONS:
            continue
        category = SECTIONS[section_name]
        for elem in header.next_elements:
            if isinstance(elem, Tag) and elem.name in ('h2', 'h3', 'h4'):
                break
            if not isinstance(elem, Tag) or elem.name != 'li':
                continue
            # Only list items visibly contained in the current grocery section.
            label = re.sub(r'\s+', ' ', elem.get_text(' ', strip=True)).strip()
            m = PRICE_ROW.fullmatch(label)
            if not m:
                continue
            name, value, denom = m.groups()
            name = name.strip(' -–:')
            price = float(value)
            if len(name) < 4 or len(name) > 95 or not (.1 <= price <= 150):
                continue
            unit = item_unit(name, denom)
            identifier = re.sub(r'[^a-z0-9]+', '-', name.lower()).strip('-')[:60]
            if not identifier or identifier in keys:
                continue
            keys.add(identifier)
            row = dict(id=f'aldiweekly-{end:%Y%m%d}-{identifier}',
                store='ALDI', name=name, price=price, unit=unit,
                seenAt=seen, validFrom=start.isoformat(), validThrough=end.isoformat(),
                source=SOURCES['ALDI']['url'],
                scope='Independent ALDI ad summary; NOT a verified price for ZIP 48864',
                confirmedLocal=False, category=category)
            mapping = grocery_mapping(name, unit)
            if mapping:
                row['mapping'] = mapping
            found.append(row)
            if len(found) >= 45:
                return found, 'third-party-priced-offers'
    return found, 'third-party-priced-offers' if found else 'no-readable-prices'



def parse_meijer_weeklyads2(html, seen):
    """Discover valid *links and dates* on WeeklyAds2; never copy ad images or
    extract prices, and never claim any regional flyer matches an Okemos receipt.
    This source's license restricts copying and public display of materials.
    """
    soup = BeautifulSoup(html, 'html.parser')
    today = dt.date.fromisoformat(seen)
    flyers, seen_urls = [], set()
    for anchor in soup.select('a[href]'):
        url = urljoin(SOURCES['Meijer']['url'], anchor.get('href', ''))
        parsed = urlparse(url)
        if parsed.scheme != 'https' or parsed.netloc not in {'www.weeklyads2.com', 'weeklyads2.com'}:
            continue
        if not re.fullmatch(r'/meijer/[a-z0-9-]+/?', parsed.path, re.I):
            continue
        label = ' '.join(x for x in (anchor.get_text(' ', strip=True), anchor.get('title', ''),
                                     anchor.get('aria-label', '')) if x).strip()
        dates = date_range(label)
        # Avoid stale pages, next week's preview and undated posts.
        if not dates or not (dates[0] <= today <= dates[1]):
            continue
        if url in seen_urls:
            continue
        seen_urls.add(url)
        slug = parsed.path.strip('/').split('/')[-1]
        if 'weekly-ad' in slug:
            title = 'Meijer weekly ad'
        elif 'holiday' in slug:
            title = 'Meijer seasonal deals'
        elif 'halloween' in slug:
            title = 'Meijer Halloween specials'
        else:
            title = 'Meijer regional circular'
        flyers.append({'title': title, 'url': url, 'validFrom': dates[0].isoformat(),
                       'validThrough': dates[1].isoformat(), 'region': 'MI / OH / IN',
                       'confirmedLocal': False})
        if len(flyers) >= 6:
            break
    flyers.sort(key=lambda x: (0 if x['title']=='Meijer weekly ad' else 1, x['title']))
    return flyers, 'regional-flyer-dated' if flyers else 'no-current-dated-flyer'


def run(output=BASE, html_override=None, now=None, meijer_html_override=None):
    seen = (now or dt.datetime.now(dt.timezone.utc).date()).isoformat()
    report = dict(schema=2, updated=seen, zip='48864', sources=[], deals=[])
    for store, source in SOURCES.items():
        status = 'unavailable'
        detail = source['detail']
        flyers = []
        try:
            if store == 'Meijer':
                # One public index request, only when robots permit access.
                # Facts about dates and links only, never pages, images or prices.
                page = meijer_html_override if meijer_html_override is not None else public_html(source['url'])
                flyers, status = parse_meijer_weeklyads2(page, seen)
                if not flyers:
                    detail += ' This cycle did not confirm a current dated flyer.'
            elif store == 'ALDI':
                page = html_override if html_override is not None else public_html(source['url'])
                report['deals'], status = parse_aldiweekly(page, seen)
                if status != 'third-party-priced-offers':
                    detail += ' No current price feed could be verified this cycle.'
            else:
                # Store flyers remain direct links pending machine-readable
                # permitted data feeds; do not crawl restricted retailer sites.
                status = 'flyer-link'
        except Exception as exc:
            status = 'flyer-link'
            detail += f' Automated retrieval unavailable ({type(exc).__name__}).'
        entry = dict(store=store, name=source['name'],
            address=source['address'], url=source['url'], status=status, detail=detail)
        if store == 'Meijer':
            entry['officialUrl'] = source['officialUrl']
            entry['flyers'] = flyers
        report['sources'].append(entry)
        if store == 'ALDI' and html_override is None:
            time.sleep(1)
    output.mkdir(parents=True, exist_ok=True)
    (output / 'ads.json').write_text(json.dumps(report, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
    js = 'window.TABLEWISE_ADS=' + json.dumps(report, separators=(',', ':'), ensure_ascii=False) + ';\n'
    (output / 'ads-data.js').write_text(js, encoding='utf-8')
    standalone = output / 'index.html'
    if standalone.exists():
        page = standalone.read_text(encoding='utf-8')
        block = '<!-- TABLEWISE_ADS_START -->\n<script>\n' + js + '</script>\n<!-- TABLEWISE_ADS_END -->'
        refreshed, count = re.subn(r'<!-- TABLEWISE_ADS_START -->.*?<!-- TABLEWISE_ADS_END -->',
                                   lambda _: block, page, flags=re.S)
        if count == 1:
            standalone.write_text(refreshed, encoding='utf-8')
    return report


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', type=pathlib.Path, default=BASE)
    args = parser.parse_args()
    result = run(args.output)
    print(json.dumps(dict(checked=result['updated'], sources=[(i['store'], i['status']) for i in result['sources']], priced_deals=len(result['deals']))))