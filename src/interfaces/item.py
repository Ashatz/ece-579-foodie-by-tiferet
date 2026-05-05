"""
FOODIE Item Service Interface
"""

# *** imports

# ** core
from abc import abstractmethod
from typing import List

# ** infra
from tiferet.interfaces import Service

# ** app
from ..domain import Item

# *** interfaces

# ** interface: item_service
class ItemService(Service):
    '''
    Vertical interface for universal/config Item data (menu, rules).
    '''

    # * method: exists
    @abstractmethod
    def exists(self, name: str) -> bool:
        '''
        Check if an item exists by name.

        :param name: The item name.
        :type name: str
        :return: True if the item exists.
        :rtype: bool
        '''
        raise NotImplementedError()

    # * method: get
    @abstractmethod
    def get(self, name: str) -> Item:
        '''
        Retrieve an item by name.

        :param name: The item name.
        :type name: str
        :return: The item domain object.
        :rtype: Item
        '''
        raise NotImplementedError()

    # * method: list
    @abstractmethod
    def list(self) -> List[Item]:
        '''
        List all configured items.

        :return: List of item domain objects.
        :rtype: List[Item]
        '''
        raise NotImplementedError()

    # * method: save
    @abstractmethod
    def save(self, item: Item) -> None:
        '''
        Persist an item.

        :param item: The item to persist.
        :type item: Item
        '''
        raise NotImplementedError()

    # * method: delete
    @abstractmethod
    def delete(self, name: str) -> None:
        '''
        Delete an item by name.

        :param name: The item name.
        :type name: str
        '''
        raise NotImplementedError()
