"""
LLM Context Builder - Export any project to a single text file optimized for LLM context
"""

__version__ = "1.0.0"
__author__ = "Tan Han Wei"
__email__ = "tanhanwei90@gmail.com"
__description__ = "Export any project to a single text file optimized for LLM context"

from .main import cli
from .project_detector import ProjectDetector
from .exporters.base_exporter import BaseExporter

__all__ = ['cli', 'ProjectDetector', 'BaseExporter']