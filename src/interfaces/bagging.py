"""
FOODIE Bagging Service Interface
"""

# *** imports

# ** core
from abc import abstractmethod
from typing import List

# ** infra
from tiferet.interfaces import Service

# ** app
from ..domain import Item
from ..mappers.bag import BagAggregate

# *** interfaces

# ** interface: bagging_service
class BaggingService(Service):
    '''
    Vertical interface for the forward-chaining bagging production system.
    '''

    # * method: bag_items
    @abstractmethod
    def bag_items(self, items: List[Item]) -> List[BagAggregate]:
        '''
        Apply bagging rules to a flat, pre-expanded list of items.

        Implementations handle size-priority sorting, frozen/fragile/capacity
        logic, and rule-firing trace output.

        :param items: Pre-expanded list of items (quantity=1 each).
        :type items: List[Item]
        :return: Completed list of bags with items assigned.
        :rtype: List[BagAggregate]
        '''
        raise NotImplementedError()
