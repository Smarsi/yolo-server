from fastapi import APIRouter

# Routes Import
from .websockets_routes import router as ws_router, get_tag_description as ws_tag_description

__version__ = 1.0

router = APIRouter(
    prefix='/v1'
)

router.include_router(ws_router)

def get_tags_description():
    tags = []
    tags.append(ws_tag_description())
    return tags
