import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, HTTPException, status
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.core.init_db import init_db_data
from app.core.security import clear_auth_cookies
from app.api.v1.router import api_v1_router

logging.basicConfig(level=settings.LOG_LEVEL)
logger = logging.getLogger("policyhelper")


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Seed default roles, general department, and super admin
    logger.info("Initializing database seeds and initial admin...")
    try:
        await init_db_data()
        logger.info("Database initialized successfully.")
    except Exception as e:
        logger.error(f"Error initializing database seeds: {e}", exc_info=True)
    yield
    # Shutdown
    logger.info("Shutting down PolicyHelper API...")


app = FastAPI(
    title="PolicyHelper API",
    description="Enterprise Policy Search & Chatbot Backend with pgvector and LangGraph",
    version="1.0.0",
    lifespan=lifespan,
)

@app.exception_handler(HTTPException)
async def custom_http_exception_handler(request: Request, exc: HTTPException):
    response = JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail},
        headers=exc.headers,
    )
    if exc.status_code == status.HTTP_401_UNAUTHORIZED:
        clear_auth_cookies(response)
    return response

# CORS Middleware configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        settings.FRONTEND_URL,
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount API routes
app.include_router(api_v1_router)


@app.get("/health", tags=["Health"])
async def health_check():
    return {
        "status": "healthy",
        "service": "policyhelper-api",
        "storage_type": settings.STORAGE_TYPE,
    }
