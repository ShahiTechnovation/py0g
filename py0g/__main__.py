"""
py0g CLI entry point for module execution.

Allows running py0g as a module: python -m py0g
"""

from .cli import app

if __name__ == "__main__":
    app()