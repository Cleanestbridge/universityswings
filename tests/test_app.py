# tests/test_app.py
import re
from pathlib import Path
import pytest

from flaskapp import create_app


@pytest.fixture()
def app():
    # Default to testing mode; allow overrides via config if needed
    app = create_app({"TESTING": True})
    return app


@pytest.fixture()
def client(app):
    return app.test_client()


def test_home_renders_brand_and_assets(client):
    """Home page returns 200, shows the brand, and links to static CSS/JS."""
    res = client.get("/")
    assert res.status_code == 200
    html = res.data.decode("utf-8")

    # Brand string
    assert "University Swings" in html

    # Very simple checks for assets (linked in HTML)
    assert "styles.css" in html and "/static/" in html
    assert "app.js" in html and "/static/" in html


def test_static_assets_exist_and_are_served(client):
    """styles.css and app.js are served and non-empty."""
    # Flask serves /static/* in local dev; if not, skip (Pages handles prod).
    for path in ("/static/styles.css", "/static/app.js"):
        res = client.get(path)
        if res.status_code == 404:
            pytest.skip(f"{path} not served by Flask (ok for Cloudflare Pages deploy).")
        assert res.status_code == 200, f"{path} should be served"
        assert len(res.data) > 50, f"{path} looks empty"


def test_events_api_shape_and_values(client):
    """
    GET /api/events returns a list of event dicts with expected fields and reasonable values.
    If not implemented in Flask (because Pages Functions handle prod), skip.
    """
    res = client.get("/api/events")
    if res.status_code == 404:
        pytest.skip("/api/events not implemented in Flask locally (handled by Pages Functions in prod).")
    assert res.status_code == 200
    data = res.get_json()
    assert isinstance(data, list), "Expected a list of events"
    assert len(data) >= 1, "Expected at least one demo event"

    allowed_status = {"past", "open", "hold", "sold"}
    date_re = re.compile(r"^\d{4}-\d{2}-\d{2}$")
    state_re = re.compile(r"^[A-Z]{2}$")

    for ev in data:
        for key in ("id", "date", "university", "city", "state", "type", "status"):
            assert key in ev, f"Event missing key: {key}"

        assert isinstance(ev["id"], int)
        assert isinstance(ev["university"], str) and ev["university"].strip()
        assert isinstance(ev["city"], str) and ev["city"].strip()
        assert isinstance(ev["state"], str) and state_re.match(ev["state"]), f"Bad state: {ev['state']}"
        assert isinstance(ev["type"], str) and ev["type"].strip()
        assert ev["status"] in allowed_status, f"Bad status: {ev['status']}"
        assert date_re.match(ev["date"]), f"Bad date format: {ev['date']}"


def test_request_api_validation(client):
    """
    POST /api/request validates required fields and returns ok:true for valid payloads.
    If not implemented in Flask, skip (handled by Pages Functions in prod).
    """
    bad = client.post("/api/request", json={"name": "A"})
    if bad.status_code == 404:
        pytest.skip("/api/request not implemented in Flask locally (handled by Pages Functions in prod).")

    assert bad.status_code == 400

    payload = {"name": "Bobby", "email": "b@u.edu", "university": "Indiana University"}
    ok = client.post("/api/request", json=payload)
    assert ok.status_code == 200
    out = ok.get_json()
    assert out.get("ok") is True


def test_frontend_has_ics_generator_if_present():
    """
    Optional: If app.js includes .ics generation, sanity-check it exists.
    Looks in /static/app.js (Flask dev) or /docs/static/app.js (Pages).
    Auto-skip if not present.
    """
    candidates = [
        Path("static/app.js"),
        Path("docs/static/app.js"),
    ]
    path = next((p for p in candidates if p.exists()), None)
    if not path:
        pytest.skip("No app.js found in static or docs/static (skip).")

    content = path.read_text(encoding="utf-8", errors="ignore")
    if "BEGIN:VCALENDAR" not in content:
        pytest.skip("ICS generator not present in app.js (skip).")
    assert "BEGIN:VCALENDAR" in content and "SUMMARY:" in content