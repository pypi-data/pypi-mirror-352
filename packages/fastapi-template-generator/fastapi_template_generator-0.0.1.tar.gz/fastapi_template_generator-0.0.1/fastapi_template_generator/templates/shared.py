"""
Шаблоны для shared компонентов
"""

def get_shared_templates() -> dict:
    return {
        "__init__.py": "",
        "schemas/__init__.py": "",
        "models/__init__.py": "",
        
        "schemas/common.py": '''"""
Общие схемы для всего приложения
Базовые модели ответов, пагинация и тд
"""

from typing import Generic, TypeVar, Optional, List, Any, Dict
from pydantic import BaseModel, Field
from datetime import datetime
import uuid

T = TypeVar('T')


class ResponseModel(BaseModel, Generic[T]):
    """Базовая модель успешного ответа"""
    status: str = "ok"
    data: T
    message: Optional[str] = None


class ErrorResponse(BaseModel):
    """Модель ошибки"""
    status: str = "error"
    message: str
    error_code: Optional[int] = None
    details: Optional[Dict[str, Any]] = None


class PaginationParams(BaseModel):
    """Параметры пагинации"""
    page: int = Field(1, ge=1, description="Номер страницы")
    page_size: int = Field(20, ge=1, le=100, description="Количество элементов на странице")
    
    @property
    def skip(self) -> int:
        """Количество элементов для пропуска"""
        return (self.page - 1) * self.page_size
    
    @property
    def limit(self) -> int:
        """Лимит элементов для запроса"""
        return self.page_size


class PaginatedResponse(BaseModel, Generic[T]):
    """Ответ с пагинацией"""
    status: str = "ok"
    items: List[T]
    total: int
    page: int
    page_size: int
    pages: int
    
    @classmethod
    def create(cls, items: List[T], total: int, pagination: PaginationParams):
        """Создать ответ с пагинацией"""
        pages = (total + pagination.page_size - 1) // pagination.page_size
        return cls(
            items=items,
            total=total,
            page=pagination.page,
            page_size=pagination.page_size,
            pages=pages
        )


class BaseSchema(BaseModel):
    """Базовая схема с общими полями"""
    id: uuid.UUID
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True
        json_encoders = {
            datetime: lambda v: v.isoformat(),
            uuid.UUID: str
        }


class HealthResponse(BaseModel):
    """Ответ health check"""
    status: str
    service: str
    version: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    uptime: Optional[float] = None


class CreateResponse(BaseModel):
    """Ответ при создании ресурса"""
    status: str = "ok"
    message: str = "Resource created successfully"
    id: uuid.UUID


class UpdateResponse(BaseModel):
    """Ответ при обновлении ресурса"""
    status: str = "ok"
    message: str = "Resource updated successfully"
    id: uuid.UUID


class DeleteResponse(BaseModel):
    """Ответ при удалении ресурса"""
    status: str = "ok"
    message: str = "Resource deleted successfully"
    id: uuid.UUID
''',
        
        "models/base.py": '''"""
Базовые модели для наследования
"""

from typing import Optional, List, Any, Dict
from sqlalchemy import Column, String, Text, Boolean
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.orm import relationship

from core.db import BaseModel


class TimestampedMixin:
    """Миксин для моделей с временными метками"""
    # Уже есть в BaseModel: created_at, updated_at
    pass


class SoftDeleteMixin:
    """Миксин для мягкого удаления"""
    # Уже есть в BaseModel: deleted_at
    pass


class NamedMixin:
    """Миксин для моделей с названием"""
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)


class StatusMixin:
    """Миксин для моделей со статусом"""
    is_active = Column(Boolean, default=True)
    status = Column(String(50), default="active")


class MetadataMixin:
    """Миксин для дополнительных данных"""
    # Можно добавить JSON поле для метаданных
    # metadata = Column(JSON, nullable=True)
    pass


class AuditMixin:
    """Миксин для аудита изменений"""
    created_by = Column(String(255), nullable=True)
    updated_by = Column(String(255), nullable=True)
    
    @declared_attr
    def created_by_user(cls):
        # Связь с таблицей пользователей (когда она будет)
        # return relationship("User", foreign_keys=[cls.created_by])
        pass
'''
    }