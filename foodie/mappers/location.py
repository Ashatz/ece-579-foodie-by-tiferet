"""
FOODIE Location Mappers

Aggregate and SqlObject for the Location domain model.
Used for campus terrain graph and route planning (Goal A).
"""

# *** imports

# ** core
from typing import Any

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

# ** mapper: location_sql_object
class LocationSqlObject(Location, TransferObject):
    '''
    SqlObject for the Location domain object (SQLite serialization).

    No nested objects, so standard serialization is sufficient.
    '''

    class Options:
        serialize_when_none = False
        roles = {
            'to_data.sqlite': TransferObject.deny('id'),   # id is derived
            'to_model': TransferObject.allow(),
        }