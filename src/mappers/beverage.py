"""
FOODIE Beverage Mappers

Aggregate and YamlObject for the Beverage domain model.
Used for persistence of the backward-chaining knowledge base (Goal C).
"""

# *** imports

# ** core
from typing import Any, ClassVar, Dict

# ** infra
from tiferet.mappers import Aggregate, TransferObject

# ** app
from ..domain import Beverage

# *** mappers

# ** mapper: beverage_aggregate
class BeverageAggregate(Beverage, Aggregate):
    '''
    Aggregate for the Beverage domain object.

    Adds validated mutation methods while inheriting all domain behavior.
    '''

    # * method: update_allergens
    def update_allergens(self, new_allergens: str) -> None:
        '''
        Validated mutation: update the list of avoided allergens.

        :param new_allergens: Comma-separated list of allergens.
        :type new_allergens: str
        '''

        self.set_attribute('avoids_allergens', new_allergens)


# ** mapper: beverage_yaml_object
class BeverageYamlObject(Beverage, TransferObject):
    '''
    YamlObject for the Beverage domain object (YAML serialization).

    Flat model - standard serialization is sufficient.
    '''

    # * attribute: _ROLES
    _ROLES: ClassVar[Dict[str, Dict[str, Any]]] = {
        'to_model': {},
        'to_data.yaml': {'exclude': {'name'}},
    }

    # * method: map
    def map(self, target: type = None, **overrides) -> BeverageAggregate:
        '''
        Map the YAML transfer object to a BeverageAggregate.

        :param target: The aggregate class (defaults to BeverageAggregate).
        :type target: type
        :param overrides: Additional keyword arguments.
        :type overrides: dict
        :return: A BeverageAggregate instance.
        :rtype: BeverageAggregate
        '''

        return super().map(
            target or BeverageAggregate,
            **overrides,
        )

    # * method: from_data
    @classmethod
    def from_data(cls, data: dict, **overrides) -> 'BeverageYamlObject':
        '''
        Create a BeverageYamlObject from a raw YAML dict.

        :param data: The raw dict from YAML.
        :type data: dict
        :param overrides: Additional keyword arguments (e.g., name).
        :type overrides: dict
        :return: A BeverageYamlObject instance.
        :rtype: BeverageYamlObject
        '''

        data.update(overrides)
        return cls.model_validate(data)

    # * method: from_model
    @classmethod
    def from_model(cls, beverage: Beverage, **overrides) -> 'BeverageYamlObject':
        '''
        Create a BeverageYamlObject from a Beverage model.

        :param beverage: The source Beverage instance.
        :type beverage: Beverage
        :param overrides: Additional keyword arguments.
        :type overrides: dict
        :return: A BeverageYamlObject instance.
        :rtype: BeverageYamlObject
        '''

        return super().from_model(beverage, **overrides)
