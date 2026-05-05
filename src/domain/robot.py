"""
FOODIE Robot Domain Model

Represents one autonomous food-delivery robot in the fleet.
Used for multi-robot route optimization, bagging, and simulation (Goal A).
"""

# *** imports

# ** core
from typing import Literal, List

# ** infra
from pydantic import Field
from tiferet import DomainObject

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
    '''

    # * attribute: robot_id
    robot_id: str = Field(..., description='Unique robot identifier (e.g., R1, R2)')

    # * attribute: current_location
    current_location: Location = Field(..., description='Current position on campus')

    # * attribute: battery_level
    battery_level: float = Field(default=100.0, ge=0.0, le=100.0, description='Battery percentage')

    # * attribute: compartments
    compartments: List[Bag] = Field(default_factory=list, description='Bags loaded in the robot')

    # * attribute: status
    status: Literal['idle', 'charging', 'en_route', 'delivering', 'returning'] = Field(
        default='idle',
        description='Current operational status',
    )

    # * method: load_bag
    def load_bag(self, bag: Bag) -> bool:
        '''
        Load a completed bag into a compartment (simulates robotic arm).

        :param bag: The bag to load.
        :type bag: Bag
        :return: True if bag was loaded successfully.
        :rtype: bool
        '''

        # Cannot load while moving.
        if self.status in ['en_route', 'delivering']:
            return False

        # Append via list reassignment for pydantic validation.
        self.compartments = self.compartments + [bag]
        return True

    # * method: consume_energy
    def consume_energy(self, distance: float, energy_per_meter: float = 0.12) -> None:
        '''
        Update battery based on distance traveled (used in route simulation).

        :param distance: Meters traveled.
        :type distance: float
        :param energy_per_meter: Energy consumed per meter.
        :type energy_per_meter: float
        '''

        # Compute consumption and clamp to zero.
        consumption = distance * energy_per_meter
        self.battery_level = max(0.0, self.battery_level - consumption)

    # * method: is_low_battery
    def is_low_battery(self, threshold: float = 20.0) -> bool:
        '''
        Check if robot needs to return to FW for recharging.

        :param threshold: Battery threshold percentage.
        :type threshold: float
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

        # Format location.
        loc = self.current_location.format_for_trace()
        return (
            f'Robot {self.robot_id} | Loc: {loc} | '
            f'Battery: {self.battery_level:.1f}% | '
            f'Status: {self.status} | '
            f'Bags: {len(self.compartments)}'
        )
