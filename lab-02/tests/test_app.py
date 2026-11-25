"""The tests the pipeline runs. No Docker, no database, no network.

COUNTER_FILE is pointed at a temporary directory, because the app's default is
/data/visits.txt and a runner has no /data. The app reads its configuration from
the environment at import time, so each test sets the environment and reloads it.
"""
import importlib

import pytest

import app


@pytest.fixture
def client(tmp_path, monkeypatch):
    monkeypatch.setenv("COUNTER_FILE", str(tmp_path / "visits.txt"))
    monkeypatch.delenv("DATABASE_URL", raising=False)
    importlib.reload(app)
    app.app.config.update(TESTING=True)
    return app.app.test_client()


def test_health_is_ok(client):
    r = client.get("/health")
    assert r.status_code == 200
    assert r.data.decode().strip() == "ok"


def test_ready_reports_the_file_store_when_there_is_no_database(client):
    r = client.get("/ready")
    assert r.status_code == 200
    body = r.get_json()
    assert body["ready"] is True
    assert body["store"].startswith("file:")


def test_visits_counts_up(client):
    first = client.get("/visits").get_json()["visits"]
    second = client.get("/visits").get_json()["visits"]
    assert second == first + 1


def test_price_fails_loudly_when_the_partner_is_unreachable(monkeypatch):
    """We do not own the partner, so a test must never call it.

    Pointed at a port nothing is listening on, the app must answer 502 and say
    which URL it tried — not hang, and not pretend the price is zero.
    """
    monkeypatch.setenv("PARTNER_URL", "http://127.0.0.1:9")
    monkeypatch.setenv("PARTNER_TIMEOUT", "0.25")
    importlib.reload(app)
    r = app.app.test_client().get("/price/MK-II")
    assert r.status_code == 502
    body = r.get_json()
    assert body["sku"] == "MK-II"
    assert "127.0.0.1:9" in body["source"]
