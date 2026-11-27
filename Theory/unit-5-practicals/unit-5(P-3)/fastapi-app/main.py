"""FastAPI SMS API with latency profiling (Lecture 58, section 4).

Run:  uvicorn main:app --port 3200
Then: curl localhost:3200/api/ping ; curl localhost:3200/metrics

Bottleneck switches (environment variables, read per request):
  PING_DELAY_MS   awaits asyncio.sleep: a slow "database" that does NOT block the event loop
"""
import asyncio
import os
import time

from fastapi import FastAPI, Request

from metrics import Recorder

app = FastAPI(title="SMS API (profiling demo)")
recorder = Recorder()


@app.middleware("http")
async def timing_middleware(request: Request, call_next):
    if request.url.path in recorder.ignore_paths:
        return await call_next(request)
    start = time.perf_counter()
    status = 500
    try:
        response = await call_next(request)
        status = response.status_code
        return response
    finally:                                          # an unhandled exception is still timed and counted as an error
        recorder.record(request.url.path, (time.perf_counter() - start) * 1000, status)


@app.get("/api/ping")
async def ping():
    delay = float(os.environ.get("PING_DELAY_MS", "0"))
    if delay:
        await asyncio.sleep(delay / 1000)
    return {"ok": True}


@app.get("/api/attendance")
async def attendance():
    return [{"studentId": f"S{100 + i}", "classId": "class-5A", "present": i % 7 != 0, "at": 1730000000000 + i} for i in range(200)]


# The classic FastAPI mistake, side by side. Both "wait" 50 ms, but:
@app.get("/api/blocking-in-async")
async def blocking_in_async():
    time.sleep(0.05)              # BLOCKS the event loop: every other request waits
    return {"ok": True}


@app.get("/api/blocking-in-sync")
def blocking_in_sync():
    time.sleep(0.05)              # plain def: FastAPI runs it in a thread pool, the event loop stays free
    return {"ok": True}


@app.get("/api/error")
async def error():
    raise RuntimeError("deliberate")                  # unhandled -> 500, counted in the error rate


@app.get("/metrics")
async def metrics(path: str | None = None):
    return recorder.snapshot(path)


@app.post("/metrics/reset")
async def reset():
    recorder.reset()
    return {"reset": True}
