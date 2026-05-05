"""
FOODIE Item Mappers

Aggregate and YamlObject for the Item domain model.
Used for persistence of menu/inventory items and bagging rules (Goal B).
"""

# *** imports

# ** core
from typing import Any, ClassVar, Dict

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

    Flat model - standard serialization is sufficient.
    '''

    # * attribute: _ROLES
    _ROLES: ClassVar[Dict[str, Dict[str, Any]]] = {
        'to_model': {},
        'to_data.yaml': {'exclude': {'name'}},
    }

    # * method: map
    def map(self, target: type = None, **overrides) -> ItemAggregate:
        '''
        Map the YAML transfer object to an ItemAggregate.

        :param target: The aggregate class (defaults to ItemAggregate).
        :type target: type
        :param overrides: Additional keyword arguments.
        :type overrides: dict
        :return: An ItemAggregate instance.
        :rtype: ItemAggregate
        '''

        return super().map(
            target or ItemAggregate,
            **overrides,
        )

    # * method: from_data
    @classmethod
    def from_data(cls, data: dict, **overrides) -> 'ItemYamlObject':
        '''
        Create an ItemYamlObject from a raw YAML dict.

        :param data: The raw dict from YAML.
        :type data: dict
        :param overrides: Additional keyword arguments (e.g., name).
        :type overrides: dict
        :return: An ItemYamlObject instance.
        :rtype: ItemYamlObject
        '''

        data.update(overrides)
        return cls.model_validate(data)

    # * method: from_model
    @classmethod
    def from_model(cls, item: Item, **overrides) -> 'ItemYamlObject':
        '''
        Create an ItemYamlObject from an Item model.

        :param item: The source Item instance.
        :type item: Item
        :param overrides: Additional keyword arguments.
        :type overrides: dict
        :return: An ItemYamlObject instance.
        :rtype: ItemYamlObject
        '''

        return super().from_model(item, **overrides)
