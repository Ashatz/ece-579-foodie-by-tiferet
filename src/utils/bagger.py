"""
FOODIE Forward-Chain Bagger Utility

Concrete implementation of BaggingService.
Encapsulates the rule-based forward-chaining production system for bagging
(Goal B of the project spec).
"""

# *** imports

# ** core
from typing import List

# ** app
from ..domain import Item
from ..mappers.bag import BagAggregate
from ..interfaces.bagging import BaggingService

# *** utils

# ** util: forward_chain_bagger
class ForwardChainBagger(BaggingService):
    '''
    Forward-chaining production system for bagging items.

    Applies size-priority sorting (large -> medium -> small),
    frozen/fragile/capacity rules, and produces the rule-firing
    trace required by the project specification.
    '''

    # * method: bag_items
    def bag_items(self, items: List[Item]) -> List[BagAggregate]:
        '''
        Apply bagging rules to a flat, pre-expanded list of items.

        :param items: Pre-expanded list of items (quantity=1 each).
        :type items: List[Item]
        :return: Completed list of bags with items assigned.
        :rtype: List[BagAggregate]
        '''

        bags: List[BagAggregate] = []
        current_bag = None
        rule_counter = 1

        def rule_id():
            nonlocal rule_counter
            rid = f'R{rule_counter}'
            rule_counter += 1
            return rid

        # Sort items by size priority (large -> medium -> small).
        size_priority = {'large': 0, 'medium': 1, 'small': 2}
        sorted_items = sorted(items, key=lambda i: size_priority[i.size])

        # Phase tracking for trace output.
        current_phase = None

        for item in sorted_items:

            # Phase announcement.
            if item.size != current_phase:
                current_phase = item.size
                print(f'Rule {rule_id()} says:   Bag {current_phase} items.')

            # Rule: Frozen items always go in a freezer bag.
            if item.is_frozen:
                current_bag = BagAggregate.new_freezer_bag(len(bags) + 1)
                bags.append(current_bag)
                print(f'Rule {rule_id()} says:   Put {item.name} in a freezer bag.')
                current_bag.add_item(item)
                continue

            # Rule: Fragile items start a new bag (prevent crushing).
            if item.is_fragile:
                print(f'Rule {rule_id()} says:   Start a new bag (fragile item).')
                current_bag = BagAggregate.new_fragile_bag(len(bags) + 1)
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
                current_bag = BagAggregate.new_regular_bag(len(bags) + 1)
                bags.append(current_bag)

            # Add item to current bag.
            current_bag.add_item(item)
            print(f'Rule {rule_id()} says:   Put {item.name} in {current_bag.bag_id}.')

        return bags
