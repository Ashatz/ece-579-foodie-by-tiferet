"""
FOODIE Service Interfaces

Abstract service contracts for domain-specific data access.
"""

# *** imports

# ** app
from .location import LocationService
from .order import OrderService
from .robot import RobotService

# *** exports

__all__ = [
    'LocationService',
    'OrderService',
    'RobotService',
]
