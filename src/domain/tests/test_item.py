'''FOODIE Item Domain Model Tests'''

# *** imports

# ** infra
import pytest
from pydantic import ValidationError

# ** app
from ..item import Item


# *** fixtures

# ** fixture: default_item
@pytest.fixture
def default_item() -> Item:
    '''
    Create an Item with only required fields, relying on defaults.

    :return: An Item instance with default optional values.
    :rtype: Item
    '''
    return Item(name='Apple', size='small')


# ** fixture: full_item
@pytest.fixture
def full_item() -> Item:
    '''
    Create an Item with all fields explicitly set.

    :return: An Item instance with all fields populated.
    :rtype: Item
    '''
    return Item(
        name='Ice Cream',
        size='large',
        is_frozen=True,
        is_fragile=True,
        quantity=3,
    )


# *** tests

# ** test: item_instantiation_defaults
def test_item_instantiation_defaults(default_item: Item) -> None:
    '''
    Test that an Item created with only required fields has correct defaults.

    :param default_item: Item fixture with defaults.
    :type default_item: Item
    '''

    # Assert required fields are set.
    assert default_item.name == 'Apple'
    assert default_item.size == 'small'

    # Assert optional fields have correct defaults.
    assert default_item.is_frozen is False
    assert default_item.is_fragile is False
    assert default_item.quantity == 1


# ** test: item_instantiation_all_fields
def test_item_instantiation_all_fields(full_item: Item) -> None:
    '''
    Test that an Item created with all fields has correct values.

    :param full_item: Item fixture with all fields.
    :type full_item: Item
    '''

    # Assert all fields are set correctly.
    assert full_item.name == 'Ice Cream'
    assert full_item.size == 'large'
    assert full_item.is_frozen is True
    assert full_item.is_fragile is True
    assert full_item.quantity == 3


# ** test: item_invalid_size
def test_item_invalid_size() -> None:
    '''
    Test that an invalid size raises a ValidationError.
    '''

    # Attempt to create an Item with an invalid size.
    with pytest.raises(ValidationError):
        Item(name='Apple', size='extra-large')


# ** test: item_quantity_minimum
def test_item_quantity_minimum() -> None:
    '''
    Test that a quantity below 1 raises a ValidationError.
    '''

    # Attempt to create an Item with quantity 0.
    with pytest.raises(ValidationError):
        Item(name='Apple', size='small', quantity=0)


# ** test: item_format_for_bagger_plain
def test_item_format_for_bagger_plain(default_item: Item) -> None:
    '''
    Test format_for_bagger with no flags.

    :param default_item: Item fixture with defaults.
    :type default_item: Item
    '''

    # Assert the formatted string has no flag annotations.
    assert default_item.format_for_bagger() == '1x Apple [small]'


# ** test: item_format_for_bagger_frozen
def test_item_format_for_bagger_frozen() -> None:
    '''
    Test format_for_bagger with frozen flag only.
    '''

    # Create a frozen item.
    item = Item(name='Peas', size='medium', is_frozen=True)

    # Assert the formatted string includes frozen annotation.
    assert item.format_for_bagger() == '1x Peas (frozen) [medium]'


# ** test: item_format_for_bagger_both_flags
def test_item_format_for_bagger_both_flags(full_item: Item) -> None:
    '''
    Test format_for_bagger with both frozen and fragile flags.

    :param full_item: Item fixture with all fields.
    :type full_item: Item
    '''

    # Assert the formatted string includes both annotations.
    assert full_item.format_for_bagger() == '3x Ice Cream (frozen, fragile) [large]'
