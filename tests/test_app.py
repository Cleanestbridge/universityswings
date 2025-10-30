# tests/test_app.py
import re
from pathlib import Path
import pytest

from flaskapp import create_app


@pytest.fixture()
def app():
    app = create_app({"TESTING": True})
    yield app


@pytest.fixture()
def client(app):
    return app.test_client()


def test_home_renders_brand_and_assets(client):
    """Home page returns 200, shows the brand, and links to static CSS/JS."""
    res = client.get("/")
    assert res.status_code == 200
    html = res.data.decode("utf-8")

    # Brand name (you rebranded to University Swings)
    assert "University Swings" in html

    # Very simple checks for assets
    assert "styles.css" in html and "/static/" in html
    assert "app.js" in html and "/static/" in html


def test_static_assets_exist_and_are_served(client):
    """styles.css and app.js are served and non-empty."""
    for path in ("/static/styles.css", "/static/app.js"):
        res = client.get(path)
        assert res.status_code == 200, f"{path} should be served"
        assert len(res.data) > 20, f"{path} looks empty"


def test_events_api_shape_and_values(client):
    """GET /api/events returns a list of event dicts with expected fields and reasonable values."""
    res = client.get("/api/events")
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


def test_request_stop_validation(client):
    """POST /api/request-stop validates required fields and returns ok for valid payloads."""
    res = client.post("/api/request-stop", json={"name": "A"})
    assert res.status_code == 400

    payload = {"name": "Bobby", "email": "b@u.edu", "university": "Indiana University"}
    res2 = client.post("/api/request-stop", json=payload)
    assert res2.status_code == 200
    out = res2.get_json()
    assert out.get("ok") is True


def test_frontend_has_ics_generator_if_present():
    """
    Optional: If your static/app.js includes .ics generation, sanity-check it exists.
    Auto-skip if not present.
    """
    p = Path("static/app.js")
    if not p.exists():
        pytest.skip("static/app.js not found")
    content = p.read_text(encoding="utf-8", errors="ignore")
    if "BEGIN:VCALENDAR" not in content:
        pytest.skip("ICS generator not present in app.js (skip)")
    assert "BEGIN:VCALENDAR" in content and "SUMMARY:" in content