# flaskapp/__init__.py
from datetime import datetime
from flask import Flask, jsonify, render_template, request

def create_app(test_config=None):
    # IMPORTANT: static/templates are at the project root, so go up one level
    app = Flask(
        __name__,
        static_folder="../static",
        template_folder="../templates",
    )
    app.config.update(JSON_SORT_KEYS=False, SECRET_KEY="dev-not-secret")
    if test_config:
        app.config.update(test_config)

    EVENTS = [
        {"id": 1, "date": "2025-09-06", "university": "Indiana University", "city": "Bloomington", "state": "IN", "type": "Tailgate Stop", "status": "past"},
        {"id": 2, "date": "2025-10-11", "university": "Ohio State University", "city": "Columbus", "state": "OH", "type": "Tailgate Stop", "status": "past"},
        {"id": 3, "date": "2025-10-25", "university": "University of Wisconsin", "city": "Madison", "state": "WI", "type": "Tailgate Stop", "status": "open"},
        {"id": 4, "date": "2025-11-08", "university": "University of Michigan", "city": "Ann Arbor", "state": "MI", "type": "Tailgate Stop", "status": "open"},
        {"id": 5, "date": "2025-11-15", "university": "Purdue University", "city": "West Lafayette", "state": "IN", "type": "Club Night", "status": "open"},
        {"id": 6, "date": "2025-11-22", "university": "Penn State University", "city": "State College", "state": "PA", "type": "Tailgate Stop", "status": "hold"},
    ]

    @app.route("/")
    def home():
        return render_template("index.html", year=datetime.now().year)

    @app.get("/api/events")
    def api_events():
        return jsonify(EVENTS)

    @app.post("/api/request-stop")
    def api_request_stop():
        data = request.get_json(force=True, silent=True) or {}
        required = ["name", "email", "university"]
        missing = [k for k in required if not data.get(k)]
        if missing:
            return {"ok": False, "error": f"Missing: {', '.join(missing)}"}, 400
        return {"ok": True}
    return app
