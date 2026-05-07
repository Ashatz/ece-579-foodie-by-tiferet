"""
FOODIE Order Service Interface
"""

# *** imports

# ** core
from abc import abstractmethod
from typing import List

# ** infra
from tiferet.interfaces import Service

# ** app
from ..domain import Order

# *** interfaces

# ** interface: order_service
class OrderService(Service):
    '''
    Vertical interface for instance-specific Order data.
    '''

    # * method: exists
    @abstractmethod
    def exists(self, order_id: str) -> bool:
        '''
        Check if an order exists by ID.

        :param order_id: The order identifier.
        :type order_id: str
        :return: True if the order exists.
        :rtype: bool
        '''
        raise NotImplementedError()

    # * method: get
    @abstractmethod
    def get(self, order_id: str) -> Order:
        '''
        Retrieve an order by ID.

        :param order_id: The order identifier.
        :type order_id: str
        :return: The order domain object.
        :rtype: Order
        '''
        raise NotImplementedError()

    # * method: list
    @abstractmethod
    def list(self) -> List[Order]:
        '''
        List all orders.

        :return: List of order domain objects.
        :rtype: List[Order]
        '''
        raise NotImplementedError()

    # * method: save
    @abstractmethod
    def save(self, order: Order) -> None:
        '''
        Persist an order.

        :param order: The order to persist.
        :type order: Order
        '''
        raise NotImplementedError()

    # * method: delete
    @abstractmethod
    def delete(self, order_id: str) -> None:
        '''
        Delete an order by ID.

        :param order_id: The order identifier.
        :type order_id: str
        '''
        raise NotImplementedError()
