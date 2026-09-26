from fastapi import APIRouter
from app.api.v1.auth import router as auth_router
from app.api.v1.organization import router as organization_router
from app.api.v1.llm_config import router as llm_config_router
from app.api.v1.departments import router as departments_router
from app.api.v1.users import router as users_router
from app.api.v1.roles import router as roles_router
from app.api.v1.documents import router as documents_router
from app.api.v1.chat import router as chat_router
from app.api.v1.logs import router as logs_router

api_v1_router = APIRouter(prefix="/api/v1")

api_v1_router.include_router(auth_router)
api_v1_router.include_router(organization_router)
api_v1_router.include_router(llm_config_router)
api_v1_router.include_router(departments_router)
api_v1_router.include_router(users_router)
api_v1_router.include_router(roles_router)
api_v1_router.include_router(documents_router)
api_v1_router.include_router(chat_router)
api_v1_router.include_router(logs_router)
