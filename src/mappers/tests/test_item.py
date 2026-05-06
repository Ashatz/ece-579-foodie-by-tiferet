"""
FOODIE Item Mapper Tests
"""

# *** imports

# ** infra
import pytest
from pydantic import ValidationError
from tiferet.assets.exceptions import TiferetError

# ** app
from ..item import ItemAggregate, ItemYamlObject

# *** constants

# ** constant: aggregate_sample_data
AGGREGATE_SAMPLE_DATA = dict(
    name='Water Bottle',
    size='large',
    is_frozen=False,
    is_fragile=False,
    quantity=2,
)

# ** constant: yaml_sample_data
YAML_SAMPLE_DATA = dict(
    name='Water Bottle',
    size='large',
    is_frozen=False,
    is_fragile=False,
    quantity=2,
)

# *** fixtures

# ** fixture: aggregate
@pytest.fixture
def aggregate() -> ItemAggregate:
    '''
    A sample ItemAggregate.

    :return: An ItemAggregate instance.
    :rtype: ItemAggregate
    '''

    return ItemAggregate(**AGGREGATE_SAMPLE_DATA)


# *** tests

# ** test: aggregate_instantiation
def test_aggregate_instantiation(aggregate: ItemAggregate) -> None:
    '''
    Test that the aggregate is created with correct field values.

    :param aggregate: The sample aggregate.
    :type aggregate: ItemAggregate
    '''

    assert aggregate.name == 'Water Bottle'
    assert aggregate.size == 'large'
    assert aggregate.quantity == 2


# ** test: aggregate_update_quantity
def test_aggregate_update_quantity(aggregate: ItemAggregate) -> None:
    '''
    Test that update_quantity mutates the quantity field.

    :param aggregate: The sample aggregate.
    :type aggregate: ItemAggregate
    '''

    aggregate.update_quantity(5)

    assert aggregate.quantity == 5


# ** test: aggregate_update_quantity_invalid
def test_aggregate_update_quantity_invalid(aggregate: ItemAggregate) -> None:
    '''
    Test that update_quantity rejects invalid values (quantity < 1).

    :param aggregate: The sample aggregate.
    :type aggregate: ItemAggregate
    '''

    with pytest.raises(ValidationError):
        aggregate.update_quantity(0)


# ** test: aggregate_set_attribute_invalid
def test_aggregate_set_attribute_invalid(aggregate: ItemAggregate) -> None:
    '''
    Test that set_attribute raises TiferetError for unknown attributes.

    :param aggregate: The sample aggregate.
    :type aggregate: ItemAggregate
    '''

    with pytest.raises(TiferetError):
        aggregate.set_attribute('nonexistent', 'value')


# ** test: yaml_map
def test_yaml_map() -> None:
    '''
    Test that a YamlObject maps to an ItemAggregate with correct fields.
    '''

    yaml_obj = ItemYamlObject.model_validate(YAML_SAMPLE_DATA)
    result = yaml_obj.map()

    assert isinstance(result, ItemAggregate)
    assert result.name == 'Water Bottle'
    assert result.size == 'large'
    assert result.quantity == 2


# ** test: yaml_from_data
def test_yaml_from_data() -> None:
    '''
    Test that from_data creates a YamlObject from a raw dict.
    '''

    data = dict(size='medium', is_frozen=True, quantity=1)
    yaml_obj = ItemYamlObject.from_data(data, name='Ice Cream')

    assert yaml_obj.name == 'Ice Cream'
    assert yaml_obj.size == 'medium'
    assert yaml_obj.is_frozen is True


# ** test: yaml_from_model
def test_yaml_from_model(aggregate: ItemAggregate) -> None:
    '''
    Test that from_model creates a YamlObject from an aggregate.

    :param aggregate: The sample aggregate.
    :type aggregate: ItemAggregate
    '''

    yaml_obj = ItemYamlObject.from_model(aggregate)

    assert yaml_obj.name == 'Water Bottle'
    assert yaml_obj.size == 'large'
    assert yaml_obj.quantity == 2


# ** test: yaml_round_trip
def test_yaml_round_trip(aggregate: ItemAggregate) -> None:
    '''
    Test that aggregate -> YamlObject -> aggregate preserves data.

    :param aggregate: The sample aggregate.
    :type aggregate: ItemAggregate
    '''

    yaml_obj = ItemYamlObject.from_model(aggregate)
    result = yaml_obj.map()

    assert result.name == aggregate.name
    assert result.size == aggregate.size
    assert result.is_frozen == aggregate.is_frozen
    assert result.is_fragile == aggregate.is_fragile
    assert result.quantity == aggregate.quantity
