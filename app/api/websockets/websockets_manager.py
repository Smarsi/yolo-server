from uuid import uuid4 as uuid
from fastapi import WebSocket, WebSocketDisconnect



class WebSocketConnectionManager:

    def __init__(self):
        self.active_connections: list[WebSocket] = []
    
    async def connect(self, websocket: WebSocket) -> str:
        await websocket.accept()
        self.active_connections.append(websocket)
        connection_id = str(uuid()).replace("-", "")
        return connection_id

    async def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)
