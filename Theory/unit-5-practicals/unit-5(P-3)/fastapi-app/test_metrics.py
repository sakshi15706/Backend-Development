import time

import pytest
from fastapi.testclient import TestClient

import main
from metrics import Recorder, percentile


@pytest.fixture()
def client():
    main.recorder.reset()
    with TestClient(main.app, raise_server_exceptions=False) as c:
        yield c


def test_percentile_nearest_rank():
    values = list(range(1, 101))
    assert percentile(values, 0.50) == 50
    assert percentile(values, 0.95) == 95
    assert percentile(values, 0.99) == 99          # the slide's int(100 * 0.99) = index 99 -> 100 (the max)
    assert percentile([], 0.99) == 0


def test_task1_ping_then_metrics_has_count_and_percentiles(client):
    for _ in range(10):
        client.get("/api/ping")
    m = client.get("/metrics").json()
    assert m["count"] == 10
    assert 0 < m["p50"] <= m["p95"] <= m["p99"] <= m["max"]


def test_reading_metrics_does_not_change_them(client):
    client.get("/api/ping")
    for _ in range(3):
        client.get("/metrics")
    assert client.get("/metrics").json()["count"] == 1


def test_window_is_bounded_but_counters_keep_counting():
    r = Recorder(window_size=5)
    for i in range(12):
        r.record("/x", float(i), 200)
    s = r.snapshot()
    assert (s["count"], s["totalRequests"], s["max"]) == (5, 12, 11.0)


def test_error_rate_counts_unhandled_exceptions_as_500(client):
    client.get("/api/ping")
    assert client.get("/api/error").status_code == 500
    m = client.get("/metrics").json()
    assert m["errors"] == 1 and m["errorRate"] == 50.0


def test_filter_by_path(client):
    client.get("/api/ping")
    client.get("/api/attendance")
    client.get("/api/attendance")
    assert client.get("/metrics", params={"path": "/api/attendance"}).json()["count"] == 2


def test_reset(client):
    client.get("/api/ping")
    client.post("/metrics/reset")
    assert client.get("/metrics").json()["totalRequests"] == 0


def test_task3_delay_raises_latency_by_about_50ms(client, monkeypatch):
    for _ in range(10):
        client.get("/api/ping")
    before = client.get("/metrics").json()["p50"]
    client.post("/metrics/reset")
    monkeypatch.setenv("PING_DELAY_MS", "50")
    for _ in range(10):
        client.get("/api/ping")
    after = client.get("/metrics").json()["p50"]
    assert 40 <= after - before <= 120, (before, after)


def test_blocking_call_in_async_endpoint_serialises_requests():
    """time.sleep inside `async def` blocks the loop; the same wait in a plain `def` does not."""
    import asyncio
    import httpx

    async def burst(path, n=8):
        transport = httpx.ASGITransport(app=main.app)
        async with httpx.AsyncClient(transport=transport, base_url="http://test") as c:
            start = time.perf_counter()
            await asyncio.gather(*[c.get(path) for _ in range(n)])
            return time.perf_counter() - start

    blocked = asyncio.run(burst("/api/blocking-in-async"))
    threaded = asyncio.run(burst("/api/blocking-in-sync"))
    assert blocked >= 8 * 0.05 * 0.9, blocked      # strictly one after another: ~0.4 s
    assert threaded < blocked * 0.6, (threaded, blocked)   # overlapped in the thread pool
