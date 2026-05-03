"""
FOODIE Order Service Interface (SQLite-backed)
"""

# *** imports

# ** infra
from tiferet.interfaces import Service
from typing import List

# ** app
from ..mappers import OrderAggregate

# *** interfaces

# ** interface: order_service
class OrderService(Service):
    '''
    Vertical interface for instance-specific Order data.
    '''

    # * method: exists
    def exists(self, order_id: str) -> bool: ...

    # * method: get
    def get(self, order_id: str) -> OrderAggregate: ...

    # * method: list
    def list(self) -> List[OrderAggregate]: ...

    # * method: save
    def save(self, order: OrderAggregate) -> None: ...

    # * method: delete
    def delete(self, order_id: str) -> None: ...