"""
FOODIE Contexts Subpackage

Runtime orchestration layer for the Food Intelligence Electrified expert system
(ECE 479/579 Spring 2026 Final Project/Exam).

High-level FoodieContext coordinates low-level contexts for all three project goals.
"""

# *** imports

# ** app
from .foodie import FoodieContext
from .bagger import BaggerContext
from .route_planner import RoutePlannerContext
from .beverage import BeverageContext

# *** exports

__all__ = [
    'FoodieContext',
    'BaggerContext',
    'RoutePlannerContext',
    'BeverageContext',
]