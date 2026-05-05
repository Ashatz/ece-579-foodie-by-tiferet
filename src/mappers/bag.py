"""
FOODIE Bag Mappers

Aggregate for the Bag domain model.
Provides typed factory methods for the forward-chaining bagger (Goal B).
"""

# *** imports

# ** infra
from tiferet.mappers import Aggregate

# ** app
from ..domain import Bag

# *** mappers

# ** mapper: bag_aggregate
class BagAggregate(Bag, Aggregate):
    '''
    Aggregate for the Bag domain object.

    Provides static factory methods that encapsulate bag-type derivation
    logic for the FOODIE_BAGGER production system.
    '''

    # * method: new_freezer_bag (static)
    @staticmethod
    def new_freezer_bag(bag_number: int) -> 'BagAggregate':
        '''
        Create a freezer bag for frozen items.

        :param bag_number: Sequential bag number for ID generation.
        :type bag_number: int
        :return: A new freezer BagAggregate.
        :rtype: BagAggregate
        '''

        return BagAggregate(
            bag_id=f'freezer_bag_{bag_number}',
            bag_type='freezer',
        )

    # * method: new_fragile_bag (static)
    @staticmethod
    def new_fragile_bag(bag_number: int) -> 'BagAggregate':
        '''
        Create a paper bag for a fragile item.

        :param bag_number: Sequential bag number for ID generation.
        :type bag_number: int
        :return: A new paper BagAggregate for fragile items.
        :rtype: BagAggregate
        '''

        return BagAggregate(
            bag_id=f'bag_{bag_number}',
            bag_type='paper',
        )

    # * method: new_regular_bag (static)
    @staticmethod
    def new_regular_bag(bag_number: int) -> 'BagAggregate':
        '''
        Create a standard paper bag for regular items.

        :param bag_number: Sequential bag number for ID generation.
        :type bag_number: int
        :return: A new paper BagAggregate.
        :rtype: BagAggregate
        '''

        return BagAggregate(
            bag_id=f'bag_{bag_number}',
            bag_type='paper',
        )
