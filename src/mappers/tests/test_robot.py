"""
FOODIE Robot Mapper Tests
"""

# *** imports

# ** core
import json

# ** infra
import pytest

# ** app
from ...domain import Location, Bag, Item
from ..robot import RobotAggregate, RobotSqlObject

# *** constants

# ** constant: home_location_data
HOME_LOCATION = Location(name='FW', x=0.0, y=0.0, is_food_warehouse=True)

# ** constant: building_a_location
BUILDING_A = Location(name='Building_A', x=3.0, y=4.0)

# ** constant: sample_bag
SAMPLE_BAG = Bag(bag_id='bag_1', items=[Item(name='Sandwich', size='medium')])

# ** constant: aggregate_sample_data
AGGREGATE_SAMPLE_DATA = dict(
    robot_id='R1',
    current_location=HOME_LOCATION,
    battery_level=85.0,
    compartments=[SAMPLE_BAG],
    status='idle',
)

# *** fixtures

# ** fixture: aggregate
@pytest.fixture
def aggregate() -> RobotAggregate:
    '''
    A sample RobotAggregate.

    :return: A RobotAggregate instance.
    :rtype: RobotAggregate
    '''

    return RobotAggregate(**AGGREGATE_SAMPLE_DATA)


# *** tests

# ** test: aggregate_instantiation
def test_aggregate_instantiation(aggregate: RobotAggregate) -> None:
    '''
    Test that the aggregate is created with correct field values.

    :param aggregate: The sample aggregate.
    :type aggregate: RobotAggregate
    '''

    assert aggregate.robot_id == 'R1'
    assert aggregate.current_location.name == 'FW'
    assert aggregate.battery_level == 85.0
    assert len(aggregate.compartments) == 1
    assert aggregate.status == 'idle'


# ** test: aggregate_update_battery
def test_aggregate_update_battery(aggregate: RobotAggregate) -> None:
    '''
    Test that update_battery mutates the battery_level field.

    :param aggregate: The sample aggregate.
    :type aggregate: RobotAggregate
    '''

    aggregate.update_battery(50.0)

    assert aggregate.battery_level == 50.0


# ** test: aggregate_update_location
def test_aggregate_update_location(aggregate: RobotAggregate) -> None:
    '''
    Test that update_location mutates the current_location field.

    :param aggregate: The sample aggregate.
    :type aggregate: RobotAggregate
    '''

    aggregate.update_location(BUILDING_A)

    assert aggregate.current_location.name == 'Building_A'
    assert aggregate.current_location.x == 3.0


# ** test: aggregate_update_status
def test_aggregate_update_status(aggregate: RobotAggregate) -> None:
    '''
    Test that update_status mutates the status field.

    :param aggregate: The sample aggregate.
    :type aggregate: RobotAggregate
    '''

    aggregate.update_status('en_route')

    assert aggregate.status == 'en_route'


# ** test: sql_to_primitive_sqlite
def test_sql_to_primitive_sqlite(aggregate: RobotAggregate) -> None:
    '''
    Test that to_primitive with sqlite role produces JSON columns.

    :param aggregate: The sample aggregate.
    :type aggregate: RobotAggregate
    '''

    sql_obj = RobotSqlObject.from_model(aggregate)
    data = sql_obj.to_primitive(role='to_data.sqlite')

    # current_location_json should be a valid JSON string.
    assert 'current_location_json' in data
    loc = json.loads(data['current_location_json'])
    assert loc['name'] == 'FW'
    assert loc['x'] == 0.0

    # compartments_json should be a valid JSON string with one bag.
    assert 'compartments_json' in data
    bags = json.loads(data['compartments_json'])
    assert len(bags) == 1
    assert bags[0]['bag_id'] == 'bag_1'

    # Nested fields should be excluded from the dict.
    assert 'current_location' not in data
    assert 'compartments' not in data


# ** test: sql_to_primitive_default
def test_sql_to_primitive_default(aggregate: RobotAggregate) -> None:
    '''
    Test that to_primitive without sqlite role does not add JSON columns.

    :param aggregate: The sample aggregate.
    :type aggregate: RobotAggregate
    '''

    sql_obj = RobotSqlObject.from_model(aggregate)
    data = sql_obj.to_primitive()

    assert 'current_location_json' not in data
    assert 'compartments_json' not in data


# ** test: sql_from_data
def test_sql_from_data() -> None:
    '''
    Test that from_data deserializes JSON columns into domain objects.
    '''

    loc_data = dict(name='Dorm_1', x=5.0, y=2.0, is_food_warehouse=False, is_obstacle_prone=False)
    bag_data = [dict(bag_id='bag_2', bag_type='paper', items=[], max_capacity=10)]
    row = dict(
        robot_id='R2',
        battery_level=70.0,
        status='en_route',
        current_location_json=json.dumps(loc_data),
        compartments_json=json.dumps(bag_data),
    )

    sql_obj = RobotSqlObject.from_data(row)

    assert sql_obj.robot_id == 'R2'
    assert isinstance(sql_obj.current_location, Location)
    assert sql_obj.current_location.name == 'Dorm_1'
    assert len(sql_obj.compartments) == 1
    assert isinstance(sql_obj.compartments[0], Bag)
    assert sql_obj.compartments[0].bag_id == 'bag_2'


# ** test: sql_map
def test_sql_map(aggregate: RobotAggregate) -> None:
    '''
    Test that a SqlObject maps to a RobotAggregate with correct fields.

    :param aggregate: The sample aggregate.
    :type aggregate: RobotAggregate
    '''

    sql_obj = RobotSqlObject.from_model(aggregate)
    result = sql_obj.map()

    assert isinstance(result, RobotAggregate)
    assert result.robot_id == 'R1'
    assert result.current_location.name == 'FW'
    assert len(result.compartments) == 1


# ** test: sql_from_model
def test_sql_from_model(aggregate: RobotAggregate) -> None:
    '''
    Test that from_model creates a SqlObject from an aggregate.

    :param aggregate: The sample aggregate.
    :type aggregate: RobotAggregate
    '''

    sql_obj = RobotSqlObject.from_model(aggregate)

    assert sql_obj.robot_id == 'R1'
    assert sql_obj.battery_level == 85.0


# ** test: sql_round_trip
def test_sql_round_trip(aggregate: RobotAggregate) -> None:
    '''
    Test that aggregate -> SqlObject -> to_primitive -> from_data -> map preserves data.

    :param aggregate: The sample aggregate.
    :type aggregate: RobotAggregate
    '''

    # Serialize to SQL format.
    sql_obj = RobotSqlObject.from_model(aggregate)
    primitive = sql_obj.to_primitive(role='to_data.sqlite')

    # Deserialize back from SQL row.
    restored_sql = RobotSqlObject.from_data(dict(primitive))
    result = restored_sql.map()

    assert result.robot_id == aggregate.robot_id
    assert result.battery_level == aggregate.battery_level
    assert result.status == aggregate.status
    assert result.current_location.name == aggregate.current_location.name
    assert result.current_location.x == aggregate.current_location.x
    assert len(result.compartments) == len(aggregate.compartments)
    assert result.compartments[0].bag_id == aggregate.compartments[0].bag_id
