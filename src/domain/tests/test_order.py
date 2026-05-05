"""
FOODIE Order Domain Model Tests
"""

# *** imports

# ** infra
import pytest
from pydantic import ValidationError

# ** app
from ..item import Item
from ..order import Order

# *** fixtures

# ** fixture: sample_items
@pytest.fixture
def sample_items() -> list:
    '''
    A list of sample items with varying quantities.

    :return: List of Item instances.
    :rtype: list[Item]
    '''

    return [
        Item(name='Water Bottle', size='large', quantity=2),
        Item(name='Sandwich', size='medium', quantity=1),
        Item(name='Cookies', size='small', quantity=3),
    ]


# ** fixture: sample_order
@pytest.fixture
def sample_order(sample_items: list) -> Order:
    '''
    A sample order with items.

    :param sample_items: List of sample items.
    :type sample_items: list[Item]
    :return: An Order instance.
    :rtype: Order
    '''

    return Order(
        order_id='ORD-001',
        items=sample_items,
        destination='Building_A',
    )


# *** tests

# ** test: instantiation_defaults
def test_instantiation_defaults() -> None:
    '''
    Test that default field values are applied correctly.
    '''

    order = Order(order_id='ORD-EMPTY', destination='Dorm_1')

    assert order.order_id == 'ORD-EMPTY'
    assert order.items == []
    assert order.destination == 'Dorm_1'
    assert order.status == 'pending'


# ** test: instantiation_all_fields
def test_instantiation_all_fields(sample_order: Order) -> None:
    '''
    Test that all fields are set correctly.

    :param sample_order: A sample Order instance.
    :type sample_order: Order
    '''

    assert sample_order.order_id == 'ORD-001'
    assert len(sample_order.items) == 3
    assert sample_order.destination == 'Building_A'
    assert sample_order.status == 'pending'


# ** test: invalid_status_rejected
def test_invalid_status_rejected() -> None:
    '''
    Test that an invalid status literal raises a validation error.
    '''

    with pytest.raises(ValidationError):
        Order(order_id='ORD-BAD', destination='Dorm_1', status='cancelled')


# ** test: total_items_empty
def test_total_items_empty() -> None:
    '''
    Test total_items on an order with no items.
    '''

    order = Order(order_id='ORD-EMPTY', destination='Dorm_1')

    assert order.total_items() == 0


# ** test: total_items_with_quantities
def test_total_items_with_quantities(sample_order: Order) -> None:
    '''
    Test total_items sums all item quantities.

    :param sample_order: A sample Order instance.
    :type sample_order: Order
    '''

    # 2 + 1 + 3 = 6
    assert sample_order.total_items() == 6


# ** test: format_for_bagger
def test_format_for_bagger(sample_order: Order) -> None:
    '''
    Test format_for_bagger produces the expected output.

    :param sample_order: A sample Order instance.
    :type sample_order: Order
    '''

    result = sample_order.format_for_bagger()

    assert result == (
        'Order ORD-001 -> Building_A | '
        'Items: 2x Water Bottle [large], 1x Sandwich [medium], 3x Cookies [small] '
        '(total: 6)'
    )


# ** test: format_for_bagger_empty
def test_format_for_bagger_empty() -> None:
    '''
    Test format_for_bagger on an order with no items.
    '''

    order = Order(order_id='ORD-EMPTY', destination='Dorm_1')
    result = order.format_for_bagger()

    assert result == 'Order ORD-EMPTY -> Dorm_1 | Items:  (total: 0)'
