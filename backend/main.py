import asyncio
import os
import sqlite3
import httpx
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv

load_dotenv()

STEAM_API_KEY = os.getenv("STEAM_API_KEY", "")
STEAM_ID = os.getenv("STEAM_ID", "")
APP_ID = os.getenv("APP_ID", "")
DB_PATH = os.path.join(os.path.dirname(__file__), "achievements.db")

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)


# ---------------------------------------------------------------------------
# Database
# ---------------------------------------------------------------------------

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    with get_db() as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS achievement_states (
                api_name TEXT PRIMARY KEY,
                state    TEXT NOT NULL DEFAULT 'backlog'
            )
            """
        )
        conn.commit()


init_db()


# ---------------------------------------------------------------------------
# Steam helpers
# ---------------------------------------------------------------------------

async def fetch_schema(client: httpx.AsyncClient) -> dict:
    """Fetch the full achievement schema (icons)."""
    url = "https://api.steampowered.com/ISteamUserStats/GetSchemaForGame/v2/"
    resp = await client.get(url, params={"key": STEAM_API_KEY, "appid": APP_ID})
    resp.raise_for_status()
    data = resp.json()
    achievements = (
        data.get("game", {})
        .get("availableGameStats", {})
        .get("achievements", [])
    )
    return {a["name"]: a for a in achievements}


async def fetch_player_achievements(client: httpx.AsyncClient) -> dict:
    """Fetch achievements including display name and description via l=english."""
    url = "https://api.steampowered.com/ISteamUserStats/GetPlayerAchievements/v1/"
    resp = await client.get(
        url,
        params={
            "key": STEAM_API_KEY,
            "steamid": STEAM_ID,
            "appid": APP_ID,
            "l": "english",
        },
    )
    resp.raise_for_status()
    data = resp.json()
    player_stats = data.get("playerstats", {})
    if not player_stats.get("success"):
        raise HTTPException(status_code=400, detail="Steam API returned success=false. Check your STEAM_ID and APP_ID.")
    achievements = player_stats.get("achievements", [])
    return {a["apiname"]: a for a in achievements}


# ---------------------------------------------------------------------------
# Models
# ---------------------------------------------------------------------------

class StateUpdate(BaseModel):
    state: str  # "backlog" | "todo" | "done"


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------

@app.get("/achievements")
async def get_achievements():
    """
    Merge Steam player achievements + persisted kanban state.
    New achievements are seeded: unlocked → done, locked → backlog.
    """
    async with httpx.AsyncClient() as client:
        schema, player = await asyncio.gather(
            fetch_schema(client),
            fetch_player_achievements(client),
        )

    with get_db() as conn:
        rows = conn.execute("SELECT api_name, state FROM achievement_states").fetchall()
        persisted = {r["api_name"]: r["state"] for r in rows}

        # Seed any achievements not yet in DB
        to_insert = []
        for api_name, pdata in player.items():
            if api_name not in persisted:
                default_state = "done" if pdata.get("achieved") == 1 else "backlog"
                to_insert.append((api_name, default_state))
                persisted[api_name] = default_state

        # Also handle newly unlocked achievements that were previously in backlog/todo
        for api_name, pdata in player.items():
            if pdata.get("achieved") == 1 and persisted.get(api_name) in ("backlog", "todo"):
                # Auto-promote to done on fresh unlock
                persisted[api_name] = "done"
                conn.execute(
                    "INSERT OR REPLACE INTO achievement_states (api_name, state) VALUES (?, ?)",
                    (api_name, "done"),
                )

        if to_insert:
            conn.executemany(
                "INSERT OR IGNORE INTO achievement_states (api_name, state) VALUES (?, ?)",
                to_insert,
            )
        conn.commit()

    result = []
    for api_name, pdata in player.items():
        s = schema.get(api_name, {})
        result.append(
            {
                "api_name": api_name,
                "display_name": pdata.get("name", api_name),
                "description": pdata.get("description", ""),
                "icon": s.get("icon", ""),
                "icon_gray": s.get("icongray", ""),
                "achieved": pdata.get("achieved") == 1,
                "state": persisted.get(api_name, "backlog"),
            }
        )

    # Sort: done last, then alphabetically
    state_order = {"backlog": 0, "todo": 1, "done": 2}
    result.sort(key=lambda x: (state_order.get(x["state"], 0), x["display_name"].lower()))
    return result


@app.put("/achievements/{api_name}/state")
async def update_state(api_name: str, body: StateUpdate):
    if body.state not in ("backlog", "todo", "done"):
        raise HTTPException(status_code=400, detail="Invalid state. Must be backlog, todo, or done.")
    with get_db() as conn:
        conn.execute(
            "INSERT OR REPLACE INTO achievement_states (api_name, state) VALUES (?, ?)",
            (api_name, body.state),
        )
        conn.commit()
    return {"api_name": api_name, "state": body.state}


# ---------------------------------------------------------------------------
# Entrypoint
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
