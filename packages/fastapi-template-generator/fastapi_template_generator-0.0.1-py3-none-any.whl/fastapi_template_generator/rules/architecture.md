# Архитектура FastAPI проекта

## Основные принципы

### 1. Модульность
- Каждая бизнес-функция в отдельном модуле
- Модули независимы друг от друга
- Общий код выносится в `shared/`

### 2. Слоистая архитектура
```
API Layer (router.py) → Business Logic (services.py) → Data Access (models.py)
```

### 3. Dependency Injection
- Все зависимости инжектятся через FastAPI DI
- База данных, аутентификация, конфигурация

### 4. Разделение ответственности
- **Router**: только маршрутизация и валидация
- **Service**: бизнес-логика
- **Model**: работа с данными
- **Schema**: валидация входных/выходных данных

## Структура модуля

```
modules/module_name/
├── router.py      # API эндпоинты
├── schemas.py     # Pydantic модели
├── services.py    # Бизнес логика
├── models.py      # ORM модели
├── funcs.py       # Вспомогательные функции
├── constants.py   # Константы модуля
└── exceptions.py  # Исключения модуля
```

## Правила

### Размер файлов
- Если файл больше 600 строк → разбить на подмодули
- Создать папку с именем модуля и разнести по файлам

### Импорты
1. Стандартные библиотеки Python
2. Сторонние библиотеки
3. Локальные модули проекта

```python
# Правильно
import os
import sys
from typing import List

from fastapi import APIRouter
from sqlalchemy import select

from core.db import get_db
from .schemas import UserCreate
```

### Комментарии
- Комментарии только для сложной логики
- Docstrings для всех публичных функций и классов
- Не комментировать очевидные вещи

### Обработка ошибок
- Обрабатывать только там, где можем что-то исправить
- Логировать на уровне сервиса
- Возвращать понятные ошибки клиенту

## Паттерны

### Service Layer
```python
class UserService:
    async def create_user(self, db: AsyncSession, data: UserCreate) -> User:
        # Валидация
        # Бизнес-логика
        # Сохранение
        pass
```

### Repository (опционально)
Для сложных запросов можно выделить отдельный слой:
```python
class UserRepository:
    async def find_by_email(self, db: AsyncSession, email: str) -> User:
        # Сложные запросы к БД
        pass
```

### Dependency Injection
```python
# dependencies.py
async def get_current_user(token: str = Depends(oauth2_scheme)):
    # Логика получения пользователя
    return user

# router.py
@router.get("/profile")
async def get_profile(user: User = Depends(get_current_user)):
    return user
```