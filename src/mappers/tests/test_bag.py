"""
FOODIE BagAggregate Mapper Tests
"""

# *** imports

# ** infra
import pytest

# ** app
from ..bag import BagAggregate

# *** tests

# ** test: new_freezer_bag
def test_new_freezer_bag() -> None:
    '''
    Test that new_freezer_bag creates a freezer bag with correct attributes.
    '''

    bag = BagAggregate.new_freezer_bag(3)

    assert bag.bag_id == 'freezer_bag_3'
    assert bag.bag_type == 'freezer'
    assert bag.items == []
    assert bag.max_capacity == 10


# ** test: new_fragile_bag
def test_new_fragile_bag() -> None:
    '''
    Test that new_fragile_bag creates a paper bag with correct attributes.
    '''

    bag = BagAggregate.new_fragile_bag(5)

    assert bag.bag_id == 'bag_5'
    assert bag.bag_type == 'paper'
    assert bag.items == []
    assert bag.max_capacity == 10


# ** test: new_regular_bag
def test_new_regular_bag() -> None:
    '''
    Test that new_regular_bag creates a standard paper bag with correct attributes.
    '''

    bag = BagAggregate.new_regular_bag(1)

    assert bag.bag_id == 'bag_1'
    assert bag.bag_type == 'paper'
    assert bag.items == []
    assert bag.max_capacity == 10
