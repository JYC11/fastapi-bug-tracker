from fastapi import APIRouter

from app.common.settings import settings
from app.entrypoints.api_v1.enduser.user import router as enduser_user_router

api_v1_router = APIRouter()
external_router = APIRouter()
backoffice_router = APIRouter()
enduser_router = APIRouter()

enduser_router.include_router(enduser_user_router, tags=["external-enduser-user"])

external_router.include_router(enduser_router, prefix=settings.enduser_prefix)

api_v1_router.include_router(external_router, prefix=settings.external_prefix)
