from fastapi import FastAPI, Query
from fastapi.responses import HTMLResponse
import httpx

app = FastAPI()

KALSHI_BASE = "https://api.elections.kalshi.com/trade-api/v2"
HEADERS = {"Accept": "application/json"}

# Sports series we care about — grouped by sport
SPORTS_SERIES = {
    "MLB": {
        "KXMLBHR": "Home Runs",
        "KXMLBGAME": "Game (Moneyline)",
        "KXMLBSPREAD": "Spread",
        "KXMLBTB": "Total Bases",
        "KXMLBHIT": "Hits",
        "KXMLBKS": "Strikeouts",
        "KXMLBRBI": "RBIs",
    },
    "NBA": {
        "KXNBAGAME": "Game (Moneyline)",
        "KXNBASPREAD": "Spread",
        "KXNBAOU": "Over/Under",
        "KXNBAPTS": "Player Points",
        "KXNBAREB": "Player Rebounds",
        "KXNBAAST": "Player Assists",
        "KXNBA3PT": "Player 3-Pointers",
    },
    "NHL": {
        "KXNHLGAME": "Game (Moneyline)",
        "KXNHLSPREAD": "Spread",
        "KXNHLOU": "Over/Under",
        "KXNHLGOAL": "Player Goals",
        "KXNHLPTS": "Player Points",
    },
    "Soccer": {
        "KXEPLGAME": "EPL Game",
        "KXLALIGAGAME": "La Liga Game",
        "KXSERIAGAME": "Serie A Game",
        "KXBUNDESLIGAGAME": "Bundesliga Game",
        "KXUCLGAME": "Champions League Game",
        "KXUELGAME": "Europa League Game",
        "KXMLSGAME": "MLS Game",
    },
    "UFC/MMA": {
        "KXUFCFIGHT": "Fight Winner",
        "KXUFCMETHOD": "Method of Victory",
    },
    "Tennis": {
        "KXATPMATCH": "ATP Match",
        "KXWTAMATCH": "WTA Match",
    },
    "Golf": {
        "KXPGAWINNER": "PGA Winner",
        "KXPGATOP5": "PGA Top 5",
    },
}


async def kalshi_get(path: str, params: dict = None):
    async with httpx.AsyncClient(timeout=15) as client:
        resp = await client.get(f"{KALSHI_BASE}{path}", params=params, headers=HEADERS)
        resp.raise_for_status()
        return resp.json()


@app.get("/api/sports")
async def list_sports():
    """Return the curated sports series grouped by sport."""
    return {"sports": SPORTS_SERIES}


@app.get("/api/events")
async def list_events(
    series_ticker: str = Query(...),
    limit: int = Query(50),
    cursor: str = Query(None),
    status: str = Query("open"),
):
    params = {"series_ticker": series_ticker, "limit": limit, "status": status}
    if cursor:
        params["cursor"] = cursor
    data = await kalshi_get("/events", params)
    return data


@app.get("/api/markets")
async def list_markets(
    event_ticker: str = Query(None),
    series_ticker: str = Query(None),
    limit: int = Query(100),
    cursor: str = Query(None),
):
    params = {"limit": limit}
    if event_ticker:
        params["event_ticker"] = event_ticker
    if series_ticker:
        params["series_ticker"] = series_ticker
    if cursor:
        params["cursor"] = cursor
    data = await kalshi_get("/markets", params)
    return data


@app.get("/api/markets/{ticker}")
async def get_market(ticker: str):
    data = await kalshi_get(f"/markets/{ticker}")
    return data


@app.get("/api/markets/{ticker}/orderbook")
async def get_orderbook(ticker: str):
    data = await kalshi_get(f"/markets/{ticker}/orderbook")
    return data


@app.get("/", response_class=HTMLResponse)
async def index():
    with open("index.html") as f:
        return f.read()
