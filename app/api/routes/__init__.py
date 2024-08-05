from fastapi import APIRouter

# Routes Import
from .yolo_routes import router as yolo_router, get_tag_description as yolo_tag_description

__version__ = 1.0

router = APIRouter(
    prefix='/v1'
)

router.include_router(yolo_router) # Adding a route to project

def get_tags_description():
    tags = []
    tags.append(yolo_tag_description()) # Adding a documentation tag from a specific router to project
    return tags
