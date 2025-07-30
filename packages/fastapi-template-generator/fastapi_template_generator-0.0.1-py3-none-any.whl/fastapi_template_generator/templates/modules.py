"""
Шаблоны для модулей
"""

def get_module_templates(module_name: str) -> dict:
    return {
        "__init__.py": "",
        
        "router.py": f'''"""
{module_name.title()} модуль - роутер
API эндпоинты для {module_name} функциональности
"""

from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from loguru import logger

from core.dependencies import get_db, verify_bearer_token
from shared.schemas.common import ResponseModel, PaginatedResponse, PaginationParams
from .schemas import {module_name.title()}Request, {module_name.title()}Response, {module_name.title()}Create
from .services import {module_name}_service
from .exceptions import {module_name.title()}NotFoundError

router = APIRouter()


@router.get("/", response_model=PaginatedResponse[{module_name.title()}Response])
async def get_{module_name}s(
    pagination: PaginationParams = Depends(),
    db: AsyncSession = Depends(get_db)
):
    """Получить список всех {module_name}"""
    try:
        items, total = await {module_name}_service.get_all(db, pagination)
        return PaginatedResponse.create(items, total, pagination)
    except Exception as e:
        logger.error(f"Error getting {module_name}s: {{e}}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve {module_name}s"
        )


@router.get("/{{item_id}}", response_model=ResponseModel[{module_name.title()}Response])
async def get_{module_name}(
    item_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Получить {module_name} по ID"""
    try:
        item = await {module_name}_service.get_by_id(db, item_id)
        return ResponseModel(data=item)
    except {module_name.title()}NotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"{module_name.title()} not found"
        )


@router.post("/", response_model=ResponseModel[{module_name.title()}Response])
async def create_{module_name}(
    request: {module_name.title()}Create,
    db: AsyncSession = Depends(get_db)
):
    """Создать новый {module_name}"""
    try:
        item = await {module_name}_service.create(db, request)
        return ResponseModel(
            data=item,
            message=f"{module_name.title()} created successfully"
        )
    except Exception as e:
        logger.error(f"Error creating {module_name}: {{e}}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create {module_name}"
        )


@router.post("/protected", 
    response_model=ResponseModel[{module_name.title()}Response],
    dependencies=[Depends(verify_bearer_token)]
)
async def create_protected_{module_name}(
    request: {module_name.title()}Create,
    db: AsyncSession = Depends(get_db)
):
    """Создать {module_name} (защищенный эндпоинт)"""
    try:
        item = await {module_name}_service.create(db, request, is_protected=True)
        return ResponseModel(
            data=item,
            message=f"Protected {module_name} created successfully"
        )
    except Exception as e:
        logger.error(f"Error creating protected {module_name}: {{e}}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create protected {module_name}"
        )


@router.delete("/{{item_id}}", dependencies=[Depends(verify_bearer_token)])
async def delete_{module_name}(
    item_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Удалить {module_name} (мягкое удаление)"""
    try:
        await {module_name}_service.delete(db, item_id)
        return ResponseModel(
            data={{"id": item_id}},
            message=f"{module_name.title()} deleted successfully"
        )
    except {module_name.title()}NotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"{module_name.title()} not found"
        )
''',
        
        "schemas.py": f'''"""
Схемы для {module_name} модуля
Pydantic модели для входных и выходных данных
"""

from typing import Optional
from pydantic import BaseModel, Field
from datetime import datetime
import uuid

from shared.schemas.common import BaseSchema


class {module_name.title()}Base(BaseModel):
    """Базовые поля {module_name}"""
    message: str = Field(..., min_length=1, max_length=1000, description="Сообщение")
    category: Optional[str] = Field(None, max_length=100, description="Категория")


class {module_name.title()}Create({module_name.title()}Base):
    """Схема создания {module_name}"""
    pass


class {module_name.title()}Update(BaseModel):
    """Схема обновления {module_name}"""
    message: Optional[str] = Field(None, min_length=1, max_length=1000)
    category: Optional[str] = Field(None, max_length=100)


class {module_name.title()}Response(BaseSchema):
    """Ответ с данными {module_name}"""
    message: str
    category: Optional[str]
    processed_message: str
    is_protected: bool = False
    
    class Config:
        from_attributes = True


class {module_name.title()}Request(BaseModel):
    """Запрос для обработки {module_name}"""
    message: str = Field(..., min_length=1, max_length=1000)
    options: Optional[dict] = Field(None, description="Дополнительные опции")
''',
        
        "services.py": f'''"""
Сервисы для {module_name} модуля
Бизнес-логика и работа с базой данных
"""

from typing import List, Tuple, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from loguru import logger

from shared.schemas.common import PaginationParams
from .models import {module_name.title()}
from .schemas import {module_name.title()}Create, {module_name.title()}Response
from .funcs import process_message
from .exceptions import {module_name.title()}NotFoundError


class {module_name.title()}Service:
    """Сервис для работы с {module_name}"""
    
    async def get_all(
        self, 
        db: AsyncSession, 
        pagination: PaginationParams
    ) -> Tuple[List[{module_name.title()}Response], int]:
        """Получить все {module_name} с пагинацией"""
        # Запрос с пагинацией
        query = select({module_name.title()}).where(
            {module_name.title()}.deleted_at.is_(None)
        ).offset(pagination.skip).limit(pagination.limit)
        
        result = await db.execute(query)
        items = result.scalars().all()
        
        # Общее количество
        count_query = select(func.count({module_name.title()}.id)).where(
            {module_name.title()}.deleted_at.is_(None)
        )
        total_result = await db.execute(count_query)
        total = total_result.scalar()
        
        # Преобразование в схемы
        response_items = []
        for item in items:
            response_items.append({module_name.title()}Response(
                id=item.id,
                created_at=item.created_at,
                updated_at=item.updated_at,
                message=item.message,
                category=item.category,
                processed_message=item.processed_message,
                is_protected=item.is_protected
            ))
        
        logger.info(f"Retrieved {{len(response_items)}} {module_name}s")
        return response_items, total
    
    async def get_by_id(self, db: AsyncSession, item_id: str) -> {module_name.title()}Response:
        """Получить {module_name} по ID"""
        query = select({module_name.title()}).where(
            {module_name.title()}.id == item_id,
            {module_name.title()}.deleted_at.is_(None)
        )
        result = await db.execute(query)
        item = result.scalar_one_or_none()
        
        if not item:
            raise {module_name.title()}NotFoundError()
        
        return {module_name.title()}Response(
            id=item.id,
            created_at=item.created_at,
            updated_at=item.updated_at,
            message=item.message,
            category=item.category,
            processed_message=item.processed_message,
            is_protected=item.is_protected
        )
    
    async def create(
        self, 
        db: AsyncSession, 
        data: {module_name.title()}Create,
        is_protected: bool = False
    ) -> {module_name.title()}Response:
        """Создать новый {module_name}"""
        # Обработка сообщения
        processed_message = process_message(data.message)
        
        # Создание модели
        item = {module_name.title()}(
            message=data.message,
            category=data.category,
            processed_message=processed_message,
            is_protected=is_protected
        )
        
        db.add(item)
        await db.commit()
        await db.refresh(item)
        
        logger.info(f"Created {module_name} with ID: {{item.id}}")
        
        return {module_name.title()}Response(
            id=item.id,
            created_at=item.created_at,
            updated_at=item.updated_at,
            message=item.message,
            category=item.category,
            processed_message=item.processed_message,
            is_protected=item.is_protected
        )
    
    async def delete(self, db: AsyncSession, item_id: str) -> bool:
        """Мягкое удаление {module_name}"""
        query = select({module_name.title()}).where(
            {module_name.title()}.id == item_id,
            {module_name.title()}.deleted_at.is_(None)
        )
        result = await db.execute(query)
        item = result.scalar_one_or_none()
        
        if not item:
            raise {module_name.title()}NotFoundError()
        
        item.soft_delete()
        await db.commit()
        
        logger.info(f"Soft deleted {module_name} with ID: {{item_id}}")
        return True


# Singleton instance
{module_name}_service = {module_name.title()}Service()
''',
        
        "models.py": f'''"""
Модели БД для {module_name} модуля
SQLAlchemy модели
"""

from sqlalchemy import Column, String, Text, Boolean

from core.db import BaseModel


class {module_name.title()}(BaseModel):
    """Модель {module_name}"""
    __tablename__ = "{module_name}_items"
    
    message = Column(Text, nullable=False, comment="Исходное сообщение")
    category = Column(String(100), nullable=True, comment="Категория")
    processed_message = Column(Text, nullable=False, comment="Обработанное сообщение")
    is_protected = Column(Boolean, default=False, comment="Создано через защищенный эндпоинт")
    
    def __repr__(self):
        return f"<{module_name.title()}(id={{self.id}}, message={{self.message[:50]}})>"
''',
        
        "funcs.py": f'''"""
Вспомогательные функции для {module_name} модуля
Логика обработки данных
"""

from typing import Optional
from loguru import logger


def process_message(message: str) -> str:
    """
    Обработка сообщения
    Пример: переворачивание строки
    """
    if not message:
        return ""
    
    # Простая обработка - переворачивание
    processed = message[::-1]
    
    logger.debug(f"Processed message: {{message[:20]}}... -> {{processed[:20]}}...")
    return processed


def validate_category(category: Optional[str]) -> bool:
    """Валидация категории"""
    if not category:
        return True
    
    allowed_categories = ["general", "test", "demo", "important"]
    return category.lower() in allowed_categories


def format_response(message: str, processed: str) -> dict:
    """Форматирование ответа"""
    return {{
        "original": message,
        "processed": processed,
        "length": len(message),
        "processed_length": len(processed)
    }}
''',
        
        "constants.py": f'''"""
Константы для {module_name} модуля
"""

# Ограничения
MAX_MESSAGE_LENGTH = 1000
MIN_MESSAGE_LENGTH = 1
MAX_CATEGORY_LENGTH = 100

# Категории
ALLOWED_CATEGORIES = [
    "general",
    "test", 
    "demo",
    "important"
]

# Статусы
STATUS_ACTIVE = "active"
STATUS_INACTIVE = "inactive"
STATUS_DELETED = "deleted"

# Сообщения
MSG_CREATED = f"{module_name.title()} created successfully"
MSG_UPDATED = f"{module_name.title()} updated successfully"
MSG_DELETED = f"{module_name.title()} deleted successfully"
MSG_NOT_FOUND = f"{module_name.title()} not found"
''',
        
        "exceptions.py": f'''"""
Исключения для {module_name} модуля
"""

from fastapi import HTTPException, status


class {module_name.title()}Exception(HTTPException):
    """Базовое исключение для {module_name} модуля"""
    pass


class {module_name.title()}NotFoundError({module_name.title()}Exception):
    """Исключение когда {module_name} не найден"""
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"{module_name.title()} not found"
        )


class {module_name.title()}ValidationError({module_name.title()}Exception):
    """Ошибка валидации данных"""
    def __init__(self, detail: str):
        super().__init__(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=detail
        )


class {module_name.title()}AccessDeniedError({module_name.title()}Exception):
    """Ошибка доступа"""
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )
''',
    }