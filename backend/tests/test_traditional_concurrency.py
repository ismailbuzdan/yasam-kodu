from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
import socket

from app.schemas.astrology import AstrologyRequest
from app.services.astrology_service import AstrologyService
from app.services.human_design_core import calculate_human_design_core
from app.services.traditional.lunar import calculate_lunar
from app.services.traditional.planetary_hours import calculate_planetary_hour


def test_mixed_native_repeated_concurrent_and_no_state_drift(monkeypatch):
    def no_network(*args, **kwargs):
        raise AssertionError('Core must not use the network')
    monkeypatch.setattr(socket, 'create_connection', no_network)
    instants = [datetime(y, m, 15, 12, tzinfo=timezone.utc)
                for y,m in ((1900,1),(2000,6),(2020,12))]
    jobs = []
    for instant in instants:
        jobs.extend([
            lambda dt=instant: calculate_lunar(dt),
            lambda dt=instant: calculate_planetary_hour(dt,40,30,'Europe/Istanbul'),
            lambda dt=instant: AstrologyService().calculate(AstrologyRequest(
                utc_datetime=dt,latitude=40,longitude=30)),
            lambda dt=instant: calculate_human_design_core(dt)])
    baseline = [job() for job in jobs]
    assert [job() for job in jobs] == baseline
    with ThreadPoolExecutor(max_workers=8) as pool:
        assert list(pool.map(lambda job: job(), jobs * 4)) == baseline * 4
    assert [job() for job in jobs] == baseline
