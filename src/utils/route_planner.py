"""
FOODIE A* Route Planner Utility

Concrete implementation of RoutePlannerService.
Encapsulates A* search and obstacle-aware replanning on a campus graph
composed of LocationAggregate nodes.
"""

# *** imports

# ** core
import heapq
from typing import Dict, List, Set, Tuple

# ** app
from ..mappers.location import LocationAggregate
from ..interfaces.route_planner import RoutePlannerService

# *** utils

# ** util: a_star_route_planner
class AStarRoutePlanner(RoutePlannerService):
    '''
    A* route planner for the campus terrain graph.

    Accepts LocationAggregate instances for graph nodes and provides
    shortest-path search with obstacle detection and replanning.
    '''

    # * method: find_path
    def find_path(
        self,
        start: str,
        goal: str,
        loc_map: Dict[str, LocationAggregate],
        edges: Dict[str, List[str]],
        obstacles: Set[Tuple[str, str]],
    ) -> Tuple[List[str] | None, float]:
        '''
        A* search on the campus graph.

        :param start: Start location name.
        :type start: str
        :param goal: Goal location name.
        :type goal: str
        :param loc_map: Location lookup by name.
        :type loc_map: Dict[str, LocationAggregate]
        :param edges: Adjacency list.
        :type edges: Dict[str, List[str]]
        :param obstacles: Set of blocked edges.
        :type obstacles: Set[Tuple[str, str]]
        :return: (path as list of names, total distance) or (None, 0.0).
        :rtype: Tuple[List[str] | None, float]
        '''

        if start not in loc_map or goal not in loc_map:
            return None, 0.0

        # Priority queue: (f_score, node_name).
        open_set = [(0.0, start)]
        came_from: Dict[str, str] = {}
        g_score: Dict[str, float] = {start: 0.0}

        goal_loc = loc_map[goal]

        while open_set:
            _, current = heapq.heappop(open_set)

            # Goal reached.
            if current == goal:
                path = []
                node = current
                while node in came_from:
                    path.append(node)
                    node = came_from[node]
                path.append(start)
                path.reverse()
                return path, g_score[goal]

            # Expand neighbors.
            for neighbor in edges.get(current, []):

                # Skip blocked edges.
                if (current, neighbor) in obstacles:
                    continue

                # Edge cost = Manhattan distance between nodes.
                edge_cost = loc_map[current].distance_to(loc_map[neighbor])
                tentative_g = g_score[current] + edge_cost

                if tentative_g < g_score.get(neighbor, float('inf')):
                    came_from[neighbor] = current
                    g_score[neighbor] = tentative_g
                    f_score = tentative_g + loc_map[neighbor].distance_to(goal_loc)
                    heapq.heappush(open_set, (f_score, neighbor))

        # No path found.
        return None, 0.0

    # * method: detect_and_replan
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

        If the path has more than 3 nodes, an obstacle is injected at the
        midpoint edge. The planner then re-searches from the obstacle point
        to the goal, splicing the new tail onto the original prefix.

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
        :return: (new_path, new_distance, updated_obstacles) or (None, 0.0, obstacles).
        :rtype: Tuple[List[str] | None, float, Set[Tuple[str, str]]]
        '''

        # Determine midpoint index for obstacle injection.
        obstacle_idx = len(path) // 2 if len(path) > 2 else None

        # Only inject obstacle if path is long enough.
        if not obstacle_idx or len(path) <= 3:
            return None, 0.0, obstacles

        blocked_from = path[obstacle_idx]
        blocked_to = path[obstacle_idx + 1]
        obstacle_edge = (blocked_from, blocked_to)

        # Skip if this edge is already blocked.
        if obstacle_edge in obstacles:
            return None, 0.0, obstacles

        # Block the edge in both directions.
        obstacles.add(obstacle_edge)
        obstacles.add((blocked_to, blocked_from))

        # Replan from the obstacle point to the goal.
        new_tail, new_dist = self.find_path(blocked_from, goal, loc_map, edges, obstacles)

        if new_tail is None:
            return None, 0.0, obstacles

        # Splice original prefix with new tail.
        new_path = path[:obstacle_idx] + new_tail

        # Recompute total distance for the spliced path.
        total_dist = sum(
            loc_map[new_path[j]].distance_to(loc_map[new_path[j + 1]])
            for j in range(len(new_path) - 1)
        )

        return new_path, total_dist, obstacles
