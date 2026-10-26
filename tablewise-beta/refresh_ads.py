#!/usr/bin/env python3
"""Refresh limited public weekly-ad metadata + reasonably parseable ALDI listing.
No logins, browser automation, paywall bypass, image OCR, or undocumented APIs.
Crawling is limited to 3 public pages, conditional on robots permissions. Official
retailers' terms must still be respected. Cannot verify live local shelf prices.
"""
import argparse, datetime as dt, json, pathlib, re, sys, time
from urllib.parse import urlparse
from urllib.request import Request, urlopen
from urllib.robotparser import RobotFileParser
from bs4 import BeautifulSoup

BASE=pathlib.Path(__file__).parent
AGENT='TablewiseBetaAdCheck/0.1 (+human-reviewed personal grocery planner)'
SOURCES={
 'Meijer': {'url':'https://www.meijer.com/shopping/weekly-ad?storeId=25','name':'Meijer Okemos','address':'2055 W Grand River, Okemos, MI 48864','detail':'Local flyer is largely image based; per-item prices need confirmation.'},
 'ALDI': {'url':'https://www.aldi.us/store/aldi/pages/weekly-specials','name':'ALDI Okemos','address':'5165 Marsh Rd, Okemos, MI 48864','detail':'Public online listing; not necessarily 48864 shelf prices.'},
 'Kroger': {'url':'https://www.weeklyad.io/kroger','name':'Kroger Okemos','address':'4884 Marsh Rd, Okemos, MI 48864','detail':'Michigan regional circular can be browsed, but local coupons may vary.'},
}

def allowed(url):
    p=urlparse(url);r=RobotFileParser();r.set_url(f'{p.scheme}://{p.netloc}/robots.txt')
    try:
        r.read();return r.can_fetch(AGENT,url)
    except Exception:
        return False # fail closed

def public_html(url):
    if not allowed(url):raise RuntimeError('robots.txt blocks or could not be retrieved')
    req=Request(url,headers={'User-Agent':AGENT,'Accept':'text/html','Accept-Language':'en-US,en;q=0.8'})
    with urlopen(req,timeout=14) as r:
        if 'text/html' not in r.headers.get('Content-Type',''):raise ValueError('not HTML')
        b=r.read(2_000_001)
        if len(b)>2_000_000:raise ValueError('page too large')
        return b.decode('utf-8','replace')

def parse_aldi(html,seen):
    soup=BeautifulSoup(html,'html.parser')
    # Be conservative: only candidates whose visible/accessible names contain
    # explicit current price and a plain product name; exclude Sponsored.
    candidates=[]
    for item in soup.find_all(['a','article','li'],limit=1000):
        title=item.get('aria-label') or item.get_text(' ',strip=True)
        if not ('Current price:' in title and '$' in title):continue
        if 'Sponsored' in title or 'Sponsored' in item.get_text(' ',strip=True):continue
        match=re.search(r'Current price:\s*\$([0-9]{1,4}\.[0-9]{2})',title,re.I)
        if not match:continue
        price=float(match.group(1))
        if not (0.1<=price<=200):continue
        # Instacart's accessibility markup contains a price twice:
        # "$2.29$229 Product name". Keep the name after that segment.
        label=title[match.end():]
        label=re.sub(r'^\s*(?:per package \(estimated\))?\s*\$\d+(?:/\w+)?\s*(?:\(est\.\))?','',label).strip()
        if 'Original Price:' in label:label=label.split('Original Price:',1)[-1]
        label=re.sub(r'^\s*\$\d+(?:\.\d+)?\s*(?:per package \(estimated\))?\s*(?:\d+% off)?\s*','',label)
        label=re.sub(r'\s+Many in stock$','',label).strip()
        if not label or len(label)>110 or re.match(r'^(Current price|Original Price)',label):continue
        if re.search(r'\$\d',label):continue # ambiguous price/size
        candidates.append((label,price))
    unique=[];seen_keys=set()
    for name,price in candidates:
        key=name.lower()
        if key in seen_keys:continue
        seen_keys.add(key)
        unique.append(dict(id='aldi-'+re.sub('[^a-z0-9]+','-',key).strip('-')[:55]+'-'+seen.replace('-',''),store='ALDI',name=name,price=price,unit='listed product',seenAt=seen,validThrough=seen,source=SOURCES['ALDI']['url'],scope='Public online offer, exact local price/eligibility unconfirmed',confirmedLocal=False))
    # No detected start/end dates: expire the day captured, not an invented week
    return unique[:30]

def parse_local_flyers(html,store):
    soup=BeautifulSoup(html,'html.parser');text=soup.get_text(' ',strip=True)
    state='flyer-link'
    if len(text)>200 and store=='Meijer' and 'Weekly' in text:state='flyer-link'
    if len(text)>200 and store=='Kroger' and 'Michigan' in text:state='regional-flyer-link'
    return state

def run(output=BASE):
    seen=dt.datetime.now(dt.timezone.utc).date().isoformat()
    report={'schema':1,'updated':seen,'zip':'48864','sources':[],'deals':[]}
    for store,info in SOURCES.items():
        status='unavailable';detail=info['detail']
        try:
            if store=='ALDI':
                # ALDI online store uses Instacart, whose terms prohibit automated scraping.
                # Provide the weekly ad link without fetching or republishing a product feed.
                status='flyer-link';detail+=' Automatic access is disabled per terms.'
                raise PermissionError('ALDI / Instacart terms prohibit automated scraping')
            html=public_html(info['url']);status=parse_local_flyers(html,store)
            # No automated price extraction where retailer terms prohibit it.
        except PermissionError:
            pass
        except Exception as exc:
            detail+=' Fetch unavailable ('+type(exc).__name__+').' 
        report['sources'].append(dict(store=store,name=info['name'],address=info['address'],url=info['url'],status=status,detail=detail))
        time.sleep(1.2)
    if not report['deals']:
        # Avoid overwriting an old feed with fake "fresh" deals; expired deals
        # should not survive. Retailer URLs are still made available.
        pass
    payload=json.dumps(report,indent=2,ensure_ascii=False)
    (output/'ads.json').write_text(payload+'\n',encoding='utf8')
    new_script='window.TABLEWISE_ADS='+json.dumps(report,separators=(',',':'),ensure_ascii=False)+';\n'
    (output/'ads-data.js').write_text(new_script,encoding='utf8')
    standalone=output/'index.html'
    if standalone.is_file():
        page=standalone.read_text(encoding='utf8')
        block='<!-- TABLEWISE_ADS_START -->\n<script>\n'+new_script+'</script>\n<!-- TABLEWISE_ADS_END -->'
        refreshed,count=re.subn(r'<!-- TABLEWISE_ADS_START -->.*?<!-- TABLEWISE_ADS_END -->',lambda match:block,page,flags=re.S)
        if count==1:standalone.write_text(refreshed,encoding='utf8')
    return report

if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--output',type=pathlib.Path,default=BASE);args=ap.parse_args()
    res=run(args.output);print(json.dumps({'checked':res['updated'],'sources':[(s['store'],s['status']) for s in res['sources']],'priced_deals':len(res['deals'])}))