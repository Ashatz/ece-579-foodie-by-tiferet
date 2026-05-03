"""
FOODIE Location Service Interface (SQLite-backed)
"""

# *** imports

# ** infra
from tiferet.interfaces import Service
from typing import List

# ** app
from ..mappers import LocationAggregate

# *** interfaces

# ** interface: location_service
class LocationService(Service):
    '''
    Vertical interface for campus terrain Location data.
    '''

    # * method: exists
    def exists(self, name: str) -> bool: ...

    # * method: get
    def get(self, name: str) -> LocationAggregate: ...

    # * method: list
    def list(self) -> List[LocationAggregate]: ...

    # * method: save
    def save(self, location: LocationAggregate) -> None: ...

    # * method: delete
    def delete(self, name: str) -> None: ...