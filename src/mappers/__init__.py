"""
FOODIE Mappers

Aggregates (mutation) and TransferObjects (serialization) for domain persistence.
"""

# *** imports

# ** app
from .bag import BagAggregate
from .beverage import BeverageAggregate, BeverageYamlObject
from .item import ItemAggregate, ItemYamlObject
from .location import LocationAggregate, LocationYamlObject
from .order import OrderAggregate, OrderSqlObject
from .robot import RobotAggregate, RobotSqlObject

# *** exports

__all__ = [
    'BagAggregate',
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
