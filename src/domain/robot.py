"""
FOODIE Robot Domain Model

Represents one autonomous food-delivery robot in the fleet.
Used for multi-robot route optimization, bagging, and simulation (Goal A).
"""

# *** imports

# ** core
from typing import List

from tiferet import DomainObject, StringType, FloatType, ListType

# ** app
from .location import Location
from .bag import Bag

# *** models

# ** model: robot
class Robot(DomainObject):
    '''
    An autonomous food delivery robot.

    Equipped with compartments (bags), robotic arm, battery/energy model,
    and intelligence for route planning and replanning (Goal A).
    Supports concurrent operation with other robots.
    '''

    # * attribute: robot_id
    robot_id = StringType(required=True, metadata={'description': 'Unique robot identifier (e.g., R1, R2)'})

    # * attribute: current_location
    current_location = Location  # reference to Location domain object

    # * attribute: battery_level
    battery_level = FloatType(default=100.0, min_value=0.0, max_value=100.0)

    # * attribute: compartments
    compartments = ListType(Bag, default=list, metadata={'description': 'Bags currently loaded in the robot'})

    # * attribute: status
    status = StringType(
        default='idle',
        choices=['idle', 'charging', 'en_route', 'delivering', 'returning'],
        metadata={'description': 'Current operational status'}
    )

    # * method: new (static)
    @staticmethod
    def new(robot_id: str, current_location: Location, battery_level: float = 100.0,
            compartments: List[dict] | List[Bag] = None, status: str = 'idle', **kwargs):
        '''
        Factory for creating a new Robot (Tiferet DomainObject pattern).

        :param robot_id: Unique robot identifier.
        :type robot_id: str
        :param current_location: Starting location (usually FW).
        :type current_location: Location
        :param battery_level: Initial battery percentage.
        :type battery_level: float
        :param compartments: Initial list of loaded bags.
        :type compartments: list
        '''
        bag_objects = []
        if compartments:
            for bag_data in compartments:
                if isinstance(bag_data, dict):
                    bag_objects.append(Bag.new(**bag_data))
                else:
                    bag_objects.append(bag_data)

        return DomainObject.new(
            model_type=Robot,
            robot_id=robot_id,
            current_location=current_location,
            battery_level=battery_level,
            compartments=bag_objects,
            status=status,
            **kwargs
        )

    # * method: load_bag
    def load_bag(self, bag: Bag) -> bool:
        '''
        Load a completed bag into a compartment (simulates robotic arm).

        :return: True if bag was loaded successfully.
        :rtype: bool
        '''
        if self.status in ['en_route', 'delivering']:
            return False  # cannot load while moving
        self.compartments.append(bag)
        return True

    # * method: consume_energy
    def consume_energy(self, distance: float, energy_per_meter: float = 0.12) -> None:
        '''
        Update battery based on distance traveled (used in route simulation).

        :param distance: Meters traveled.
        :type distance: float
        '''
        consumption = distance * energy_per_meter
        self.battery_level = max(0.0, self.battery_level - consumption)

    # * method: is_low_battery
    def is_low_battery(self, threshold: float = 20.0) -> bool:
        '''
        Check if robot needs to return to FW for recharging.

        :return: True if battery is critically low.
        :rtype: bool
        '''
        return self.battery_level <= threshold

    # * method: format_for_trace
    def format_for_trace(self) -> str:
        '''
        Human-readable status for simulation / fleet monitoring trace.

        :return: Formatted robot status line.
        :rtype: str
        '''
        loc = self.current_location.format_for_trace() if self.current_location else "Unknown"
        return (f"Robot {self.robot_id} | Loc: {loc} | "
                f"Battery: {self.battery_level:.1f}% | "
                f"Status: {self.status} | "
                f"Bags: {len(self.compartments)}")