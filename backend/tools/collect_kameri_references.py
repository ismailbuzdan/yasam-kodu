"""Explicit network evidence collector. No production or Swiss imports.

Never overwrites captured evidence. Only synthetic instants and coarse locations.
Normal tests run offline; this tool is not part of the calculation package.
"""
from datetime import datetime, timezone
import hashlib
import html
import json
from pathlib import Path
import re
from urllib.parse import urlencode
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[1] / 'tests/fixtures/kameri_sources'
DATES = ('2000-01-01', '2000-01-08', '2000-01-15', '2000-01-22')


def capture(name, url, source_id, settings, scope, limitation, extract_pre=False):
    path = ROOT / name
    if path.exists():
        print('Preserved', name, flush=True)
        return
    with urlopen(Request(url, headers={'User-Agent': 'YasamKodu-KameriQualification/1.0'}), timeout=45) as response:
        body = response.read()
    receipt = dict(source_id=source_id, url=url, retrieved_at=datetime.now(timezone.utc).isoformat(),
        settings=settings, scope=scope, limitation=limitation,
        http_body_sha256=hashlib.sha256(body).hexdigest())
    if extract_pre:
        match = re.search(r'<pre[^>]*>(.*?)</pre>', body.decode(), re.S | re.I)
        if not match:
            raise ValueError('Missing swetest output')
        body = (html.unescape(re.sub(r'<[^>]+>', '', match[1])).strip() + '\n').encode()
        receipt['extraction'] = 'PRE text only; numeric characters unchanged'
    elif name.endswith('.json'):
        parsed = json.loads(body)
        if 'error' in parsed:
            raise ValueError(parsed['error'])
    receipt['sha256'] = hashlib.sha256(body).hexdigest()
    ROOT.mkdir(exist_ok=True)
    path.write_bytes(body)
    path.with_suffix(path.suffix + '.provenance.json').write_text(
        json.dumps(receipt, indent=2) + '\n', encoding='utf-8')
    print('Captured', name, flush=True)


def main():
    command = '-b1.1.2000 -ut0 -p0 -emos'
    capture('swetest_version.txt', 'https://www.astro.com/cgi/swetest.cgi?' + urlencode({'arg': command}),
        'K1-SWETEST', {'command': command}, 'Remote reported version',
        'Separate request: rise endpoint does not expose build identity.', True)
    dates = [datetime.fromisoformat(d + 'T12:00:00+00:00') for d in DATES]
    tlist = ','.join(str(dt.timestamp() / 86400 + 2440587.5) for dt in dates)
    for label, target, quantities in (('moon','301','10,31'), ('sun','10','31')):
        params = dict(format='json', COMMAND=f"'{target}'", EPHEM_TYPE="'OBSERVER'",
            CENTER="'500@399'", TLIST=f"'{tlist}'", TLIST_TYPE="'JD'", TIME_TYPE="'UT'",
            QUANTITIES=f"'{quantities}'", REF_SYSTEM="'ICRF'", APPARENT="'AIRLESS'",
            CSV_FORMAT="'YES'", EXTRA_PREC="'YES'")
        capture(f'horizons_{label}.json', 'https://ssd.jpl.nasa.gov/api/horizons.api?' + urlencode(params),
            'K1-JPL', params, 'INDEPENDENT: apparent longitude; Moon disk fraction',
            'Geocentric IAU76/80 ecliptic of date; model/frame differences versus Swiss. '
            'Not bit-identical validation. UTC after 1962. Four synthetic dates only.')
    for date_text in ('2000-01-01', '2000-06-15', '2020-12-15'):
        dt = datetime.fromisoformat(date_text)
        command = (f'-b{dt.day}.{dt.month}.{dt.year} -ut0 -p0 -rise -n2 '
                   '-geopos30,40,0 -at1013.25,15,40,0 -emos')
        capture(f'swetest_rise_{date_text}.txt',
            'https://www.astro.com/cgi/swetest.cgi?' + urlencode({'arg': command}),
            'K1-SWETEST', {'command': command}, 'SHARED: upper-limb refracted Sun rise/set UT1',
            'External execution but shared Swiss/Moshier algorithm; printed second precision. '
            'Not independent astronomy. Version only reported by separate swetest_version capture; '
            'rise output has no version/build identity.', True)
        params = dict(date=date_text, coords='40,30', tz='0', dst='false')
        capture(f'usno_rise_{date_text}.json',
            'https://aa.usno.navy.mil/api/rstt/oneday?' + urlencode(params),
            'K1-USNO', params, 'INDEPENDENT APPROXIMATE: sunrise/sunset in UT1',
            'USNO standard limb/refraction convention; no selectable pressure/temperature. '
            'Minute precision, not exact field/model matching to Swiss atmospheric model.')


if __name__ == '__main__':
    main()
