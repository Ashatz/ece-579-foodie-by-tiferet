"""
FOODIE Beverage Service Interface (SQLite-backed)
"""

# *** imports

# ** infra
from tiferet.interfaces import Service
from typing import List

# ** app
from ..mappers import BeverageAggregate

# *** interfaces

# ** interface: beverage_service
class BeverageService(Service):
    '''
    Vertical interface for backward-chaining Beverage knowledge base.
    '''

    # * method: exists
    def exists(self, name: str) -> bool: ...

    # * method: get
    def get(self, name: str) -> BeverageAggregate: ...

    # * method: list
    def list(self) -> List[BeverageAggregate]: ...

    # * method: save
    def save(self, beverage: BeverageAggregate) -> None: ...

    # * method: delete
    def delete(self, name: str) -> None: ...