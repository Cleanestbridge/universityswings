# University Swings — Mobile Golf Simulator Campus Tour

Bring the *tailgate swing vibes* to your campus. **University Swings** is a small business that hauls a trailer with a **pro-grade golf simulator** to universities for tailgates, fan zones, student org nights, and campus events. Students and alumni can take a few swings, run mini-contests, and win bragging rights before the game.

This repo contains a simple single-page site plus a **Flask** backend that can grow with you. The current UX is **tour-only** (no online bookings): visitors can view the schedule and **request a stop** on the tour.

---

## ✨ What’s in here

- **Front end (static):** HTML/CSS/JS  
  - Light, cheerful theme (greens/sky/amber), confetti hero, smooth scrolling  
  - Filterable **Schedule** with “Add to calendar (.ics)”  
  - **Request a tour stop** form (name, email, university, date window, notes)
- **Backend (Flask):**  
  - `GET /` renders the front end  
  - `GET /api/events` serves demo schedule data (replace with DB later)  
  - `POST /api/request-stop` accepts tour-stop submissions (currently echoes; wire to email/DB later)
- **Testing (TDD ready):** `pytest` + `pytest-flask` with basic route tests  
- **Run styles:** either as a pure static site or as a Flask package you can run via `python -m flaskapp`