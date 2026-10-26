from refresh_ads import parse_meijer_weeklyads2, SOURCES, run
import tempfile, pathlib, datetime

sample='''<html><h1>Meijer Weekly Ad</h1><h2>Current ads</h2>
<a href="/meijer/meijer-weekly-ad-october-21-27-2026/">This week MI · OH · IN Meijer Weekly Ad October 21 - 27, 2026</a>
<a href="/meijer/meijer-early-holiday-deals-october-21-27-2026/">This week MI · OH · IN early holiday deals October 21 - 27, 2026</a>
<a href="/meijer/meijer-weekly-ad-october-14-20-2026/">Last week October 14 - 20, 2026</a>
<a href="/meijer/meijer-weekly-ad-october-28-november-3-2026/">Next week October 28 - November 3, 2026</a>
<a href="https://evil.example/meijer/meijer-weekly-ad-october-21-27-2026/">October 21-27, 2026</a>
<a href="javascript:alert(1)">October 21-27, 2026</a>
<a href="/meijer/">Store home October 21 - 27, 2026</a>
</html>'''
r,status=parse_meijer_weeklyads2(sample,'2026-10-26')
assert len(r)==2,r
assert status=='regional-flyer-dated'
assert r[0]['title']=='Meijer weekly ad'
assert all(item['validThrough']=='2026-10-27' for item in r)
assert all(item['confirmedLocal'] is False for item in r)
assert all(item['url'].startswith('https://www.weeklyads2.com/meijer/') for item in r)
assert not parse_meijer_weeklyads2(sample,'2026-11-06')[0]
assert not parse_meijer_weeklyads2(sample.replace('2026','2025'),'2026-10-26')[0]
assert SOURCES['Meijer']['url']=='https://www.weeklyads2.com/meijer/'
with tempfile.TemporaryDirectory() as td:
    out=pathlib.Path(td)
    (out/'index.html').write_text('<html><!-- TABLEWISE_ADS_START --><script>old</script><!-- TABLEWISE_ADS_END --></html>')
    data=run(out,html_override='<html><h1>ALDI no current ad</h1></html>',meijer_html_override=sample,now=datetime.date(2026,10,26))
    meijer=data['sources'][0]
    assert meijer['status']=='regional-flyer-dated'
    assert len(meijer['flyers'])==2
    assert meijer['officialUrl'].startswith('https://www.meijer.com')
    assert not any(d['store']=='Meijer' for d in data['deals'])
    assert 'www.weeklyads2.com/meijer/' in (out/'index.html').read_text()
print('PASS: WeeklyAds2 Meijer discovery, expiry, source scope, no republished prices')
