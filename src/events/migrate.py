"""
FOODIE SeedDatabase Domain Event

Idempotent database seeding operation that pre-populates the SQLite
database with demo orders and robots before the simulation runs.
Prerequisite for Goal A (route planning) and Goal B (bagging).
"""

# *** imports

# ** core
from typing import Any, Dict, List

# ** infra
from tiferet.events import DomainEvent

# ** app
from ..interfaces.order import OrderService
from ..interfaces.robot import RobotService
from ..interfaces.item import ItemService
from ..interfaces.location import LocationService
from ..mappers.order import OrderAggregate
from ..mappers.robot import RobotAggregate

# *** events

# ** event: seed_database
class SeedDatabase(DomainEvent):
    '''
    Idempotent database seeding event.

    Clears existing orders and robots, then seeds 3 demo orders
    and 3 robots stationed at the Food Warehouse. Demonstrates
    Tiferet's multi-service dependency injection pattern.
    '''

    # * attribute: order_service
    order_service: OrderService

    # * attribute: robot_service
    robot_service: RobotService

    # * attribute: item_service
    item_service: ItemService

    # * attribute: location_service
    location_service: LocationService

    # * init
    def __init__(self,
            order_service: OrderService,
            robot_service: RobotService,
            item_service: ItemService,
            location_service: LocationService,
        ):
        '''
        Initialize the SeedDatabase event.

        :param order_service: Service for persisting and clearing orders.
        :type order_service: OrderService
        :param robot_service: Service for persisting and clearing robots.
        :type robot_service: RobotService
        :param item_service: Service for loading the menu catalog.
        :type item_service: ItemService
        :param location_service: Service for loading campus locations.
        :type location_service: LocationService
        '''

        # Set the service dependencies.
        self.order_service = order_service
        self.robot_service = robot_service
        self.item_service = item_service
        self.location_service = location_service

    # * method: execute
    def execute(self, **kwargs) -> Dict[str, Any]:
        '''
        Seed the database with demo orders and robots.

        Idempotent: clears all existing data before seeding.

        :param kwargs: Additional keyword arguments (unused).
        :type kwargs: dict
        :return: Summary dict with counts and status.
        :rtype: Dict[str, Any]
        '''

        # Clear existing orders.
        existing_orders = self.order_service.list()
        for order in existing_orders:
            self.order_service.delete(order.order_id)

        # Clear existing robots.
        existing_robots = self.robot_service.list()
        for robot in existing_robots:
            self.robot_service.delete(robot.robot_id)

        # Load the Food Warehouse location.
        food_warehouse = self.location_service.get('FW')

        # Seed 3 robots at the Food Warehouse.
        robots = [
            RobotAggregate(
                robot_id='R1',
                current_location=food_warehouse,
            ),
            RobotAggregate(
                robot_id='R2',
                current_location=food_warehouse,
            ),
            RobotAggregate(
                robot_id='R3',
                current_location=food_warehouse,
            ),
        ]

        for robot in robots:
            self.robot_service.save(robot)
            print(f'  Seeded robot: {robot.robot_id} at {food_warehouse.name}')

        # Return the seeding summary.
        return {
            'robots_seeded': len(robots),
            'status': 'complete',
        }
