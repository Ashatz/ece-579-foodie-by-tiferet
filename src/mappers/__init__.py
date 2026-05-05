"""
FOODIE Mappers

Aggregates (mutation) and TransferObjects (serialization) for domain persistence.
"""

# *** imports

# ** app
from .location import LocationAggregate, LocationYamlObject
from .order import OrderAggregate, OrderSqlObject
from .robot import RobotAggregate, RobotSqlObject

# *** exports

__all__ = [
    'LocationAggregate',
    'LocationYamlObject',
    'OrderAggregate',
    'OrderSqlObject',
    'RobotAggregate',
    'RobotSqlObject',
]
