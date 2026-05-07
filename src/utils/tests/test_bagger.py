"""
FOODIE ForwardChainBagger Utility Tests
"""

# *** imports

# ** infra
import pytest

# ** app
from ...domain import Item
from ..bagger import ForwardChainBagger

# *** fixtures

# ** fixture: bagger
@pytest.fixture
def bagger() -> ForwardChainBagger:
    '''
    Create a ForwardChainBagger instance.

    :return: The bagger utility.
    :rtype: ForwardChainBagger
    '''

    return ForwardChainBagger()


# *** tests

# ** test: bag_items_regular_only
def test_bag_items_regular_only(bagger: ForwardChainBagger) -> None:
    '''
    Test bagging regular items fills bags up to capacity then splits.

    :param bagger: The bagger utility.
    :type bagger: ForwardChainBagger
    '''

    # Create 12 small regular items (exceeds single bag capacity of 10).
    items = [
        Item(name=f'Apple_{i}', size='small', quantity=1)
        for i in range(12)
    ]

    bags = bagger.bag_items(items)

    # Should produce 2 bags: first with 10, second with 2.
    assert len(bags) == 2
    assert len(bags[0].items) == 10
    assert len(bags[1].items) == 2
    assert bags[0].bag_type == 'paper'
    assert bags[1].bag_type == 'paper'


# ** test: bag_items_frozen
def test_bag_items_frozen(bagger: ForwardChainBagger) -> None:
    '''
    Test that each frozen item gets its own freezer bag.

    :param bagger: The bagger utility.
    :type bagger: ForwardChainBagger
    '''

    items = [
        Item(name='Ice Cream', size='medium', is_frozen=True, quantity=1),
        Item(name='Frozen Pizza', size='large', is_frozen=True, quantity=1),
    ]

    bags = bagger.bag_items(items)

    # Each frozen item gets its own freezer bag.
    assert len(bags) == 2
    assert all(b.bag_type == 'freezer' for b in bags)
    assert all(len(b.items) == 1 for b in bags)


# ** test: bag_items_fragile
def test_bag_items_fragile(bagger: ForwardChainBagger) -> None:
    '''
    Test that fragile items start a new bag and force a new bag after.

    :param bagger: The bagger utility.
    :type bagger: ForwardChainBagger
    '''

    items = [
        Item(name='Bread', size='medium', quantity=1),
        Item(name='Eggs', size='medium', is_fragile=True, quantity=1),
        Item(name='Milk', size='medium', quantity=1),
    ]

    bags = bagger.bag_items(items)

    # Bread -> bag_1, Eggs -> bag_2 (fragile, forces new bag after),
    # Milk -> bag_3 (new bag forced by fragile rule).
    assert len(bags) == 3
    assert bags[0].items[0].name == 'Bread'
    assert bags[1].items[0].name == 'Eggs'
    assert bags[2].items[0].name == 'Milk'
    assert all(b.bag_type == 'paper' for b in bags)


# ** test: bag_items_mixed
def test_bag_items_mixed(bagger: ForwardChainBagger) -> None:
    '''
    Test mixed items (frozen + fragile + regular) are sorted by size
    and bagged with correct rules.

    :param bagger: The bagger utility.
    :type bagger: ForwardChainBagger
    '''

    items = [
        Item(name='Watermelon', size='large', quantity=1),
        Item(name='Frozen Peas', size='small', is_frozen=True, quantity=1),
        Item(name='Eggs', size='small', is_fragile=True, quantity=1),
        Item(name='Apple', size='small', quantity=1),
    ]

    bags = bagger.bag_items(items)

    # Size-priority sort: large first, then small.
    # Watermelon (large, regular) -> paper bag.
    # Frozen Peas (small, frozen) -> freezer bag.
    # Eggs (small, fragile) -> new paper bag, forces new after.
    # Apple (small, regular) -> new paper bag.
    assert len(bags) == 4

    # Watermelon in first bag (large items first).
    assert bags[0].items[0].name == 'Watermelon'
    assert bags[0].bag_type == 'paper'

    # Frozen Peas in freezer bag.
    frozen_bags = [b for b in bags if b.bag_type == 'freezer']
    assert len(frozen_bags) == 1
    assert frozen_bags[0].items[0].name == 'Frozen Peas'

    # Eggs in their own paper bag.
    eggs_bag = [b for b in bags if len(b.items) == 1 and b.items[0].name == 'Eggs']
    assert len(eggs_bag) == 1

    # Apple in its own paper bag (forced new after fragile).
    apple_bag = [b for b in bags if len(b.items) == 1 and b.items[0].name == 'Apple']
    assert len(apple_bag) == 1


# ** test: bag_items_empty
def test_bag_items_empty(bagger: ForwardChainBagger) -> None:
    '''
    Test that an empty item list returns an empty bag list.

    :param bagger: The bagger utility.
    :type bagger: ForwardChainBagger
    '''

    bags = bagger.bag_items([])

    assert bags == []
