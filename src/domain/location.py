"""
FOODIE Location Domain Model

Represents a node in the campus terrain graph (pathways, Food Warehouse, buildings).
Used for state-space search and A* route planning (Goal A).
"""

# *** imports

# ** infra
from pydantic import Field
from tiferet import DomainObject

# *** models

# ** model: location
class Location(DomainObject):
    '''
    A location (node) on the bounded campus terrain.

    Forms the graph for robot movement, state-space search,
    and dynamic obstacle handling (Lectures 2-6).
    '''

    # * attribute: name
    name: str = Field(..., description='Unique location identifier (e.g., FW, Building_A)')

    # * attribute: x
    x: float = Field(..., description='X coordinate for distance heuristics')

    # * attribute: y
    y: float = Field(..., description='Y coordinate for distance heuristics')

    # * attribute: is_food_warehouse
    is_food_warehouse: bool = Field(default=False, description='Whether this is the Food Warehouse')

    # * attribute: is_obstacle_prone
    is_obstacle_prone: bool = Field(default=False, description='May become blocked dynamically')

    # * method: distance_to
    def distance_to(self, other: 'Location') -> float:
        '''
        Manhattan distance heuristic (perfect for grid-like campus pathways).

        :param other: The target location.
        :type other: Location
        :return: Heuristic distance.
        :rtype: float
        '''

        # Compute Manhattan distance.
        return abs(self.x - other.x) + abs(self.y - other.y)

    # * method: format_for_trace
    def format_for_trace(self) -> str:
        '''
        Human-readable string for simulation / route trace output.

        :return: Formatted location description.
        :rtype: str
        '''

        # Format with optional FW label.
        fw = ' (Food Warehouse)' if self.is_food_warehouse else ''
        return f'{self.name}{fw} @ ({self.x:.1f}, {self.y:.1f})'
