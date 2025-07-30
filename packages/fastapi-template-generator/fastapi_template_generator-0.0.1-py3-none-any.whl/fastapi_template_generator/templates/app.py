"""
Шаблон основного app.py файла
"""

def get_app_template() -> str:
    return '''"""
FastAPI приложение
Точка входа, настройка middleware и подключение роутеров
"""

import asyncio
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from loguru import logger

from core.settings import settings
from core.logger import setup_logging
from core.db import init_database, close_database
from middleware.error_handler import error_handler_middleware
from middleware.logging import logging_middleware
from modules.echo.router import router as echo_router

# Настройка логирования
setup_logging()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Управление жизненным циклом приложения"""
    # Startup
    logger.info(f"🚀 Запуск {settings.APP_NAME} v{settings.APP_VERSION}")
    
    # Инициализация БД
    if not await init_database():
        logger.error("❌ Не удалось инициализировать БД. Завершение работы.")
        raise RuntimeError("Database initialization failed")
    
    logger.info("✅ Приложение готово к работе")
    
    yield
    
    # Shutdown
    logger.info("🛑 Завершение работы приложения...")
    await close_database()
    logger.info("👋 Приложение остановлено")


# Создание приложения
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="FastAPI приложение с модульной архитектурой",
    docs_url="/docs" if settings.DEBUG else None,
    redoc_url="/redoc" if settings.DEBUG else None,
    lifespan=lifespan,
)

# Middleware (порядок важен!)
app.middleware("http")(error_handler_middleware)
app.middleware("http")(logging_middleware)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Подключение роутеров
app.include_router(echo_router, prefix="/api/echo", tags=["echo"])


@app.get("/health")
async def health_check():
    """Проверка состояния сервиса и БД"""
    from core.db import check_database_connection
    
    db_status = await check_database_connection()
    
    return {
        "status": "ok" if db_status else "warning",
        "service": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "database": "connected" if db_status else "disconnected"
    }


@app.get("/")
async def root():
    """Корневой endpoint"""
    return {
        "message": f"Welcome to {settings.APP_NAME}!",
        "version": settings.APP_VERSION,
        "docs": "/docs" if settings.DEBUG else "Documentation disabled in production",
        "health": "/health"
    }
'''