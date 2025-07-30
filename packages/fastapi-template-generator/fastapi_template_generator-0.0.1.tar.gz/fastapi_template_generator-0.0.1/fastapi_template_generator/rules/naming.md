# Правила именования

## Общие правила

### Python PEP 8
- Переменные и функции: `snake_case`
- Классы: `CamelCase` 
- Константы: `UPPER_CASE`
- Модули: `lowercase`

### Файлы и папки
- Файлы: `snake_case.py`
- Папки: `snake_case`

## API Endpoints

### URL пути
- Множественное число: `/users`, `/posts`
- Kebab-case: `/user-profiles`
- Версионирование (если нужно): `/api/v1/users`

### HTTP методы
- `GET /users` - список пользователей
- `GET /users/{id}` - конкретный пользователь
- `POST /users` - создать пользователя
- `PUT /users/{id}` - обновить пользователя
- `DELETE /users/{id}` - удалить пользователя

### Параметры
- Path параметры: `{user_id}`
- Query параметры: `?page=1&limit=10`
- Body в POST/PUT запросах

## Базы данных

### Таблицы
- Множественное число: `users`, `posts`
- Snake_case: `user_profiles`

### Колонки
- Snake_case: `first_name`, `created_at`
- Булевы поля: `is_active`, `has_permission`

### Связи
- Foreign keys: `user_id`, `post_id`
- Many-to-many: `user_roles`

## Переменные окружения

### Префикс
Все переменные с префиксом `APP_`:
- `APP_DATABASE_URL`
- `APP_BEARER_TOKEN`
- `APP_DEBUG`

### Формат
- `UPPER_CASE`
- Описательные имена: `APP_MAX_UPLOAD_SIZE`

## Схемы Pydantic

### Модели
- Базовая модель: `UserBase`
- Создание: `UserCreate`
- Обновление: `UserUpdate`
- Ответ: `UserResponse`
- Список: `UserList`

### Поля
- Snake_case: `first_name`
- Описательные: `email_address`
- Булевы: `is_verified`

## Сервисы и функции

### Классы сервисов
- `UserService`
- `EmailService`
- `PaymentService`

### Методы
- Глаголы: `create_user`, `send_email`
- Async: `async def get_user`

### Функции
- Описательные: `validate_email`
- Вспомогательные: `format_phone_number`

## Исключения

### Классы
- Наследование от HTTPException
- Описательные имена: `UserNotFoundError`
- Модульные: `AuthenticationError`

### Сообщения
- Понятные пользователю: "User not found"
- Без технических деталей

## Константы

### Группировка
```python
# Статусы
STATUS_ACTIVE = "active"
STATUS_INACTIVE = "inactive"

# Роли
ROLE_ADMIN = "admin"
ROLE_USER = "user"

# Ограничения
MAX_FILE_SIZE = 10_000_000  # 10MB
MAX_USERNAME_LENGTH = 50
```

### Названия
- Описательные: `DEFAULT_PAGE_SIZE`
- Группированные: `EMAIL_TEMPLATES`

## Примеры

### Хорошо
```python
# Модель
class UserResponse(BaseModel):
    id: UUID
    email: str
    is_active: bool
    created_at: datetime

# Сервис
class UserService:
    async def get_user_by_id(self, db: AsyncSession, user_id: UUID) -> User:
        pass

# Endpoint
@router.get("/users/{user_id}", response_model=UserResponse)
async def get_user(user_id: UUID, db: AsyncSession = Depends(get_db)):
    pass
```

### Плохо
```python
# Модель
class userResp(BaseModel):
    ID: UUID
    Mail: str
    active: bool
    createdAt: datetime

# Сервис  
class userSvc:
    async def getUser(self, db: AsyncSession, id: UUID) -> User:
        pass

# Endpoint
@router.get("/user/{id}", response_model=userResp)
async def user(id: UUID, db: AsyncSession = Depends(get_db)):
    pass
```