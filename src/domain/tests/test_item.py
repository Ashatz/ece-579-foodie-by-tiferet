"""
FOODIE Item Domain Model Tests
"""

# *** imports

# ** infra
import pytest
from pydantic import ValidationError

# ** app
from ..item import Item

# *** fixtures

# ** fixture: plain_item
@pytest.fixture
def plain_item() -> Item:
    '''
    A plain item with no special flags.

    :return: A plain Item instance.
    :rtype: Item
    '''

    return Item(name='Water Bottle', size='large')


# ** fixture: frozen_item
@pytest.fixture
def frozen_item() -> Item:
    '''
    A frozen item.

    :return: A frozen Item instance.
    :rtype: Item
    '''

    return Item(name='Ice Cream', size='medium', is_frozen=True)


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
def test_instantiation_defaults(plain_item: Item) -> None:
    '''
    Test that default field values are applied correctly.

    :param plain_item: A plain Item instance.
    :type plain_item: Item
    '''

    assert plain_item.name == 'Water Bottle'
    assert plain_item.size == 'large'
    assert plain_item.is_frozen is False
    assert plain_item.is_fragile is False
    assert plain_item.quantity == 1


# ** test: instantiation_all_fields
def test_instantiation_all_fields() -> None:
    '''
    Test that all fields can be set explicitly.
    '''

    item = Item(name='Pizza', size='large', is_frozen=True, is_fragile=False, quantity=3)

    assert item.name == 'Pizza'
    assert item.size == 'large'
    assert item.is_frozen is True
    assert item.is_fragile is False
    assert item.quantity == 3


# ** test: invalid_size_rejected
def test_invalid_size_rejected() -> None:
    '''
    Test that an invalid size literal raises a validation error.
    '''

    with pytest.raises(ValidationError):
        Item(name='Unknown', size='huge')


# ** test: quantity_minimum
def test_quantity_minimum() -> None:
    '''
    Test that quantity below 1 is rejected.
    '''

    with pytest.raises(ValidationError):
        Item(name='Water', size='small', quantity=0)


# ** test: format_for_bagger_plain
def test_format_for_bagger_plain(plain_item: Item) -> None:
    '''
    Test format_for_bagger with no flags.

    :param plain_item: A plain Item instance.
    :type plain_item: Item
    '''

    result = plain_item.format_for_bagger()

    assert result == '1x Water Bottle [large]'


# ** test: format_for_bagger_frozen
def test_format_for_bagger_frozen(frozen_item: Item) -> None:
    '''
    Test format_for_bagger with frozen flag.

    :param frozen_item: A frozen Item instance.
    :type frozen_item: Item
    '''

    result = frozen_item.format_for_bagger()

    assert result == '1x Ice Cream (frozen) [medium]'


# ** test: format_for_bagger_fragile
def test_format_for_bagger_fragile(fragile_item: Item) -> None:
    '''
    Test format_for_bagger with fragile flag.

    :param fragile_item: A fragile Item instance.
    :type fragile_item: Item
    '''

    result = fragile_item.format_for_bagger()

    assert result == '1x Eggs (fragile) [small]'


# ** test: format_for_bagger_both_flags
def test_format_for_bagger_both_flags() -> None:
    '''
    Test format_for_bagger with both frozen and fragile flags.
    '''

    item = Item(name='Gelato', size='small', is_frozen=True, is_fragile=True, quantity=2)
    result = item.format_for_bagger()

    assert result == '2x Gelato (frozen, fragile) [small]'
