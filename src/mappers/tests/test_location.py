"""
FOODIE Location Mapper Tests
"""

# *** imports

# ** infra
import pytest
from tiferet.assets.exceptions import TiferetError

# ** app
from ..location import LocationAggregate, LocationYamlObject

# *** constants

# ** constant: aggregate_sample_data
AGGREGATE_SAMPLE_DATA = dict(
    name='Building_A',
    x=3.0,
    y=4.0,
    is_food_warehouse=False,
    is_obstacle_prone=True,
)

# ** constant: yaml_sample_data
YAML_SAMPLE_DATA = dict(
    name='Building_A',
    x=3.0,
    y=4.0,
    is_food_warehouse=False,
    is_obstacle_prone=True,
)

# *** fixtures

# ** fixture: aggregate
@pytest.fixture
def aggregate() -> LocationAggregate:
    '''
    A sample LocationAggregate.

    :return: A LocationAggregate instance.
    :rtype: LocationAggregate
    '''

    return LocationAggregate(**AGGREGATE_SAMPLE_DATA)


# *** tests

# ** test: aggregate_instantiation
def test_aggregate_instantiation(aggregate: LocationAggregate) -> None:
    '''
    Test that the aggregate is created with correct field values.

    :param aggregate: The sample aggregate.
    :type aggregate: LocationAggregate
    '''

    assert aggregate.name == 'Building_A'
    assert aggregate.x == 3.0
    assert aggregate.y == 4.0
    assert aggregate.is_food_warehouse is False
    assert aggregate.is_obstacle_prone is True


# ** test: aggregate_update_coordinates
def test_aggregate_update_coordinates(aggregate: LocationAggregate) -> None:
    '''
    Test that update_coordinates mutates x and y fields.

    :param aggregate: The sample aggregate.
    :type aggregate: LocationAggregate
    '''

    aggregate.update_coordinates(10.0, 20.0)

    assert aggregate.x == 10.0
    assert aggregate.y == 20.0


# ** test: aggregate_set_attribute_invalid
def test_aggregate_set_attribute_invalid(aggregate: LocationAggregate) -> None:
    '''
    Test that set_attribute raises TiferetError for unknown attributes.

    :param aggregate: The sample aggregate.
    :type aggregate: LocationAggregate
    '''

    with pytest.raises(TiferetError):
        aggregate.set_attribute('nonexistent', 'value')


# ** test: yaml_map
def test_yaml_map() -> None:
    '''
    Test that a YamlObject maps to a LocationAggregate with correct fields.
    '''

    yaml_obj = LocationYamlObject.model_validate(YAML_SAMPLE_DATA)
    result = yaml_obj.map()

    assert isinstance(result, LocationAggregate)
    assert result.name == 'Building_A'
    assert result.x == 3.0
    assert result.y == 4.0
    assert result.is_obstacle_prone is True


# ** test: yaml_from_data
def test_yaml_from_data() -> None:
    '''
    Test that from_data creates a YamlObject from a raw dict.
    '''

    data = dict(x=0.0, y=0.0, is_food_warehouse=True)
    yaml_obj = LocationYamlObject.from_data(data, name='FW')

    assert yaml_obj.name == 'FW'
    assert yaml_obj.x == 0.0
    assert yaml_obj.is_food_warehouse is True


# ** test: yaml_from_model
def test_yaml_from_model(aggregate: LocationAggregate) -> None:
    '''
    Test that from_model creates a YamlObject from an aggregate.

    :param aggregate: The sample aggregate.
    :type aggregate: LocationAggregate
    '''

    yaml_obj = LocationYamlObject.from_model(aggregate)

    assert yaml_obj.name == 'Building_A'
    assert yaml_obj.x == 3.0
    assert yaml_obj.y == 4.0


# ** test: yaml_round_trip
def test_yaml_round_trip(aggregate: LocationAggregate) -> None:
    '''
    Test that aggregate -> YamlObject -> aggregate preserves data.

    :param aggregate: The sample aggregate.
    :type aggregate: LocationAggregate
    '''

    yaml_obj = LocationYamlObject.from_model(aggregate)
    result = yaml_obj.map()

    assert result.name == aggregate.name
    assert result.x == aggregate.x
    assert result.y == aggregate.y
    assert result.is_food_warehouse == aggregate.is_food_warehouse
    assert result.is_obstacle_prone == aggregate.is_obstacle_prone
