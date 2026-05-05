"""
FOODIE BagOrder Domain Event

Implements the rule-based forward-chaining production system for bagging
(Goal B of the project spec).

Production System (Lecture 1):
- Database: current bags and unbagged items
- Operators: bagging rules (large -> medium -> small, frozen, fragile, capacity)
- Control Strategy: forward chaining with priority ordering and trace output
"""

# *** imports

# ** core
from typing import List

# ** infra
from tiferet.events import DomainEvent

# ** app
from ..domain import Item
from ..mappers.bag import BagAggregate
from ..interfaces import OrderService
from ..interfaces.bagging import BaggingService

# *** events

# ** event: bag_order
class BagOrder(DomainEvent):
    '''
    Forward-chaining event for FOODIE_BAGGER (Goal B).

    Loads the order, expands items by quantity, and delegates
    the forward-chaining production system to an injected BaggingService.
    '''

    # * attribute: order_service
    order_service: OrderService

    # * attribute: bagging_service
    bagging_service: BaggingService

    # * init
    def __init__(self, order_service: OrderService, bagging_service: BaggingService):
        '''
        Initialize the BagOrder event.

        :param order_service: The order service for loading and saving orders.
        :type order_service: OrderService
        :param bagging_service: The bagging service for forward-chaining bag assignment.
        :type bagging_service: BaggingService
        '''

        self.order_service = order_service
        self.bagging_service = bagging_service

    # * method: execute
    @DomainEvent.parameters_required(['order_id'])
    def execute(self, order_id: str, **kwargs) -> List[BagAggregate]:
        '''
        Execute the bagging rules on the given order.

        :param order_id: The order identifier to load and bag.
        :type order_id: str
        :param kwargs: Additional keyword arguments.
        :type kwargs: dict
        :return: List of completed BagAggregate objects.
        :rtype: list[BagAggregate]
        '''

        # Load the order from the service.
        order = self.order_service.get(order_id)

        # Verify the order exists.
        self.verify(
            expression=order is not None,
            error_code='ORDER_NOT_FOUND',
            order_id=order_id,
        )

        print('FOODIE_BAGGER forward-chaining production system started...')
        print(f'Order: {order.format_for_bagger()}')
        print()

        # Expand items by quantity so each physical item is bagged individually.
        expanded_items: List[Item] = []
        for item in order.items:
            for _ in range(item.quantity):
                expanded_items.append(Item(
                    name=item.name,
                    size=item.size,
                    is_frozen=item.is_frozen,
                    is_fragile=item.is_fragile,
                    quantity=1,
                ))

        # Delegate forward-chaining bagging to the bagging service.
        bags = self.bagging_service.bag_items(expanded_items)

        # Update order status to bagged and persist.
        order.status = 'bagged'
        self.order_service.save(order)

        # Summary.
        print()
        print('Bagging complete.')
        for bag in bags:
            print(f'  {bag.format_trace()}')

        return bags
