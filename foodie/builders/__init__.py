"""
FOODIE Builders Subpackage

Contains all high-level builders for the Food Intelligence Electrified
expert system (ECE 479/579 Spring 2026 Final Project).

This subpackage follows Tiferet’s structured code style and exports the
public builder(s) for easy access from the root package.
"""

# *** imports

# ** app
from .foodie import FoodieBuilder

# *** exports

__all__ = [
    'FoodieBuilder',
]