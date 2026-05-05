"""
FOODIE Mappers

Aggregates (mutation) and TransferObjects (serialization) for domain persistence.
"""

# *** imports

# ** app
from .order import OrderAggregate, OrderSqlObject
from .robot import RobotAggregate, RobotSqlObject

# *** exports

__all__ = [
    'OrderAggregate',
    'OrderSqlObject',
    'RobotAggregate',
    'RobotSqlObject',
]
