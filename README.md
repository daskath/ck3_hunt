# Steam Achievement Kanban

A local Kanban board for tracking your Steam achievements — **Backlog / To Do / Done** — backed by SQLite so your progress survives restarts.

## Stack

| Layer     | Tech                      |
|-----------|---------------------------|
| Frontend  | Svelte + Vite             |
| Backend   | Python · FastAPI          |
| Database  | SQLite (local file)       |
| Data      | Steam Web API             |

---

## Setup

### 1. Get your credentials

| Value          | Where to find it |
|----------------|-----------------|
| `STEAM_API_KEY` | https://steamcommunity.com/dev/apikey |
| `STEAM_ID`      | Your 64-bit Steam ID (e.g. from https://steamid.io) |
| `APP_ID`        | The Steam App ID of the game (visible in the store URL) |

### 2. Configure environment

Copy `.env.example` to `.env` and fill in your values:

```bash
cp .env.example .env
# then edit .env
```

```
STEAM_API_KEY=XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
STEAM_ID=76561198XXXXXXXXX
APP_ID=730
```

---

## Running

### Backend (FastAPI)

```bash
cd backend
pip install -r requirements.txt
python main.py
# → http://localhost:8000
```

### Frontend (Svelte)

```bash
cd frontend
npm install
npm run dev
# → http://localhost:5173
```

Open **http://localhost:5173** in your browser.

---

## How it works

- On first load, achievements are fetched from Steam and seeded into SQLite:
  - **Unlocked** → `Done`
  - **Locked** → `Backlog`
- If Steam shows a newly unlocked achievement that was in Backlog/To Do, it auto-promotes to **Done**.
- All manual moves are persisted in SQLite immediately — they survive restarts.
- Click **↻ Refresh** to re-sync with Steam at any time.

---

## Project structure

```
.
├── .env.example          ← config template
├── backend/
│   ├── main.py           ← FastAPI app + Steam integration
│   ├── requirements.txt
│   └── achievements.db   ← created automatically on first run
└── frontend/
    ├── src/
    │   ├── App.svelte           ← root component + board layout
    │   └── lib/
    │       ├── api.js           ← fetch helpers
    │       ├── KanbanColumn.svelte
    │       └── AchievementCard.svelte
    └── package.json
```
