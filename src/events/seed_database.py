"""
FOODIE SeedDatabase Domain Event

Pre-seeds the SQLite database with demo orders and robots.
Clears any existing data to ensure a fresh, repeatable state
for the simulation (Goals A and B).
"""

# *** imports

# ** core
from typing import Dict, Any, List

# ** infra
from tiferet.events import DomainEvent

# ** app
from ..mappers import OrderAggregate, RobotAggregate
from ..interfaces import OrderService, RobotService, ItemService, LocationService

# *** events

# ** event: seed_database
class SeedDatabase(DomainEvent):
    '''
    Event to pre-seed the SQLite database with demo data.

    Clears existing orders and robots, then creates sample orders
    (with items from the menu) and a fleet of robots stationed at
    the Food Warehouse.
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
            location_service: LocationService):
        '''
        Initialize the SeedDatabase event.

        :param order_service: The order service for persisting orders.
        :type order_service: OrderService
        :param robot_service: The robot service for persisting robots.
        :type robot_service: RobotService
        :param item_service: The item service for loading menu items.
        :type item_service: ItemService
        :param location_service: The location service for loading the Food Warehouse.
        :type location_service: LocationService
        '''

        self.order_service = order_service
        self.robot_service = robot_service
        self.item_service = item_service
        self.location_service = location_service

    # * method: execute
    def execute(self, **kwargs) -> Dict[str, Any]:
        '''
        Seed the database with demo orders and robots.

        Clears existing data, then creates three sample orders and
        three robots at the Food Warehouse.

        :param kwargs: Additional keyword arguments.
        :type kwargs: dict
        :return: Summary of seeded data counts.
        :rtype: Dict[str, Any]
        '''

        print('SeedDatabase: Pre-seeding SQLite database with demo data...')
        print()

        # Clear existing orders.
        existing_orders = self.order_service.list()
        for order in existing_orders:
            self.order_service.delete(order.order_id)

        # Clear existing robots.
        existing_robots = self.robot_service.list()
        for robot in existing_robots:
            self.robot_service.delete(robot.robot_id)

        # Load menu items for the first order.
        items = self.item_service.list()

        # Load the Food Warehouse as the starting location for all robots.
        fw = self.location_service.get('FW')

        # Seed orders: ORD-101 has all menu items, ORD-102 and ORD-103 are empty.
        orders = [
            OrderAggregate(order_id='ORD-101', items=items, destination='Building_A'),
            OrderAggregate(order_id='ORD-102', items=[], destination='Building_B'),
            OrderAggregate(order_id='ORD-103', items=[], destination='Dorm_1'),
        ]
        for order in orders:
            self.order_service.save(order)
            print(f'  Seeded order {order.order_id} -> {order.destination} ({len(order.items)} items)')

        print()

        # Seed robots: R1, R2, R3 all start at the Food Warehouse.
        robots = [
            RobotAggregate(robot_id='R1', current_location=fw),
            RobotAggregate(robot_id='R2', current_location=fw),
            RobotAggregate(robot_id='R3', current_location=fw),
        ]
        for robot in robots:
            self.robot_service.save(robot)
            print(f'  Seeded robot {robot.robot_id} at {fw.name}')

        print()
        print(f'SeedDatabase complete: {len(orders)} orders, {len(robots)} robots.')

        return {
            'orders_seeded': len(orders),
            'robots_seeded': len(robots),
            'status': 'complete',
        }
