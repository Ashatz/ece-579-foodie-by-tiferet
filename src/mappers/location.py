"""
FOODIE Location Mappers

Aggregate and YamlObject for the Location domain model.
Used for persistence of campus terrain graph nodes (Goal A).
"""

# *** imports

# ** core
from typing import Any, ClassVar, Dict

# ** infra
from tiferet.mappers import Aggregate, TransferObject

# ** app
from ..domain import Location

# *** mappers

# ** mapper: location_aggregate
class LocationAggregate(Location, Aggregate):
    '''
    Aggregate for the Location domain object.

    Adds validated mutation methods while inheriting all domain behavior.
    '''

    # * method: update_coordinates
    def update_coordinates(self, x: float, y: float) -> None:
        '''
        Validated mutation: change location coordinates.

        :param x: New X coordinate.
        :type x: float
        :param y: New Y coordinate.
        :type y: float
        '''

        self.set_attribute('x', x)
        self.set_attribute('y', y)


# ** mapper: location_yaml_object
class LocationYamlObject(Location, TransferObject):
    '''
    YamlObject for the Location domain object (YAML serialization).

    Flat model - standard serialization is sufficient.
    '''

    # * attribute: _ROLES
    _ROLES: ClassVar[Dict[str, Dict[str, Any]]] = {
        'to_model': {},
        'to_data.yaml': {'exclude': {'name'}},
    }

    # * method: map
    def map(self, target: type = None, **overrides) -> LocationAggregate:
        '''
        Map the YAML transfer object to a LocationAggregate.

        :param target: The aggregate class (defaults to LocationAggregate).
        :type target: type
        :param overrides: Additional keyword arguments.
        :type overrides: dict
        :return: A LocationAggregate instance.
        :rtype: LocationAggregate
        '''

        return super().map(
            target or LocationAggregate,
            **overrides,
        )

    # * method: from_data
    @classmethod
    def from_data(cls, data: dict, **overrides) -> 'LocationYamlObject':
        '''
        Create a LocationYamlObject from a raw YAML dict.

        :param data: The raw dict from YAML.
        :type data: dict
        :param overrides: Additional keyword arguments (e.g., name).
        :type overrides: dict
        :return: A LocationYamlObject instance.
        :rtype: LocationYamlObject
        '''

        data.update(overrides)
        return cls.model_validate(data)

    # * method: from_model
    @classmethod
    def from_model(cls, location: Location, **overrides) -> 'LocationYamlObject':
        '''
        Create a LocationYamlObject from a Location model.

        :param location: The source Location instance.
        :type location: Location
        :param overrides: Additional keyword arguments.
        :type overrides: dict
        :return: A LocationYamlObject instance.
        :rtype: LocationYamlObject
        '''

        return super().from_model(location, **overrides)
