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
from ..domain import Bag, Item
from ..interfaces import OrderService

# *** events

# ** event: bag_order
class BagOrder(DomainEvent):
    '''
    Forward-chaining event for FOODIE_BAGGER (Goal B).

    Produces the exact rule-firing trace required by the project specification.
    '''

    # * attribute: order_service
    order_service: OrderService

    # * init
    def __init__(self, order_service: OrderService):
        '''
        Initialize the BagOrder event.

        :param order_service: The order service for loading and saving orders.
        :type order_service: OrderService
        '''

        self.order_service = order_service

    # * method: execute
    @DomainEvent.parameters_required(['order_id'])
    def execute(self, order_id: str, **kwargs) -> List[Bag]:
        '''
        Execute the bagging rules on the given order.

        :param order_id: The order identifier to load and bag.
        :type order_id: str
        :param kwargs: Additional keyword arguments.
        :type kwargs: dict
        :return: List of completed Bag objects.
        :rtype: list[Bag]
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

        bags: List[Bag] = []
        current_bag = None
        rule_counter = 1

        def rule_id():
            nonlocal rule_counter
            rid = f'R{rule_counter}'
            rule_counter += 1
            return rid

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

        # Sort items by size priority (large -> medium -> small).
        size_priority = {'large': 0, 'medium': 1, 'small': 2}
        sorted_items = sorted(expanded_items, key=lambda i: size_priority[i.size])

        # Phase tracking for trace output.
        current_phase = None

        for item in sorted_items:

            # Phase announcement.
            if item.size != current_phase:
                current_phase = item.size
                print(f'Rule {rule_id()} says:   Bag {current_phase} items.')

            # Rule: Frozen items always go in a freezer bag.
            if item.is_frozen:
                current_bag = Bag(bag_id=f'freezer_bag_{len(bags)+1}', bag_type='freezer')
                bags.append(current_bag)
                print(f'Rule {rule_id()} says:   Put {item.name} in a freezer bag.')
                current_bag.add_item(item)
                continue

            # Rule: Fragile items start a new bag (prevent crushing).
            if item.is_fragile:
                print(f'Rule {rule_id()} says:   Start a new bag (fragile item).')
                current_bag = Bag(bag_id=f'bag_{len(bags)+1}', bag_type='paper')
                bags.append(current_bag)
                current_bag.add_item(item)
                print(f'Rule {rule_id()} says:   Put {item.name} in {current_bag.bag_id}.')
                # After fragile item, force a new bag for the next item.
                current_bag = None
                continue

            # Rule: Need a new bag if none exists or current is full.
            if current_bag is None or not current_bag.can_accept_item(item):
                if current_bag is not None:
                    print(f'Rule {rule_id()} says:   Start a new bag.')
                current_bag = Bag(bag_id=f'bag_{len(bags)+1}', bag_type='paper')
                bags.append(current_bag)

            # Add item to current bag.
            current_bag.add_item(item)
            print(f'Rule {rule_id()} says:   Put {item.name} in {current_bag.bag_id}.')

        # Update order status to bagged and persist.
        order.status = 'bagged'
        self.order_service.save(order)

        # Summary.
        print()
        print('Bagging complete.')
        for bag in bags:
            print(f'  {bag.format_trace()}')

        return bags
