"""
FOODIE Bag Domain Model

Represents a single bag (paper or freezer) that holds Items.
Used by the rule-based FOODIE_BAGGER production system (Goal B).
"""

# *** imports

# ** core
from typing import List

from tiferet import DomainObject, StringType, ListType, IntType

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
    bag_id = StringType(required=True, metadata={'description': 'Unique bag identifier (e.g., bag_1, freezer_bag_2)'})

    # * attribute: bag_type
    bag_type = StringType(
        required=True,
        choices=['paper', 'freezer'],
        metadata={'description': 'Paper for normal items, freezer for frozen items'}
    )

    # * attribute: items
    items = ListType(Item, default=list, metadata={'description': 'Items currently in this bag'})

    # * attribute: max_capacity
    max_capacity = IntType(default=10, metadata={'description': 'Maximum number of items per bag (per project spec)'})

    # * method: new (static)
    @staticmethod
    def new(bag_id: str, bag_type: str = 'paper', items: List[dict] | List[Item] = None, max_capacity: int = 10, **kwargs):
        '''
        Factory for creating a new Bag (Tiferet DomainObject pattern).

        :param bag_id: Unique bag identifier.
        :type bag_id: str
        :param bag_type: 'paper' or 'freezer'.
        :type bag_type: str
        :param items: Initial list of items (dicts or Item instances).
        :type items: list
        '''
        item_objects = []
        if items:
            for item_data in items:
                if isinstance(item_data, dict):
                    item_objects.append(Item.new(**item_data))
                else:
                    item_objects.append(item_data)

        return DomainObject.new(
            model_type=Bag,
            bag_id=bag_id,
            bag_type=bag_type,
            items=item_objects,
            max_capacity=max_capacity,
            **kwargs
        )

    # * method: can_accept_item
    def can_accept_item(self, item: Item) -> bool:
        '''
        Check if this bag can safely accept the given item
        (capacity + fragile no-crush rule).

        :return: True if the item can be added without violating rules.
        :rtype: bool
        '''
        if len(self.items) >= self.max_capacity:
            return False
        # Fragile items cannot be added to a bag that already contains items
        # (prevents crushing)
        if item.is_fragile and len(self.items) > 0:
            return False
        return True

    # * method: add_item
    def add_item(self, item: Item) -> bool:
        '''
        Add an item to the bag if rules allow it.

        :return: True if item was added successfully.
        :rtype: bool
        '''
        if self.can_accept_item(item):
            self.items.append(item)
            return True
        return False

    # * method: format_trace
    def format_trace(self) -> str:
        '''
        Exact format required by the project spec for simulation trace.

        Example: "Put 1-gallon water bottle in bag_1 (paper)."

        :return: Rule-firing trace line.
        :rtype: str
        '''
        item_names = ", ".join(item.format_for_bagger() for item in self.items)
        return f"Bag {self.bag_id} ({self.bag_type}) contains: {item_names} ({len(self.items)}/{self.max_capacity})"