# test_client.py
import asyncio
import websockets
import json

async def test():
    uri = "ws://localhost:8000/ws"
    async with websockets.connect(uri) as ws:
        print("Connected to WebSocket server!")
        async for message in ws:
            data = json.loads(message)
            for sym, info in data.items():
                print(f"{info['symbol']}: ${info['price']} | {info['change']}%")

asyncio.run(test())