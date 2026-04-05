# Kalshi Sports Odds Dashboard

Live sports odds dashboard that pulls data from the [Kalshi Elections API](https://api.elections.kalshi.com/trade-api/v2). View orderbooks, liquidity, and odds in both cents and American format across all major sports markets.

## Features

- **Multi-sport support**: MLB (HR, moneyline, spread, hits, strikeouts, RBIs, total bases), NBA, NHL, Soccer (EPL, La Liga, Serie A, Bundesliga, UCL, UEL, MLS), UFC/MMA, Tennis, Golf
- **Live orderbook**: Full depth-of-book with price, American odds, shares, and dollar amounts per level
- **Dual odds display**: Cents and American odds shown side-by-side everywhere
- **Auto-refresh**: Orderbook refreshes every 3 seconds when viewing a market; pauses when tab is hidden
- **Liquidity view**: Dollar amounts available at each price level, plus top-of-book liquidity in market list

## Quick Start

```bash
pip install -r requirements.txt
python -m uvicorn server:app --host 0.0.0.0 --port 8050
```

Open `http://localhost:8050` in your browser.

## How It Works

- **Backend** (`server.py`): FastAPI app that proxies the Kalshi API (no auth required for read-only market data). Endpoints:
  - `GET /api/sports` — curated sports series grouped by sport
  - `GET /api/events?series_ticker=KXMLBHR` — games/events for a series
  - `GET /api/markets?event_ticker=...` — player markets for an event
  - `GET /api/markets/{ticker}` — single market detail
  - `GET /api/markets/{ticker}/orderbook` — full L2 orderbook

- **Frontend** (`index.html`): Single-page app served by FastAPI. No build step, no dependencies.

## Kalshi API Notes

- **No authentication needed** for all read endpoints
- **Ticker format**: `KXMLBHR-26APR042138SEALAA` = series / date+time(ET)+teams
- **Prices**: In dollar units (e.g., `0.19` = 19¢ = +426 American)
- **Orderbook**: `[price, size]` pairs; yes + no prices sum to ~$1.00
- **Pagination**: Cursor-based via `cursor` query param

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
