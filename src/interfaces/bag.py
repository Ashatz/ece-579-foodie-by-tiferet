"""
FOODIE Bag Service Interface (SQLite-backed)
"""

# *** imports

# ** infra
from tiferet.interfaces import Service
from typing import List

# ** app
from ..mappers import BagAggregate

# *** interfaces

# ** interface: bag_service
class BagService(Service):
    '''
    Vertical interface for instance-specific Bag data (bagging sessions).
    '''

    # * method: exists
    def exists(self, bag_id: str) -> bool: ...

    # * method: get
    def get(self, bag_id: str) -> BagAggregate: ...

    # * method: list
    def list(self) -> List[BagAggregate]: ...

    # * method: save
    def save(self, bag: BagAggregate) -> None: ...

    # * method: delete
    def delete(self, bag_id: str) -> None: ...