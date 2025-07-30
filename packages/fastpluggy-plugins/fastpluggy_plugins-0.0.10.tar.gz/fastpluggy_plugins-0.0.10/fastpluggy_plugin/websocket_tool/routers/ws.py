# ws.py - WebSocket router with core functionality
import logging
import os
import time
from typing import Optional

from fastapi import APIRouter, Request, HTTPException
from fastapi import Body, Query
from fastapi import WebSocket, WebSocketDisconnect
from fastapi.responses import FileResponse
from starlette.responses import JSONResponse

from fastpluggy.core.flash import FlashMessage
from fastpluggy.core.tools.fastapi import redirect_to_previous
from fastpluggy.fastpluggy import FastPluggy
from ..schema.ws_message import WebSocketMessage
from ..ws_manager import DisconnectReason

ws_router = APIRouter(
    prefix="/ws",
    tags=["websocket"]
)


@ws_router.websocket("/{client_id}")
@ws_router.websocket("")  # fallback if no client_id
async def websocket_endpoint(websocket: WebSocket, client_id: Optional[str] = None):
    """WebSocket endpoint with connection management"""
    manager = FastPluggy.get_global("ws_manager")
    if manager is None:
        logging.error("WebSocket manager not available")
        await websocket.close(code=1011, reason="Server error")
        return

    # Extract client_id from URL path or query params
    if client_id is None:
        client_id = websocket.query_params.get("clientId")

    logging.info(f"WebSocket connection attempt: {client_id or 'anonymous'}")

    # Use the connection context manager for automatic cleanup
    async with manager.connection_context(websocket, client_id):
        try:
            while True:
                # Receive and echo messages
                data = await websocket.receive_text()
                logging.debug(f"Received from {client_id or 'anonymous'}: {data}")

                # Create echo response
                echo_message = WebSocketMessage(
                    type="echo",
                    content=f"Echo: {data}",
                    meta={
                        "timestamp": time.time(),
                        "from": client_id or "anonymous",
                        "original": data
                    }
                )

                # Send echo back to the specific client
                success = await manager.send_to_client(echo_message, client_id)
                if not success:
                    logging.warning(f"Failed to send echo to {client_id}")
                    break

        except WebSocketDisconnect:
            logging.info(f"Client {client_id or 'anonymous'} disconnected normally")
        except Exception as e:
            logging.error(f"WebSocket error for {client_id or 'anonymous'}: {e}")


@ws_router.post("/send-message")
async def send_message(
        request: Request,
        payload: WebSocketMessage = Body(...),
        method: str = Query('web', description="Response method: 'web' or 'api'"),
        client_id: Optional[str] = Query(None, description="Target specific client (None for broadcast)")
):
    """Send message with improved error handling"""
    manager = FastPluggy.get_global("ws_manager")

    if manager is None:
        error_msg = "WebSocket manager not available"
        if method == "web":
            FlashMessage.add(request=request, message=error_msg, category='error')
            return redirect_to_previous(request)
        else:
            raise HTTPException(status_code=503, detail=error_msg)

    # Get current stats
    stats = manager.get_stats()

    if stats["total_active_connections"] == 0:
        error_msg = "No active WebSocket connections"
        if method == "web":
            FlashMessage.add(request=request, message=error_msg, category='error')
            return redirect_to_previous(request)
        else:
            raise HTTPException(status_code=404, detail=error_msg)

    try:
        # Use thread-safe notify method
        success = manager.notify(payload, client_id)

        if not success:
            error_msg = "Failed to queue message"
            if method == "web":
                FlashMessage.add(request=request, message=error_msg, category='error')
                return redirect_to_previous(request)
            else:
                raise HTTPException(status_code=503, detail=error_msg)

        # Success message
        target_desc = f"client {client_id}" if client_id else "all connected clients"
        success_msg = f"Message queued for {target_desc}"

        if method == "web":
            FlashMessage.add(request=request, message=success_msg, category="success")
            return redirect_to_previous(request)
        else:
            return JSONResponse(content={
                "success": True,
                "message": success_msg,
                "target": client_id,
                "stats": {
                    "active_connections": stats["total_active_connections"],
                    "queue_size": stats["queue_size"]
                }
            })

    except Exception as e:
        error_msg = f"Error processing message: {str(e)}"
        logging.error(error_msg)

        if method == "web":
            FlashMessage.add(request=request, message=error_msg, category='error')
            return redirect_to_previous(request)
        else:
            raise HTTPException(status_code=500, detail=error_msg)


@ws_router.get("/stats")
async def get_websocket_stats():
    """Get WebSocket manager statistics"""
    manager = FastPluggy.get_global("ws_manager")

    if manager is None:
        raise HTTPException(status_code=503, detail="WebSocket manager not available")

    stats = manager.get_stats()

    # Add health indicators
    health_status = "healthy"
    issues = []

    if stats["queue_utilization"] > 0.9:
        health_status = "critical"
        issues.append("Queue nearly full")
    elif stats["queue_utilization"] > 0.7:
        health_status = "warning"
        issues.append("Queue usage high")

    if stats["queue_overflows"] > 0:
        health_status = "critical"
        issues.append("Queue overflows detected")

    if stats["messages_failed"] > stats["messages_sent"] * 0.1:
        health_status = "warning"
        issues.append("High message failure rate")

    return {
        "stats": stats,
        "health": {
            "status": health_status,
            "issues": issues,
            "message_success_rate": stats["messages_sent"] / max(1, stats["messages_sent"] + stats["messages_failed"])
        },
        "timestamp": time.time()
    }


@ws_router.get("/clients")
async def list_websocket_clients():
    """List all connected WebSocket clients with metadata"""
    manager = FastPluggy.get_global("ws_manager")

    if manager is None:
        raise HTTPException(status_code=503, detail="WebSocket manager not available")

    clients = manager.list_clients()

    # Add summary
    summary = {
        "total_clients": len(clients),
        "named_clients": len([c for c in clients if c["type"] == "named"]),
        "anonymous_clients": len([c for c in clients if c["type"] == "anonymous"]),
        "healthy_clients": len([c for c in clients if c["health_score"] > 0.8])
    }

    return {
        "summary": summary,
        "clients": clients,
        "timestamp": time.time()
    }


@ws_router.delete("/clients/{client_id}")
async def disconnect_websocket_client(
        client_id: str,
        reason: str = Query("admin_disconnect", description="Reason for disconnection")
):
    """Administratively disconnect a specific client"""
    manager = FastPluggy.get_global("ws_manager")

    if manager is None:
        raise HTTPException(status_code=503, detail="WebSocket manager not available")

    # Validate disconnect reason
    try:
        disconnect_reason = DisconnectReason(reason) if reason in [r.value for r in
                                                                   DisconnectReason] else DisconnectReason.SERVER_DISCONNECT
    except ValueError:
        disconnect_reason = DisconnectReason.SERVER_DISCONNECT

    try:
        await manager.disconnect(client_id, disconnect_reason)
        return {
            "success": True,
            "message": f"Client {client_id} disconnected",
            "reason": disconnect_reason.value,
            "timestamp": time.time()
        }
    except Exception as e:
        logging.error(f"Failed to disconnect client {client_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to disconnect client: {str(e)}")


@ws_router.get("/health")
async def websocket_health_check():
    """Health check endpoint for monitoring"""
    manager = FastPluggy.get_global("ws_manager")

    if manager is None:
        return {
            "status": "critical",
            "issues": ["WebSocket manager not available"],
            "timestamp": time.time()
        }

    stats = manager.get_stats()

    # Determine health status
    issues = []
    status = "healthy"

    if stats["queue_utilization"] > 0.9:
        status = "critical"
        issues.append("Queue nearly full")
    elif stats["queue_utilization"] > 0.7:
        status = "warning"
        issues.append("Queue usage high")

    if stats["queue_overflows"] > 0:
        status = "critical"
        issues.append("Queue overflows detected")

    if stats["messages_failed"] > stats["messages_sent"] * 0.1:
        status = "warning"
        issues.append("High message failure rate")

    if stats["heartbeat_timeouts"] > stats["total_connections"] * 0.05:
        status = "warning"
        issues.append("High heartbeat timeout rate")

    return {
        "status": status,
        "issues": issues,
        "stats": {
            "active_connections": stats["total_active_connections"],
            "queue_utilization": stats["queue_utilization"],
            "message_success_rate": stats["messages_sent"] / max(1, stats["messages_sent"] + stats["messages_failed"]),
            "uptime_connections": stats["total_connections"]
        },
        "timestamp": time.time()
    }


@ws_router.get("/service-worker.js")
async def service_worker(v: str = Query(None)):
    """Serve the service worker JavaScript file"""
    logging.info(f"Service worker {v} requested")
    base_dir = os.path.dirname(os.path.abspath(__file__))
    file_path = f"{base_dir}/../static/js/service-worker.js"

    if not os.path.exists(file_path):
        logging.error(f"Service worker file not found: {file_path}")
        raise HTTPException(status_code=404, detail="Service worker file not found")

    response = FileResponse(file_path)
    response.headers["Service-Worker-Allowed"] = "/"
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    return response