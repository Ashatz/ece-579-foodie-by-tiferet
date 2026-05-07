"""
FOODIE Order SQLite Repository Tests
"""

# *** imports

# ** infra
import pytest

# ** app
from ...domain import Item, Order
from ...mappers import OrderAggregate
from ..order import OrderSqliteRepository

# *** fixtures

# ** fixture: db_path
@pytest.fixture
def db_path(tmp_path) -> str:
    '''
    Provide a temporary database path for each test.

    :param tmp_path: Pytest temporary directory.
    :type tmp_path: pathlib.Path
    :return: Path to the temporary SQLite database.
    :rtype: str
    '''

    return str(tmp_path / 'test_foodie.db')


# ** fixture: order_repo
@pytest.fixture
def order_repo(db_path) -> OrderSqliteRepository:
    '''
    Create an OrderSqliteRepository backed by a temporary database.

    :param db_path: Path to the temporary database.
    :type db_path: str
    :return: The repository instance.
    :rtype: OrderSqliteRepository
    '''

    return OrderSqliteRepository(db_path=db_path)


# ** fixture: sample_items
@pytest.fixture
def sample_items() -> list:
    '''
    Build a list of sample Item domain objects.

    :return: List of items.
    :rtype: list[Item]
    '''

    return [
        Item(name='Water Bottle', size='large', is_frozen=False, is_fragile=False, quantity=2),
        Item(name='Ice Cream', size='medium', is_frozen=True, is_fragile=False, quantity=1),
    ]


# ** fixture: sample_order
@pytest.fixture
def sample_order(sample_items) -> OrderAggregate:
    '''
    Build a sample OrderAggregate for testing.

    :param sample_items: List of sample items.
    :type sample_items: list[Item]
    :return: An order aggregate.
    :rtype: OrderAggregate
    '''

    return OrderAggregate(
        order_id='ORD-TEST-1',
        items=sample_items,
        destination='Building_A',
        status='pending',
    )


# *** tests

# ** test: save_and_get
def test_save_and_get(order_repo: OrderSqliteRepository, sample_order: OrderAggregate) -> None:
    '''
    Test that saving an order and retrieving it by ID produces matching data.

    :param order_repo: The order repository.
    :type order_repo: OrderSqliteRepository
    :param sample_order: The sample order aggregate.
    :type sample_order: OrderAggregate
    '''

    order_repo.save(sample_order)
    result = order_repo.get('ORD-TEST-1')

    assert result is not None
    assert result.order_id == 'ORD-TEST-1'
    assert result.destination == 'Building_A'
    assert result.status == 'pending'
    assert len(result.items) == 2
    assert result.items[0].name == 'Water Bottle'
    assert result.items[0].quantity == 2
    assert result.items[1].is_frozen is True


# ** test: exists_true
def test_exists_true(order_repo: OrderSqliteRepository, sample_order: OrderAggregate) -> None:
    '''
    Test that exists returns True for a saved order.

    :param order_repo: The order repository.
    :type order_repo: OrderSqliteRepository
    :param sample_order: The sample order aggregate.
    :type sample_order: OrderAggregate
    '''

    order_repo.save(sample_order)
    assert order_repo.exists('ORD-TEST-1') is True


# ** test: exists_false
def test_exists_false(order_repo: OrderSqliteRepository) -> None:
    '''
    Test that exists returns False for a non-existent order.

    :param order_repo: The order repository.
    :type order_repo: OrderSqliteRepository
    '''

    assert order_repo.exists('NO-SUCH-ORDER') is False


# ** test: get_not_found
def test_get_not_found(order_repo: OrderSqliteRepository) -> None:
    '''
    Test that get returns None for a non-existent order.

    :param order_repo: The order repository.
    :type order_repo: OrderSqliteRepository
    '''

    assert order_repo.get('NO-SUCH-ORDER') is None


# ** test: list_orders
def test_list_orders(order_repo: OrderSqliteRepository, sample_items: list) -> None:
    '''
    Test that list returns all saved orders.

    :param order_repo: The order repository.
    :type order_repo: OrderSqliteRepository
    :param sample_items: List of sample items.
    :type sample_items: list[Item]
    '''

    order_repo.save(OrderAggregate(order_id='ORD-A', items=sample_items, destination='Dorm_1'))
    order_repo.save(OrderAggregate(order_id='ORD-B', items=[], destination='Building_B'))

    results = order_repo.list()
    assert len(results) == 2
    ids = {o.order_id for o in results}
    assert ids == {'ORD-A', 'ORD-B'}


# ** test: save_updates_existing
def test_save_updates_existing(order_repo: OrderSqliteRepository, sample_order: OrderAggregate) -> None:
    '''
    Test that saving an order with the same ID replaces the previous record.

    :param order_repo: The order repository.
    :type order_repo: OrderSqliteRepository
    :param sample_order: The sample order aggregate.
    :type sample_order: OrderAggregate
    '''

    order_repo.save(sample_order)
    sample_order.status = 'bagged'
    order_repo.save(sample_order)

    result = order_repo.get('ORD-TEST-1')
    assert result.status == 'bagged'
    assert len(order_repo.list()) == 1


# ** test: delete_order
def test_delete_order(order_repo: OrderSqliteRepository, sample_order: OrderAggregate) -> None:
    '''
    Test that deleting an order removes it from the database.

    :param order_repo: The order repository.
    :type order_repo: OrderSqliteRepository
    :param sample_order: The sample order aggregate.
    :type sample_order: OrderAggregate
    '''

    order_repo.save(sample_order)
    order_repo.delete('ORD-TEST-1')

    assert order_repo.exists('ORD-TEST-1') is False
    assert order_repo.get('ORD-TEST-1') is None


# ** test: delete_idempotent
def test_delete_idempotent(order_repo: OrderSqliteRepository) -> None:
    '''
    Test that deleting a non-existent order does not raise.

    :param order_repo: The order repository.
    :type order_repo: OrderSqliteRepository
    '''

    order_repo.delete('NO-SUCH-ORDER')


# ** test: round_trip_preserves_items
def test_round_trip_preserves_items(order_repo: OrderSqliteRepository) -> None:
    '''
    Test that nested Item data survives a full save/load round-trip.

    :param order_repo: The order repository.
    :type order_repo: OrderSqliteRepository
    '''

    items = [
        Item(name='Eggs', size='small', is_frozen=False, is_fragile=True, quantity=1),
        Item(name='Frozen Pizza', size='large', is_frozen=True, is_fragile=False, quantity=3),
    ]
    order = OrderAggregate(order_id='ORD-RT', items=items, destination='Dorm_1')
    order_repo.save(order)

    result = order_repo.get('ORD-RT')
    assert len(result.items) == 2
    assert result.items[0].name == 'Eggs'
    assert result.items[0].is_fragile is True
    assert result.items[1].name == 'Frozen Pizza'
    assert result.items[1].is_frozen is True
    assert result.items[1].quantity == 3
