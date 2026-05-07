"""
FOODIE Bag Domain Model

Represents a single bag (paper or freezer) that holds Items.
Used by the rule-based FOODIE_BAGGER production system (Goal B).
"""

# *** imports

# ** core
from typing import Literal, List

# ** infra
from pydantic import Field
from tiferet import DomainObject

# ** app
from .item import Item

# *** models

# ** model: bag
class Bag(DomainObject):
    '''
    A physical bag used by FOODIE_BAGGER.

    Enforces bagging rules: large/medium/small ordering,
    frozen items use freezer bags, fragile items start new bags,
    capacity limits, and no-crush constraints.
    '''

    # * attribute: bag_id
    bag_id: str = Field(..., description='Unique bag identifier (e.g., bag_1, freezer_bag_2)')

    # * attribute: bag_type
    bag_type: Literal['paper', 'freezer', 'beverage'] = Field(
        default='paper',
        description='Paper for normal items, freezer for frozen, beverage for drink orders',
    )

    # * attribute: items
    items: List[Item] = Field(default_factory=list, description='Items currently in this bag')

    # * attribute: max_capacity
    max_capacity: int = Field(default=10, description='Maximum number of items per bag (per project spec)')

    # * method: can_accept_item
    def can_accept_item(self, item: Item) -> bool:
        '''
        Check if this bag can safely accept the given item
        (capacity + fragile no-crush rule).

        :param item: The item to check.
        :type item: Item
        :return: True if the item can be added without violating rules.
        :rtype: bool
        '''

        # Check capacity.
        if len(self.items) >= self.max_capacity:
            return False

        # Fragile items cannot be added to a bag that already has items (prevents crushing).
        if item.is_fragile and len(self.items) > 0:
            return False

        return True

    # * method: add_item
    def add_item(self, item: Item) -> bool:
        '''
        Add an item to the bag if rules allow it.

        :param item: The item to add.
        :type item: Item
        :return: True if item was added successfully.
        :rtype: bool
        '''

        # Check rules then append via list reassignment (pydantic).
        if self.can_accept_item(item):
            self.items = self.items + [item]
            return True
        return False

    # * method: format_trace
    def format_trace(self) -> str:
        '''
        Exact format required by the project spec for simulation trace.

        :return: Rule-firing trace line.
        :rtype: str
        '''

        # Build a comma-separated list of item descriptions.
        item_names = ', '.join(item.format_for_bagger() for item in self.items)
        return f'Bag {self.bag_id} ({self.bag_type}) contains: {item_names} ({len(self.items)}/{self.max_capacity})'
