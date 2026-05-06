"""
FOODIE Location Domain Model Tests
"""

# *** imports

# ** infra
import pytest

# ** app
from ..location import Location

# *** fixtures

# ** fixture: food_warehouse
@pytest.fixture
def food_warehouse() -> Location:
    '''
    The Food Warehouse location.

    :return: A Location instance for the Food Warehouse.
    :rtype: Location
    '''

    return Location(name='FW', x=0.0, y=0.0, is_food_warehouse=True)


# ** fixture: building_a
@pytest.fixture
def building_a() -> Location:
    '''
    A regular building location.

    :return: A Location instance for Building A.
    :rtype: Location
    '''

    return Location(name='Building_A', x=3.0, y=4.0)


# *** tests

# ** test: instantiation_defaults
def test_instantiation_defaults(building_a: Location) -> None:
    '''
    Test that default field values are applied correctly.

    :param building_a: A regular Location instance.
    :type building_a: Location
    '''

    assert building_a.name == 'Building_A'
    assert building_a.x == 3.0
    assert building_a.y == 4.0
    assert building_a.is_food_warehouse is False
    assert building_a.is_obstacle_prone is False


# ** test: instantiation_all_fields
def test_instantiation_all_fields() -> None:
    '''
    Test that all fields can be set explicitly.
    '''

    loc = Location(name='Pathway_X', x=1.5, y=2.5, is_food_warehouse=False, is_obstacle_prone=True)

    assert loc.name == 'Pathway_X'
    assert loc.x == 1.5
    assert loc.y == 2.5
    assert loc.is_obstacle_prone is True


# ** test: distance_to_same_point
def test_distance_to_same_point(food_warehouse: Location) -> None:
    '''
    Test that distance to self is zero.

    :param food_warehouse: The Food Warehouse location.
    :type food_warehouse: Location
    '''

    assert food_warehouse.distance_to(food_warehouse) == 0.0


# ** test: distance_to_manhattan
def test_distance_to_manhattan(food_warehouse: Location, building_a: Location) -> None:
    '''
    Test Manhattan distance between two locations.

    :param food_warehouse: The Food Warehouse location (0, 0).
    :type food_warehouse: Location
    :param building_a: Building A location (3, 4).
    :type building_a: Location
    '''

    # |3-0| + |4-0| = 7.0
    assert food_warehouse.distance_to(building_a) == 7.0
    assert building_a.distance_to(food_warehouse) == 7.0


# ** test: distance_to_negative_coords
def test_distance_to_negative_coords() -> None:
    '''
    Test Manhattan distance with negative coordinates.
    '''

    a = Location(name='A', x=-2.0, y=3.0)
    b = Location(name='B', x=1.0, y=-1.0)

    # |1-(-2)| + |(-1)-3| = 3 + 4 = 7.0
    assert a.distance_to(b) == 7.0


# ** test: format_for_trace_regular
def test_format_for_trace_regular(building_a: Location) -> None:
    '''
    Test format_for_trace for a regular location.

    :param building_a: A regular Location instance.
    :type building_a: Location
    '''

    result = building_a.format_for_trace()

    assert result == 'Building_A @ (3.0, 4.0)'


# ** test: format_for_trace_food_warehouse
def test_format_for_trace_food_warehouse(food_warehouse: Location) -> None:
    '''
    Test format_for_trace for the Food Warehouse.

    :param food_warehouse: The Food Warehouse location.
    :type food_warehouse: Location
    '''

    result = food_warehouse.format_for_trace()

    assert result == 'FW (Food Warehouse) @ (0.0, 0.0)'
