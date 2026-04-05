# Kalshi Sports Odds Dashboard

Live sports odds dashboard that pulls data from the [Kalshi Elections API](https://api.elections.kalshi.com/trade-api/v2). View orderbooks, liquidity, and odds in both cents and American format across all major sports markets.

## Features

- **Multi-sport support**: MLB (HR, moneyline, spread, hits, strikeouts, RBIs, total bases), NBA, NHL, Soccer (EPL, La Liga, Serie A, Bundesliga, UCL, UEL, MLS), UFC/MMA, Tennis, Golf
- **Live orderbook**: Full depth-of-book with price, American odds, shares, and dollar amounts per level
- **Dual odds display**: Cents and American odds shown side-by-side everywhere (e.g., `YES 19¢` with `+426/-488` color-coded)
- **Auto-refresh**: Orderbook refreshes every 3 seconds when viewing a market; pauses automatically when tab is hidden
- **Liquidity color coding**: Markets color-coded red → yellow → green by 24h dollar volume relative to other markets in the same event
- **Minimum volume filter**: Adjustable min dollar volume threshold (default $100) to hide dead markets
- **Alphabetized markets**: Player markets sorted A-Z within each event for easy scanning
- **Dollar-first display**: All volumes, open interest, and liquidity shown in dollars with contract counts alongside
- **Book liquidity**: Total dollars sitting on the orderbook computed live (replaces unreliable Kalshi `liquidity_dollars` field)
- **Event times**: Game times parsed from tickers and displayed in ET

## Quick Start

```bash
pip install -r requirements.txt
python -m uvicorn server:app --host 0.0.0.0 --port 8050
```

Open `http://localhost:8050` in your browser.

## Project Structure

```
├── server.py         # FastAPI backend — proxies Kalshi API, serves frontend
├── index.html        # Single-page dashboard — no build step, no JS dependencies
├── requirements.txt  # Python deps: fastapi, uvicorn, httpx
└── README.md
```

## Architecture

### Backend (`server.py`)

FastAPI app that proxies the public Kalshi API (no auth required for read-only data). This avoids CORS issues and keeps the frontend simple.

**Endpoints:**
| Route | Description |
|-------|-------------|
| `GET /` | Serves `index.html` |
| `GET /api/sports` | Curated sports series grouped by sport (hardcoded in `SPORTS_SERIES` dict) |
| `GET /api/events?series_ticker=KXMLBHR` | Open events for a series |
| `GET /api/markets?event_ticker=...` | Player markets for an event |
| `GET /api/markets/{ticker}` | Single market detail |
| `GET /api/markets/{ticker}/orderbook` | Full L2 orderbook |

**Adding new sports/series:** Add entries to the `SPORTS_SERIES` dict in `server.py`. The key is the Kalshi series ticker, the value is the display name. Group under a sport key.

### Frontend (`index.html`)

Single self-contained HTML file with inline CSS and JS. No framework, no build step.

**Key flows:**
1. On load, fetches `/api/sports` to populate the sport/series dropdown
2. Selecting a series fetches `/api/events` to populate the game dropdown
3. Selecting a game fetches `/api/markets` to populate the market list (filtered by min vol, sorted A-Z, color-coded by volume)
4. Clicking a market fetches `/api/markets/{ticker}` + `/api/markets/{ticker}/orderbook` and starts a 3-second auto-refresh interval
5. Switching tabs pauses polling via `visibilitychange` event; returning resumes it

**Odds conversion logic:**
- Kalshi prices are in dollar units (0.00–1.00), where the price equals the implied probability
- Cents: `price × 100` (e.g., 0.19 → 19¢)
- American: `price >= 0.50` → `-(price/(1-price)×100)`, else `+((1-price)/price×100)`
- Dollar volume: `contracts × last_price`

## Kalshi API Notes

- **No authentication needed** for all read endpoints
- **Ticker format**: `KXMLBHR-26APR042138SEALAA` = series / year+month+day+time(ET) + teams
- **Prices**: In dollar units (e.g., `0.19` = 19¢ = +426 American)
- **Orderbook**: `[price, size]` pairs on `yes_dollars` and `no_dollars` sides; yes + no prices sum to ~$1.00
- **Market fields used**: `yes_ask_dollars`, `yes_ask_size_fp`, `yes_bid_size_fp`, `no_ask_dollars`, `last_price_dollars`, `volume_24h_fp`, `open_interest_fp`
- **No `no_ask_size`** in the market object — buying NO at X¢ is equivalent to selling YES at (100-X)¢, so `yes_bid_size_fp` serves as the no-side liquidity
- **`liquidity_dollars`** from the API is often 0 even for active markets — we compute book liquidity from the orderbook instead
- **Pagination**: Cursor-based via `cursor` query param
- **Rate limits**: No documented rate limits for public read endpoints, but the 3-second refresh interval is conservative

## Sports Series Reference

| Sport | Tickers |
|-------|---------|
| MLB | KXMLBHR, KXMLBGAME, KXMLBSPREAD, KXMLBTB, KXMLBHIT, KXMLBKS, KXMLBRBI |
| NBA | KXNBAGAME, KXNBASPREAD, KXNBAOU, KXNBAPTS, KXNBAREB, KXNBAAST, KXNBA3PT |
| NHL | KXNHLGAME, KXNHLSPREAD, KXNHLOU, KXNHLGOAL, KXNHLPTS |
| Soccer | KXEPLGAME, KXLALIGAGAME, KXSERIAGAME, KXBUNDESLIGAGAME, KXUCLGAME, KXUELGAME, KXMLSGAME |
| UFC/MMA | KXUFCFIGHT, KXUFCMETHOD |
| Tennis | KXATPMATCH, KXWTAMATCH |
| Golf | KXPGAWINNER, KXPGATOP5 |

## Future Ideas

- Historical odds tracking / charting
- Alerts on odds movements
- Portfolio tracking
- Additional series auto-discovery
- WebSocket connection for real-time updates (if Kalshi exposes one)
