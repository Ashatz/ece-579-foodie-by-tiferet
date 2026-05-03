"""
FOODIE Item Service Interface (YAML-backed)
"""

# *** imports

# ** infra
from tiferet.interfaces import Service
from typing import List

# ** app
from ..mappers import ItemAggregate

# *** interfaces

# ** interface: item_service
class ItemService(Service):
    '''
    Vertical interface for universal/config Item data (menu, rules).
    '''

    # * method: exists
    def exists(self, name: str) -> bool: ...

    # * method: get
    def get(self, name: str) -> ItemAggregate: ...

    # * method: list
    def list(self) -> List[ItemAggregate]: ...

    # * method: save
    def save(self, item: ItemAggregate) -> None: ...

    # * method: delete
    def delete(self, name: str) -> None: ...