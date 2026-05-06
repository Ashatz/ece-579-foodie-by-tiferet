'''FOODIE Location Domain Model'''

# *** imports

# ** core
from __future__ import annotations

# ** infra
from pydantic import Field
from tiferet import DomainObject


# *** models

# ** model: location
class Location(DomainObject):
    '''
    Represents a node in the campus terrain graph for A* route planning.
    '''

    # * attribute: name
    name: str = Field(
        ...,
        description='Unique location identifier.',
    )

    # * attribute: x
    x: float = Field(
        ...,
        description='X coordinate for heuristic computation.',
    )

    # * attribute: y
    y: float = Field(
        ...,
        description='Y coordinate for heuristic computation.',
    )

    # * attribute: is_food_warehouse
    is_food_warehouse: bool = Field(
        default=False,
        description='Marks the robot start/recharge point.',
    )

    # * attribute: is_obstacle_prone
    is_obstacle_prone: bool = Field(
        default=False,
        description='May trigger replanning.',
    )

    # * method: distance_to
    def distance_to(self, other: Location) -> float:
        '''
        Compute Manhattan distance heuristic to another location.

        :param other: The target location.
        :type other: Location
        :return: Manhattan distance |Δx| + |Δy|.
        :rtype: float
        '''

        # Compute and return the Manhattan distance.
        return abs(self.x - other.x) + abs(self.y - other.y)

    # * method: format_for_trace
    def format_for_trace(self) -> str:
        '''
        Format the location for trace display.

        :return: Formatted string with name, optional Food Warehouse label, and coordinates.
        :rtype: str
        '''

        # Build the Food Warehouse label.
        fw_label = ' (Food Warehouse)' if self.is_food_warehouse else ''

        # Return the formatted string.
        return f'{self.name}{fw_label} @ ({self.x}, {self.y})'
