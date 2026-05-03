"""
FOODIE Beverage Mappers

Aggregate and YamlObject for the Beverage domain model.
Used for persistence of the backward-chaining knowledge base (Goal C).
"""

# *** imports

# ** core
from typing import Any

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

    Flat model – standard serialization is sufficient.
    '''

    class Options:
        serialize_when_none = False
        roles = {
            'to_data.yaml': TransferObject.deny('id'),   # id is derived
            'to_model': TransferObject.allow(),
        }