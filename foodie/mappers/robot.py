"""
FOODIE Robot Mappers

Aggregate and SqlObject for the Robot domain model.
Used for persistence of fleet state and route data (Goal A).
"""

# *** imports

# ** core
import json
from typing import Any, List

# ** infra
from tiferet.mappers import Aggregate, TransferObject

# ** app
from ..domain import Robot, Location, Bag

# *** mappers

# ** mapper: robot_aggregate
class RobotAggregate(Robot, Aggregate):
    '''
    Aggregate for the Robot domain object.

    Adds validated mutation methods while inheriting all domain behavior.
    '''

    # * method: update_battery
    def update_battery(self, new_level: float) -> None:
        '''
        Validated mutation: update battery level.

        :param new_level: New battery percentage (0.0–100.0).
        :type new_level: float
        '''
        self.set_attribute('battery_level', new_level)

    # * method: update_location
    def update_location(self, new_location: Location) -> None:
        '''
        Validated mutation: change current location.
        '''
        self.set_attribute('current_location', new_location)

    # * method: load_bag
    def load_bag(self, bag: Bag) -> bool:
        '''
        Validated mutation: load a bag into compartments.
        '''
        if self.status in ['en_route', 'delivering']:
            return False
        current_compartments = list(self.compartments)
        current_compartments.append(bag)
        self.set_attribute('compartments', current_compartments)
        return True

# ** mapper: robot_sql_object
class RobotSqlObject(Robot, TransferObject):
    '''
    SqlObject for the Robot domain object (SQLite serialization).

    Nested objects (`current_location` and `compartments` list) are serialized
    as JSON strings (no separate tables needed – they are only accessed via Robot root).
    '''

    class Options:
        serialize_when_none = False
        roles = {
            'to_data.sqlite': TransferObject.deny('id'),   # id is derived
            'to_model': TransferObject.allow(),
        }

    # * method: to_primitive (override)
    def to_primitive(self, role: str = None, **kwargs) -> dict:
        '''
        Custom serialization for SQLite: convert nested objects to JSON strings.
        '''
        data = super().to_primitive(role, **kwargs)

        # Serialize current_location
        if hasattr(self, 'current_location') and self.current_location:
            data['current_location_json'] = json.dumps(self.current_location.to_primitive())

        # Serialize compartments list
        if 'compartments' in data and isinstance(data['compartments'], list):
            data['compartments_json'] = json.dumps([bag.to_primitive() for bag in self.compartments])
            del data['compartments']

        return data

    # * method: from_data (override)
    @classmethod
    def from_data(cls, data: dict, **kwargs):
        '''
        Deserialize from SQLite row: convert JSON strings back to domain objects.
        '''
        if 'current_location_json' in data:
            loc_data = json.loads(data.pop('current_location_json'))
            data['current_location'] = Location.new(**loc_data)

        if 'compartments_json' in data:
            comp_data = json.loads(data.pop('compartments_json'))
            data['compartments'] = [Bag.new(**item) for item in comp_data]

        return super().from_data(data, **kwargs)