from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from slowapi.errors import RateLimitExceeded
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
import logging

from app.core.config import settings
from app.db.base import Base, engine, SessionLocal
from app.core.rate_limit import limiter, rate_limit_exceeded_handler
from app.core.logging_config import setup_logging
from app.core.middleware import RequestIDMiddleware, RequestLoggingMiddleware, SecurityHeadersMiddleware
from app.core.openapi import tags_metadata, description
from app.core.exceptions import (
    validation_exception_handler,
    sqlalchemy_exception_handler,
    integrity_error_handler,
    general_exception_handler,
    app_exception_handler,
    AppException
)

# Import routers
from app.api.endpoints import auth, courses, reviews, categories, admin, favorites, reports, compare, search, telegram

# Настройка логирования
setup_logging(log_level=settings.LOG_LEVEL if hasattr(settings, 'LOG_LEVEL') else "INFO")
logger = logging.getLogger(__name__)

# Создание таблиц БД
Base.metadata.create_all(bind=engine)


# ============= Lifespan Context Manager (Best Practice) =============

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Modern lifespan context manager (replaces deprecated on_event).

    Best Practice: Use lifespan for startup/shutdown events as per FastAPI docs.
    This approach is more explicit and supports async cleanup properly.
    """
    # Startup
    logger.info(f"Starting {settings.PROJECT_NAME} v{settings.VERSION}")
    logger.info(f"Environment: {settings.ENVIRONMENT if hasattr(settings, 'ENVIRONMENT') else 'development'}")
    logger.info(f"API docs available at: /docs")
    logger.info(f"Health check available at: /health")

    yield  # Application runs here

    # Shutdown
    logger.info(f"Shutting down {settings.PROJECT_NAME}")
    engine.dispose()
    logger.info("Database connections closed gracefully")


# Создание приложения
app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    description=description,
    openapi_tags=tags_metadata,
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,  # Best Practice: Use lifespan instead of on_event
    contact={
        "name": "CourseRate API Support",
        "email": "support@courserate.com",
    },
    license_info={
        "name": "MIT",
        "url": "https://opensource.org/licenses/MIT",
    },
)


# ============= Exception Handlers =============

# Обработчики исключений (порядок важен - от специфичных к общим)
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(IntegrityError, integrity_error_handler)
app.add_exception_handler(SQLAlchemyError, sqlalchemy_exception_handler)
app.add_exception_handler(AppException, app_exception_handler)
app.add_exception_handler(RateLimitExceeded, rate_limit_exceeded_handler)
app.add_exception_handler(Exception, general_exception_handler)


# ============= Middleware =============

# Rate limiting
app.state.limiter = limiter

# Request ID tracking middleware
app.add_middleware(RequestIDMiddleware)

# Security headers middleware
app.add_middleware(SecurityHeadersMiddleware)

# Request logging middleware
app.add_middleware(RequestLoggingMiddleware)

# CORS middleware (должен быть последним)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router, prefix=f"{settings.API_V1_STR}/auth", tags=["auth"])
app.include_router(courses.router, prefix=f"{settings.API_V1_STR}/courses", tags=["courses"])
app.include_router(reviews.router, prefix=f"{settings.API_V1_STR}/reviews", tags=["reviews"])
app.include_router(categories.router, prefix=f"{settings.API_V1_STR}/categories", tags=["categories"])
app.include_router(admin.router, prefix=f"{settings.API_V1_STR}/admin", tags=["admin"])
app.include_router(favorites.router, prefix=f"{settings.API_V1_STR}/favorites", tags=["favorites"])
app.include_router(reports.router, prefix=f"{settings.API_V1_STR}/reports", tags=["reports"])
app.include_router(compare.router, prefix=f"{settings.API_V1_STR}/compare", tags=["compare"])
app.include_router(search.router, prefix=f"{settings.API_V1_STR}/search", tags=["search"])
app.include_router(telegram.router, prefix=f"{settings.API_V1_STR}/telegram", tags=["telegram"])



# ============= Root & Health Endpoints =============

@app.get("/", tags=["Root"])
async def root():
    """Root endpoint"""
    return {
        "success": True,
        "message": f"Welcome to {settings.PROJECT_NAME} API",
        "version": settings.VERSION,
        "docs": "/docs",
        "redoc": "/redoc"
    }


@app.get("/health", tags=["Health"])
async def health_check():
    """
    Health check endpoint
    Проверяет состояние приложения и подключения к БД
    """
    health_status = {
        "status": "healthy",
        "version": settings.VERSION,
        "database": "unknown"
    }

    # Проверка подключения к БД
    try:
        db = SessionLocal()
        db.execute(text("SELECT 1"))
        db.close()
        health_status["database"] = "connected"
    except Exception as e:
        logger.error(f"Database health check failed: {str(e)}")
        health_status["status"] = "unhealthy"
        health_status["database"] = "disconnected"
        health_status["error"] = "Database connection failed"

    return health_status


@app.get("/health/ready", tags=["Health"])
async def readiness_check():
    """
    Readiness check для Kubernetes/Docker
    Проверяет готовность приложения принимать запросы
    """
    try:
        db = SessionLocal()
        db.execute(text("SELECT 1"))
        db.close()
        return {"ready": True}
    except Exception as e:
        logger.error(f"Readiness check failed: {str(e)}")
        return {"ready": False, "error": str(e)}


@app.get("/health/live", tags=["Health"])
async def liveness_check():
    """
    Liveness check для Kubernetes/Docker
    Проверяет что приложение живо (не зависло)
    """
    return {"alive": True}
