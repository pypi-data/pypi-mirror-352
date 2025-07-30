"""
Основной класс генератора
"""

import os
import sys
from pathlib import Path
from typing import Dict, Any

from .templates import (
    get_app_template,
    get_core_templates,
    get_middleware_templates,
    get_shared_templates,
    get_module_templates,
    get_config_templates,
)


class FastAPIGenerator:
    """Генератор структуры FastAPI проекта"""
    
    # Цвета для вывода
    COLORS = {
        'green': '\033[92m',
        'blue': '\033[94m',
        'yellow': '\033[93m',
        'red': '\033[91m',
        'end': '\033[0m'
    }
    
    def __init__(self, project_name: str = "app", with_docker: bool = True):
        self.project_name = project_name
        self.base_path = Path(project_name)
        self.with_docker = with_docker
        
    def _print_colored(self, message: str, color: str = 'green') -> None:
        """Цветной вывод в консоль"""
        print(f"{self.COLORS.get(color, '')}{message}{self.COLORS['end']}")
    
    def create_directory(self, path: Path) -> None:
        """Создает директорию"""
        path.mkdir(parents=True, exist_ok=True)
        self._print_colored(f"✓ Создана папка: {path}", 'green')
    
    def create_file(self, path: Path, content: str) -> None:
        """Создает файл с содержимым"""
        # Убедимся что папка существует
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding='utf-8')
        self._print_colored(f"✓ Создан файл: {path}", 'blue')

    def _copy_rules(self) -> None:
        """Копирует rules в проект"""
        rules_src = Path(__file__).parent / "rules"
        rules_dst = self.base_path / "rules"
        
        self.create_directory(rules_dst)
        
        # Копируем все .md файлы
        for rule_file in rules_src.glob("*.md"):
            content = rule_file.read_text(encoding='utf-8')
            self.create_file(rules_dst / rule_file.name, content)
        
        # Создаем README.md для rules
        rules_readme = '''# Правила и архитектура проекта

Эта папка содержит документацию по архитектуре и правилам проекта:

- `architecture.md` - Принципы архитектуры и структура модулей
- `naming.md` - Правила именования файлов, классов, переменных
- `database.md` - Работа с базой данных, модели, миграции  
- `api_design.md` - Дизайн API, REST принципы, валидация

## Важно

Следуйте этим правилам для поддержания качества и консистентности кода.
При добавлении новых разработчиков - изучите эти документы.
'''
        self.create_file(rules_dst / "README.md", rules_readme)
    
    def generate(self) -> None:
        """Генерирует всю структуру проекта"""
        self._print_colored(f"\n🚀 Создаем FastAPI проект '{self.project_name}'...\n", 'yellow')
        
        # Проверка существования
        if self.base_path.exists():
            self._print_colored(f"Ошибка: Папка '{self.project_name}' уже существует!", 'red')
            sys.exit(1)
        
        # Создание структуры
        self._create_base_structure()
        self._create_core()
        self._create_middleware()
        self._create_shared()
        self._create_modules()
        self._create_utils()
        self._create_configs()
        
        if self.with_docker:
            self._create_docker_files()
        
        
        self._copy_rules()
        self._print_success_message()
    
    def _create_base_structure(self) -> None:
        """Создает базовую структуру"""
        self.create_directory(self.base_path)
        self.create_file(self.base_path / "app.py", get_app_template())
        self.create_file(self.base_path / "__init__.py", "")
        self.create_directory(self.base_path / "logs")
    
    def _create_core(self) -> None:
        """Создает core модуль"""
        core_path = self.base_path / "core"
        self.create_directory(core_path)
        
        templates = get_core_templates()
        for filename, content in templates.items():
            self.create_file(core_path / filename, content)
    
    def _create_middleware(self) -> None:
        """Создает middleware"""
        middleware_path = self.base_path / "middleware"
        self.create_directory(middleware_path)
        
        templates = get_middleware_templates()
        for filename, content in templates.items():
            self.create_file(middleware_path / filename, content)
    
    def _create_shared(self) -> None:
        """Создает shared модули"""
        shared_path = self.base_path / "shared"
        schemas_path = shared_path / "schemas"
        models_path = shared_path / "models"
        
        self.create_directory(schemas_path)
        self.create_directory(models_path)
        
        templates = get_shared_templates()
        for filepath, content in templates.items():
            self.create_file(shared_path / filepath, content)
    
    def _create_modules(self) -> None:
        """Создает пример модуля"""
        modules_path = self.base_path / "modules"
        echo_path = modules_path / "echo"
        
        self.create_directory(echo_path)
        self.create_file(modules_path / "__init__.py", "")
        
        templates = get_module_templates("echo")
        for filename, content in templates.items():
            self.create_file(echo_path / filename, content)
    
    def _create_utils(self) -> None:
        """Создает utils папку"""
        utils_path = self.base_path / "utils"
        self.create_directory(utils_path)
        self.create_file(utils_path / "__init__.py", "")
        self.create_file(
            utils_path / "helpers.py",
            '"""Вспомогательные функции"""\n\n# Здесь будут общие хелперы'
        )
    
    def _create_configs(self) -> None:
        """Создает конфигурационные файлы"""
        configs = get_config_templates()
        for filename, content in configs.items():
            self.create_file(self.base_path / filename, content)
    
    def _create_docker_files(self) -> None:
        """Создает Docker файлы"""
        dockerfile_content = '''FROM python:3.11-slim

WORKDIR /app

# Установка зависимостей системы
RUN apt-get update && apt-get install -y \\
    gcc \\
    && rm -rf /var/lib/apt/lists/*

# Копирование зависимостей
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Копирование приложения
COPY . .

# Создание пользователя
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

# Запуск
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]
'''
        self.create_file(self.base_path / "Dockerfile", dockerfile_content)
        
        dockerignore_content = '''__pycache__
*.pyc
*.pyo
*.pyd
.Python
env/
venv/
.venv/
pip-log.txt
pip-delete-this-directory.txt
.tox/
.coverage
.coverage.*
.cache
nosetests.xml
coverage.xml
*.cover
*.log
.git
.gitignore
.mypy_cache
.pytest_cache
.hypothesis
.env
.env.*
!.env.example
'''
        self.create_file(self.base_path / ".dockerignore", dockerignore_content)
        
        docker_compose_content = '''version: '3.8'

services:
  app:
    build: .
    ports:
      - "8000:8000"
    environment:
      - APP_DATABASE_URL=postgresql+asyncpg://postgres:postgres@db:5432/fastapi_db
    env_file:
      - .env
    depends_on:
      - db
    volumes:
      - ./logs:/app/logs

  db:
    image: postgres:15-alpine
    environment:
      - POSTGRES_USER=postgres
      - POSTGRES_PASSWORD=postgres
      - POSTGRES_DB=fastapi_db
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"

volumes:
  postgres_data:
'''
        self.create_file(self.base_path / "docker-compose.yml", docker_compose_content)
    
    def _print_success_message(self) -> None:
        """Выводит сообщение об успешном создании"""
        self._print_colored(f"\n✨ Проект '{self.project_name}' успешно создан!", 'green')
        self._print_colored("\nДальнейшие шаги:", 'yellow')
        
        steps = [
            f"cd {self.project_name}",
            "python -m venv venv",
            "source venv/bin/activate  # или venv\\Scripts\\activate на Windows",
            "pip install -r requirements.txt",
            "cp .env.example .env",
            "# Настрой переменные в .env файле",
        ]
        
        if self.with_docker:
            steps.extend([
                "\n# Или используй Docker:",
                "docker-compose up -d db  # Запуск БД",
                "docker-compose up app    # Запуск приложения"
            ])
        else:
            steps.append("uvicorn app:app --reload")
        
        for step in steps:
            print(f"  {step}")
        
        self._print_colored(f"\n📚 Документация и правила в папке {self.project_name}/rules/", 'blue')