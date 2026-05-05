"""
FOODIE Beverage Mapper Tests
"""

# *** imports

# ** infra
import pytest
from tiferet.assets.exceptions import TiferetError

# ** app
from ..beverage import BeverageAggregate, BeverageYamlObject

# *** constants

# ** constant: aggregate_sample_data
AGGREGATE_SAMPLE_DATA = dict(
    name='FreshRoots Juice',
    beverage_type='juice',
    brand='FreshRoots',
    is_health_friendly=True,
    avoids_allergens='gluten, dairy',
)

# ** constant: yaml_sample_data
YAML_SAMPLE_DATA = dict(
    name='FreshRoots Juice',
    beverage_type='juice',
    brand='FreshRoots',
    is_health_friendly=True,
    avoids_allergens='gluten, dairy',
)

# *** fixtures

# ** fixture: aggregate
@pytest.fixture
def aggregate() -> BeverageAggregate:
    '''
    A sample BeverageAggregate.

    :return: A BeverageAggregate instance.
    :rtype: BeverageAggregate
    '''

    return BeverageAggregate(**AGGREGATE_SAMPLE_DATA)


# *** tests

# ** test: aggregate_instantiation
def test_aggregate_instantiation(aggregate: BeverageAggregate) -> None:
    '''
    Test that the aggregate is created with correct field values.

    :param aggregate: The sample aggregate.
    :type aggregate: BeverageAggregate
    '''

    assert aggregate.name == 'FreshRoots Juice'
    assert aggregate.beverage_type == 'juice'
    assert aggregate.brand == 'FreshRoots'
    assert aggregate.is_health_friendly is True
    assert aggregate.avoids_allergens == 'gluten, dairy'


# ** test: aggregate_update_allergens
def test_aggregate_update_allergens(aggregate: BeverageAggregate) -> None:
    '''
    Test that update_allergens mutates the avoids_allergens field.

    :param aggregate: The sample aggregate.
    :type aggregate: BeverageAggregate
    '''

    aggregate.update_allergens('nuts, soy')

    assert aggregate.avoids_allergens == 'nuts, soy'


# ** test: aggregate_set_attribute_invalid
def test_aggregate_set_attribute_invalid(aggregate: BeverageAggregate) -> None:
    '''
    Test that set_attribute raises TiferetError for unknown attributes.

    :param aggregate: The sample aggregate.
    :type aggregate: BeverageAggregate
    '''

    with pytest.raises(TiferetError):
        aggregate.set_attribute('nonexistent', 'value')


# ** test: yaml_map
def test_yaml_map() -> None:
    '''
    Test that a YamlObject maps to a BeverageAggregate with correct fields.
    '''

    yaml_obj = BeverageYamlObject.model_validate(YAML_SAMPLE_DATA)
    result = yaml_obj.map()

    assert isinstance(result, BeverageAggregate)
    assert result.name == 'FreshRoots Juice'
    assert result.beverage_type == 'juice'
    assert result.brand == 'FreshRoots'
    assert result.is_health_friendly is True


# ** test: yaml_from_data
def test_yaml_from_data() -> None:
    '''
    Test that from_data creates a YamlObject from a raw dict.
    '''

    data = dict(beverage_type='beer', brand='Corona', is_health_friendly=False)
    yaml_obj = BeverageYamlObject.from_data(data, name='Corona')

    assert yaml_obj.name == 'Corona'
    assert yaml_obj.beverage_type == 'beer'
    assert yaml_obj.brand == 'Corona'


# ** test: yaml_from_model
def test_yaml_from_model(aggregate: BeverageAggregate) -> None:
    '''
    Test that from_model creates a YamlObject from an aggregate.

    :param aggregate: The sample aggregate.
    :type aggregate: BeverageAggregate
    '''

    yaml_obj = BeverageYamlObject.from_model(aggregate)

    assert yaml_obj.name == 'FreshRoots Juice'
    assert yaml_obj.avoids_allergens == 'gluten, dairy'


# ** test: yaml_round_trip
def test_yaml_round_trip(aggregate: BeverageAggregate) -> None:
    '''
    Test that aggregate -> YamlObject -> aggregate preserves data.

    :param aggregate: The sample aggregate.
    :type aggregate: BeverageAggregate
    '''

    yaml_obj = BeverageYamlObject.from_model(aggregate)
    result = yaml_obj.map()

    assert result.name == aggregate.name
    assert result.beverage_type == aggregate.beverage_type
    assert result.brand == aggregate.brand
    assert result.is_health_friendly == aggregate.is_health_friendly
    assert result.avoids_allergens == aggregate.avoids_allergens
