"""
FOODIE Order Mappers

Aggregate and SqlObject for the Order domain model.
Used for persistence of customer orders, bagging results, and route data (Goals A & B).
"""

# *** imports

# ** core
import json
from typing import Any, List

# ** infra
from tiferet.mappers import Aggregate, TransferObject

# ** app
from ..domain import Order, Bag, Item

# *** mappers

# ** mapper: order_aggregate
class OrderAggregate(Order, Aggregate):
    '''
    Aggregate for the Order domain object.

    Adds validated mutation methods while inheriting all domain behavior.
    '''

    # * method: update_status
    def update_status(self, new_status: str) -> None:
        '''
        Validated mutation: change order status (pending → bagged → en_route → delivered).

        :param new_status: New lifecycle status.
        :type new_status: str
        '''
        self.set_attribute('status', new_status)

    # * method: add_bag
    def add_bag(self, bag: 'Bag') -> None:
        '''
        Add a completed bag to the order (used after FOODIE_BAGGER finishes).
        '''
        # Placeholder – will be expanded when BagAggregate exists
        self.set_attribute('items', self.items + [bag])

# ** mapper: order_sql_object
class OrderSqlObject(Order, TransferObject):
    '''
    SqlObject for the Order domain object (SQLite serialization).

    Nested `items` list is automatically serialized as a JSON string
    (no separate table needed – items are only accessed via Order root).
    '''

    class Options:
        serialize_when_none = False
        roles = {
            'to_data.sqlite': TransferObject.deny('id'),   # id is derived
            'to_model': TransferObject.allow(),
        }

    # * method: to_primitive (override)
    def to_primitive(self, role: str = None, **kwargs) -> dict:
        '''
        Custom serialization for SQLite: convert items list to JSON string.
        '''
        data = super().to_primitive(role, **kwargs)
        if 'items' in data and isinstance(data['items'], list):
            # Serialize nested Items as JSON for SQLite column
            data['items_json'] = json.dumps([item.to_primitive() for item in self.items])
            del data['items']  # remove the original list
        return data

    # * method: from_data (override)
    @classmethod
    def from_data(cls, data: dict, **kwargs):
        '''
        Deserialize from SQLite row: convert items_json back to list of Items.
        '''
        if 'items_json' in data:
            items_data = json.loads(data.pop('items_json'))
            data['items'] = [Item.new(**item) for item in items_data]
        return super().from_data(data, **kwargs)