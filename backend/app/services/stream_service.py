import json
from collections.abc import Callable

from fastapi import WebSocket


class StreamManager:
    def __init__(self) -> None:
        self._connections: set[WebSocket] = set()

    async def connect(self, websocket: WebSocket) -> None:
        await websocket.accept()
        self._connections.add(websocket)

    def disconnect(self, websocket: WebSocket) -> None:
        self._connections.discard(websocket)

    async def broadcast(self, payload: dict) -> None:
        dead: list[WebSocket] = []
        message = json.dumps(payload)
        for connection in self._connections:
            try:
                await connection.send_text(message)
            except Exception:  # noqa: BLE001
                dead.append(connection)
        for stale in dead:
            self.disconnect(stale)

    def subscriber_count(self) -> int:
        return len(self._connections)


def make_broadcast_event_factory(manager: StreamManager) -> Callable[[dict], object]:
    async def publish(payload: dict) -> None:
        await manager.broadcast(payload)

    return publish


stream_manager = StreamManager()
