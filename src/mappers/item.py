"""
FOODIE Item Mappers

Aggregate and YamlObject for the Item domain model.
Used for persistence of menu/inventory items and bagging rules (Goal B).
"""

# *** imports

# ** core
from typing import Any

# ** infra
from tiferet.mappers import Aggregate, TransferObject

# ** app
from ..domain import Item

# *** mappers

# ** mapper: item_aggregate
class ItemAggregate(Item, Aggregate):
    '''
    Aggregate for the Item domain object.

    Adds validated mutation methods while inheriting all domain behavior.
    '''

    # * method: update_quantity
    def update_quantity(self, new_quantity: int) -> None:
        '''
        Validated mutation: change item quantity.

        :param new_quantity: New quantity value.
        :type new_quantity: int
        '''
        self.set_attribute('quantity', new_quantity)

# ** mapper: item_yaml_object
class ItemYamlObject(Item, TransferObject):
    '''
    YamlObject for the Item domain object (YAML serialization).

    Flat model – standard serialization is sufficient.
    '''

    class Options:
        serialize_when_none = False
        roles = {
            'to_data.yaml': TransferObject.deny('id'),   # id is derived
            'to_model': TransferObject.allow(),
        }