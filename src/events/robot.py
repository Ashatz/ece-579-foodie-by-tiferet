"""
FOODIE Robot Domain Events

Domain events that orchestrate robot operations: bagging orders,
loading compartments, and managing robot state.
"""

# *** imports

# ** core
from typing import Any, Dict, List, Set, Tuple

# ** infra
from tiferet.events import DomainEvent

# ** app
from ..domain import Item
from ..interfaces.order import OrderService
from ..interfaces.robot import RobotService
from ..interfaces.location import LocationService
from ..interfaces.bagging import BaggingService
from ..interfaces.route_planner import RoutePlannerService
from ..mappers.bag import BagAggregate
from ..mappers.location import LocationAggregate

# *** events

# ** event: bag_order
class BagOrder(DomainEvent):
    '''
    Robot-centric order bagging event (Goal B — FOODIE_BAGGER).

    Loads a robot and an order, expands items by quantity into individual
    units, delegates rule-based bagging to the BaggingService, then loads
    the resulting bags into the robot's compartments and updates the order
    status to 'bagged'.
    '''

    # * attribute: order_service
    order_service: OrderService

    # * attribute: robot_service
    robot_service: RobotService

    # * attribute: bagging_service
    bagging_service: BaggingService

    # * init
    def __init__(self,
            order_service: OrderService,
            robot_service: RobotService,
            bagging_service: BaggingService,
        ):
        '''
        Initialize the BagOrder event.

        :param order_service: Service for loading and saving orders.
        :type order_service: OrderService
        :param robot_service: Service for loading and saving robots.
        :type robot_service: RobotService
        :param bagging_service: Service for forward-chaining bag assignment.
        :type bagging_service: BaggingService
        '''

        # Set the service dependencies.
        self.order_service = order_service
        self.robot_service = robot_service
        self.bagging_service = bagging_service

    # * method: execute
    @DomainEvent.parameters_required(['robot_id', 'order_id'])
    def execute(self,
            robot_id: str,
            order_id: str,
            **kwargs,
        ) -> Dict[str, Any]:
        '''
        Bag an order and load the bags onto a robot.

        :param robot_id: The robot to load bags onto.
        :type robot_id: str
        :param order_id: The order to bag.
        :type order_id: str
        :param kwargs: Additional keyword arguments.
        :type kwargs: dict
        :return: Summary dict with robot_id, order_id, bags_packed, and status.
        :rtype: Dict[str, Any]
        '''

        # Load the robot and verify it exists.
        robot = self.robot_service.get(robot_id)
        self.verify(
            expression=robot is not None,
            error_code='ROBOT_NOT_FOUND',
            robot_id=robot_id,
        )

        # Verify the robot is at the Food Warehouse.
        self.verify(
            expression=robot is not None and robot.current_location.is_food_warehouse,
            error_code='ROBOT_NOT_AT_WAREHOUSE',
            robot_id=robot_id,
        )

        # Verify the robot has no beverage bags (exclusive transport).
        self.verify(
            expression=all(b.bag_type != 'beverage' for b in robot.compartments),
            error_code='ROBOT_CARGO_CONFLICT',
            robot_id=robot_id,
        )

        # Load the order and verify it exists.
        order = self.order_service.get(order_id)
        self.verify(
            expression=order is not None,
            error_code='ORDER_NOT_FOUND',
            order_id=order_id,
        )

        # Verify the order is an item order.
        self.verify(
            expression=order.order_type == 'item',
            error_code='ORDER_TYPE_MISMATCH',
            order_id=order_id,
            expected='item',
            actual=order.order_type,
        )

        # Print trace header.
        print(f'\n  Bagging {order.format_for_bagger()}')
        print(f'  Assigned to Robot {robot.robot_id}')

        # Expand items by quantity into individual units.
        expanded_items = []
        for item in order.items:
            for _ in range(item.quantity):
                expanded_items.append(
                    Item(
                        name=item.name,
                        size=item.size,
                        is_frozen=item.is_frozen,
                        is_fragile=item.is_fragile,
                        quantity=1,
                    )
                )

        # Delegate bagging to the forward-chaining production system.
        bags: List[BagAggregate] = self.bagging_service.bag_items(expanded_items)

        # Load each bag onto the robot.
        for bag in bags:
            robot.load_bag(bag)

        # Update order status to bagged and persist.
        order.status = 'bagged'
        self.order_service.save(order)

        # Persist the updated robot (now carrying bags).
        self.robot_service.save(robot)

        # Print bag summary.
        print(f'\n  {len(bags)} bag(s) packed and loaded onto Robot {robot.robot_id}:')
        for bag in bags:
            print(f'    {bag.format_trace()}')

        # Return the summary.
        return {
            'robot_id': robot_id,
            'order_id': order_id,
            'bags_packed': len(bags),
            'status': 'complete',
        }


# ** event: plan_route
class PlanRoute(DomainEvent):
    '''
    Plan and execute an A* route for a single robot to an order destination.

    The robot must have bags loaded (from BagOrder). Plans the shortest
    path, handles obstacle replanning, simulates energy consumption, and
    updates the robot's location to the destination.
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
            location_service: LocationService,
        ):
        '''
        Initialize the PlanRoute event.

        :param robot_service: Service for loading and saving robots.
        :type robot_service: RobotService
        :param order_service: Service for loading orders.
        :type order_service: OrderService
        :param route_planner: Service for A* search and replanning.
        :type route_planner: RoutePlannerService
        :param location_service: Service for loading campus graph data.
        :type location_service: LocationService
        '''

        # Set the service dependencies.
        self.robot_service = robot_service
        self.order_service = order_service
        self.route_planner = route_planner
        self.location_service = location_service

    # * method: execute
    @DomainEvent.parameters_required(['robot_id', 'order_id'])
    def execute(self,
            robot_id: str,
            order_id: str,
            **kwargs,
        ) -> Dict[str, Any]:
        '''
        Plan a route for a robot to deliver an order.

        :param robot_id: The robot to route.
        :type robot_id: str
        :param order_id: The order whose destination is the goal.
        :type order_id: str
        :param kwargs: Optional 'obstacles' set of blocked edge tuples.
        :type kwargs: dict
        :return: Summary dict with route details.
        :rtype: Dict[str, Any]
        '''

        # Load the robot and verify it exists.
        robot = self.robot_service.get(robot_id)
        self.verify(
            expression=robot is not None,
            error_code='ROBOT_NOT_FOUND',
            robot_id=robot_id,
        )

        # Verify the robot has bags loaded.
        self.verify(
            expression=len(robot.compartments) > 0,
            error_code='ROBOT_NO_BAGS',
            robot_id=robot_id,
        )

        # Load the order and verify it exists.
        order = self.order_service.get(order_id)
        self.verify(
            expression=order is not None,
            error_code='ORDER_NOT_FOUND',
            order_id=order_id,
        )

        # Build the campus graph.
        locations = self.location_service.list()
        edges = self.location_service.get_edges()
        loc_map = {
            loc.name: LocationAggregate(**loc.model_dump())
            for loc in locations
        }

        # Initialize obstacles.
        obstacles: Set[Tuple[str, str]] = kwargs.get('obstacles', set())

        # Plan the A* route from robot's location to order destination.
        start = robot.current_location.name
        goal = order.destination
        print(f'\n  Planning route: Robot {robot_id} from {start} to {goal}')

        path, distance = self.route_planner.find_path(
            start, goal, loc_map, edges, obstacles,
        )

        # Handle no path found.
        if path is None:
            print(f'  No path found from {start} to {goal}.')
            return {
                'robot_id': robot_id,
                'order_id': order_id,
                'path': None,
                'distance': 0.0,
                'status': 'no_path',
            }

        # Attempt obstacle detection and replanning.
        new_path, new_dist, obstacles = self.route_planner.detect_and_replan(
            path, goal, loc_map, edges, obstacles,
        )
        if new_path is not None:
            print(f'  Replanned route: {" -> ".join(new_path)} (dist: {new_dist:.1f})')
            path, distance = new_path, new_dist

        # Simulate energy consumption and update robot.
        robot.consume_energy(distance)
        robot.status = 'en_route'
        robot.current_location = loc_map[goal]
        self.robot_service.save(robot)

        # Print route summary.
        print(f'  Route: {" -> ".join(path)} (dist: {distance:.1f})')
        print(f'  Robot {robot_id} battery: {robot.battery_level:.1f}%')

        # Return the summary.
        return {
            'robot_id': robot_id,
            'order_id': order_id,
            'path': path,
            'distance': distance,
            'status': 'complete',
        }


# ** event: deliver_order
class DeliverOrder(DomainEvent):
    '''
    Deliver an order at the destination.

    The robot must be at the order's destination and have bags loaded.
    Clears the robot's compartments, updates the order status to
    'delivered', and persists both.
    '''

    # * attribute: robot_service
    robot_service: RobotService

    # * attribute: order_service
    order_service: OrderService

    # * init
    def __init__(self,
            robot_service: RobotService,
            order_service: OrderService,
        ):
        '''
        Initialize the DeliverOrder event.

        :param robot_service: Service for loading and saving robots.
        :type robot_service: RobotService
        :param order_service: Service for loading and saving orders.
        :type order_service: OrderService
        '''

        # Set the service dependencies.
        self.robot_service = robot_service
        self.order_service = order_service

    # * method: execute
    @DomainEvent.parameters_required(['robot_id', 'order_id'])
    def execute(self,
            robot_id: str,
            order_id: str,
            **kwargs,
        ) -> Dict[str, Any]:
        '''
        Deliver an order at the robot's current location.

        :param robot_id: The robot performing the delivery.
        :type robot_id: str
        :param order_id: The order to deliver.
        :type order_id: str
        :param kwargs: Additional keyword arguments.
        :type kwargs: dict
        :return: Summary dict with delivery status.
        :rtype: Dict[str, Any]
        '''

        # Load the robot and verify it exists.
        robot = self.robot_service.get(robot_id)
        self.verify(
            expression=robot is not None,
            error_code='ROBOT_NOT_FOUND',
            robot_id=robot_id,
        )

        # Load the order and verify it exists.
        order = self.order_service.get(order_id)
        self.verify(
            expression=order is not None,
            error_code='ORDER_NOT_FOUND',
            order_id=order_id,
        )

        # Verify the robot is at the order's destination.
        self.verify(
            expression=robot.current_location.name == order.destination,
            error_code='ROBOT_NOT_AT_DESTINATION',
            robot_id=robot_id,
            destination=order.destination,
        )

        # Verify the robot has bags to deliver.
        self.verify(
            expression=len(robot.compartments) > 0,
            error_code='ROBOT_NO_BAGS',
            robot_id=robot_id,
        )

        # Clear the robot's compartments (bags delivered).
        bags_delivered = len(robot.compartments)
        robot.compartments = []
        robot.status = 'idle'
        self.robot_service.save(robot)

        # Update order status to delivered and persist.
        order.status = 'delivered'
        self.order_service.save(order)

        # Print delivery trace.
        print(f'  Robot {robot_id} delivered {bags_delivered} bag(s) for {order_id} at {order.destination}')

        # Return the summary.
        return {
            'robot_id': robot_id,
            'order_id': order_id,
            'bags_delivered': bags_delivered,
            'status': 'complete',
        }


# ** event: return_to_warehouse
class ReturnToWarehouse(DomainEvent):
    '''
    Route a robot back to the Food Warehouse.

    The robot must not already be at the warehouse. Plans an A* route
    back, consumes energy, and updates the robot's location to FW.
    '''

    # * attribute: robot_service
    robot_service: RobotService

    # * attribute: route_planner
    route_planner: RoutePlannerService

    # * attribute: location_service
    location_service: LocationService

    # * init
    def __init__(self,
            robot_service: RobotService,
            route_planner: RoutePlannerService,
            location_service: LocationService,
        ):
        '''
        Initialize the ReturnToWarehouse event.

        :param robot_service: Service for loading and saving robots.
        :type robot_service: RobotService
        :param route_planner: Service for A* search.
        :type route_planner: RoutePlannerService
        :param location_service: Service for loading campus graph data.
        :type location_service: LocationService
        '''

        # Set the service dependencies.
        self.robot_service = robot_service
        self.route_planner = route_planner
        self.location_service = location_service

    # * method: execute
    @DomainEvent.parameters_required(['robot_id'])
    def execute(self,
            robot_id: str,
            **kwargs,
        ) -> Dict[str, Any]:
        '''
        Route a robot back to the Food Warehouse.

        :param robot_id: The robot to return.
        :type robot_id: str
        :param kwargs: Optional 'obstacles' set of blocked edge tuples.
        :type kwargs: dict
        :return: Summary dict with return route details.
        :rtype: Dict[str, Any]
        '''

        # Load the robot and verify it exists.
        robot = self.robot_service.get(robot_id)
        self.verify(
            expression=robot is not None,
            error_code='ROBOT_NOT_FOUND',
            robot_id=robot_id,
        )

        # Verify the robot is NOT at the Food Warehouse.
        self.verify(
            expression=not robot.current_location.is_food_warehouse,
            error_code='ROBOT_ALREADY_AT_WAREHOUSE',
            robot_id=robot_id,
        )

        # Build the campus graph.
        locations = self.location_service.list()
        edges = self.location_service.get_edges()
        loc_map = {
            loc.name: LocationAggregate(**loc.model_dump())
            for loc in locations
        }

        # Find the Food Warehouse in the graph.
        fw_name = next(name for name, loc in loc_map.items() if loc.is_food_warehouse)

        # Plan the A* route back to the Food Warehouse.
        obstacles: Set[Tuple[str, str]] = kwargs.get('obstacles', set())
        start = robot.current_location.name
        print(f'  Robot {robot_id} returning from {start} to {fw_name}')

        path, distance = self.route_planner.find_path(
            start, fw_name, loc_map, edges, obstacles,
        )

        # Simulate energy consumption and update robot.
        if path is not None:
            robot.consume_energy(distance)

        robot.current_location = loc_map[fw_name]
        robot.status = 'idle'
        self.robot_service.save(robot)

        # Print return trace.
        if path is not None:
            print(f'  Route: {" -> ".join(path)} (dist: {distance:.1f})')
        print(f'  Robot {robot_id} returned to {fw_name}, battery: {robot.battery_level:.1f}%')

        # Return the summary.
        return {
            'robot_id': robot_id,
            'path': path,
            'distance': distance if path else 0.0,
            'status': 'complete',
        }


# ** event: charge_robot
class ChargeRobot(DomainEvent):
    '''
    Charge a robot at the Food Warehouse.

    The robot must be at the Food Warehouse. Resets battery to 100%.
    '''

    # * attribute: robot_service
    robot_service: RobotService

    # * init
    def __init__(self, robot_service: RobotService):
        '''
        Initialize the ChargeRobot event.

        :param robot_service: Service for loading and saving robots.
        :type robot_service: RobotService
        '''

        # Set the service dependency.
        self.robot_service = robot_service

    # * method: execute
    @DomainEvent.parameters_required(['robot_id'])
    def execute(self,
            robot_id: str,
            **kwargs,
        ) -> Dict[str, Any]:
        '''
        Charge a robot to full battery.

        :param robot_id: The robot to charge.
        :type robot_id: str
        :param kwargs: Additional keyword arguments.
        :type kwargs: dict
        :return: Summary dict with charge status.
        :rtype: Dict[str, Any]
        '''

        # Load the robot and verify it exists.
        robot = self.robot_service.get(robot_id)
        self.verify(
            expression=robot is not None,
            error_code='ROBOT_NOT_FOUND',
            robot_id=robot_id,
        )

        # Verify the robot is at the Food Warehouse.
        self.verify(
            expression=robot.current_location.is_food_warehouse,
            error_code='ROBOT_NOT_AT_WAREHOUSE',
            robot_id=robot_id,
        )

        # Charge the battery and update status.
        previous_level = robot.battery_level
        robot.battery_level = 100.0
        robot.status = 'idle'
        self.robot_service.save(robot)

        # Print charge trace.
        print(f'  Robot {robot_id} charged: {previous_level:.1f}% -> 100.0%')

        # Return the summary.
        return {
            'robot_id': robot_id,
            'previous_battery': previous_level,
            'battery_level': 100.0,
            'status': 'complete',
        }


# ** event: dispatch_fleet
class DispatchFleet(DomainEvent):
    '''
    Fleet-level round-robin route dispatch (Goal A — Route Optimization).

    Loads all robots and bagged orders, assigns orders to robots via
    round-robin, and plans individual A* routes for each assignment.
    Each robot must have bags loaded or the dispatch fails.
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
            location_service: LocationService,
        ):
        '''
        Initialize the DispatchFleet event.

        :param robot_service: Service for loading and saving robots.
        :type robot_service: RobotService
        :param order_service: Service for loading orders.
        :type order_service: OrderService
        :param route_planner: Service for A* search and replanning.
        :type route_planner: RoutePlannerService
        :param location_service: Service for loading campus graph data.
        :type location_service: LocationService
        '''

        # Set the service dependencies.
        self.robot_service = robot_service
        self.order_service = order_service
        self.route_planner = route_planner
        self.location_service = location_service

    # * method: execute
    def execute(self, **kwargs) -> Dict[str, Any]:
        '''
        Dispatch the fleet with round-robin order assignment.

        :param kwargs: Optional 'obstacles' set of blocked edge tuples.
        :type kwargs: dict
        :return: Summary dict with fleet route details.
        :rtype: Dict[str, Any]
        '''

        # Load fleet and bagged orders.
        robots = self.robot_service.list()
        orders = [o for o in self.order_service.list() if o.status == 'bagged']

        # Build the campus graph once.
        locations = self.location_service.list()
        edges = self.location_service.get_edges()
        loc_map = {
            loc.name: LocationAggregate(**loc.model_dump())
            for loc in locations
        }

        # Initialize obstacles.
        obstacles: Set[Tuple[str, str]] = kwargs.get('obstacles', set())

        # Route each order via round-robin robot assignment.
        total_distance = 0.0
        details = []

        for i, order in enumerate(orders):

            # Round-robin assignment.
            robot = robots[i % len(robots)]
            start = robot.current_location.name
            goal = order.destination

            print(f'\n  [{i+1}/{len(orders)}] Robot {robot.robot_id}: {start} -> {goal} ({order.order_id})')

            # Verify the robot has bags.
            self.verify(
                expression=len(robot.compartments) > 0,
                error_code='ROBOT_NO_BAGS',
                robot_id=robot.robot_id,
            )

            # Plan the A* route.
            path, distance = self.route_planner.find_path(
                start, goal, loc_map, edges, obstacles,
            )

            # Handle no path.
            if path is None:
                print(f'    No path found.')
                details.append({
                    'robot_id': robot.robot_id,
                    'order_id': order.order_id,
                    'path': None,
                    'distance': 0.0,
                    'status': 'no_path',
                })
                continue

            # Attempt obstacle detection and replanning.
            new_path, new_dist, obstacles = self.route_planner.detect_and_replan(
                path, goal, loc_map, edges, obstacles,
            )
            if new_path is not None:
                print(f'    Replanned: {" -> ".join(new_path)} (dist: {new_dist:.1f})')
                path, distance = new_path, new_dist

            # Simulate energy consumption and update robot.
            robot.consume_energy(distance)
            robot.status = 'en_route'
            robot.current_location = loc_map[goal]
            self.robot_service.save(robot)

            total_distance += distance

            print(f'    Route: {" -> ".join(path)} (dist: {distance:.1f})')
            print(f'    Battery: {robot.battery_level:.1f}%')

            details.append({
                'robot_id': robot.robot_id,
                'order_id': order.order_id,
                'path': path,
                'distance': distance,
                'status': 'complete',
            })

        # Print fleet status.
        print(f'\n  Fleet status:')
        for robot in robots:
            print(f'    {robot.format_for_trace()}')

        # Return the summary.
        return {
            'total_distance': total_distance,
            'routes_planned': len(details),
            'details': details,
            'status': 'complete',
        }
