"""
Шаблоны для core модуля
"""

def get_core_templates() -> dict:
    return {
        "__init__.py": "",
        
        "settings.py": '''"""
Настройки приложения через pydantic-settings
Все настройки через переменные окружения с префиксом APP_
"""

from typing import List, Optional
from pydantic_settings import BaseSettings
from pydantic import computed_field


class Settings(BaseSettings):
    """Настройки приложения"""
    
    # Основные настройки
    APP_NAME: str = "FastAPI App"
    APP_VERSION: str = "0.1.0"
    DEBUG: bool = True
    
    # База данных - отдельные компоненты
    DB_HOST: str = "localhost"
    DB_PORT: int = 5432
    DB_NAME: str = "fastapi_db"
    DB_USER: str = "postgres"
    DB_PASSWORD: str = "postgres"
    
    # Безопасность
    BEARER_TOKEN: str = "change-me-in-production"
    
    # CORS
    ALLOWED_ORIGINS: List[str] = ["*"]
    
    # Логирование
    LOG_LEVEL: str = "INFO"
    LOG_FILE: str = "logs/app.log"
    
    @computed_field
    @property
    def DATABASE_URL(self) -> str:
        """Собираем URL БД из компонентов"""
        return f"postgresql+asyncpg://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
    
    class Config:
        env_file = ".env"
        env_prefix = "APP_"
        case_sensitive = False


# Глобальный экземпляр настроек
settings = Settings()
''',
        
        "db.py": '''"""
Настройка базы данных и сессий
Базовые модели с общими полями
Инициализация и проверка подключения
"""

from datetime import datetime
from sqlalchemy import Column, DateTime, String, func, text
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.sql.sqltypes import TypeDecorator, CHAR
from sqlalchemy.dialects.postgresql import UUID
from loguru import logger
import uuid
import asyncio

from core.settings import settings

# Создание движка БД
engine = create_async_engine(
    settings.DATABASE_URL,
    echo=settings.DEBUG,  # SQL логи в debug режиме
    future=True,
    pool_pre_ping=True,  # Проверка соединения перед использованием
    pool_recycle=3600,   # Пересоздание соединений каждый час
)

# Фабрика сессий
SessionLocal = sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False,
)

# Базовый класс для моделей
Base = declarative_base()


class GUID(TypeDecorator):
    """Тип данных для UUID"""
    impl = CHAR
    cache_ok = True
    
    def load_dialect_impl(self, dialect):
        if dialect.name == 'postgresql':
            return dialect.type_descriptor(UUID())
        else:
            return dialect.type_descriptor(CHAR(32))
    
    def process_bind_param(self, value, dialect):
        if value is None:
            return value
        elif dialect.name == 'postgresql':
            return str(value)
        else:
            if not isinstance(value, uuid.UUID):
                return str(uuid.UUID(value)).replace('-', '')
            else:
                return str(value).replace('-', '')
    
    def process_result_value(self, value, dialect):
        if value is None:
            return value
        else:
            if not isinstance(value, uuid.UUID):
                return uuid.UUID(value)
            return value


class BaseModel(Base):
    """
    Базовая модель с общими полями
    Все модели должны наследоваться от неё
    """
    __abstract__ = True
    
    id = Column(GUID(), primary_key=True, default=uuid.uuid4, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    deleted_at = Column(DateTime(timezone=True), nullable=True)  # Для soft delete
    
    def soft_delete(self):
        """Мягкое удаление записи"""
        self.deleted_at = datetime.utcnow()
    
    @property
    def is_deleted(self) -> bool:
        """Проверка удалена ли запись"""
        return self.deleted_at is not None


async def check_database_connection() -> bool:
    """Проверка подключения к базе данных"""
    try:
        async with engine.begin() as conn:
            await conn.execute(text("SELECT 1"))
        logger.info("✓ Подключение к БД успешно")
        return True
    except Exception as e:
        logger.error(f"✗ Ошибка подключения к БД: {e}")
        logger.error(f"URL подключения: {settings.DATABASE_URL.replace(settings.DB_PASSWORD, '***')}")
        return False


async def create_tables():
    """Создание всех таблиц"""
    try:
        logger.info("Создание таблиц БД...")
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        logger.info("✓ Таблицы БД созданы успешно")
        return True
    except Exception as e:
        logger.error(f"✗ Ошибка создания таблиц: {e}")
        return False


async def drop_tables():
    """Удаление всех таблиц"""
    try:
        logger.info("Удаление таблиц БД...")
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)
        logger.info("✓ Таблицы БД удалены успешно")
        return True
    except Exception as e:
        logger.error(f"✗ Ошибка удаления таблиц: {e}")
        return False


async def init_database():
    """
    Инициализация базы данных
    Проверка подключения и создание таблиц
    """
    logger.info("Инициализация базы данных...")
    
    # Проверяем подключение
    if not await check_database_connection():
        logger.error("Не удалось подключиться к БД. Проверьте настройки.")
        return False
    
    # Создаем таблицы
    if not await create_tables():
        logger.error("Не удалось создать таблицы БД.")
        return False
    
    logger.info("✓ База данных инициализирована успешно")
    return True


async def close_database():
    """Закрытие соединений с БД"""
    try:
        await engine.dispose()
        logger.info("✓ Соединения с БД закрыты")
    except Exception as e:
        logger.error(f"✗ Ошибка закрытия соединений с БД: {e}")
''',
        
        "logger.py": '''"""
Настройка логирования через loguru
Один раз настроить здесь, потом везде просто импортить logger
"""

import sys
from pathlib import Path
from loguru import logger

from core.settings import settings


def setup_logging():
    """Настройка логирования для приложения"""
    # Удаляем стандартный handler
    logger.remove()
    
    # Создаем папку для логов если её нет
    log_dir = Path(settings.LOG_FILE).parent
    log_dir.mkdir(exist_ok=True)
    
    # Формат логов
    log_format = (
        "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | "
        "<level>{level: <8}</level> | "
        "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> | "
        "<level>{message}</level>"
    )
    
    # Консольный вывод
    logger.add(
        sys.stdout,
        format=log_format,
        level="DEBUG" if settings.DEBUG else settings.LOG_LEVEL,
        colorize=True,
    )
    
    # Файловый вывод
    logger.add(
        settings.LOG_FILE,
        format=log_format,
        rotation="10 MB",
        retention="7 days",
        compression="zip",
        level=settings.LOG_LEVEL,
        encoding="utf-8",
    )
    
    # Отдельный файл для ошибок
    logger.add(
        settings.LOG_FILE.replace(".log", "_errors.log"),
        format=log_format,
        level="ERROR",
        rotation="10 MB",
        retention="30 days",
        compression="zip",
        encoding="utf-8",
    )
    
    logger.info(f"Логирование настроено. Debug: {settings.DEBUG}, Level: {settings.LOG_LEVEL}")
''',
        
        "dependencies.py": '''"""
Общие зависимости для всего приложения
Используются через Dependency Injection в FastAPI
"""

from typing import AsyncGenerator
from fastapi import HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from loguru import logger

from core.settings import settings
from core.db import SessionLocal

# Bearer схема безопасности
security = HTTPBearer()


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Получение сессии БД
    Автоматически закрывается после использования
    """
    async with SessionLocal() as session:
        try:
            yield session
        except Exception as e:
            logger.error(f"Database session error: {e}")
            await session.rollback()
            raise
        finally:
            await session.close()


async def verify_bearer_token(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> str:
    """
    Проверка Bearer токена
    Используется только на защищенных эндпоинтах
    """
    if credentials.credentials != settings.BEARER_TOKEN:
        logger.warning(f"Invalid bearer token attempt: {credentials.credentials[:10]}...")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid bearer token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return credentials.credentials


async def get_current_user_id(
    token: str = Depends(verify_bearer_token)
) -> str:
    """
    Получение ID текущего пользователя
    Заглушка для будущей системы аутентификации
    """
    # TODO: Реализовать получение пользователя из токена
    return "system_user"
'''
    }