"""Offline field-scoped evidence; expected numbers parsed only from external artifacts."""
import csv
from datetime import date, datetime, timezone
import hashlib
import json
from pathlib import Path
import re

import pytest

from app.services.traditional.hijri import calculate_hijri, _from_jdn
from app.services.traditional.lunar import calculate_lunar
from app.services.traditional.planetary_hours import calculate_planetary_hour

ROOT = Path(__file__).parent / 'fixtures/kameri_sources'


def horizons(body):
    payload = json.loads((ROOT / f'horizons_{body}.json').read_text())
    assert 'DE441' in payload['result'] and 'GEOCENTRIC' in payload['result']
    table = payload['result'].split('$$SOE')[1].split('$$EOE')[0].strip()
    return list(csv.reader(table.splitlines()))


@pytest.mark.parametrize('index', range(4))
def test_independent_jpl_longitudes_and_fraction(index):
    moon, sun = horizons('moon')[index], horizons('sun')[index]
    dt = datetime.strptime(moon[0].strip(), '%Y-%b-%d %H:%M:%S.%f').replace(tzinfo=timezone.utc)
    result = calculate_lunar(dt)
    # A priori scope: 0.001 deg accounts for model/frame differences; 0.0001
    # fraction is 0.01 percentage point. Neither is bitwise equality.
    assert abs(result.moon_longitude - float(moon[4])) < 0.001
    assert abs(result.sun_longitude - float(sun[3])) < 0.001
    assert abs(result.illuminated_fraction - float(moon[3]) / 100) < 0.0001


def event_jd(date_text, time_text):
    day = datetime.strptime(date_text.strip(), '%d.%m.%Y').date()
    hour, minute, seconds = map(float, time_text.split(':'))
    # These are explicitly UT1 calendar labels in swetest, not UTC.
    return day.toordinal() + 1721424.5 + (hour*3600 + minute*60 + seconds)/86400


@pytest.mark.parametrize('day', ['2000-01-01','2000-06-15','2020-12-15'])
def test_external_shared_swetest_solar_events(day):
    raw = (ROOT / f'swetest_rise_{day}.txt').read_text()
    rows = re.findall(r'rise\s+(\d+\.\d+\.\d+)\s+(\d+:\d+:\d+\.\d+)\s+set\s+(\d+\.\d+\.\d+)\s+(\d+:\d+:\d+\.\d+)', raw)
    assert len(rows) >= 2
    expected = [event_jd(rows[0][0],rows[0][1]), event_jd(rows[0][2],rows[0][3]),
                event_jd(rows[1][0],rows[1][1])]
    actual = calculate_planetary_hour(datetime.fromisoformat(day+'T12:00:00+00:00'),40,30,'Europe/Istanbul').events
    # 0.1-second printed precision plus search convergence; shared integration only.
    for value, ref in zip((actual.sunrise,actual.sunset,actual.next_sunrise), expected):
        assert abs(value-ref)*86400 < 0.2


@pytest.mark.parametrize('day', ['2000-01-01','2000-06-15','2020-12-15'])
def test_independent_approximate_usno_solar_events(day):
    payload = json.loads((ROOT / f'usno_rise_{day}.json').read_text())
    assert payload['apiversion'] == '4.0.1'
    data = payload['properties']['data']
    assert data['tz'] == 0 and not data['isdst']
    refs = {v['phen']:v['time'] for v in data['sundata']}
    actual = calculate_planetary_hour(datetime.fromisoformat(day+'T12:00:00+00:00'),40,30,'Europe/Istanbul').events
    midnight = date.fromisoformat(day).toordinal() + 1721424.5
    for value, field in ((actual.sunrise,'Rise'),(actual.sunset,'Set')):
        hour, minute = map(int, refs[field].split(':'))
        # Coarse cross-model check only: fixed USNO 50' depression, minute output.
        assert abs((value-midnight)*86400 - (hour*3600+minute*60)) < 120


def test_published_calendar_correspondences():
    epoch = _from_jdn(1948440)
    assert (epoch.hijri_year,epoch.hijri_month,epoch.hijri_day) == (1,1,1)
    value = calculate_hijri(date(1945,11,12))
    assert date(1945,11,12).toordinal() == 710347
    assert (value.hijri_year,value.hijri_month,value.hijri_day) == (1364,12,6)


def test_evidence_inventory_and_hashes():
    expected = {'horizons_moon.json','horizons_sun.json','calendar_excerpt.txt','swetest_version.txt'}
    expected |= {f'{prefix}_{day}.{ext}' for day in ('2000-01-01','2000-06-15','2020-12-15')
                 for prefix,ext in (('swetest_rise','txt'),('usno_rise','json'))}
    receipts = list(ROOT.glob('*.provenance.json'))
    assert {p.name.removesuffix('.provenance.json') for p in receipts} == expected
    for path in receipts:
        metadata = json.loads(path.read_text())
        artifact = path.with_name(path.name.removesuffix('.provenance.json'))
        assert hashlib.sha256(artifact.read_bytes()).hexdigest() == metadata['sha256']
        assert metadata['source_id'] and metadata['retrieved_at'] and metadata['limitation']
        assert metadata['scope'] and metadata['url'].startswith('https://')
