import sys
import os
import json
import asyncio
from datetime import datetime
from typing import List, Dict, Any, Optional

# Add parent directory to path to import xq modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi import FastAPI, HTTPException, Request, Form, Depends, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import redis
import uvicorn

from xq.queue import Queue
from xq.message import Message

# Initialize FastAPI app
app = FastAPI(title="XQ Queue Manager")

# WebSocket connection manager
class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, List[WebSocket]] = {}

    async def connect(self, websocket: WebSocket, queue_name: str):
        await websocket.accept()
        if queue_name not in self.active_connections:
            self.active_connections[queue_name] = []
        self.active_connections[queue_name].append(websocket)

    def disconnect(self, websocket: WebSocket, queue_name: str):
        if queue_name in self.active_connections:
            if websocket in self.active_connections[queue_name]:
                self.active_connections[queue_name].remove(websocket)

    async def broadcast_to_queue(self, queue_name: str, message: dict):
        if queue_name in self.active_connections:
            for connection in self.active_connections[queue_name]:
                await connection.send_json(message)

manager = ConnectionManager()

# Setup Redis connection
redis_client = redis.Redis(host="localhost", port=6379, db=0, decode_responses=False)

# Function to check Redis availability
def check_redis_available():
    try:
        return redis_client.ping()
    except:
        return False

# Setup templates
templates = Jinja2Templates(directory="server/templates")

# Create static files directory if it doesn't exist
os.makedirs("server/static", exist_ok=True)

# Mount static files
app.mount("/static", StaticFiles(directory="server/static"), name="static")

# Helper function to get all queue names
def get_queue_names():
    if not check_redis_available():
        return []
    try:
        keys = redis_client.keys("xq_prefix_*")
        return [key.decode('utf-8').replace("xq_prefix_", "") for key in keys]
    except:
        return []

# API Routes
@app.get("/api/health")
async def health_check():
    """Health check endpoint to verify Redis availability"""
    redis_available = check_redis_available()
    if not redis_available:
        return {"status": "error", "redis_available": False}
    return {"status": "ok", "redis_available": True}

@app.get("/api/queues", response_model=List[str])
async def list_queues():
    """List all available queues"""
    if not check_redis_available():
        return []
    return get_queue_names()

@app.get("/api/queues/{queue_name}/messages")
async def list_messages(queue_name: str):
    """List all messages in a specific queue"""
    if not check_redis_available():
        return []
        
    queue = Queue(redis_client, queue_name)
    queue_key = f"xq_prefix_{queue_name}"
    
    # Get all messages from the queue
    messages_data = redis_client.zrange(queue_key, 0, -1, withscores=True)
    
    messages = []
    for msg_str, timestamp in messages_data:
        try:
            msg = Message.from_json(msg_str)
            messages.append({
                "id": msg.id,
                "body": msg.body if isinstance(msg.body, str) else str(msg.body),
                "timestamp": msg.timestamp,
                "scheduled_time": datetime.fromtimestamp(msg.timestamp).strftime("%Y-%m-%d %H:%M:%S"),
                "cron_expression": msg.cron_expression
            })
        except Exception as e:
            messages.append({
                "error": f"Failed to parse message: {str(e)}",
                "raw": str(msg_str)
            })
    
    return messages

from fastapi import Form, Body

@app.post("/api/queues/{queue_name}/messages")
async def add_message(
    queue_name: str, 
    body: str = Form(None),
    cron_expression: Optional[str] = Form(None),
    request: Request = None
):
    """Add a new message to the queue"""
    if not check_redis_available():
        raise HTTPException(status_code=503, detail="Redis server is not available")
        
    # If form data is not provided, try to get from request body
    if body is None and request:
        try:
            json_body = await request.json()
            body = json_body.get("body", "")
            if cron_expression is None:
                cron_expression = json_body.get("cron_expression")
        except:
            # If JSON parsing fails, try to get form data
            form_data = await request.form()
            body = form_data.get("body", "")
            if cron_expression is None:
                cron_expression = form_data.get("cron_expression")
    
    if not body:
        raise HTTPException(status_code=400, detail="Message body is required")
        
    queue = Queue(redis_client, queue_name)
    queue.enqueue(body, cron_expression)
    
    # Notify WebSocket clients about the new message
    message_data = {
        "action": "new_message",
        "body": body,
        "cron_expression": cron_expression,
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    await manager.broadcast_to_queue(queue_name, message_data)
    
    # If this is a new queue, notify the home page
    queue_names = get_queue_names()
    if len(queue_names) == 1 and queue_names[0] == queue_name:
        await manager.broadcast_to_queue("home", {
            "action": "new_queue",
            "queue_name": queue_name
        })
    
    return {"status": "success", "message": "Message added to queue"}

@app.delete("/api/queues/{queue_name}/messages/{message_id}")
async def delete_message(queue_name: str, message_id: str):
    """Delete a message from the queue"""
    if not check_redis_available():
        raise HTTPException(status_code=503, detail="Redis server is not available")
        
    queue_key = f"xq_prefix_{queue_name}"
    
    # Get all messages from the queue
    messages_data = redis_client.zrange(queue_key, 0, -1, withscores=True)
    
    for msg_str, timestamp in messages_data:
        try:
            msg = Message.from_json(msg_str)
            if msg.id == message_id:
                redis_client.zrem(queue_key, msg_str)
                
                # Notify WebSocket clients about the deleted message
                await manager.broadcast_to_queue(queue_name, {
                    "action": "delete_message",
                    "message_id": message_id
                })
                
                return {"status": "success", "message": "Message deleted"}
        except Exception:
            pass
    
    raise HTTPException(status_code=404, detail="Message not found")

@app.post("/api/queues/{queue_name}/poll")
async def poll_queue(queue_name: str):
    """Poll messages from the queue"""
    if not check_redis_available():
        raise HTTPException(status_code=503, detail="Redis server is not available")
        
    queue = Queue(redis_client, queue_name)
    messages = queue.poll()
    
    result = []
    for msg in messages:
        result.append({
            "id": msg.id,
            "body": msg.body if isinstance(msg.body, str) else str(msg.body),
            "timestamp": msg.timestamp,
            "cron_expression": msg.cron_expression
        })
    
    # Notify WebSocket clients about the poll action
    if messages:
        await manager.broadcast_to_queue(queue_name, {
            "action": "poll_messages",
            "count": len(messages)
        })
    
    return result

# Web UI Routes
@app.get("/", response_class=HTMLResponse)
async def home_page(request: Request):
    """Render the home page"""
    redis_available = check_redis_available()
    queues = get_queue_names() if redis_available else []
    return templates.TemplateResponse("index.html", {
        "request": request, 
        "queues": queues,
        "redis_available": redis_available
    })

@app.get("/queues/{queue_name}", response_class=HTMLResponse)
async def queue_page(request: Request, queue_name: str):
    """Render the queue detail page"""
    redis_available = check_redis_available()
    return templates.TemplateResponse("queue.html", {
        "request": request, 
        "queue_name": queue_name,
        "redis_available": redis_available
    })

@app.post("/queues/{queue_name}/add")
async def add_message_form(
    request: Request, 
    queue_name: str, 
    body: str = Form(...), 
    cron_expression: Optional[str] = Form(None)
):
    """Handle form submission to add a message"""
    redis_available = check_redis_available()
    if not redis_available:
        return templates.TemplateResponse("queue.html", {
            "request": request, 
            "queue_name": queue_name,
            "redis_available": redis_available,
            "error_message": "Cannot add message: Redis server is not available"
        })
        
    queue = Queue(redis_client, queue_name)
    queue.enqueue(body, cron_expression)
    
    # Notify WebSocket clients about the new message
    message_data = {
        "action": "new_message",
        "body": body,
        "cron_expression": cron_expression,
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    await manager.broadcast_to_queue(queue_name, message_data)
    
    return RedirectResponse(url=f"/queues/{queue_name}", status_code=303)

@app.websocket("/ws/queues/{queue_name}")
async def websocket_endpoint(websocket: WebSocket, queue_name: str):
    """WebSocket endpoint for real-time queue updates"""
    await manager.connect(websocket, queue_name)
    try:
        while True:
            # Wait for any message from the client (like ping)
            data = await websocket.receive_text()
            # Echo back to confirm connection is alive
            await websocket.send_text(json.dumps({"status": "ok", "message": "ping received"}))
    except WebSocketDisconnect:
        manager.disconnect(websocket, queue_name)

@app.websocket("/ws/queues/home")
async def home_websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for home page updates"""
    await manager.connect(websocket, "home")
    try:
        while True:
            # Wait for any message from the client (like ping)
            data = await websocket.receive_text()
            # Echo back to confirm connection is alive
            await websocket.send_text(json.dumps({"status": "ok", "message": "ping received"}))
    except WebSocketDisconnect:
        manager.disconnect(websocket, "home")

@app.websocket("/ws/health")
async def health_websocket(websocket: WebSocket):
    """WebSocket endpoint for health status updates"""
    await websocket.accept()
    try:
        while True:
            # Check Redis availability and send status
            redis_available = check_redis_available()
            await websocket.send_json({
                "status": "ok" if redis_available else "error",
                "redis_available": redis_available
            })
            # Wait before sending the next update
            await asyncio.sleep(5)
    except WebSocketDisconnect:
        pass

def main():
    """Entry point for the console script."""
    uvicorn.run("server.api:app", host="0.0.0.0", port=8000)

if __name__ == "__main__":
    uvicorn.run("api:app", host="0.0.0.0", port=8000, reload=True)