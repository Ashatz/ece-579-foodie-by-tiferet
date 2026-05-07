"""
FOODIE Order Domain Events

Domain events that orchestrate order operations: beverage selection
via backward chaining and order-type management.
"""

# *** imports

# ** core
from typing import Any, Dict, List

# ** infra
from tiferet.events import DomainEvent

# ** app
from ..interfaces.order import OrderService
from ..interfaces.robot import RobotService
from ..interfaces.beverage import BeverageService
from ..interfaces.beverage_select import BeverageSelectService
from ..mappers.beverage import BeverageAggregate
from ..mappers.bag import BagAggregate
from ..assets.beverage import BEVERAGE_RULES, FALLBACK_BEVERAGE

# *** events

# ** event: select_beverage
class SelectBeverage(DomainEvent):
    '''
    Backward-chaining beverage selection event (Goal C — FOODIE_SPA).

    Loads a beverage order and a robot, runs backward-chaining inference
    to select the best beverage for the guest, creates a beverage bag,
    and loads it onto the robot. Falls back to Sparkling Water if no
    rule fires.
    '''

    # * attribute: order_service
    order_service: OrderService

    # * attribute: robot_service
    robot_service: RobotService

    # * attribute: beverage_service
    beverage_service: BeverageService

    # * attribute: beverage_select_service
    beverage_select_service: BeverageSelectService

    # * init
    def __init__(self,
            order_service: OrderService,
            robot_service: RobotService,
            beverage_service: BeverageService,
            beverage_select_service: BeverageSelectService,
        ):
        '''
        Initialize the SelectBeverage event.

        :param order_service: Service for loading and saving orders.
        :type order_service: OrderService
        :param robot_service: Service for loading and saving robots.
        :type robot_service: RobotService
        :param beverage_service: Service for loading candidate beverages.
        :type beverage_service: BeverageService
        :param beverage_select_service: Service for backward-chaining inference.
        :type beverage_select_service: BeverageSelectService
        '''

        # Set the service dependencies.
        self.order_service = order_service
        self.robot_service = robot_service
        self.beverage_service = beverage_service
        self.beverage_select_service = beverage_select_service

    # * method: execute
    @DomainEvent.parameters_required(['robot_id', 'order_id'])
    def execute(self,
            robot_id: str,
            order_id: str,
            **kwargs,
        ) -> Dict[str, Any]:
        '''
        Select a beverage and load it onto a robot for delivery.

        :param robot_id: The robot to load the beverage onto.
        :type robot_id: str
        :param order_id: The beverage order to fulfill.
        :type order_id: str
        :param kwargs: Optional 'facts' dict or list of key=value strings.
        :type kwargs: dict
        :return: Summary dict with selection result.
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

        # Verify the robot has no item bags (exclusive transport).
        self.verify(
            expression=all(b.bag_type == 'beverage' or b.bag_type not in ('paper', 'freezer') for b in robot.compartments)
                if robot.compartments else True,
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

        # Verify the order is a beverage order.
        self.verify(
            expression=order.order_type == 'beverage',
            error_code='ORDER_TYPE_MISMATCH',
            order_id=order_id,
            expected='beverage',
            actual=order.order_type,
        )

        # Load candidate beverages from the knowledge base.
        candidates = self.beverage_service.list()

        # Parse facts from kwargs.
        facts = kwargs.get('facts', {})
        if isinstance(facts, list):
            parsed = {}
            for fact_str in facts:
                key, value = fact_str.split('=', 1)
                if value == 'True':
                    value = True
                elif value == 'False':
                    value = False
                parsed[key] = value
            facts = parsed

        print(f'\n  Selecting beverage for order {order_id} (Robot {robot_id})')
        print(f'  Guest facts: {facts}')

        # Delegate backward-chaining inference.
        selected = self.beverage_select_service.select(
            candidates, facts, BEVERAGE_RULES,
        )

        # Fall back to safe default if no rule fires.
        if selected is None:
            selected = BeverageAggregate(**FALLBACK_BEVERAGE)
            print(f'  No rule fired — fallback: {selected.name} ({selected.brand})')
        else:
            print(f'  Selected: {selected.format_for_trace()}')

        # Create a beverage bag and load onto the robot.
        bev_bag = BagAggregate(bag_id=f'bev_{order_id}', bag_type='beverage')
        robot.load_bag(bev_bag)

        # Update order status to bagged and persist.
        order.status = 'bagged'
        self.order_service.save(order)

        # Persist the updated robot.
        self.robot_service.save(robot)

        # Print summary.
        print(f'  Beverage bag loaded onto Robot {robot_id}')

        # Return the summary.
        return {
            'robot_id': robot_id,
            'order_id': order_id,
            'beverage': selected.name,
            'brand': selected.brand,
            'status': 'complete',
        }
