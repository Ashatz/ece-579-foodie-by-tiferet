"""
FOODIE Order Mapper Tests
"""

# *** imports

# ** core
import json

# ** infra
import pytest

# ** app
from ...domain import Item
from ..order import OrderAggregate, OrderSqlObject

# *** constants

# ** constant: sample_items
SAMPLE_ITEMS = [
    Item(name='Water Bottle', size='large', is_frozen=False, is_fragile=False, quantity=2),
    Item(name='Ice Cream', size='medium', is_frozen=True, is_fragile=False, quantity=1),
]

# ** constant: aggregate_sample_data
AGGREGATE_SAMPLE_DATA = dict(
    order_id='ORD-001',
    items=SAMPLE_ITEMS,
    destination='Building_A',
    status='pending',
)

# *** fixtures

# ** fixture: aggregate
@pytest.fixture
def aggregate() -> OrderAggregate:
    '''
    A sample OrderAggregate.

    :return: An OrderAggregate instance.
    :rtype: OrderAggregate
    '''

    return OrderAggregate(**AGGREGATE_SAMPLE_DATA)


# *** tests

# ** test: aggregate_instantiation
def test_aggregate_instantiation(aggregate: OrderAggregate) -> None:
    '''
    Test that the aggregate is created with correct field values.

    :param aggregate: The sample aggregate.
    :type aggregate: OrderAggregate
    '''

    assert aggregate.order_id == 'ORD-001'
    assert len(aggregate.items) == 2
    assert aggregate.destination == 'Building_A'
    assert aggregate.status == 'pending'


# ** test: aggregate_update_status
def test_aggregate_update_status(aggregate: OrderAggregate) -> None:
    '''
    Test that update_status mutates the status field.

    :param aggregate: The sample aggregate.
    :type aggregate: OrderAggregate
    '''

    aggregate.update_status('bagged')

    assert aggregate.status == 'bagged'


# ** test: sql_to_primitive_sqlite
def test_sql_to_primitive_sqlite(aggregate: OrderAggregate) -> None:
    '''
    Test that to_primitive with sqlite role produces items_json column.

    :param aggregate: The sample aggregate.
    :type aggregate: OrderAggregate
    '''

    sql_obj = OrderSqlObject.from_model(aggregate)
    data = sql_obj.to_primitive(role='to_data.sqlite')

    # items_json should be a JSON string containing 2 items.
    assert 'items_json' in data
    parsed = json.loads(data['items_json'])
    assert len(parsed) == 2
    assert parsed[0]['name'] == 'Water Bottle'
    assert parsed[1]['is_frozen'] is True

    # items field should be excluded from the dict.
    assert 'items' not in data


# ** test: sql_to_primitive_default
def test_sql_to_primitive_default(aggregate: OrderAggregate) -> None:
    '''
    Test that to_primitive without sqlite role does not add items_json.

    :param aggregate: The sample aggregate.
    :type aggregate: OrderAggregate
    '''

    sql_obj = OrderSqlObject.from_model(aggregate)
    data = sql_obj.to_primitive()

    assert 'items_json' not in data


# ** test: sql_from_data
def test_sql_from_data() -> None:
    '''
    Test that from_data deserializes items_json into Item domain objects.
    '''

    items_list = [
        dict(name='Eggs', size='small', is_frozen=False, is_fragile=True, quantity=1),
    ]
    row = dict(
        order_id='ORD-002',
        destination='Dorm_1',
        status='pending',
        items_json=json.dumps(items_list),
    )

    sql_obj = OrderSqlObject.from_data(row)

    assert sql_obj.order_id == 'ORD-002'
    assert len(sql_obj.items) == 1
    assert isinstance(sql_obj.items[0], Item)
    assert sql_obj.items[0].name == 'Eggs'
    assert sql_obj.items[0].is_fragile is True


# ** test: sql_map
def test_sql_map(aggregate: OrderAggregate) -> None:
    '''
    Test that a SqlObject maps to an OrderAggregate with correct fields.

    :param aggregate: The sample aggregate.
    :type aggregate: OrderAggregate
    '''

    sql_obj = OrderSqlObject.from_model(aggregate)
    result = sql_obj.map()

    assert isinstance(result, OrderAggregate)
    assert result.order_id == 'ORD-001'
    assert len(result.items) == 2
    assert result.items[0].name == 'Water Bottle'


# ** test: sql_from_model
def test_sql_from_model(aggregate: OrderAggregate) -> None:
    '''
    Test that from_model creates a SqlObject from an aggregate.

    :param aggregate: The sample aggregate.
    :type aggregate: OrderAggregate
    '''

    sql_obj = OrderSqlObject.from_model(aggregate)

    assert sql_obj.order_id == 'ORD-001'
    assert len(sql_obj.items) == 2


# ** test: sql_round_trip
def test_sql_round_trip(aggregate: OrderAggregate) -> None:
    '''
    Test that aggregate -> SqlObject -> to_primitive -> from_data -> map preserves data.

    :param aggregate: The sample aggregate.
    :type aggregate: OrderAggregate
    '''

    # Serialize to SQL format.
    sql_obj = OrderSqlObject.from_model(aggregate)
    primitive = sql_obj.to_primitive(role='to_data.sqlite')

    # Deserialize back from SQL row.
    restored_sql = OrderSqlObject.from_data(dict(primitive))
    result = restored_sql.map()

    assert result.order_id == aggregate.order_id
    assert result.destination == aggregate.destination
    assert result.status == aggregate.status
    assert len(result.items) == len(aggregate.items)
    assert result.items[0].name == aggregate.items[0].name
    assert result.items[1].is_frozen == aggregate.items[1].is_frozen
