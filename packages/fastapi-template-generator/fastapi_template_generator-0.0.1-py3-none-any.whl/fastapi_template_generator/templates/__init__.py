"""
Шаблоны файлов для генератора
"""

from .app import get_app_template
from .core import get_core_templates
from .middleware import get_middleware_templates
from .shared import get_shared_templates
from .modules import get_module_templates
from .configs import get_config_templates

__all__ = [
    "get_app_template",
    "get_core_templates", 
    "get_middleware_templates",
    "get_shared_templates",
    "get_module_templates",
    "get_config_templates",
]