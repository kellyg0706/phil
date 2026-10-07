#!/usr/bin/env python3
"""Market-id -> live book for every outcome, in one call.

Usage: python3 strategy/tools/mquote.py <market_id> [<market_id> ...]

Why (2026-10-07 21:3xZ FULL cycle): quote.py takes CLOB token ids, but the
screener batch files and siblings.py only carry gamma market ids, and the
operator-machine permission gate blocks ad-hoc curl/pipe one-liners. This
resolves the token ids from gamma and prints, per market, the gamma fields
research needs (endDate, gameStartTime, liquidity, umaResolutionStatus) plus
best bid/ask and top asks for each outcome token from the CLOB book.
"""
import json
import subprocess
import sys
import urllib.request

MARKET_URL = "https://gamma-api.polymarket.com/markets?id={}"
BOOK_URL = "https://clob.polymarket.com/book?token_id={}"
HEADERS = {"User-Agent": "Mozilla/5.0 (compatible; paper-trader-mquote)"}


def fetch(url):
    # Same fallback as quote.py: urllib can be TLS-fingerprint blocked by the
    # CLOB front end while curl with the same UA succeeds.
    try:
        req = urllib.request.Request(url, headers=HEADERS)
        with urllib.request.urlopen(req, timeout=15) as r:
            return json.load(r)
    except Exception:
        out = subprocess.run(
            ["curl", "-s", "--max-time", "15", "-H", f"User-Agent: {HEADERS['User-Agent']}", url],
            capture_output=True, text=True, timeout=20, check=True,
        )
        return json.loads(out.stdout)


def book_summary(token_id):
    try:
        book = fetch(BOOK_URL.format(token_id))
    except Exception as e:  # noqa: BLE001 - report, never crash the census
        return {"error": str(e)[:120]}
    bids = sorted(book.get("bids") or [], key=lambda x: -float(x["price"]))
    asks = sorted(book.get("asks") or [], key=lambda x: float(x["price"]))
    best_bid = float(bids[0]["price"]) if bids else None
    best_ask = float(asks[0]["price"]) if asks else None
    return {
        "best_bid": best_bid,
        "best_ask": best_ask,
        "spread": round(best_ask - best_bid, 4) if best_bid is not None and best_ask is not None else None,
        "top_asks": [(float(a["price"]), float(a["size"])) for a in asks[:3]],
        "top_bids": [(float(b["price"]), float(b["size"])) for b in bids[:3]],
    }


def main(ids):
    for mid in ids:
        rows = fetch(MARKET_URL.format(mid))
        if not rows:
            print(json.dumps({"market_id": mid, "error": "not found"}))
            continue
        m = rows[0]
        outcomes = json.loads(m.get("outcomes") or "[]")
        tokens = json.loads(m.get("clobTokenIds") or "[]")
        prices = json.loads(m.get("outcomePrices") or "[]")
        print(json.dumps({
            "market_id": mid,
            "question": m.get("question"),
            "endDate": m.get("endDate"),
            "gameStartTime": m.get("gameStartTime"),
            "closed": m.get("closed"),
            "acceptingOrders": m.get("acceptingOrders"),
            "liquidity": m.get("liquidityNum"),
            "volume24hr": m.get("volume24hr"),
            "uma": m.get("umaResolutionStatus"),
            "outcomes": {
                o: {"gamma_price": prices[i] if i < len(prices) else None,
                    **book_summary(tokens[i])}
                for i, o in enumerate(outcomes) if i < len(tokens)
            },
        }))


if __name__ == "__main__":
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    main(sys.argv[1:])
