# FastAPI Template Generator

🚀 Генератор структуры FastAPI приложений с лучшими практиками разработки.

Создает готовую к продакшену архитектуру с модульной структурой, документацией и всеми необходимыми компонентами.

## Быстрый старт

### Установка

```bash
pip install fastapi-template-generator
```

### Создание проекта

```bash
# Создать проект с указанным именем
python -m fastapi_template_generator my_awesome_api

# Создать проект с именем по умолчанию (app)
python -m fastapi_template_generator

# Создать проект без Docker файлов
python -m fastapi_template_generator my_project --no-docker
```

### Запуск созданного проекта

```bash
cd my_awesome_api

# Создать виртуальное окружение
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Установить зависимости
pip install -r requirements.txt

# Настроить переменные окружения
cp .env.example .env
# Отредактируйте .env файл под ваши нужды

# Запустить приложение
uvicorn app:app --reload
```

🎉 Готово! Ваше API доступно по адресу http://localhost:8000

## Что создается

### Структура проекта

```
my_awesome_api/
├── app.py                 # Точка входа приложения
├── core/                  # Ядро приложения
│   ├── settings.py       # Настройки через pydantic-settings
│   ├── db.py            # Конфигурация базы данных + инициализация
│   ├── logger.py        # Настройка логирования (Loguru)
│   └── dependencies.py  # Общие зависимости (БД, авторизация)
├── middleware/           # Middleware компоненты
│   ├── error_handler.py # Глобальная обработка ошибок
│   ├── logging.py       # Логирование всех запросов
│   └── cors.py          # CORS настройки
├── shared/              # Общие компоненты
│   ├── schemas/         # Базовые схемы (ResponseModel, Pagination)
│   └── models/          # Базовые модели для наследования
├── modules/             # Бизнес модули
│   └── echo/           # Готовый пример модуля
│       ├── router.py    # API эндпоинты
│       ├── schemas.py   # Pydantic модели
│       ├── services.py  # Бизнес-логика
│       ├── models.py    # ORM модели
│       ├── funcs.py     # Вспомогательные функции
│       ├── constants.py # Константы
│       └── exceptions.py # Исключения модуля
├── utils/               # Общие утилиты
├── rules/               # 📚 Документация и best practices
├── logs/                # Папка для логов
├── requirements.txt     # Зависимости Python
├── .env.example        # Пример настроек окружения
├── .gitignore          # Git исключения
├── pyproject.toml      # Настройки форматирования (Black, isort)
├── Makefile            # Команды для разработки
├── Dockerfile          # Docker образ
├── docker-compose.yml  # Docker Compose с PostgreSQL
└── README.md           # Документация проекта
```

### Готовые возможности

✅ **Async/await из коробки** - все операции асинхронные  
✅ **PostgreSQL + SQLAlchemy** - настроенная база данных  
✅ **Модульная архитектура** - легко масштабируемая структура  
✅ **Автоматическая инициализация БД** - таблицы создаются при запуске  
✅ **Bearer токен авторизация** - защита эндпоинтов  
✅ **Логирование Loguru** - красивые структурированные логи  
✅ **Middleware для обработки ошибок** - сервер не падает  
✅ **Валидация Pydantic** - типизированные схемы  
✅ **Soft delete** - безопасное удаление записей  
✅ **Пагинация** - готовые схемы для списков  
✅ **Health check** - мониторинг состояния  
✅ **Docker поддержка** - контейнеризация  
✅ **Форматирование кода** - Black + isort + flake8  
✅ **Документация API** - автогенерируемая Swagger  
✅ **Best practices** - правила разработки в `rules/`

## Использование созданного проекта

### API Документация

После запуска доступна по адресам:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **Health Check**: http://localhost:8000/health

### Примеры запросов

```bash
# Публичный эндпоинт
curl -X POST http://localhost:8000/api/echo/ \
     -H "Content-Type: application/json" \
     -d '{"message": "Hello World", "category": "test"}'

# Защищенный эндпоинт (требует Bearer токен)
curl -X POST http://localhost:8000/api/echo/protected \
     -H "Content-Type: application/json" \
     -H "Authorization: Bearer your-bearer-token-from-env" \
     -d '{"message": "Protected Hello", "category": "important"}'

# Получить список всех записей
curl http://localhost:8000/api/echo/?page=1&page_size=10
```

### Настройка окружения

Все настройки в файле `.env`:

```bash
# Основные настройки
APP_APP_NAME="My Awesome API"
APP_DEBUG=true

# База данных (отдельные компоненты)
APP_DB_HOST=localhost
APP_DB_PORT=5432
APP_DB_NAME=my_api_db
APP_DB_USER=postgres
APP_DB_PASSWORD=secretpassword

# Безопасность
APP_BEARER_TOKEN=your-super-secret-bearer-token

# CORS
APP_ALLOWED_ORIGINS=["http://localhost:3000", "http://localhost:8080"]
```

## Разработка

### Полезные команды

```bash
# Форматирование и проверка кода
make format  # Автоформатирование (Black + isort)
make lint    # Проверка стиля (flake8)

# Запуск
make dev     # Запуск в режиме разработки
make run     # Запуск в продакшен режиме

# Работа с базой данных
make db-check    # Проверить подключение к БД
make db-init     # Инициализировать БД
make db-url      # Показать URL подключения

# Docker
make docker-up   # Запустить через Docker Compose
make docker-down # Остановить Docker Compose
```

### Создание нового модуля

1. Создайте папку в `modules/my_module/`
2. Скопируйте структуру из `modules/echo/`
3. Адаптируйте под свою логику
4. Подключите роутер в `app.py`:

```python
from modules.my_module.router import router as my_module_router

app.include_router(my_module_router, prefix="/api/my-module", tags=["my-module"])
```

### Docker развертывание

```bash
# Запуск с PostgreSQL
docker-compose up -d

# Или только приложение
docker build -t my-api .
docker run -p 8000:8000 my-api
```

## Архитектура

### Принципы

- **Модульность**: каждая функция в отдельном модуле
- **Слоистость**: API → Service → Repository → Database
- **DRY**: общий код в `shared/` и `utils/`
- **Типизация**: Pydantic схемы для всех данных
- **Асинхронность**: async/await везде

### Структура модуля

```python
# router.py - API эндпоинты
@router.get("/items", response_model=PaginatedResponse[ItemResponse])
async def get_items(pagination: PaginationParams = Depends()):
    pass

# schemas.py - Pydantic модели
class ItemCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)

# services.py - бизнес-логика
class ItemService:
    async def create_item(self, db: AsyncSession, data: ItemCreate):
        pass

# models.py - ORM модели
class Item(BaseModel):  # Наследуется от BaseModel с id, created_at, etc.
    __tablename__ = "items"
    name = Column(String(100), nullable=False)
```

### Стандартные ответы

Все API ответы в едином формате:

```json
{
  "status": "ok",
  "data": {...},
  "message": "Optional success message"
}
```

Ошибки:

```json
{
  "status": "error",
  "message": "Human readable error",
  "error_code": 400,
  "details": {...}
}
```

## Безопасность

- **Bearer токен** для защищенных эндпоинтов
- **Валидация входных данных** через Pydantic
- **CORS настройки** для фронтенда
- **SQL инъекции** защищены ORM
- **Логирование подозрительной активности**

## Мониторинг

- **Health check** эндпоинт с проверкой БД
- **Структурированные логи** (консоль + файлы)
- **Метрики времени обработки** в заголовках ответов
- **Отслеживание ошибок** с stack trace

## Производительность

- **Async/await** для всех операций
- **Connection pooling** для БД
- **Пагинация** для больших списков
- **Оптимизированные запросы** с proper indexing
- **Мягкое удаление** вместо физического

## Документация

Созданный проект содержит папку `rules/` с подробными правилами:

- `architecture.md` - Принципы архитектуры
- `naming.md` - Правила именования
- `database.md` - Работа с БД
- `api_design.md` - Дизайн API

## Опции генератора

```bash
# Справка
python -m fastapi_template_generator --help

# Создать без Docker файлов
python -m fastapi_template_generator my_project --no-docker

# Показать версию
python -m fastapi_template_generator --version
```

## Примеры использования

### Стартап MVP

```bash
python -m fastapi_template_generator my_startup_api
cd my_startup_api
# Настроить .env
make dev
```

### Корпоративный проект

```bash
python -m fastapi_template_generator corporate_api
cd corporate_api
# Настроить production окружение
docker-compose up -d
```

### Микросервис

```bash
python -m fastapi_template_generator user_service --no-docker
cd user_service
# Интегрировать в существующую инфраструктуру
```

## Совместимость

- **Python**: 3.8+
- **FastAPI**: 0.104+
- **SQLAlchemy**: 2.0+
- **PostgreSQL**: 12+
- **Docker**: 20+

## Вклад в проект

Приветствуются:
- Новые шаблоны модулей
- Улучшения архитектуры
- Дополнения в документацию
- Исправления багов

## Лицензия

MIT License - используйте свободно в коммерческих и открытых проектах.

---

**Создавайте качественные FastAPI приложения быстро и с удовольствием!** 🚀

**GitHub**: https://github.com/daswer123/fastapi-template-generator  
**PyPI**: https://pypi.org/project/fastapi-template-generator/
