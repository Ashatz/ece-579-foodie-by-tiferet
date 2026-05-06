"""
FOODIE Route Planner Service Interface
"""

# *** imports

# ** core
from abc import abstractmethod
from typing import Dict, List, Set, Tuple

# ** infra
from tiferet.interfaces import Service

# ** app
from ..mappers.location import LocationAggregate

# *** interfaces

# ** interface: route_planner_service
class RoutePlannerService(Service):
    '''
    Vertical interface for A* route planning and obstacle-aware replanning.
    '''

    # * method: find_path
    @abstractmethod
    def find_path(
        self,
        start: str,
        goal: str,
        loc_map: Dict[str, LocationAggregate],
        edges: Dict[str, List[str]],
        obstacles: Set[Tuple[str, str]],
    ) -> Tuple[List[str] | None, float]:
        '''
        Find the shortest path between two locations using A* search.

        :param start: Start location name.
        :type start: str
        :param goal: Goal location name.
        :type goal: str
        :param loc_map: Location lookup by name.
        :type loc_map: Dict[str, LocationAggregate]
        :param edges: Adjacency list as dict of {name: [neighbor_name, ...]}.
        :type edges: Dict[str, List[str]]
        :param obstacles: Set of blocked edge tuples.
        :type obstacles: Set[Tuple[str, str]]
        :return: (path as list of names, total distance) or (None, 0.0).
        :rtype: Tuple[List[str] | None, float]
        '''
        raise NotImplementedError()

    # * method: detect_and_replan
    @abstractmethod
    def detect_and_replan(
        self,
        path: List[str],
        goal: str,
        loc_map: Dict[str, LocationAggregate],
        edges: Dict[str, List[str]],
        obstacles: Set[Tuple[str, str]],
    ) -> Tuple[List[str] | None, float, Set[Tuple[str, str]]]:
        '''
        Simulate obstacle detection at the midpoint of a path and replan.

        :param path: The current planned path.
        :type path: List[str]
        :param goal: Goal location name.
        :type goal: str
        :param loc_map: Location lookup by name.
        :type loc_map: Dict[str, LocationAggregate]
        :param edges: Adjacency list.
        :type edges: Dict[str, List[str]]
        :param obstacles: Current set of blocked edge tuples (mutated in place).
        :type obstacles: Set[Tuple[str, str]]
        :return: (new_path, new_distance, updated_obstacles) or (None, 0.0, obstacles) if no replan needed/possible.
        :rtype: Tuple[List[str] | None, float, Set[Tuple[str, str]]]
        '''
        raise NotImplementedError()
