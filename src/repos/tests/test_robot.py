"""
FOODIE Robot SQLite Repository Tests
"""

# *** imports

# ** infra
import pytest

# ** app
from ...domain import Location, Bag, Item, Robot
from ...mappers import RobotAggregate
from ..robot import RobotSqliteRepository

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


# ** fixture: robot_repo
@pytest.fixture
def robot_repo(db_path) -> RobotSqliteRepository:
    '''
    Create a RobotSqliteRepository backed by a temporary database.

    :param db_path: Path to the temporary database.
    :type db_path: str
    :return: The repository instance.
    :rtype: RobotSqliteRepository
    '''

    return RobotSqliteRepository(db_path=db_path)


# ** fixture: fw_location
@pytest.fixture
def fw_location() -> Location:
    '''
    Build the Food Warehouse location for testing.

    :return: A Location domain object.
    :rtype: Location
    '''

    return Location(name='FW', x=0.0, y=0.0, is_food_warehouse=True)


# ** fixture: sample_robot
@pytest.fixture
def sample_robot(fw_location) -> RobotAggregate:
    '''
    Build a sample RobotAggregate for testing.

    :param fw_location: The Food Warehouse location.
    :type fw_location: Location
    :return: A robot aggregate.
    :rtype: RobotAggregate
    '''

    return RobotAggregate(
        robot_id='R1',
        current_location=fw_location,
        battery_level=100.0,
        status='idle',
    )


# *** tests

# ** test: save_and_get
def test_save_and_get(robot_repo: RobotSqliteRepository, sample_robot: RobotAggregate) -> None:
    '''
    Test that saving a robot and retrieving it by ID produces matching data.

    :param robot_repo: The robot repository.
    :type robot_repo: RobotSqliteRepository
    :param sample_robot: The sample robot aggregate.
    :type sample_robot: RobotAggregate
    '''

    robot_repo.save(sample_robot)
    result = robot_repo.get('R1')

    assert result is not None
    assert result.robot_id == 'R1'
    assert result.battery_level == 100.0
    assert result.status == 'idle'
    assert result.current_location.name == 'FW'
    assert result.current_location.is_food_warehouse is True
    assert result.compartments == []


# ** test: exists_true
def test_exists_true(robot_repo: RobotSqliteRepository, sample_robot: RobotAggregate) -> None:
    '''
    Test that exists returns True for a saved robot.

    :param robot_repo: The robot repository.
    :type robot_repo: RobotSqliteRepository
    :param sample_robot: The sample robot aggregate.
    :type sample_robot: RobotAggregate
    '''

    robot_repo.save(sample_robot)
    assert robot_repo.exists('R1') is True


# ** test: exists_false
def test_exists_false(robot_repo: RobotSqliteRepository) -> None:
    '''
    Test that exists returns False for a non-existent robot.

    :param robot_repo: The robot repository.
    :type robot_repo: RobotSqliteRepository
    '''

    assert robot_repo.exists('NO-SUCH-ROBOT') is False


# ** test: get_not_found
def test_get_not_found(robot_repo: RobotSqliteRepository) -> None:
    '''
    Test that get returns None for a non-existent robot.

    :param robot_repo: The robot repository.
    :type robot_repo: RobotSqliteRepository
    '''

    assert robot_repo.get('NO-SUCH-ROBOT') is None


# ** test: list_robots
def test_list_robots(robot_repo: RobotSqliteRepository, fw_location: Location) -> None:
    '''
    Test that list returns all saved robots.

    :param robot_repo: The robot repository.
    :type robot_repo: RobotSqliteRepository
    :param fw_location: The Food Warehouse location.
    :type fw_location: Location
    '''

    robot_repo.save(RobotAggregate(robot_id='R1', current_location=fw_location))
    robot_repo.save(RobotAggregate(robot_id='R2', current_location=fw_location))
    robot_repo.save(RobotAggregate(robot_id='R3', current_location=fw_location))

    results = robot_repo.list()
    assert len(results) == 3
    ids = {r.robot_id for r in results}
    assert ids == {'R1', 'R2', 'R3'}


# ** test: save_updates_existing
def test_save_updates_existing(robot_repo: RobotSqliteRepository, sample_robot: RobotAggregate) -> None:
    '''
    Test that saving a robot with the same ID replaces the previous record.

    :param robot_repo: The robot repository.
    :type robot_repo: RobotSqliteRepository
    :param sample_robot: The sample robot aggregate.
    :type sample_robot: RobotAggregate
    '''

    robot_repo.save(sample_robot)
    sample_robot.battery_level = 85.0
    sample_robot.status = 'en_route'
    robot_repo.save(sample_robot)

    result = robot_repo.get('R1')
    assert result.battery_level == 85.0
    assert result.status == 'en_route'
    assert len(robot_repo.list()) == 1


# ** test: delete_robot
def test_delete_robot(robot_repo: RobotSqliteRepository, sample_robot: RobotAggregate) -> None:
    '''
    Test that deleting a robot removes it from the database.

    :param robot_repo: The robot repository.
    :type robot_repo: RobotSqliteRepository
    :param sample_robot: The sample robot aggregate.
    :type sample_robot: RobotAggregate
    '''

    robot_repo.save(sample_robot)
    robot_repo.delete('R1')

    assert robot_repo.exists('R1') is False
    assert robot_repo.get('R1') is None


# ** test: delete_idempotent
def test_delete_idempotent(robot_repo: RobotSqliteRepository) -> None:
    '''
    Test that deleting a non-existent robot does not raise.

    :param robot_repo: The robot repository.
    :type robot_repo: RobotSqliteRepository
    '''

    robot_repo.delete('NO-SUCH-ROBOT')


# ** test: round_trip_preserves_location
def test_round_trip_preserves_location(robot_repo: RobotSqliteRepository) -> None:
    '''
    Test that nested Location data survives a full save/load round-trip.

    :param robot_repo: The robot repository.
    :type robot_repo: RobotSqliteRepository
    '''

    loc = Location(name='Building_A', x=5.0, y=8.0, is_obstacle_prone=True)
    robot = RobotAggregate(robot_id='R-LOC', current_location=loc, battery_level=72.5)
    robot_repo.save(robot)

    result = robot_repo.get('R-LOC')
    assert result.current_location.name == 'Building_A'
    assert result.current_location.x == 5.0
    assert result.current_location.y == 8.0
    assert result.current_location.is_obstacle_prone is True
    assert result.current_location.is_food_warehouse is False


# ** test: round_trip_preserves_compartments
def test_round_trip_preserves_compartments(robot_repo: RobotSqliteRepository, fw_location: Location) -> None:
    '''
    Test that nested Bag/Item compartment data survives a full save/load round-trip.

    :param robot_repo: The robot repository.
    :type robot_repo: RobotSqliteRepository
    :param fw_location: The Food Warehouse location.
    :type fw_location: Location
    '''

    bag = Bag(
        bag_id='bag_1',
        bag_type='paper',
        items=[Item(name='Bread', size='medium', quantity=1)],
    )
    robot = RobotAggregate(
        robot_id='R-COMP',
        current_location=fw_location,
        compartments=[bag],
    )
    robot_repo.save(robot)

    result = robot_repo.get('R-COMP')
    assert len(result.compartments) == 1
    assert result.compartments[0].bag_id == 'bag_1'
    assert result.compartments[0].bag_type == 'paper'
    assert len(result.compartments[0].items) == 1
    assert result.compartments[0].items[0].name == 'Bread'
