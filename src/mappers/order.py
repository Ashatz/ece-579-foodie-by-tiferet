"""
FOODIE Order Mappers

Aggregate and SqlObject for the Order domain model.
Used for persistence of customer orders, bagging results, and route data.
"""

# *** imports

# ** core
import json
from typing import Any, ClassVar, Dict, List

# ** infra
from tiferet.mappers import Aggregate, TransferObject

# ** app
from ..domain import Order, Item

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
        Change order status (pending → bagged → en_route → delivered).

        :param new_status: New lifecycle status.
        :type new_status: str
        '''

        self.status = new_status


# ** mapper: order_sql_object
class OrderSqlObject(Order, TransferObject):
    '''
    SqlObject for the Order domain object (SQLite serialization).

    Nested items list is serialized as a JSON string for storage
    in a single SQLite column.
    '''

    # * attribute: _ROLES
    _ROLES: ClassVar[Dict[str, Dict[str, Any]]] = {
        'to_model': {'exclude': {'items'}},
        'to_data.sqlite': {'exclude': {'items'}},
    }

    # * method: to_primitive
    def to_primitive(self, role: str = None, **overrides) -> dict:
        '''
        Custom serialization for SQLite: convert items list to JSON string.

        :param role: The serialization role to apply.
        :type role: str
        :param overrides: Additional keyword arguments.
        :type overrides: dict
        :return: Serialized dictionary with items_json column.
        :rtype: dict
        '''

        # Delegate to base for standard field serialization.
        data = super().to_primitive(role, **overrides)

        # Only add items_json for the sqlite serialization role.
        if role == 'to_data.sqlite':
            data['items_json'] = json.dumps(
                [item.model_dump() for item in self.items]
            )

        return data

    # * method: map
    def map(self, target: type = None, **overrides) -> OrderAggregate:
        '''
        Map the SQL transfer object to an OrderAggregate.

        :param target: The aggregate class (defaults to OrderAggregate).
        :type target: type
        :param overrides: Additional keyword arguments.
        :type overrides: dict
        :return: An OrderAggregate instance.
        :rtype: OrderAggregate
        '''

        # Pass items through since from_data already deserialized them.
        return super().map(
            target or OrderAggregate,
            items=list(self.items),
            **overrides,
        )

    # * method: from_data
    @classmethod
    def from_data(cls, data: dict, **overrides) -> 'OrderSqlObject':
        '''
        Create an OrderSqlObject from a raw SQLite row dict.

        Parses items_json into Item domain objects before validation.

        :param data: The raw row dict from SQLite.
        :type data: dict
        :param overrides: Additional keyword arguments.
        :type overrides: dict
        :return: An OrderSqlObject instance.
        :rtype: OrderSqlObject
        '''

        # Extract and deserialize items_json into domain objects.
        items_json = data.pop('items_json', '[]')
        data['items'] = [Item(**item_data) for item_data in json.loads(items_json)]

        # Apply overrides and validate.
        data.update(overrides)
        return cls.model_validate(data)

    # * method: from_model
    @classmethod
    def from_model(cls, order: Order, **overrides) -> 'OrderSqlObject':
        '''
        Create an OrderSqlObject from an Order model.

        :param order: The source Order instance.
        :type order: Order
        :param overrides: Additional keyword arguments.
        :type overrides: dict
        :return: An OrderSqlObject instance.
        :rtype: OrderSqlObject
        '''

        return super().from_model(order, **overrides)
