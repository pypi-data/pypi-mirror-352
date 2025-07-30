"""
Шаблоны конфигурационных файлов
"""

def get_config_templates() -> dict:
    return {
        "requirements.txt": '''# FastAPI и зависимости
fastapi==0.104.1
uvicorn[standard]==0.24.0
pydantic==2.5.0
pydantic-settings==2.1.0

# База данных
sqlalchemy==2.0.23
asyncpg==0.29.0
alembic==1.12.1

# Логирование
loguru==0.7.2

# Для загрузки файлов
python-multipart==0.0.6

# Для разработки
black==23.11.0
isort==5.12.0
flake8==6.1.0
pre-commit==3.5.0

# Для тестирования (опционально)
pytest==7.4.3
pytest-asyncio==0.21.1
httpx==0.25.2
''',
        
        ".env.example": '''# Основные настройки
APP_APP_NAME="FastAPI Template App"
APP_APP_VERSION="0.1.0"
APP_DEBUG=true

# База данных (компоненты)
APP_DB_HOST=localhost
APP_DB_PORT=5432
APP_DB_NAME=fastapi_db
APP_DB_USER=postgres
APP_DB_PASSWORD=postgres

# Безопасность  
APP_BEARER_TOKEN=your-super-secret-bearer-token-change-me

# CORS (для разработки можно оставить *)
APP_ALLOWED_ORIGINS=["http://localhost:3000", "http://localhost:8080"]

# Логирование
APP_LOG_LEVEL=INFO
APP_LOG_FILE=logs/app.log
''',
        
        ".gitignore": '''# Byte-compiled / optimized / DLL files
__pycache__/
*.py[cod]
*$py.class

# C extensions
*.so

# Distribution / packaging
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg

# PyInstaller
*.manifest
*.spec

# Installer logs
pip-log.txt
pip-delete-this-directory.txt

# Unit test / coverage reports
htmlcov/
.tox/
.coverage
.coverage.*
.cache
nosetests.xml
coverage.xml
*.cover
.hypothesis/
.pytest_cache/

# Translations
*.mo
*.pot

# Django stuff:
*.log
local_settings.py
db.sqlite3

# Flask stuff:
instance/
.webassets-cache

# Scrapy stuff:
.scrapy

# Sphinx documentation
docs/_build/

# PyBuilder
target/

# Jupyter Notebook
.ipynb_checkpoints

# pyenv
.python-version

# celery beat schedule file
celerybeat-schedule

# SageMath parsed files
*.sage.py

# Environments
.env
.venv
env/
venv/
ENV/
env.bak/
venv.bak/

# Spyder project settings
.spyderproject
.spyproject

# Rope project settings
.ropeproject

# mkdocs documentation
/site

# mypy
.mypy_cache/
.dmypy.json
dmypy.json

# IDE
.idea/
.vscode/
*.swp
*.swo
*~

# OS
.DS_Store
.DS_Store?
._*
.Spotlight-V100
.Trashes
ehthumbs.db
Thumbs.db

# Logs
logs/
*.log

# Database
*.db
*.sqlite3

# Temporary files
*.tmp
*.temp
''',
        
        "pyproject.toml": '''[build-system]
requires = ["setuptools>=45", "wheel"]
build-backend = "setuptools.build_meta"

[tool.black]
line-length = 88
target-version = ['py311']
include = '\\.pyi?$'

[tool.isort]
profile = "black"
line_length = 88
multi_line_output = 3
include_trailing_comma = true
force_grid_wrap = 0
use_parentheses = true
ensure_newline_before_comments = true

[tool.flake8]
max-line-length = 88
extend-ignore = ["E203", "E501", "W503"]
exclude = [
    ".git",
    "__pycache__",
    "docs/source/conf.py",
    "old",
    "build",
    "dist",
    ".venv",
    "venv",
    ".env"
]

[tool.pytest.ini_options]
testpaths = ["tests"]
python_files = "test_*.py"
python_functions = "test_*"
addopts = "-v --tb=short"
asyncio_mode = "auto"
''',
        
        "Makefile": '''# Makefile для удобной работы с проектом

.PHONY: help install run dev test lint format clean docker-up docker-down

help: ## Показать справку
\t@echo "Доступные команды:"
\t@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  \\033[36m%-15s\\033[0m %s\\n", $$1, $$2}'

install: ## Установить зависимости
\tpip install -r requirements.txt

run: ## Запустить сервер
\tuvicorn app:app --host 0.0.0.0 --port 8000

dev: ## Запустить в режиме разработки
\tuvicorn app:app --reload --host 0.0.0.0 --port 8000

test: ## Запустить тесты
\tpytest

lint: ## Проверить код линтерами
\tflake8 .
\tblack --check .
\tisort --check .

format: ## Автоформатирование кода  
\tblack .
\tisort .

clean: ## Очистить временные файлы
\tfind . -type d -name __pycache__ -exec rm -rf {} +
\tfind . -type f -name "*.pyc" -delete
\tfind . -type f -name "*.pyo" -delete
\tfind . -type f -name "*.pyd" -delete
\tfind . -type f -name ".coverage" -delete
\tfind . -type d -name "*.egg-info" -exec rm -rf {} +

docker-up: ## Запустить через Docker Compose
\tdocker-compose up -d

docker-down: ## Остановить Docker Compose
\tdocker-compose down

docker-logs: ## Посмотреть логи Docker
\tdocker-compose logs -f

docker-build: ## Пересобрать Docker образы
\tdocker-compose build

# Команды для работы с БД
db-check: ## Проверить подключение к БД
\tpython -c "import asyncio; from core.db import check_database_connection; asyncio.run(check_database_connection())"

db-init: ## Инициализировать БД (создать таблицы)
\tpython -c "import asyncio; from core.db import init_database; asyncio.run(init_database())"

db-reset: ## Пересоздать все таблицы (ОСТОРОЖНО!)
\tpython -c "import asyncio; from core.db import drop_tables, create_tables; asyncio.run(drop_tables()); asyncio.run(create_tables())"

db-url: ## Показать URL подключения к БД
\tpython -c "from core.settings import settings; print(settings.DATABASE_URL.replace(settings.DB_PASSWORD, '***'))"
''',
        
        "README.md": '''# FastAPI Project

Проект создан с помощью FastAPI Template Generator.

## Структура проекта

```
app/
├── app.py                 # Точка входа приложения
├── core/                  # Ядро приложения
│   ├── settings.py       # Настройки через pydantic-settings
│   ├── db.py            # Конфигурация базы данных
│   ├── logger.py        # Настройка логирования
│   └── dependencies.py  # Общие зависимости
├── middleware/           # Middleware компоненты
│   ├── error_handler.py # Обработка ошибок
│   ├── logging.py       # Логирование запросов
│   └── cors.py          # CORS настройки
├── shared/              # Общие компоненты
│   ├── schemas/         # Базовые схемы
│   └── models/          # Базовые модели
├── modules/             # Бизнес модули
│   └── echo/           # Пример модуля
├── utils/               # Утилиты
└── logs/                # Логи
```

## Установка и запуск

### Локально

```bash
# Установка зависимостей
python -m venv venv
source venv/bin/activate  # Windows: venv\\Scripts\\activate
pip install -r requirements.txt

# Настройка окружения
cp .env.example .env
# Отредактировать .env файл

# Запуск
uvicorn app:app --reload
```

### Docker

```bash
# Запуск с базой данных
docker-compose up -d

# Только приложение
docker build -t fastapi-app .
docker run -p 8000:8000 fastapi-app
```

## Использование

### API Документация

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

### Health Check

- Health endpoint: http://localhost:8000/health

### Примеры запросов

```bash
# Публичный эндпоинт
curl -X POST http://localhost:8000/api/echo/ \\
     -H "Content-Type: application/json" \\
     -d '{"message": "Hello World"}'

# Защищенный эндпоинт (требует Bearer токен)
curl -X POST http://localhost:8000/api/echo/protected \\
     -H "Content-Type: application/json" \\
     -H "Authorization: Bearer your-bearer-token" \\
     -d '{"message": "Protected Hello"}'
```

## Разработка

### Форматирование кода

```bash
make format  # Автоформатирование
make lint    # Проверка стиля
```

### Создание нового модуля

1. Создайте папку в `modules/`
2. Добавьте файлы: `router.py`, `schemas.py`, `services.py`, `models.py`
3. Подключите роутер в `app.py`

### Работа с базой данных

```bash
# Создать новую миграцию
make db-revision MSG="Описание изменений"

# Применить миграции
make db-upgrade

# Откатить миграции
make db-downgrade
```

## Настройки

Все настройки в файле `.env`:

- `APP_DATABASE_URL` - строка подключения к БД
- `APP_BEARER_TOKEN` - токен для защищенных эндпоинтов
- `APP_DEBUG` - режим отладки
- `APP_ALLOWED_ORIGINS` - разрешенные origins для CORS

## Логирование

Логи пишутся в:
- Консоль (для разработки)
- `logs/app.log` (все логи)
- `logs/app_errors.log` (только ошибки)

## Особенности

### Модульная архитектура

Каждый модуль содержит:
- `router.py` - API эндпоинты
- `schemas.py` - Pydantic модели
- `services.py` - бизнес-логика
- `models.py` - ORM модели
- `funcs.py` - вспомогательные функции

### Стандартные ответы

Все ответы в формате:
```json
{
  "status": "ok",
  "data": {...},
  "message": "Optional message"
}
```

### Базовые модели

Все модели БД наследуются от `BaseModel` и содержат:
- `id` (UUID)
- `created_at` 
- `updated_at`
- `deleted_at` (для soft delete)

### Middleware

- Обработка ошибок
- Логирование запросов
- CORS настройки
- Добавление заголовков ответа

## Безопасность

- Bearer токен для защищенных эндпоинтов
- Валидация всех входных данных
- CORS настройки
- Логирование подозрительной активности

## Производительность

- Async/await для всех операций
- Connection pooling для БД
- Оптимизированные запросы с пагинацией
- Кеширование (при необходимости)

## Мониторинг

- Health check эндпоинт
- Подробные логи
- Метрики времени обработки запросов
- Отслеживание ошибок
'''
    }