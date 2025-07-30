"""
CLI интерфейс для генератора
"""

import argparse
from .generator import FastAPIGenerator


def main():
    """Основная функция CLI"""
    parser = argparse.ArgumentParser(
        description="FastAPI Template Generator - создает структуру FastAPI проекта"
    )
    
    parser.add_argument(
        "project_name",
        nargs="?",
        default="app",
        help="Название проекта (по умолчанию: app)"
    )
    
    parser.add_argument(
        "--no-docker",
        action="store_true",
        help="Не создавать Docker файлы"
    )
    
    parser.add_argument(
        "-v", "--version",
        action="version",
        version="%(prog)s 0.1.0"
    )

    parser.add_argument(
    "--check-db",
    action="store_true",
    help="Добавить команды для проверки БД в Makefile"
    )
    
    args = parser.parse_args()
    
    # Создание генератора
    generator = FastAPIGenerator(
        project_name=args.project_name,
        with_docker=not args.no_docker,
        # check_db=args.check_db
    )
    
    # Генерация
    generator.generate()


if __name__ == "__main__":
    main()