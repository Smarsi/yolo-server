from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Request

from .websockets_manager import WebSocketConnectionManager
wsocket_manager = WebSocketConnectionManager()

# YOLO Service Import
from app.service import get_global_yolo_service

router = APIRouter(
    prefix="/inference",
    tags=["WebSocket Routes - YOLO AS A SERVICE"]
)

def get_tag_description():
    return {
        "name": "WebSocket Routes - YOLO AS A SERVICE",
        "description": """ Used to interact with the YOLO server inference as a service. """
    }

@router.websocket("/")
async def websocket_endpoint(websocket: WebSocket):
    connection_id = await wsocket_manager.connect(websocket)
    try:
        yolo_service = get_global_yolo_service()
        while True:
            image_bytes = await websocket.receive_bytes()
            image = yolo_service.convert_bytes_to_image(image_bytes)
            yolo_service.add_frame(connection_id, image)
            result = yolo_service.get_result(connection_id)
            await websocket.send_json(result)
    except WebSocketDisconnect:
        await wsocket_manager.disconnect(websocket)

