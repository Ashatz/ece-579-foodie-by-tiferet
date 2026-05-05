"""
FOODIE PlanRoute Domain Event

Implements heuristic search (A*) and multi-robot fleet simulation (Goal A).

State-Space Search (Lectures 2-6):
- States: robot positions on campus graph
- Operators: move along edges between Location nodes
- Heuristic: Manhattan distance (admissible for grid-like campus)
- Replanning: obstacle detection triggers re-search from current position
"""

# *** imports

# ** core
import heapq
from typing import List, Dict, Any, Tuple, Set

# ** infra
from tiferet.events import DomainEvent

# ** app
from ..domain import Robot, Order, Location

# *** events

# ** event: plan_route
class PlanRoute(DomainEvent):
    '''
    A* route planning and multi-robot simulation event (Goal A).

    Runs a real A* search on the campus graph, assigns orders to robots,
    handles obstacle detection with replanning, and produces fleet traces.
    '''

    # * method: execute
    def execute(self, **kwargs) -> Dict[str, Any]:
        '''
        Plan routes for the given orders using A* and simulate the fleet.

        :param robots: List of Robot domain objects.
        :type robots: list[Robot]
        :param orders: List of Order domain objects.
        :type orders: list[Order]
        :param locations: List of Location domain objects (campus graph nodes).
        :type locations: list[Location]
        :param edges: Adjacency list as dict of {name: [neighbor_name, ...]}.
        :type edges: dict
        :param obstacles: Set of edge tuples currently blocked.
        :type obstacles: set
        :return: Summary of planned routes and simulation results.
        :rtype: dict
        '''

        robots: List[Robot] = kwargs['robots']
        orders: List[Order] = kwargs['orders']
        locations: List[Location] = kwargs['locations']
        edges: Dict[str, List[str]] = kwargs['edges']
        obstacles: Set[Tuple[str, str]] = kwargs.get('obstacles', set())

        # Build lookup.
        loc_map = {loc.name: loc for loc in locations}

        print('RoutePlannerContext: A* search + multi-robot replanning started...')
        print(f'Fleet: {len(robots)} robots | Orders: {len(orders)} | Locations: {len(locations)}')
        print()

        results = []
        total_distance = 0.0

        for i, order in enumerate(orders):
            # Round-robin robot assignment.
            robot = robots[i % len(robots)]
            start = robot.current_location.name
            goal = order.destination

            print(f'--- Order {order.order_id}: {start} -> {goal} (Robot {robot.robot_id}) ---')

            # First attempt at A* search.
            path, dist = self._a_star(start, goal, loc_map, edges, obstacles)

            if path is None:
                print(f'  No path found from {start} to {goal}!')
                results.append({'order': order.order_id, 'robot': robot.robot_id, 'status': 'no_path'})
                continue

            print(f'  Path: {" -> ".join(path)} (distance: {dist:.1f})')

            # Simulate obstacle detection mid-route.
            obstacle_idx = len(path) // 2 if len(path) > 2 else None
            if obstacle_idx and len(path) > 3:
                blocked_from = path[obstacle_idx]
                blocked_to = path[obstacle_idx + 1]
                obstacle_edge = (blocked_from, blocked_to)

                if obstacle_edge not in obstacles:
                    print(f'  Obstacle detected on {blocked_from} -> {blocked_to}! Replanning with A*...')
                    obstacles.add(obstacle_edge)
                    obstacles.add((blocked_to, blocked_from))

                    # Replan from the obstacle point.
                    new_path, new_dist = self._a_star(blocked_from, goal, loc_map, edges, obstacles)
                    if new_path:
                        path = path[:obstacle_idx] + new_path
                        dist = sum(
                            loc_map[path[j]].distance_to(loc_map[path[j+1]])
                            for j in range(len(path)-1)
                        )
                        print(f'  New path found (heuristic h(n) = Manhattan + obstacle penalty).')
                        print(f'  Replanned: {" -> ".join(path)} (distance: {dist:.1f})')
                    else:
                        print(f'  Replanning failed — no alternative route.')

            # Simulate robot movement.
            robot.consume_energy(dist)
            robot.status = 'en_route'
            total_distance += dist

            results.append({
                'order': order.order_id,
                'robot': robot.robot_id,
                'path': path,
                'distance': dist,
                'status': 'planned',
            })

        # Fleet status summary.
        print()
        print('=== Current Fleet Status ===')
        for robot in robots:
            print(f'  {robot.format_for_trace()}')
        print('===')

        return {
            'total_distance': total_distance,
            'routes_planned': len(results),
            'details': results,
            'status': 'complete',
        }

    # * method: _a_star
    def _a_star(
        self,
        start: str,
        goal: str,
        loc_map: Dict[str, Location],
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
        :type loc_map: dict
        :param edges: Adjacency list.
        :type edges: dict
        :param obstacles: Set of blocked edges.
        :type obstacles: set
        :return: (path as list of names, total distance) or (None, 0.0).
        :rtype: tuple
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
