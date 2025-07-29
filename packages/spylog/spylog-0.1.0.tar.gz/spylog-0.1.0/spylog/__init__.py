"""
Spylog - Python Validator Proxy

Waliduje pliki Python przed uruchomieniem i przekazuje wykonanie
do oryginalnego interpretera Python.
"""

__version__ = "0.1.0"
__author__ = "Spylog Team"
__email__ = "spylog@example.com"
__description__ = "Python Validator Proxy - waliduje pliki Python przed uruchomieniem"

from .main import main
from .validator import validate_python_file
from .config import SpylogConfig

__all__ = ["main", "validate_python_file", "SpylogConfig"]
