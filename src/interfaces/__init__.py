"""
FOODIE Service Interfaces

Abstract service contracts for domain-specific data access.
"""

# *** imports

# ** app
from .order import OrderService
from .robot import RobotService

# *** exports

__all__ = [
    'OrderService',
    'RobotService',
]
