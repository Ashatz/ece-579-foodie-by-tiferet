"""
FOODIE_BAGGER Low-Level Context

Implements the rule-based forward-chaining production system for bagging items
(Goal B of the project spec).
"""

# *** imports

# ** core
from typing import List, Dict, Any

# ** app
from tiferet.contexts import AppInterfaceContext  # Low-level context base
from ..domain import Item, Bag, Order
from ..events import DomainEvent  # Will call BagOrder event later

# *** contexts

# ** context: bagger_context
class BaggerContext(AppInterfaceContext):
    '''
    Low-level context for the FOODIE_BAGGER rule-based expert module (Goal B).

    Implements the Production System (Lecture 1):
    - Database: current bags and items
    - Operators: bagging rules (large → medium → small, frozen, fragile, capacity)
    - Control Strategy: forward chaining with trace output
    '''

    # * init
    def __init__(self, **kwargs):
        '''
        Initialize the BaggerContext.
        '''
        super().__init__(**kwargs)

    # * method: bag_order
    def bag_order(self, order: Order) -> List[Bag]:
        '''
        Main entry point for bagging an order.

        Produces the exact rule-firing trace required by the project spec.

        :param order: The Order domain object to bag.
        :type order: Order
        :return: List of completed Bag objects.
        :rtype: list[Bag]
        '''
        print("FOODIE_BAGGER forward-chaining production system started...")

        bags: List[Bag] = []
        current_bag = None

        # Sort items by size priority (large → medium → small)
        sorted_items = sorted(order.items, key=lambda i: {'large': 0, 'medium': 1, 'small': 2}[i.size])

        for item in sorted_items:
            # Rule: Large items first
            if item.size == 'large':
                print("Rule Ri says:   Bag large items.")
                if current_bag is None or current_bag.bag_type != 'paper':
                    current_bag = Bag.new(bag_id=f"bag_{len(bags)+1}", bag_type='paper')
                    bags.append(current_bag)
                print(f"Rule Rk says:   Put {item.format_for_bagger()} in {current_bag.bag_id}.")

            # Rule: Frozen items
            elif item.is_frozen:
                print("Rule Ry says:   Put ice cream in a freezer bag.")
                current_bag = Bag.new(bag_id=f"freezer_bag_{len(bags)+1}", bag_type='freezer')
                bags.append(current_bag)

            # Rule: Fragile / new bag
            elif item.is_fragile or (current_bag and not current_bag.can_accept_item(item)):
                print("Rule Rx says:   Start a new bag.")
                current_bag = Bag.new(bag_id=f"bag_{len(bags)+1}", bag_type='paper')
                bags.append(current_bag)

            # Add item to current bag
            current_bag.add_item(item)
            print(f"Rule Rm says:   Put {item.name} in {current_bag.bag_id}.")

        print("Bagging complete.")
        for bag in bags:
            print(bag.format_trace())

        return bags

    # * method: simulate_sample_order
    def simulate_sample_order(self) -> List[Bag]:
        '''
        Convenience method for the exact sample order in the project spec.
        '''
        sample_items = [
            Item.new(name="1-gallon water bottle", size="large", quantity=2),
            Item.new(name="pint ice cream", size="medium", is_frozen=True),
            Item.new(name="granola box", size="medium"),
            Item.new(name="loaf of bread", size="medium"),
        ]
        sample_order = Order.new(order_id="SAMPLE-001", items=sample_items, destination="Demo House")
        return self.bag_order(sample_order)