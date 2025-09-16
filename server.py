import asyncio
import logging
import time
from datetime import datetime

from fastapi import FastAPI, Request, WebSocket
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(message)s")

app = FastAPI()
templates = Jinja2Templates(directory="templates")

async def handle_connection_logging(websocket: WebSocket, endpoint: str):
    """Logs connection start and disconnection."""
    start_time = datetime.now()
    logging.info(f"🟢 Connection established at /{endpoint} from {websocket.client.host}:{websocket.client.port} at {start_time}")
    try:
        # Keep the connection alive
        await websocket.receive_text()
    except Exception as e:
        end_time = datetime.now()
        duration = end_time - start_time
        logging.info(f"🔴 Connection at /{endpoint} from {websocket.client.host}:{websocket.client.port} disconnected. Duration: {duration.total_seconds():.2f} seconds.")

@app.websocket("/idle")
async def websocket_endpoint_idle(websocket: WebSocket):
    """Stays connected indefinitely without sending data."""
    await websocket.accept()
    await handle_connection_logging(websocket, "idle")

@app.websocket("/active")
async def websocket_endpoint_active(websocket: WebSocket):
    """Sends a message every minute."""
    await websocket.accept()
    
    # Log connection start
    start_time = datetime.now()
    logging.info(f"🟢 Connection established at /active from {websocket.client.host}:{websocket.client.port} at {start_time}")

    try:
        while True:
            current_time = datetime.now().isoformat()
            await websocket.send_text(f"Active data: {current_time}")
            await asyncio.sleep(60)
    except Exception as e:
        end_time = datetime.now()
        duration = end_time - start_time
        logging.info(f"🔴 Connection at /active from {websocket.client.host}:{websocket.client.port} disconnected. Duration: {duration.total_seconds():.2f} seconds.")

@app.get("/", response_class=HTMLResponse)
async def get_client(request: Request):
    """Serves the HTML client."""
    return templates.TemplateResponse("client.html", {"request": request})

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=10000)