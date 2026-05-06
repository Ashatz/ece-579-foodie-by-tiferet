"""
FOODIE Robot Domain Model Tests
"""

# *** imports

# ** infra
import pytest
from pydantic import ValidationError

# ** app
from ..location import Location
from ..item import Item
from ..bag import Bag
from ..robot import Robot

# *** fixtures

# ** fixture: home_location
@pytest.fixture
def home_location() -> Location:
    '''
    The Food Warehouse location (robot home base).

    :return: A Location instance for the Food Warehouse.
    :rtype: Location
    '''

    return Location(name='FW', x=0.0, y=0.0, is_food_warehouse=True)


# ** fixture: sample_bag
@pytest.fixture
def sample_bag() -> Bag:
    '''
    A bag with one item for loading tests.

    :return: A Bag instance with one item.
    :rtype: Bag
    '''

    return Bag(
        bag_id='bag_1',
        items=[Item(name='Sandwich', size='medium')],
    )


# ** fixture: idle_robot
@pytest.fixture
def idle_robot(home_location: Location) -> Robot:
    '''
    An idle robot at the Food Warehouse with full battery.

    :param home_location: The Food Warehouse location.
    :type home_location: Location
    :return: An idle Robot instance.
    :rtype: Robot
    '''

    return Robot(robot_id='R1', current_location=home_location)


# *** tests

# ** test: instantiation_defaults
def test_instantiation_defaults(idle_robot: Robot) -> None:
    '''
    Test that default field values are applied correctly.

    :param idle_robot: An idle Robot instance.
    :type idle_robot: Robot
    '''

    assert idle_robot.robot_id == 'R1'
    assert idle_robot.current_location.name == 'FW'
    assert idle_robot.battery_level == 100.0
    assert idle_robot.compartments == []
    assert idle_robot.status == 'idle'


# ** test: battery_bounds
def test_battery_bounds(home_location: Location) -> None:
    '''
    Test that battery_level enforces bounds.

    :param home_location: The Food Warehouse location.
    :type home_location: Location
    '''

    with pytest.raises(ValidationError):
        Robot(robot_id='R_BAD', current_location=home_location, battery_level=101.0)

    with pytest.raises(ValidationError):
        Robot(robot_id='R_BAD', current_location=home_location, battery_level=-1.0)


# ** test: invalid_status_rejected
def test_invalid_status_rejected(home_location: Location) -> None:
    '''
    Test that an invalid status literal raises a validation error.

    :param home_location: The Food Warehouse location.
    :type home_location: Location
    '''

    with pytest.raises(ValidationError):
        Robot(robot_id='R_BAD', current_location=home_location, status='broken')


# ** test: load_bag_idle
def test_load_bag_idle(idle_robot: Robot, sample_bag: Bag) -> None:
    '''
    Test that an idle robot can load a bag.

    :param idle_robot: An idle Robot instance.
    :type idle_robot: Robot
    :param sample_bag: A Bag instance.
    :type sample_bag: Bag
    '''

    result = idle_robot.load_bag(sample_bag)

    assert result is True
    assert len(idle_robot.compartments) == 1
    assert idle_robot.compartments[0].bag_id == 'bag_1'


# ** test: load_bag_en_route_rejected
def test_load_bag_en_route_rejected(home_location: Location, sample_bag: Bag) -> None:
    '''
    Test that a robot in en_route status cannot load bags.

    :param home_location: The Food Warehouse location.
    :type home_location: Location
    :param sample_bag: A Bag instance.
    :type sample_bag: Bag
    '''

    robot = Robot(robot_id='R2', current_location=home_location, status='en_route')

    result = robot.load_bag(sample_bag)

    assert result is False
    assert len(robot.compartments) == 0


# ** test: load_bag_delivering_rejected
def test_load_bag_delivering_rejected(home_location: Location, sample_bag: Bag) -> None:
    '''
    Test that a robot in delivering status cannot load bags.

    :param home_location: The Food Warehouse location.
    :type home_location: Location
    :param sample_bag: A Bag instance.
    :type sample_bag: Bag
    '''

    robot = Robot(robot_id='R3', current_location=home_location, status='delivering')

    result = robot.load_bag(sample_bag)

    assert result is False


# ** test: consume_energy_normal
def test_consume_energy_normal(idle_robot: Robot) -> None:
    '''
    Test that consume_energy reduces battery correctly.

    :param idle_robot: An idle Robot instance.
    :type idle_robot: Robot
    '''

    idle_robot.consume_energy(100.0, energy_per_meter=0.12)

    # 100 - (100 * 0.12) = 88.0
    assert idle_robot.battery_level == pytest.approx(88.0)


# ** test: consume_energy_clamps_to_zero
def test_consume_energy_clamps_to_zero(home_location: Location) -> None:
    '''
    Test that consume_energy clamps battery to zero (not negative).

    :param home_location: The Food Warehouse location.
    :type home_location: Location
    '''

    robot = Robot(robot_id='R4', current_location=home_location, battery_level=5.0)
    robot.consume_energy(1000.0, energy_per_meter=0.12)

    assert robot.battery_level == 0.0


# ** test: is_low_battery_below_threshold
def test_is_low_battery_below_threshold(home_location: Location) -> None:
    '''
    Test that is_low_battery returns True when battery is below threshold.

    :param home_location: The Food Warehouse location.
    :type home_location: Location
    '''

    robot = Robot(robot_id='R5', current_location=home_location, battery_level=15.0)

    assert robot.is_low_battery() is True


# ** test: is_low_battery_at_threshold
def test_is_low_battery_at_threshold(home_location: Location) -> None:
    '''
    Test that is_low_battery returns True when battery equals threshold.

    :param home_location: The Food Warehouse location.
    :type home_location: Location
    '''

    robot = Robot(robot_id='R6', current_location=home_location, battery_level=20.0)

    assert robot.is_low_battery() is True


# ** test: is_low_battery_above_threshold
def test_is_low_battery_above_threshold(idle_robot: Robot) -> None:
    '''
    Test that is_low_battery returns False when battery is above threshold.

    :param idle_robot: An idle Robot with full battery.
    :type idle_robot: Robot
    '''

    assert idle_robot.is_low_battery() is False


# ** test: is_low_battery_custom_threshold
def test_is_low_battery_custom_threshold(home_location: Location) -> None:
    '''
    Test is_low_battery with a custom threshold.

    :param home_location: The Food Warehouse location.
    :type home_location: Location
    '''

    robot = Robot(robot_id='R7', current_location=home_location, battery_level=50.0)

    assert robot.is_low_battery(threshold=60.0) is True
    assert robot.is_low_battery(threshold=40.0) is False


# ** test: format_for_trace
def test_format_for_trace(idle_robot: Robot) -> None:
    '''
    Test format_for_trace produces the expected output.

    :param idle_robot: An idle Robot instance.
    :type idle_robot: Robot
    '''

    result = idle_robot.format_for_trace()

    assert result == 'Robot R1 | Loc: FW (Food Warehouse) @ (0.0, 0.0) | Battery: 100.0% | Status: idle | Bags: 0'


# ** test: format_for_trace_with_bags
def test_format_for_trace_with_bags(idle_robot: Robot, sample_bag: Bag) -> None:
    '''
    Test format_for_trace after loading a bag.

    :param idle_robot: An idle Robot instance.
    :type idle_robot: Robot
    :param sample_bag: A Bag instance.
    :type sample_bag: Bag
    '''

    idle_robot.load_bag(sample_bag)
    result = idle_robot.format_for_trace()

    assert 'Bags: 1' in result
