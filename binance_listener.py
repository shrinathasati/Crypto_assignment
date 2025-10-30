# binance_listener.py
import asyncio
import json
import websockets
from datetime import datetime

SYMBOLS = ["btcusdt", "ethusdt", "bnbusdt"]
latest_prices = {}

def build_url(symbols):
    streams = "/".join(f"{s}@ticker" for s in symbols)
    return f"wss://stream.binance.com:9443/stream?streams={streams}"

BINANCE_URL = build_url(SYMBOLS)

async def handle_message(payload):
    data = payload.get("data", payload)
    symbol = data.get("s")
    if not symbol:
        return
    symbol = symbol.upper()
    latest_prices[symbol] = {
        "symbol": symbol,
        "price": data.get("c"),
        "change": data.get("P"),
        "timestamp": datetime.utcnow().isoformat() + "Z"
    }

async def run_binance_listener():
    backoff = 1
    while True:
        try:
            async with websockets.connect(
                BINANCE_URL,
                ping_interval=20,
                ping_timeout=20,
                max_size=None
            ) as ws:
                print("Connected to Binance WebSocket")
                backoff = 1
                async for msg in ws:
                    try:
                        payload = json.loads(msg)
                        await handle_message(payload)
                    except:
                        continue
        except Exception as e:
            print(f"Binance error: {e}, reconnecting in {backoff}s...")
            await asyncio.sleep(backoff)
            backoff = min(backoff * 2, 60)