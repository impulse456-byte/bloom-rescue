from refresh_ads import parse_kroger_weeklyads2, run
import datetime as dt
from pathlib import Path
from tempfile import TemporaryDirectory
def link(region, suffix):
    return f'<a href="/kroger/kroger-weekly-ad-october-21-27-2026{suffix}">This week {region} October 21 - 27, 2026</a>'
sample='<html>'+''.join([
link('MI','-mi/'),link('IN','-in/'),link('OH','-oh/'),
link('OH','/'),link('TN','-tn/'),link('GA','-ga/'),
link('GA','-ga-30303/'),link('TX','-tx/'),link('TX','-tx-77385/')
])+'<a href="/kroger/kroger-weekly-ad-october-14-20-2026-mi/">Last week MI October 14 - 20, 2026</a></html>'
rows,status=parse_kroger_weeklyads2(sample,'2026-10-26')
assert status=='regional-flyer-dated' and len(rows)==9,(status,rows)
assert {x['region'] for x in rows}=={'MI','IN','OH','TN','GA','TX'}
assert all(not r['confirmedLocal'] for r in rows)
assert parse_kroger_weeklyads2(sample,'2026-11-08')[0]==[]
with TemporaryDirectory() as d:
    p=Path(d)
    (p/'index.html').write_text('<html><!-- TABLEWISE_ADS_START --><script>old</script><!-- TABLEWISE_ADS_END --></html>')
    report=run(p,html_override='<html/>',meijer_html_override='<html/>',
               kroger_html_override=sample,now=dt.date(2026,10,26))
    k=next(x for x in report['sources'] if x['store']=='Kroger')
    assert len(k['flyers'])==9 and k['status']=='regional-flyer-dated'
    assert not any(x['store']=='Kroger' for x in report['deals'])
    assert 'weeklyads2.com/kroger/' in (p/'index.html').read_text()
print('PASS: nine Kroger regional flyers, date filters and no invented prices')
