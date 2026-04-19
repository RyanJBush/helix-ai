import json
from datetime import datetime

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from app.services.stream_service import stream_manager

router = APIRouter()


@router.get("/status")
def status() -> dict[str, int | str]:
    return {"stream": "available", "subscribers": stream_manager.subscriber_count()}


@router.websocket("/ws")
async def websocket_stream(websocket: WebSocket):
    await stream_manager.connect(websocket)
    await websocket.send_json({"event": "connected", "timestamp": datetime.utcnow().isoformat()})

    try:
        while True:
            message = await websocket.receive_text()
            await stream_manager.broadcast(
                {
                    "event": "stream_echo",
                    "payload": message,
                    "timestamp": datetime.utcnow().isoformat(),
                }
            )
    except WebSocketDisconnect:
        stream_manager.disconnect(websocket)
        await stream_manager.broadcast(
            {
                "event": "subscriber_left",
                "timestamp": datetime.utcnow().isoformat(),
            }
        )
    except json.JSONDecodeError:
        await websocket.send_json({"event": "error", "detail": "invalid JSON payload"})
