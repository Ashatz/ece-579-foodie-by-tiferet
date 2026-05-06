"""
FOODIE Robot Mappers

Aggregate and SqlObject for the Robot domain model.
Used for persistence of fleet state and route data.
"""

# *** imports

# ** core
import json
from typing import Any, ClassVar, Dict, List

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
        Update battery level.

        :param new_level: New battery percentage (0.0–100.0).
        :type new_level: float
        '''

        self.battery_level = new_level

    # * method: update_location
    def update_location(self, new_location: Location) -> None:
        '''
        Change current location.

        :param new_location: The new Location domain object.
        :type new_location: Location
        '''

        self.current_location = new_location

    # * method: update_status
    def update_status(self, new_status: str) -> None:
        '''
        Change robot operational status.

        :param new_status: New status value.
        :type new_status: str
        '''

        self.status = new_status


# ** mapper: robot_sql_object
class RobotSqlObject(Robot, TransferObject):
    '''
    SqlObject for the Robot domain object (SQLite serialization).

    Nested objects (current_location and compartments list) are serialized
    as JSON strings for storage in SQLite columns.
    '''

    # * attribute: _ROLES
    _ROLES: ClassVar[Dict[str, Dict[str, Any]]] = {
        'to_model': {'exclude': {'current_location', 'compartments'}},
        'to_data.sqlite': {'exclude': {'current_location', 'compartments'}},
    }

    # * method: to_primitive
    def to_primitive(self, role: str = None, **overrides) -> dict:
        '''
        Custom serialization for SQLite: convert nested objects to JSON strings.

        :param role: The serialization role to apply.
        :type role: str
        :param overrides: Additional keyword arguments.
        :type overrides: dict
        :return: Serialized dictionary with JSON columns.
        :rtype: dict
        '''

        # Delegate to base for standard field serialization.
        data = super().to_primitive(role, **overrides)

        # Only add JSON columns for the sqlite serialization role.
        if role == 'to_data.sqlite':
            data['current_location_json'] = json.dumps(
                self.current_location.model_dump()
            )
            data['compartments_json'] = json.dumps(
                [bag.model_dump() for bag in self.compartments]
            )

        return data

    # * method: map
    def map(self, target: type = None, **overrides) -> RobotAggregate:
        '''
        Map the SQL transfer object to a RobotAggregate.

        :param target: The aggregate class (defaults to RobotAggregate).
        :type target: type
        :param overrides: Additional keyword arguments.
        :type overrides: dict
        :return: A RobotAggregate instance.
        :rtype: RobotAggregate
        '''

        # Pass nested objects through since from_data already deserialized them.
        return super().map(
            target or RobotAggregate,
            current_location=self.current_location,
            compartments=list(self.compartments),
            **overrides,
        )

    # * method: from_data
    @classmethod
    def from_data(cls, data: dict, **overrides) -> 'RobotSqlObject':
        '''
        Create a RobotSqlObject from a raw SQLite row dict.

        Parses JSON columns into domain objects before validation.

        :param data: The raw row dict from SQLite.
        :type data: dict
        :param overrides: Additional keyword arguments.
        :type overrides: dict
        :return: A RobotSqlObject instance.
        :rtype: RobotSqlObject
        '''

        # Extract and deserialize current_location_json.
        loc_json = data.pop('current_location_json', '{}')
        data['current_location'] = Location(**json.loads(loc_json))

        # Extract and deserialize compartments_json.
        comp_json = data.pop('compartments_json', '[]')
        data['compartments'] = [Bag(**bag_data) for bag_data in json.loads(comp_json)]

        # Apply overrides and validate.
        data.update(overrides)
        return cls.model_validate(data)

    # * method: from_model
    @classmethod
    def from_model(cls, robot: Robot, **overrides) -> 'RobotSqlObject':
        '''
        Create a RobotSqlObject from a Robot model.

        :param robot: The source Robot instance.
        :type robot: Robot
        :param overrides: Additional keyword arguments.
        :type overrides: dict
        :return: A RobotSqlObject instance.
        :rtype: RobotSqlObject
        '''

        return super().from_model(robot, **overrides)
