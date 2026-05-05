"""
FOODIE Mappers

Aggregates (mutation) and TransferObjects (serialization) for domain persistence.
"""

# *** imports

# ** app
from .beverage import BeverageAggregate, BeverageYamlObject
from .item import ItemAggregate, ItemYamlObject
from .location import LocationAggregate, LocationYamlObject
from .order import OrderAggregate, OrderSqlObject
from .robot import RobotAggregate, RobotSqlObject

# *** exports

__all__ = [
    'BeverageAggregate',
    'BeverageYamlObject',
    'ItemAggregate',
    'ItemYamlObject',
    'LocationAggregate',
    'LocationYamlObject',
    'OrderAggregate',
    'OrderSqlObject',
    'RobotAggregate',
    'RobotSqlObject',
]
