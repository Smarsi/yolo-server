__version__ = "0.1.0"


from .yolo_service import Yolo_Service, newYolo_Service

__all__ = ["Yolo_Service"]


def set_global_yolo_service(service: Yolo_Service) -> None:
    global yolo_service
    yolo_service = service

def get_global_yolo_service() -> Yolo_Service:
    return yolo_service


def new_set_global_yolo_service(service: newYolo_Service) -> None:
    global yolo_service
    yolo_service = service

def new_get_global_yolo_service() -> newYolo_Service:
    return yolo_service

