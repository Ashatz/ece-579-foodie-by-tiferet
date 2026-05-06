'''FOODIE Location Domain Model Tests'''

# *** imports

# ** infra
import pytest

# ** app
from ..location import Location


# *** fixtures

# ** fixture: default_location
@pytest.fixture
def default_location() -> Location:
    '''
    Create a Location with only required fields, relying on defaults.

    :return: A Location instance with default optional values.
    :rtype: Location
    '''
    return Location(name='Library', x=3.0, y=4.0)


# ** fixture: warehouse_location
@pytest.fixture
def warehouse_location() -> Location:
    '''
    Create a Location marked as a food warehouse.

    :return: A Location instance marked as food warehouse.
    :rtype: Location
    '''
    return Location(
        name='Central Kitchen',
        x=0.0,
        y=0.0,
        is_food_warehouse=True,
        is_obstacle_prone=True,
    )


# *** tests

# ** test: location_instantiation_defaults
def test_location_instantiation_defaults(default_location: Location) -> None:
    '''
    Test that a Location created with only required fields has correct defaults.

    :param default_location: Location fixture with defaults.
    :type default_location: Location
    '''

    # Assert required fields are set.
    assert default_location.name == 'Library'
    assert default_location.x == 3.0
    assert default_location.y == 4.0

    # Assert optional fields have correct defaults.
    assert default_location.is_food_warehouse is False
    assert default_location.is_obstacle_prone is False


# ** test: location_instantiation_all_fields
def test_location_instantiation_all_fields(warehouse_location: Location) -> None:
    '''
    Test that a Location created with all fields has correct values.

    :param warehouse_location: Location fixture with all fields.
    :type warehouse_location: Location
    '''

    # Assert all fields are set correctly.
    assert warehouse_location.name == 'Central Kitchen'
    assert warehouse_location.x == 0.0
    assert warehouse_location.y == 0.0
    assert warehouse_location.is_food_warehouse is True
    assert warehouse_location.is_obstacle_prone is True


# ** test: location_distance_to_self
def test_location_distance_to_self(default_location: Location) -> None:
    '''
    Test that distance to self is zero.

    :param default_location: Location fixture with defaults.
    :type default_location: Location
    '''

    # Assert distance to self is 0.
    assert default_location.distance_to(default_location) == 0.0


# ** test: location_distance_to_manhattan
def test_location_distance_to_manhattan(default_location: Location, warehouse_location: Location) -> None:
    '''
    Test Manhattan distance computation between two locations.

    :param default_location: Location at (3, 4).
    :type default_location: Location
    :param warehouse_location: Location at (0, 0).
    :type warehouse_location: Location
    '''

    # Assert Manhattan distance is |3-0| + |4-0| = 7.0.
    assert default_location.distance_to(warehouse_location) == 7.0


# ** test: location_distance_to_negative_coords
def test_location_distance_to_negative_coords() -> None:
    '''
    Test Manhattan distance with negative coordinates.
    '''

    # Create two locations with negative coordinates.
    loc_a = Location(name='A', x=-2.0, y=3.0)
    loc_b = Location(name='B', x=1.0, y=-1.0)

    # Assert Manhattan distance is |-2-1| + |3-(-1)| = 3 + 4 = 7.0.
    assert loc_a.distance_to(loc_b) == 7.0


# ** test: location_format_for_trace_regular
def test_location_format_for_trace_regular(default_location: Location) -> None:
    '''
    Test format_for_trace for a regular location.

    :param default_location: Location fixture with defaults.
    :type default_location: Location
    '''

    # Assert the formatted string has no Food Warehouse label.
    assert default_location.format_for_trace() == 'Library @ (3.0, 4.0)'


# ** test: location_format_for_trace_warehouse
def test_location_format_for_trace_warehouse(warehouse_location: Location) -> None:
    '''
    Test format_for_trace for a food warehouse location.

    :param warehouse_location: Location fixture marked as food warehouse.
    :type warehouse_location: Location
    '''

    # Assert the formatted string includes the Food Warehouse label.
    assert warehouse_location.format_for_trace() == 'Central Kitchen (Food Warehouse) @ (0.0, 0.0)'
