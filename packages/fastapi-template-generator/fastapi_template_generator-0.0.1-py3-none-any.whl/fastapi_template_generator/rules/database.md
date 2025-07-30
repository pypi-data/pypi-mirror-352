# Работа с базой данных

## Модели SQLAlchemy

### Базовая модель
Все модели наследуются от `BaseModel`:
```python
from core.db import BaseModel

class User(BaseModel):
    __tablename__ = "users"
    
    email = Column(String(255), unique=True, nullable=False)
    name = Column(String(100), nullable=False)
```

### Обязательные поля
Базовая модель содержит:
- `id` (UUID) - первичный ключ
- `created_at` - время создания
- `updated_at` - время обновления
- `deleted_at` - время удаления (для soft delete)

### Связи
```python
# One-to-Many
class User(BaseModel):
    posts = relationship("Post", back_populates="user")

class Post(BaseModel):
    user_id = Column(GUID, ForeignKey("users.id"))
    user = relationship("User", back_populates="posts")

# Many-to-Many
association_table = Table(
    "user_roles", Base.metadata,
    Column("user_id", GUID, ForeignKey("users.id")),
    Column("role_id", GUID, ForeignKey("roles.id"))
)

class User(BaseModel):
    roles = relationship("Role", secondary=association_table)
```

## Работа с сессиями

### Dependency Injection
```python
async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with SessionLocal() as session:
        try:
            yield session
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()
```

### Использование в сервисах
```python
async def create_user(db: AsyncSession, user_data: UserCreate) -> User:
    user = User(**user_data.dict())
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user
```

## Запросы

### Async запросы
```python
# Получить по ID
async def get_user(db: AsyncSession, user_id: UUID) -> User:
    result = await db.execute(select(User).where(User.id == user_id))
    return result.scalar_one_or_none()

# Список с фильтрацией
async def get_users(db: AsyncSession, skip: int = 0, limit: int = 100):
    result = await db.execute(
        select(User)
        .where(User.deleted_at.is_(None))
        .offset(skip)
        .limit(limit)
    )
    return result.scalars().all()
```

### Сложные запросы
```python
# Joins
async def get_users_with_posts(db: AsyncSession):
    result = await db.execute(
        select(User)
        .join(Post)
        .where(User.deleted_at.is_(None))
        .options(selectinload(User.posts))
    )
    return result.scalars().all()

# Агрегации
async def count_users(db: AsyncSession) -> int:
    result = await db.execute(
        select(func.count(User.id))
        .where(User.deleted_at.is_(None))
    )
    return result.scalar()
```

## Soft Delete

### Реализация
```python
class BaseModel(Base):
    deleted_at = Column(DateTime(timezone=True), nullable=True)
    
    def soft_delete(self):
        self.deleted_at = datetime.utcnow()
    
    @property
    def is_deleted(self) -> bool:
        return self.deleted_at is not None
```

### Использование
```python
# Удаление
async def delete_user(db: AsyncSession, user_id: UUID):
    user = await get_user(db, user_id)
    if user:
        user.soft_delete()
        await db.commit()

# Фильтрация в запросах
select(User).where(User.deleted_at.is_(None))
```

## Миграции

### Alembic
```bash
# Инициализация
alembic init alembic

# Создание миграции
alembic revision --autogenerate -m "Add users table"

# Применение миграций
alembic upgrade head

# Откат
alembic downgrade -1
```

### Настройка
В `alembic.ini`:
```ini
sqlalchemy.url = postgresql+asyncpg://user:pass@localhost/db
```

## Лучшие практики

### Транзакции
```python
async def complex_operation(db: AsyncSession):
    async with db.begin():
        # Все операции в одной транзакции
        user = User(...)
        db.add(user)
        
        profile = Profile(user_id=user.id, ...)
        db.add(profile)
        
        # Коммит автоматически
```

### Обработка ошибок
```python
async def create_user(db: AsyncSession, user_data: UserCreate):
    try:
        user = User(**user_data.dict())
        db.add(user)
        await db.commit()
        await db.refresh(user)
        return user
    except IntegrityError as e:
        await db.rollback()
        if "unique constraint" in str(e):
            raise HTTPException(400, "Email already exists")
        raise HTTPException(500, "Database error")
```

### Пагинация
```python
async def get_paginated_users(
    db: AsyncSession, 
    page: int = 1, 
    page_size: int = 20
):
    skip = (page - 1) * page_size
    
    # Получаем данные
    users_result = await db.execute(
        select(User)
        .where(User.deleted_at.is_(None))
        .offset(skip)
        .limit(page_size)
    )
    users = users_result.scalars().all()
    
    # Подсчитываем общее количество
    count_result = await db.execute(
        select(func.count(User.id))
        .where(User.deleted_at.is_(None))
    )
    total = count_result.scalar()
    
    return users, total
```

### Оптимизация
```python
# Eager loading
result = await db.execute(
    select(User)
    .options(selectinload(User.posts))
    .where(User.id == user_id)
)

# Batch operations
users = [User(...) for data in user_data_list]
db.add_all(users)
await db.commit()
```

## Индексы

### Создание индексов
```python
class User(BaseModel):
    __tablename__ = "users"
    
    email = Column(String(255), unique=True, nullable=False, index=True)
    name = Column(String(100), nullable=False)
    
    # Составной индекс
    __table_args__ = (
        Index('idx_user_email_active', 'email', 'is_active'),
    )
```

### Мониторинг
- Используйте EXPLAIN для анализа запросов
- Следите за медленными запросами
- Регулярно обновляйте статистику БД
```