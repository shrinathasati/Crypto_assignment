# # # main.py
# # import asyncio
# # import json
# # from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Request, HTTPException
# # from fastapi.responses import JSONResponse
# # from fastapi_limiter import FastAPILimiter
# # from fastapi_limiter.depends import RateLimiter
# # import redis.asyncio as aioredis
# # import uvicorn
# # from binance_listener import run_binance_listener, latest_prices

# # app = FastAPI(title="Crypto Price WebSocket Server")

# # # Shared state
# # connected_clients: set[WebSocket] = set()
# # MAX_CONNECTIONS = 50
# # broadcast_queue = asyncio.Queue()

# # # -------------------------------
# # # Background Tasks
# # # -------------------------------
# # async def price_broadcaster():
# #     last_sent = None
# #     while True:
# #         if latest_prices and latest_prices != last_sent:
# #             msg = json.dumps(latest_prices)
# #             await broadcast_queue.put(msg)
# #             last_sent = latest_prices.copy()
# #         await asyncio.sleep(0.1)

# # async def broadcast_to_clients():
# #     while True:
# #         message = await broadcast_queue.get()
# #         disconnected = set()
# #         for client in connected_clients:
# #             try:
# #                 await client.send_text(message)
# #             except:
# #                 disconnected.add(client)
# #         connected_clients.difference_update(disconnected)
# #         broadcast_queue.task_done()

# # # -------------------------------
# # # Startup
# # # -------------------------------
# # @app.on_event("startup")
# # async def startup():
# #     asyncio.create_task(run_binance_listener())
# #     asyncio.create_task(price_broadcaster())
# #     asyncio.create_task(broadcast_to_clients())

# #     # Try Redis, fallback gracefully
# #     try:
# #         redis = await aioredis.from_url("redis://redis:6379", decode_responses=True)
# #         await FastAPILimiter.init(redis)
# #         print("Rate limiter: Redis connected")
# #     except Exception as e:
# #         print(f"Rate limiter: Redis failed ({e}), disabled")

# # # -------------------------------
# # # REST API
# # # -------------------------------
# # # main.py
# # from fastapi_limiter.depends import RateLimiter
# # from fastapi import Depends  # Make sure this is imported
# # @app.get("/price", dependencies=[Depends(RateLimiter(times=10, seconds=60))])
# # async def get_latest_prices(request: Request):
# #     """Return latest crypto prices (rate-limited)."""
# #     if not latest_prices:
# #         raise HTTPException(status_code=404, detail="No price data yet.")
# #     return JSONResponse(content=latest_prices)
# # # @app.get("/price")
# # # async def get_price(request: Request):
# # #     # Rate limiting only if Redis is available
# # #     if FastAPILimiter.identifier:
# # #         rate_limiter = RateLimiter(times=10, seconds=60)
# # #         await rate_limiter(request)
# # #     if not latest_prices:
# # #         raise HTTPException(status_code=404, detail="No price data yet")
# # #     return latest_prices

# # # -------------------------------
# # # WebSocket
# # # -------------------------------
# # @app.websocket("/ws")
# # async def websocket_endpoint(websocket: WebSocket):
# #     if len(connected_clients) >= MAX_CONNECTIONS:
# #         await websocket.close(code=1008, reason="Too many connections")
# #         return

# #     await websocket.accept()
# #     connected_clients.add(websocket)
# #     print(f"WebSocket client connected: {len(connected_clients)}")

# #     try:
# #         while True:
# #             await asyncio.sleep(30)  # keep-alive
# #     except WebSocketDisconnect:
# #         pass
# #     finally:
# #         connected_clients.discard(websocket)
# #         print(f"WebSocket client disconnected: {len(connected_clients)}")

# # # -------------------------------
# # # Health Check
# # # -------------------------------
# # @app.get("/health")
# # async def health():
# #     return {"status": "healthy", "clients": len(connected_clients)}

# # # -------------------------------
# # # Run
# # # -------------------------------
# # if __name__ == "__main__":
# #     uvicorn.run("main:app", host="0.0.0.0", port=8000, log_level="info")


# # main.py
# import asyncio
# import json
# from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Request, HTTPException
# from fastapi.responses import HTMLResponse, JSONResponse
# from fastapi.templating import Jinja2Templates
# from fastapi.staticfiles import StaticFiles
# from fastapi_limiter import FastAPILimiter
# from fastapi_limiter.depends import RateLimiter
# from fastapi import Depends
# import redis.asyncio as aioredis
# import uvicorn
# from binance_listener import run_binance_listener, latest_prices

# app = FastAPI(title="Crypto Price Dashboard")

# # Templates & Static
# templates = Jinja2Templates(directory="templates")

# # Shared state
# connected_clients: set[WebSocket] = set()
# MAX_CONNECTIONS = 50
# broadcast_queue = asyncio.Queue()

# # -------------------------------
# # Background Tasks
# # -------------------------------
# async def price_broadcaster():
#     last_sent = None
#     while True:
#         if latest_prices and latest_prices != last_sent:
#             msg = json.dumps(latest_prices)
#             await broadcast_queue.put(msg)
#             last_sent = latest_prices.copy()
#         await asyncio.sleep(0.1)

# async def broadcast_to_clients():
#     while True:
#         message = await broadcast_queue.get()
#         disconnected = set()
#         for client in connected_clients:
#             try:
#                 await client.send_text(message)
#             except:
#                 disconnected.add(client)
#         connected_clients.difference_update(disconnected)
#         broadcast_queue.task_done()

# # -------------------------------
# # Startup
# # -------------------------------
# @app.on_event("startup")
# async def startup():
#     asyncio.create_task(run_binance_listener())
#     asyncio.create_task(price_broadcaster())
#     asyncio.create_task(broadcast_to_clients())

#     try:
#         redis = await aioredis.from_url("redis://redis:6379", decode_responses=True)
#         await FastAPILimiter.init(redis)
#         print("Rate limiter: Redis connected")
#     except Exception as e:
#         print(f"Rate limiter disabled: {e}")

# # -------------------------------
# # HTML Dashboard
# # -------------------------------
# @app.get("/", response_class=HTMLResponse)
# async def dashboard(request: Request):
#     return templates.TemplateResponse("index.html", {"request": request})

# # -------------------------------
# # REST API
# # -------------------------------
# @app.get("/price", dependencies=[Depends(RateLimiter(times=10, seconds=60))])
# async def get_latest_prices(request: Request):
#     """Return latest crypto prices (rate-limited)."""
#     if not latest_prices:
#         raise HTTPException(status_code=404, detail="No price data yet.")
#     return JSONResponse(content=latest_prices)

# # -------------------------------
# # WebSocket
# # -------------------------------
# @app.websocket("/ws")
# async def websocket_endpoint(websocket: WebSocket):
#     if len(connected_clients) >= MAX_CONNECTIONS:
#         await websocket.close(code=1008, reason="Too many connections")
#         return

#     await websocket.accept()
#     connected_clients.add(websocket)

#     try:
#         while True:
#             await asyncio.sleep(30)
#     except WebSocketDisconnect:
#         pass
#     finally:
#         connected_clients.discard(websocket)

# # -------------------------------
# # Health
# # -------------------------------
# @app.get("/health")
# async def health():
#     return {"status": "ok", "clients": len(connected_clients)}


# main.py
import asyncio
import json
from contextlib import asynccontextmanager
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Request, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi_limiter import FastAPILimiter
from fastapi_limiter.depends import RateLimiter
from fastapi import Depends
import redis.asyncio as aioredis
import uvicorn
from binance_listener import run_binance_listener, latest_prices

# -------------------------------
# Shared State
# -------------------------------
connected_clients: set[WebSocket] = set()
MAX_CONNECTIONS = 50
broadcast_queue = asyncio.Queue()

# -------------------------------
# Background Tasks
# -------------------------------
async def price_broadcaster():
    last_sent = None
    while True:
        if latest_prices and latest_prices != last_sent:
            msg = json.dumps(latest_prices)
            await broadcast_queue.put(msg)
            last_sent = latest_prices.copy()
        await asyncio.sleep(0.1)

async def broadcast_to_clients():
    while True:
        message = await broadcast_queue.get()
        disconnected = set()
        for client in connected_clients:
            try:
                await client.send_text(message)
            except:
                disconnected.add(client)
        connected_clients.difference_update(disconnected)
        broadcast_queue.task_done()

# -------------------------------
# Lifespan (Replaces @on_event)
# -------------------------------
# @asynccontextmanager
# async def lifespan(app: FastAPI):
#     # Startup
#     task1 = asyncio.create_task(run_binance_listener())
#     task2 = asyncio.create_task(price_broadcaster())
#     task3 = asyncio.create_task(broadcast_to_clients())

#     # Redis
#     try:
#         redis = await aioredis.from_url("redis://redis:6379" if "redis" in globals() else "redis://redis:6379", decode_responses=True)
#         await FastAPILimiter.init(redis)
#         print("Rate limiter: Redis connected")
#     except Exception as e:
#         print(f"Rate limiter disabled: {e}")

#     yield  # App runs here

#     # Shutdown
#     task1.cancel()
#     task2.cancel()
#     task3.cancel()
#     try:
#         await task1
#         await task2
#         await task3
#     except asyncio.CancelledError:
#         pass


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    task1 = asyncio.create_task(run_binance_listener())
    task2 = asyncio.create_task(price_broadcaster())
    task3 = asyncio.create_task(broadcast_to_clients())

    # Redis - Smart detection
    import os
    def get_redis_url():
        if os.getenv("DOCKER_ENV") or os.path.exists("/.dockerenv"):
            return "redis://redis:6379"
        return "redis://localhost:6379"

    try:
        redis_url = get_redis_url()
        redis = await aioredis.from_url(redis_url, decode_responses=True)
        await FastAPILimiter.init(redis)
        print(f"Rate limiter: Redis connected ({redis_url})")
    except Exception as e:
        print(f"Rate limiter disabled: {e}")

    yield

    # Shutdown
    for t in [task1, task2, task3]:
        t.cancel()
        try:
            await t
        except asyncio.CancelledError:
            pass
# -------------------------------
# FastAPI App
# -------------------------------
app = FastAPI(title="Crypto Price Dashboard", lifespan=lifespan)

# Templates & Static
templates = Jinja2Templates(directory="templates")

# -------------------------------
# Routes
# -------------------------------
@app.get("/", response_class=HTMLResponse)
async def dashboard(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

from fastapi.responses import JSONResponse
@app.get("/price", dependencies=[Depends(RateLimiter(times=20, seconds=60))])
async def get_latest_prices(request: Request):
    """Return latest crypto prices (rate-limited)."""
    if not latest_prices:
        raise HTTPException(status_code=404, detail="No price data yet.")
    return JSONResponse(content=latest_prices)



@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    if len(connected_clients) >= MAX_CONNECTIONS:
        await websocket.close(code=1008, reason="Too many connections")
        return
    await websocket.accept()
    connected_clients.add(websocket)
    try:
        while True:
            await asyncio.sleep(30)
    except WebSocketDisconnect:
        pass
    finally:
        connected_clients.discard(websocket)

@app.get("/health")
async def health():
    return {"status": "ok", "clients": len(connected_clients)}

# -------------------------------
# Run
# -------------------------------
if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, log_level="info")