"""
FOODIE (Food Intelligence Electrified)
AI Expert System for campus food delivery robots

ECE 479/579 Spring 2026 Final Project/Exam
"""

# *** imports

# ** core
from tiferet.builders import CLI

# ** app
from .builders import FoodieBuilder

# *** exports

__version__ = "0.1.0-dev"

# Public API (Tiferet style)
__all__ = [
    'CLI',
    'FoodieBuilder',
]