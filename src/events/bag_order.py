"""
FOODIE BagOrder Domain Event

Implements the rule-based forward-chaining production system for bagging
(Goal B of the project spec).
"""

# *** imports

# ** core
from typing import List

# ** infra
from tiferet.events import DomainEvent

# ** app
from ..interfaces import BagService, ItemService
from ..domain import Order, Bag

# *** events

# ** event: bag_order
class BagOrder(DomainEvent):
    '''
    Forward-chaining event for FOODIE_BAGGER (Goal B).

    Produces the exact rule-firing trace required by the project specification.
    '''

    # * attribute: bag_service
    bag_service: BagService

    # * attribute: item_service
    item_service: ItemService

    # * init
    def __init__(self, bag_service: BagService, item_service: ItemService):
        self.bag_service = bag_service
        self.item_service = item_service

    # * method: execute
    @DomainEvent.parameters_required(['order'])
    def execute(self, **kwargs) -> List[Bag]:
        '''
        Execute the bagging rules on the given order.
        '''
        order: Order = kwargs['order']
        print("FOODIE_BAGGER forward-chaining production system started...")

        bags: List[Bag] = []
        current_bag = None

        sorted_items = sorted(order.items, key=lambda i: {'large': 0, 'medium': 1, 'small': 2}[i.size])

        for item in sorted_items:
            if item.size == 'large':
                print("Rule Ri says:   Bag large items.")
                if current_bag is None or current_bag.bag_type != 'paper':
                    current_bag = Bag.new(bag_id=f"bag_{len(bags)+1}", bag_type='paper')
                    bags.append(current_bag)
                print(f"Rule Rk says:   Put {item.format_for_bagger()} in {current_bag.bag_id}.")

            elif item.is_frozen:
                print("Rule Ry says:   Put ice cream in a freezer bag.")
                current_bag = Bag.new(bag_id=f"freezer_bag_{len(bags)+1}", bag_type='freezer')
                bags.append(current_bag)

            elif item.is_fragile or (current_bag and not current_bag.can_accept_item(item)):
                print("Rule Rx says:   Start a new bag.")
                current_bag = Bag.new(bag_id=f"bag_{len(bags)+1}", bag_type='paper')
                bags.append(current_bag)

            current_bag.add_item(item)
            print(f"Rule Rm says:   Put {item.name} in {current_bag.bag_id}.")

        print("Bagging complete.")
        for bag in bags:
            print(bag.format_trace())

        # Persist the bags
        for bag in bags:
            self.bag_service.save(bag)

        return bags