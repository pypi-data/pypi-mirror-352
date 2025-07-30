# Дизайн API

## Принципы REST

### Ресурсы и коллекции
- Коллекции: `/users`, `/posts`
- Ресурсы: `/users/123`, `/posts/456`
- Вложенные: `/users/123/posts`

### HTTP методы
- `GET` - получение данных (idempotent)
- `POST` - создание ресурса
- `PUT` - полное обновление (idempotent)
- `PATCH` - частичное обновление
- `DELETE` - удаление (idempotent)

### Статус коды
- `200` - успешно
- `201` - создано
- `204` - нет содержимого
- `400` - плохой запрос
- `401` - не авторизован
- `403` - запрещено
- `404` - не найдено
- `422` - ошибка валидации
- `500` - ошибка сервера

## Структура ответов

### Успешные ответы
```json
{
  "status": "ok",
  "data": {...},
  "message": "Optional success message"
}
```

### Ошибки
```json
{
  "status": "error",
  "message": "Human readable error message",
  "error_code": 400,
  "details": {
    "field": "validation error"
  }
}
```

### Пагинация
```json
{
  "status": "ok",
  "items": [...],
  "total": 100,
  "page": 1,
  "page_size": 20,
  "pages": 5
}
```

## Валидация

### Входные данные
```python
class UserCreate(BaseModel):
    email: str = Field(..., regex=r'^[^@]+@[^@]+\.[^@]+$')
    name: str = Field(..., min_length=2, max_length=100)
    age: int = Field(..., ge=0, le=150)
    
    @validator('email')
    def validate_email(cls, v):
        if User.objects.filter(email=v).exists():
            raise ValueError('Email already exists')
        return v
```

### Ошибки валидации
```python
try:
    user_data = UserCreate(**request_data)
except ValidationError as e:
    raise HTTPException(
        status_code=422,
        detail={
            "status": "error",
            "message": "Validation error",
            "details": e.errors()
        }
    )
```

## Версионирование

### URL Versioning
```python
# v1
@router.get("/api/v1/users")
async def get_users_v1():
    pass

# v2
@router.get("/api/v2/users")
async def get_users_v2():
    pass
```

### Header Versioning
```python
@router.get("/api/users")
async def get_users(version: str = Header("v1", alias="API-Version")):
    if version == "v1":
        return get_users_v1()
    elif version == "v2":
        return get_users_v2()
```

## Фильтрация и поиск

### Query параметры
```python
@router.get("/users")
async def get_users(
    page: int = 1,
    page_size: int = 20,
    search: Optional[str] = None,
    status: Optional[str] = None,
    created_after: Optional[datetime] = None
):
    # Фильтрация
    query = select(User)
    
    if search:
        query = query.where(User.name.contains(search))
    
    if status:
        query = query.where(User.status == status)
        
    if created_after:
        query = query.where(User.created_at >= created_after)
```

### Сортировка
```python
@router.get("/users")
async def get_users(
    sort_by: str = "created_at",
    sort_order: str = "desc"
):
    order_column = getattr(User, sort_by, User.created_at)
    
    if sort_order == "desc":
        order_column = order_column.desc()
    
    query = select(User).order_by(order_column)
```

## Аутентификация

### Bearer Token
```python
@router.get("/protected")
async def protected_endpoint(
    token: str = Depends(verify_bearer_token)
):
    return {"message": "Access granted"}
```

### Dependency Injection
```python
async def get_current_user(token: str = Depends(verify_bearer_token)):
    # Логика получения пользователя из токена
    return user

@router.get("/profile")
async def get_profile(user: User = Depends(get_current_user)):
    return user
```

## Загрузка файлов

### Один файл
```python
@router.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    # Валидация
    if file.size > MAX_FILE_SIZE:
        raise HTTPException(400, "File too large")
    
    # Сохранение
    with open(f"uploads/{file.filename}", "wb") as f:
        content = await file.read()
        f.write(content)
    
    return {"filename": file.filename}
```

### Несколько файлов
```python
@router.post("/upload-multiple")
async def upload_files(files: List[UploadFile] = File(...)):
    uploaded_files = []
    
    for file in files:
        # Обработка каждого файла
        uploaded_files.append(file.filename)
    
    return {"uploaded_files": uploaded_files}
```

## Rate Limiting

### По IP
```python
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)

@router.get("/api/users")
@limiter.limit("100/minute")
async def get_users(request: Request):
    pass
```

### По пользователю
```python
def get_user_id(request: Request):
    # Получить ID пользователя из токена
    return user_id

@router.get("/api/users")
@limiter.limit("1000/hour", key_func=get_user_id)
async def get_users(request: Request):
    pass
```

## Кеширование

### Response caching
```python
from fastapi_cache import cache

@router.get("/users")
@cache(expire=300)  # 5 минут
async def get_users():
    # Долгая операция
    return users
```

### Cache invalidation
```python
@router.post("/users")
async def create_user(user_data: UserCreate):
    user = await create_user_service(user_data)
    
    # Инвалидация кеша
    await cache.clear(pattern="users:*")
    
    return user
```

## Документация

### Swagger/OpenAPI
```python
@router.get(
    "/users/{user_id}",
    response_model=UserResponse,
    summary="Get user by ID",
    description="Retrieve a specific user by their unique identifier",
    responses={
        404: {"description": "User not found"},
        422: {"description": "Validation error"}
    }
)
async def get_user(
    user_id: UUID = Path(..., description="User unique identifier")
):
    pass
```

### Примеры
```python
class UserCreate(BaseModel):
    email: str = Field(..., example="user@example.com")
    name: str = Field(..., example="John Doe")
    
    class Config:
        schema_extra = {
            "example": {
                "email": "user@example.com",
                "name": "John Doe"
            }
        }
```

## Мониторинг

### Логирование
```python
@router.post("/users")
async def create_user(user_data: UserCreate):
    logger.info(f"Creating user: {user_data.email}")
    
    try:
        user = await create_user_service(user_data)
        logger.info(f"User created: {user.id}")
        return user
    except Exception as e:
        logger.error(f"Failed to create user: {e}")
        raise
```

### Метрики
```python
from prometheus_client import Counter, Histogram

REQUEST_COUNT = Counter('requests_total', 'Total requests')
REQUEST_LATENCY = Histogram('request_duration_seconds', 'Request latency')

@router.get("/users")
async def get_users():
    REQUEST_COUNT.inc()
    with REQUEST_LATENCY.time():
        return await get_users_service()
```

## Безопасность

### CORS
```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://example.com"],
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)
```

### Headers
```python
@router.get("/users")
async def get_users(response: Response):
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    return users
```

### Валидация входных данных
```python
class UserCreate(BaseModel):
    email: str = Field(..., regex=r'^[^@]+@[^@]+\.[^@]+$')
    name: str = Field(..., min_length=2, max_length=100)
    
    @validator('name')
    def validate_name(cls, v):
        if any(char in v for char in '<>'):
            raise ValueError('Name contains invalid characters')
        return v
```