"""
Promptplex - A Python library for mastering AI prompts with versioning, templating, and testing.
"""

from .core import PromptManager, PromptTemplate, PromptTester, setup_builtin_templates

__version__ = "0.1.0"
__author__ = "Ejiga Peter Ojonugwa Oluwafemi"
__email__ = "ejigsonpeter@gmail.com"

__all__ = [
    "PromptManager",
    "PromptTemplate", 
    "PromptTester",
    "setup_builtin_templates"
]