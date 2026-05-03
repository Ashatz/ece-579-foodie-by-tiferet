"""
FOODIE Bag Mappers

Aggregate and SqlObject for the Bag domain model.
Used for persistence of bagging results in FOODIE_BAGGER (Goal B).
"""

# *** imports

# ** core
import json
from typing import Any, List

# ** infra
from tiferet.mappers import Aggregate, TransferObject

# ** app
from ..domain import Bag, Item

# *** mappers

# ** mapper: bag_aggregate
class BagAggregate(Bag, Aggregate):
    '''
    Aggregate for the Bag domain object.

    Adds validated mutation methods while inheriting all domain behavior.
    '''

    # * method: add_item
    def add_item(self, item: Item) -> bool:
        '''
        Validated mutation: add an item to the bag (calls domain can_accept_item).
        '''
        if self.can_accept_item(item):
            current_items = list(self.items)
            current_items.append(item)
            self.set_attribute('items', current_items)
            return True
        return False

    # * method: clear
    def clear(self) -> None:
        '''
        Clear all items from the bag.
        '''
        self.set_attribute('items', [])

# ** mapper: bag_sql_object
class BagSqlObject(Bag, TransferObject):
    '''
    SqlObject for the Bag domain object (SQLite serialization).

    Nested `items` list is automatically serialized as a JSON string
    (no separate table needed – items are only accessed via Bag root).
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