"""
FOODIE Mappers Subpackage

Hybrid persistence:
- Universal/config data (Items, Beverages) → YamlObject
- Instance-specific runtime data → SqlObject
"""

# *** imports

# ** app
from .item import ItemAggregate, ItemYamlObject
from .order import OrderAggregate, OrderSqlObject
from .bag import BagAggregate, BagSqlObject
from .location import LocationAggregate, LocationSqlObject
from .robot import RobotAggregate, RobotSqlObject
from .beverage import BeverageAggregate, BeverageYamlObject

# *** exports

__all__ = [
    'ItemAggregate',
    'ItemYamlObject',
    'OrderAggregate',
    'OrderSqlObject',
    'BagAggregate',
    'BagSqlObject',
    'LocationAggregate',
    'LocationSqlObject',
    'RobotAggregate',
    'RobotSqlObject',
    'BeverageAggregate',
    'BeverageYamlObject',
]