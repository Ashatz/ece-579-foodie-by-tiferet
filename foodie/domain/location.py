"""
FOODIE Location Domain Model

Represents a node in the campus terrain graph (pathways, Food Warehouse, buildings).
Used for state-space search and A* route planning (Goal A).
"""

# *** imports

# ** core
from tiferet import DomainObject, StringType, FloatType, BooleanType

# *** models

# ** model: location
class Location(DomainObject):
    '''
    A location (node) on the bounded campus terrain.

    Forms the graph for robot movement, state-space search,
    and dynamic obstacle handling (Lectures 2–6).
    '''

    # * attribute: name
    name = StringType(required=True, metadata={'description': 'Unique location identifier (e.g., FW, Building_A, Pathway_3)'})

    # * attribute: x
    x = FloatType(required=True, metadata={'description': 'X coordinate for distance heuristics'})

    # * attribute: y
    y = FloatType(required=True, metadata={'description': 'Y coordinate for distance heuristics'})

    # * attribute: is_food_warehouse
    is_food_warehouse = BooleanType(default=False)

    # * attribute: is_obstacle_prone
    is_obstacle_prone = BooleanType(default=False, metadata={'description': 'May become blocked dynamically (construction, etc.)'})

    # * method: new (static)
    @staticmethod
    def new(name: str, x: float, y: float, is_food_warehouse: bool = False, is_obstacle_prone: bool = False, **kwargs):
        '''
        Factory for creating a new Location (Tiferet DomainObject pattern).

        :param name: Unique location name.
        :type name: str
        :param x: X coordinate.
        :type x: float
        :param y: Y coordinate.
        :type y: float
        '''
        return DomainObject.new(
            model_type=Location,
            name=name,
            x=x,
            y=y,
            is_food_warehouse=is_food_warehouse,
            is_obstacle_prone=is_obstacle_prone,
            **kwargs
        )

    # * method: distance_to
    def distance_to(self, other: 'Location') -> float:
        '''
        Manhattan distance heuristic (perfect for grid-like campus pathways).

        Used by A* in route planning (Goal A).

        :return: Heuristic distance.
        :rtype: float
        '''
        return abs(self.x - other.x) + abs(self.y - other.y)

    # * method: format_for_trace
    def format_for_trace(self) -> str:
        '''
        Human-readable string for simulation / route trace output.

        :return: Formatted location description.
        :rtype: str
        '''
        fw = " (Food Warehouse)" if self.is_food_warehouse else ""
        return f"{self.name}{fw} @ ({self.x:.1f}, {self.y:.1f})"