# OptionLab India — Prototype (Windows instructions)

Overview
- FastAPI backend with payoff engine (backend/)
- React + Vite frontend skeleton (frontend/)
- Tests for payoff engine (pytest)

Windows setup (PowerShell)
1) Python (3.10/3.11) + Node.js (LTS) installed.

Backend
2) Open PowerShell in the project root and create a venv:
   python -m venv .venv
   .\.venv\Scripts\Activate.ps1

3) Install backend deps:
   pip install -r backend/requirements.txt

4) Run tests:
   cd backend
   pytest -q

5) Start backend:
   uvicorn app.main:app --reload --port 8000

Frontend
6) In a new terminal (Windows PowerShell), install frontend deps:
   cd frontend
   npm install

7) Start dev server:
   npm run dev

Notes
- Demo market data is clearly labeled "DEMO DATA — PAPER MODE".
- The analyze endpoint performs expiry payoff calculations only (no live pricing).
- No database — saved strategies should be implemented client-side (localStorage).
- See backend/tests/test_payoff.py for required automated checks including the sample strategy values.
