"""
FOODIE Robot Domain Events

Domain events that orchestrate robot operations: bagging orders,
loading compartments, and managing robot state.
"""

# *** imports

# ** core
from typing import Any, Dict, List

# ** infra
from tiferet.events import DomainEvent

# ** app
from ..domain import Item
from ..interfaces.order import OrderService
from ..interfaces.robot import RobotService
from ..interfaces.bagging import BaggingService
from ..mappers.bag import BagAggregate

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

        # Load the order and verify it exists.
        order = self.order_service.get(order_id)
        self.verify(
            expression=order is not None,
            error_code='ORDER_NOT_FOUND',
            order_id=order_id,
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
