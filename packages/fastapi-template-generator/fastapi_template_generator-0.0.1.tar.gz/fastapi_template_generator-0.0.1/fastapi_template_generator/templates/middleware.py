"""
Шаблоны middleware
"""

def get_middleware_templates() -> dict:
    return {
        "__init__.py": "",
        
        "error_handler.py": '''"""
Глобальный обработчик ошибок
Ловит все необработанные исключения и возвращает красивый ответ
"""

from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
from loguru import logger

from core.settings import settings


async def error_handler_middleware(request: Request, call_next):
    """Middleware для обработки всех ошибок"""
    try:
        response = await call_next(request)
        return response
    
    except HTTPException as e:
        # FastAPI исключения
        logger.warning(f"HTTP Exception: {e.status_code} - {e.detail}")
        return JSONResponse(
            status_code=e.status_code,
            content={
                "status": "error",
                "message": e.detail,
                "error_code": e.status_code
            }
        )
    
    except Exception as e:
        # Все остальные ошибки
        logger.error(f"Unhandled error: {str(e)}", exc_info=True)
        
        # Детальная информация только в debug режиме
        error_detail = {
            "status": "error",
            "message": "Internal server error",
            "error_code": 500
        }
        
        if settings.DEBUG:
            error_detail["details"] = str(e)
            error_detail["type"] = type(e).__name__
        
        return JSONResponse(
            status_code=500,
            content=error_detail
        )
''',
        
        "logging.py": '''"""
Middleware для логирования запросов
Записывает все входящие запросы и исходящие ответы
"""

import time
from fastapi import Request
from loguru import logger


async def logging_middleware(request: Request, call_next):
    """Middleware для логирования всех запросов"""
    start_time = time.time()
    
    # Получаем IP адрес клиента
    client_ip = request.client.host if request.client else "unknown"
    
    # Логируем входящий запрос
    logger.info(
        f"→ {request.method} {request.url.path} "
        f"from {client_ip} "
        f"User-Agent: {request.headers.get('user-agent', 'unknown')}"
    )
    
    # Обрабатываем запрос
    response = await call_next(request)
    
    # Время обработки
    process_time = time.time() - start_time
    
    # Логируем ответ
    log_level = "info"
    if response.status_code >= 400:
        log_level = "warning"
    if response.status_code >= 500:
        log_level = "error"
    
    getattr(logger, log_level)(
        f"← {request.method} {request.url.path} "
        f"→ {response.status_code} "
        f"in {process_time:.3f}s"
    )
    
    # Добавляем заголовки ответа
    response.headers["X-Process-Time"] = str(process_time)
    response.headers["X-Request-ID"] = str(id(request))  # Простой ID запроса
    
    return response
''',
        
        "cors.py": '''"""
Настройки CORS для разработки и продакшена
"""

from fastapi.middleware.cors import CORSMiddleware
from core.settings import settings


def get_cors_middleware():
    """Возвращает настроенный CORS middleware"""
    return CORSMiddleware(
        allow_origins=settings.ALLOWED_ORIGINS,
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH"],
        allow_headers=["*"],
        expose_headers=["X-Process-Time", "X-Request-ID"],
    )
''',
    }