"""
FOODIE PlanRoute Domain Event

Multi-robot fleet simulation and route orchestration (Goal A).

Delegates A* search and obstacle-aware replanning to the injected
RoutePlannerService, keeping this event focused on domain orchestration.
"""

# *** imports

# ** core
from typing import List, Dict, Any, Tuple, Set

# ** infra
from tiferet.events import DomainEvent

# ** app
from ..domain import Robot, Order, Location
from ..mappers.location import LocationAggregate
from ..interfaces import LocationService, OrderService, RobotService, RoutePlannerService

# *** events

# ** event: plan_route
class PlanRoute(DomainEvent):
    '''
    Multi-robot route orchestration event (Goal A).

    Assigns orders to robots, delegates pathfinding and obstacle replanning
    to the injected RoutePlannerService, and produces fleet traces.
    '''

    # * attribute: robot_service
    robot_service: RobotService

    # * attribute: order_service
    order_service: OrderService

    # * attribute: route_planner
    route_planner: RoutePlannerService

    # * attribute: location_service
    location_service: LocationService

    # * init
    def __init__(self,
            robot_service: RobotService,
            order_service: OrderService,
            route_planner: RoutePlannerService,
            location_service: LocationService):
        '''
        Initialize the PlanRoute event.

        :param robot_service: The robot service for loading and saving robots.
        :type robot_service: RobotService
        :param order_service: The order service for loading orders.
        :type order_service: OrderService
        :param route_planner: The route planner service for A* search and replanning.
        :type route_planner: RoutePlannerService
        :param location_service: The location service for loading campus graph data.
        :type location_service: LocationService
        '''

        self.robot_service = robot_service
        self.order_service = order_service
        self.route_planner = route_planner
        self.location_service = location_service

    # * method: execute
    def execute(self, **kwargs) -> Dict[str, Any]:
        '''
        Plan routes for the given orders and simulate the fleet.

        :param obstacles: Set of edge tuples currently blocked.
        :type obstacles: set
        :param kwargs: Additional keyword arguments.
        :type kwargs: dict
        :return: Summary of planned routes and simulation results.
        :rtype: dict
        '''

        # Load robots and orders from their respective services.
        robots: List[Robot] = self.robot_service.list()
        orders: List[Order] = self.order_service.list()

        # Load campus graph from the location service.
        locations: List[Location] = self.location_service.list()
        edges: Dict[str, List[str]] = self.location_service.get_edges()
        obstacles: Set[Tuple[str, str]] = kwargs.get('obstacles', set())

        # Build lookup using LocationAggregate instances.
        loc_map: Dict[str, LocationAggregate] = {
            loc.name: LocationAggregate(**loc.model_dump())
            for loc in locations
        }

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

            # Delegate A* search to the route planner.
            path, dist = self.route_planner.find_path(start, goal, loc_map, edges, obstacles)

            if path is None:
                print(f'  No path found from {start} to {goal}!')
                results.append({'order': order.order_id, 'robot': robot.robot_id, 'status': 'no_path'})
                continue

            print(f'  Path: {" -> ".join(path)} (distance: {dist:.1f})')

            # Delegate obstacle detection and replanning to the route planner.
            new_path, new_dist, obstacles = self.route_planner.detect_and_replan(
                path, goal, loc_map, edges, obstacles,
            )

            if new_path is not None:
                print(f'  Obstacle detected! Replanning with A*...')
                print(f'  Replanned: {" -> ".join(new_path)} (distance: {new_dist:.1f})')
                path = new_path
                dist = new_dist

            # Simulate robot movement.
            robot.consume_energy(dist)
            robot.status = 'en_route'
            self.robot_service.save(robot)
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
