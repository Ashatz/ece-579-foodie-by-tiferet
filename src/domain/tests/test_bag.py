"""
FOODIE Bag Domain Model Tests
"""

# *** imports

# ** infra
import pytest

# ** app
from ..item import Item
from ..bag import Bag

# *** fixtures

# ** fixture: empty_bag
@pytest.fixture
def empty_bag() -> Bag:
    '''
    An empty paper bag.

    :return: An empty Bag instance.
    :rtype: Bag
    '''

    return Bag(bag_id='bag_1')


# ** fixture: regular_item
@pytest.fixture
def regular_item() -> Item:
    '''
    A regular non-special item.

    :return: A regular Item instance.
    :rtype: Item
    '''

    return Item(name='Sandwich', size='medium')


# ** fixture: fragile_item
@pytest.fixture
def fragile_item() -> Item:
    '''
    A fragile item.

    :return: A fragile Item instance.
    :rtype: Item
    '''

    return Item(name='Eggs', size='small', is_fragile=True)


# *** tests

# ** test: instantiation_defaults
def test_instantiation_defaults(empty_bag: Bag) -> None:
    '''
    Test that default field values are applied correctly.

    :param empty_bag: An empty Bag instance.
    :type empty_bag: Bag
    '''

    assert empty_bag.bag_id == 'bag_1'
    assert empty_bag.bag_type == 'paper'
    assert empty_bag.items == []
    assert empty_bag.max_capacity == 10


# ** test: instantiation_freezer_bag
def test_instantiation_freezer_bag() -> None:
    '''
    Test creating a freezer bag with explicit type.
    '''

    bag = Bag(bag_id='freezer_1', bag_type='freezer')

    assert bag.bag_type == 'freezer'


# ** test: can_accept_item_empty_bag
def test_can_accept_item_empty_bag(empty_bag: Bag, regular_item: Item) -> None:
    '''
    Test that an empty bag can accept a regular item.

    :param empty_bag: An empty Bag instance.
    :type empty_bag: Bag
    :param regular_item: A regular Item instance.
    :type regular_item: Item
    '''

    assert empty_bag.can_accept_item(regular_item) is True


# ** test: can_accept_item_full_bag
def test_can_accept_item_full_bag(regular_item: Item) -> None:
    '''
    Test that a full bag rejects additional items.

    :param regular_item: A regular Item instance.
    :type regular_item: Item
    '''

    items = [Item(name=f'Item_{i}', size='small') for i in range(10)]
    bag = Bag(bag_id='full_bag', items=items, max_capacity=10)

    assert bag.can_accept_item(regular_item) is False


# ** test: can_accept_item_fragile_rejected_nonempty
def test_can_accept_item_fragile_rejected_nonempty(fragile_item: Item) -> None:
    '''
    Test that a fragile item is rejected when the bag already has items.

    :param fragile_item: A fragile Item instance.
    :type fragile_item: Item
    '''

    bag = Bag(bag_id='bag_2', items=[Item(name='Bread', size='medium')])

    assert bag.can_accept_item(fragile_item) is False


# ** test: can_accept_item_fragile_accepted_empty
def test_can_accept_item_fragile_accepted_empty(empty_bag: Bag, fragile_item: Item) -> None:
    '''
    Test that a fragile item is accepted in an empty bag.

    :param empty_bag: An empty Bag instance.
    :type empty_bag: Bag
    :param fragile_item: A fragile Item instance.
    :type fragile_item: Item
    '''

    assert empty_bag.can_accept_item(fragile_item) is True


# ** test: add_item_success
def test_add_item_success(empty_bag: Bag, regular_item: Item) -> None:
    '''
    Test that add_item appends the item and returns True.

    :param empty_bag: An empty Bag instance.
    :type empty_bag: Bag
    :param regular_item: A regular Item instance.
    :type regular_item: Item
    '''

    result = empty_bag.add_item(regular_item)

    assert result is True
    assert len(empty_bag.items) == 1
    assert empty_bag.items[0].name == 'Sandwich'


# ** test: add_item_failure
def test_add_item_failure(fragile_item: Item) -> None:
    '''
    Test that add_item returns False when rules disallow the item.

    :param fragile_item: A fragile Item instance.
    :type fragile_item: Item
    '''

    bag = Bag(bag_id='bag_3', items=[Item(name='Bread', size='medium')])

    result = bag.add_item(fragile_item)

    assert result is False
    assert len(bag.items) == 1


# ** test: format_trace
def test_format_trace() -> None:
    '''
    Test that format_trace produces the expected output.
    '''

    items = [
        Item(name='Bread', size='large'),
        Item(name='Milk', size='medium', quantity=2),
    ]
    bag = Bag(bag_id='bag_1', items=items)

    result = bag.format_trace()

    assert result == 'Bag bag_1 (paper) contains: 1x Bread [large], 2x Milk [medium] (2/10)'
