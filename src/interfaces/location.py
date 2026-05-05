"""
FOODIE Location Service Interface
"""

# *** imports

# ** core
from abc import abstractmethod
from typing import Dict, List

# ** infra
from tiferet.interfaces import Service

# ** app
from ..domain import Location

# *** interfaces

# ** interface: location_service
class LocationService(Service):
    '''
    Vertical interface for campus terrain Location data.
    '''

    # * method: exists
    @abstractmethod
    def exists(self, name: str) -> bool:
        '''
        Check if a location exists by name.

        :param name: The location name.
        :type name: str
        :return: True if the location exists.
        :rtype: bool
        '''
        raise NotImplementedError()

    # * method: get
    @abstractmethod
    def get(self, name: str) -> Location:
        '''
        Retrieve a location by name.

        :param name: The location name.
        :type name: str
        :return: The location domain object.
        :rtype: Location
        '''
        raise NotImplementedError()

    # * method: list
    @abstractmethod
    def list(self) -> List[Location]:
        '''
        List all locations.

        :return: List of location domain objects.
        :rtype: List[Location]
        '''
        raise NotImplementedError()

    # * method: save
    @abstractmethod
    def save(self, location: Location) -> None:
        '''
        Persist a location.

        :param location: The location to persist.
        :type location: Location
        '''
        raise NotImplementedError()

    # * method: delete
    @abstractmethod
    def delete(self, name: str) -> None:
        '''
        Delete a location by name.

        :param name: The location name.
        :type name: str
        '''
        raise NotImplementedError()

    # * method: get_edges
    @abstractmethod
    def get_edges(self) -> Dict[str, List[str]]:
        '''
        Retrieve the campus graph adjacency list.

        :return: Dict mapping location names to lists of neighbor names.
        :rtype: Dict[str, List[str]]
        '''
        raise NotImplementedError()
