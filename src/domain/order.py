"""
FOODIE Order Domain Model

Represents a customer order containing multiple Items.
Used by FOODIE_BAGGER (Goal B), route planning (Goal A), and simulation.
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

# ** model: order
class Order(DomainObject):
    '''
    A customer food order for delivery.

    Contains a list of Items and delivery metadata.
    Serves as the central "fact" in the Production System (Lecture 1)
    for bagging rules and route optimization.
    '''

    # * attribute: order_id
    order_id: str = Field(..., description='Unique order identifier')

    # * attribute: items
    items: List[Item] = Field(default_factory=list, description='List of food items in this order')

    # * attribute: destination
    destination: str = Field(..., description='Delivery location on campus (e.g., Building A)')

    # * attribute: status
    status: Literal['pending', 'bagged', 'en_route', 'delivered'] = Field(
        default='pending',
        description='Current order lifecycle status',
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

        # Build comma-separated item list.
        item_list = ', '.join(item.format_for_bagger() for item in self.items)
        return f'Order {self.order_id} -> {self.destination} | Items: {item_list} (total: {self.total_items()})'
