# PromptTasker/__init__.py

from .cli import main as run_cli
from .backend import run_task

__version__ = "0.1.8"

__all__ = ["run_cli", "run_task"]

