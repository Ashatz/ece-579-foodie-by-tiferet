"""
FOODIE Order Domain Model

Represents a customer order containing multiple Items.
Used by FOODIE_BAGGER (Goal B), route planning (Goal A), and simulation.
"""

# *** imports

# ** core
from typing import List

from tiferet import DomainObject, StringType, ListType

# ** app
from .item import Item

# *** models

# ** model: order
class Order(DomainObject):
    '''
    A customer food order for delivery.

    Contains a list of Items and delivery metadata.
    Serves as the central "fact" in the Production System (Lecture 1)
    for bagging rules and route optimization.
    '''

    # * attribute: order_id
    order_id = StringType(required=True, metadata={'description': 'Unique order identifier'})

    # * attribute: items
    items = ListType(Item, default=list, metadata={'description': 'List of food items in this order'})

    # * attribute: destination
    destination = StringType(required=True, metadata={'description': 'Delivery location on campus (e.g., Building A, Dorm 5)'})

    # * attribute: status
    status = StringType(
        default='pending',
        choices=['pending', 'bagged', 'en_route', 'delivered'],
        metadata={'description': 'Current order lifecycle status'}
    )

    # * method: new (static)
    @staticmethod
    def new(order_id: str, items: List[dict] | List[Item], destination: str, status: str = 'pending', **kwargs):
        '''
        Factory for creating a new Order (Tiferet DomainObject pattern).

        Accepts raw dicts for items and converts them via Item.new().

        :param order_id: Unique order identifier.
        :type order_id: str
        :param items: List of item data (dicts or Item instances).
        :type items: list
        :param destination: Delivery location.
        :type destination: str
        '''
        # Convert raw item dicts to Item domain objects
        item_objects = []
        for item_data in items:
            if isinstance(item_data, dict):
                item_objects.append(Item.new(**item_data))
            else:
                item_objects.append(item_data)

        return DomainObject.new(
            model_type=Order,
            order_id=order_id,
            items=item_objects,
            destination=destination,
            status=status,
            **kwargs
        )

    # * method: total_items
    def total_items(self) -> int:
        '''
        Return the total number of individual items in the order.

        :return: Sum of all item quantities.
        :rtype: int
        '''
        return sum(item.quantity for item in self.items)

    # * method: format_for_bagger
    def format_for_bagger(self) -> str:
        '''
        Human-readable summary for FOODIE_BAGGER simulation trace (Goal B).

        :return: Formatted order description.
        :rtype: str
        '''
        item_list = ", ".join(item.format_for_bagger() for item in self.items)
        return f"Order {self.order_id} → {self.destination} | Items: {item_list} (total: {self.total_items()})"