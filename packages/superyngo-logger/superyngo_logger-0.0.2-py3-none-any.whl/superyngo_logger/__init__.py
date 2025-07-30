"""
Superyngo Logger - A simple and efficient logging utility for Python applications.

This package provides an easy-to-use logging solution with file rotation,
custom formatting, and log cleanup capabilities.
"""

from .logger_module import clean_logs, init_logger

__version__ = "0.0.2"
__author__ = "Wenyang"
__email__ = "superyngo@gmail.com"

__all__ = ["init_logger", "clean_logs", "__version__"]
