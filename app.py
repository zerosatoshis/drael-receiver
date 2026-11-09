from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import time
import os

app = FastAPI()

# Capturas em memória
captures = {}

@app.post("/capture")
async def capture(request: Request):
    try:
        data = await request.json()
    except:
        data = {"raw": await request.body().decode()}
    
    capture_id = int(time.time() * 1000)
    captures[capture_id] = {
        "data": data,
        "ip": request.client.host if request.client else "unknown",
        "ts": time.time(),
        "ua": request.headers.get("user-agent", "")
    }
    
    # Auto-delete em 120s
    def delete():
        captures.pop(capture_id, None)
    import threading
    threading.Timer(120, delete).start()
    
    return {"status": "ok", "id": capture_id}

@app.get("/check")
async def check():
    return {
        "status": "alive",
        "captures_active": len(captures),
        "time": time.time()
    }

@app.get("/")
async def root():
    return FileResponse("static/index.html")

# Servir arquivos estáticos
app.mount("/static", StaticFiles(directory="static"), name="static")
