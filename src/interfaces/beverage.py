"""
FOODIE Beverage Service Interface
"""

# *** imports

# ** core
from abc import abstractmethod
from typing import List

# ** infra
from tiferet.interfaces import Service

# ** app
from ..domain import Beverage

# *** interfaces

# ** interface: beverage_service
class BeverageService(Service):
    '''
    Vertical interface for backward-chaining Beverage knowledge base.
    '''

    # * method: exists
    @abstractmethod
    def exists(self, name: str) -> bool:
        '''
        Check if a beverage exists by name.

        :param name: The beverage name.
        :type name: str
        :return: True if the beverage exists.
        :rtype: bool
        '''
        raise NotImplementedError()

    # * method: get
    @abstractmethod
    def get(self, name: str) -> Beverage:
        '''
        Retrieve a beverage by name.

        :param name: The beverage name.
        :type name: str
        :return: The beverage domain object.
        :rtype: Beverage
        '''
        raise NotImplementedError()

    # * method: list
    @abstractmethod
    def list(self) -> List[Beverage]:
        '''
        List all configured beverages.

        :return: List of beverage domain objects.
        :rtype: List[Beverage]
        '''
        raise NotImplementedError()

    # * method: save
    @abstractmethod
    def save(self, beverage: Beverage) -> None:
        '''
        Persist a beverage.

        :param beverage: The beverage to persist.
        :type beverage: Beverage
        '''
        raise NotImplementedError()

    # * method: delete
    @abstractmethod
    def delete(self, name: str) -> None:
        '''
        Delete a beverage by name.

        :param name: The beverage name.
        :type name: str
        '''
        raise NotImplementedError()
