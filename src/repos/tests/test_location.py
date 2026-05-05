"""
FOODIE Location YAML Repository Tests
"""

# *** imports

# ** infra
import pytest

# ** app
from ...domain import Location
from ...mappers import LocationAggregate
from ..location import LocationYamlRepository

# *** constants

# ** constant: seed_yaml
SEED_YAML = """\
locations:
  FW:
    name: FW
    x: 0.0
    y: 0.0
    is_food_warehouse: true
    is_obstacle_prone: false
  Pathway_1:
    name: Pathway_1
    x: 2.0
    y: 0.0
  Building_A:
    name: Building_A
    x: 5.0
    y: 8.0

edges:
  FW: [Pathway_1]
  Pathway_1: [FW, Building_A]
  Building_A: [Pathway_1]
"""

# *** fixtures

# ** fixture: yaml_path
@pytest.fixture
def yaml_path(tmp_path) -> str:
    '''
    Write seed YAML data to a temporary file and return its path.

    :param tmp_path: Pytest temporary directory.
    :type tmp_path: pathlib.Path
    :return: Path to the temporary YAML file.
    :rtype: str
    '''

    path = tmp_path / 'test_campus.yml'
    path.write_text(SEED_YAML, encoding='utf-8')
    return str(path)


# ** fixture: location_repo
@pytest.fixture
def location_repo(yaml_path) -> LocationYamlRepository:
    '''
    Create a LocationYamlRepository backed by the temporary YAML file.

    :param yaml_path: Path to the temporary YAML file.
    :type yaml_path: str
    :return: The repository instance.
    :rtype: LocationYamlRepository
    '''

    return LocationYamlRepository(campus_yaml_file=yaml_path)


# ** fixture: sample_location
@pytest.fixture
def sample_location() -> LocationAggregate:
    '''
    Build a sample LocationAggregate for testing.

    :return: A location aggregate.
    :rtype: LocationAggregate
    '''

    return LocationAggregate(
        name='Dorm_1',
        x=0.0,
        y=5.0,
        is_food_warehouse=False,
        is_obstacle_prone=False,
    )


# *** tests

# ** test: save_and_get
def test_save_and_get(location_repo: LocationYamlRepository, sample_location: LocationAggregate) -> None:
    '''
    Test that saving a location and retrieving it by name produces matching data.

    :param location_repo: The location repository.
    :type location_repo: LocationYamlRepository
    :param sample_location: The sample location aggregate.
    :type sample_location: LocationAggregate
    '''

    location_repo.save(sample_location)
    result = location_repo.get('Dorm_1')

    assert result is not None
    assert result.name == 'Dorm_1'
    assert result.x == 0.0
    assert result.y == 5.0
    assert result.is_food_warehouse is False
    assert result.is_obstacle_prone is False


# ** test: exists_true
def test_exists_true(location_repo: LocationYamlRepository) -> None:
    '''
    Test that exists returns True for a seeded location.

    :param location_repo: The location repository.
    :type location_repo: LocationYamlRepository
    '''

    assert location_repo.exists('FW') is True


# ** test: exists_false
def test_exists_false(location_repo: LocationYamlRepository) -> None:
    '''
    Test that exists returns False for a non-existent location.

    :param location_repo: The location repository.
    :type location_repo: LocationYamlRepository
    '''

    assert location_repo.exists('NO_SUCH_PLACE') is False


# ** test: get_not_found
def test_get_not_found(location_repo: LocationYamlRepository) -> None:
    '''
    Test that get returns None for a non-existent location.

    :param location_repo: The location repository.
    :type location_repo: LocationYamlRepository
    '''

    assert location_repo.get('NO_SUCH_PLACE') is None


# ** test: list_locations
def test_list_locations(location_repo: LocationYamlRepository) -> None:
    '''
    Test that list returns all seeded locations.

    :param location_repo: The location repository.
    :type location_repo: LocationYamlRepository
    '''

    results = location_repo.list()
    assert len(results) == 3
    names = {loc.name for loc in results}
    assert names == {'FW', 'Pathway_1', 'Building_A'}


# ** test: get_seeded_location
def test_get_seeded_location(location_repo: LocationYamlRepository) -> None:
    '''
    Test that a seeded location is returned with correct attributes.

    :param location_repo: The location repository.
    :type location_repo: LocationYamlRepository
    '''

    fw = location_repo.get('FW')
    assert fw is not None
    assert fw.name == 'FW'
    assert fw.x == 0.0
    assert fw.y == 0.0
    assert fw.is_food_warehouse is True


# ** test: save_updates_existing
def test_save_updates_existing(location_repo: LocationYamlRepository) -> None:
    '''
    Test that saving a location with the same name replaces the previous entry.

    :param location_repo: The location repository.
    :type location_repo: LocationYamlRepository
    '''

    updated = LocationAggregate(name='FW', x=1.0, y=1.0, is_food_warehouse=True)
    location_repo.save(updated)

    result = location_repo.get('FW')
    assert result.x == 1.0
    assert result.y == 1.0
    assert len(location_repo.list()) == 3


# ** test: delete_location
def test_delete_location(location_repo: LocationYamlRepository) -> None:
    '''
    Test that deleting a location removes it from the YAML file.

    :param location_repo: The location repository.
    :type location_repo: LocationYamlRepository
    '''

    location_repo.delete('Building_A')

    assert location_repo.exists('Building_A') is False
    assert location_repo.get('Building_A') is None
    assert len(location_repo.list()) == 2


# ** test: delete_idempotent
def test_delete_idempotent(location_repo: LocationYamlRepository) -> None:
    '''
    Test that deleting a non-existent location does not raise.

    :param location_repo: The location repository.
    :type location_repo: LocationYamlRepository
    '''

    location_repo.delete('NO_SUCH_PLACE')


# ** test: get_edges
def test_get_edges(location_repo: LocationYamlRepository) -> None:
    '''
    Test that get_edges returns the seeded adjacency list.

    :param location_repo: The location repository.
    :type location_repo: LocationYamlRepository
    '''

    edges = location_repo.get_edges()
    assert isinstance(edges, dict)
    assert edges['FW'] == ['Pathway_1']
    assert edges['Pathway_1'] == ['FW', 'Building_A']
    assert edges['Building_A'] == ['Pathway_1']


# ** test: round_trip_preserves_attributes
def test_round_trip_preserves_attributes(location_repo: LocationYamlRepository) -> None:
    '''
    Test that all Location attributes survive a full save/load round-trip.

    :param location_repo: The location repository.
    :type location_repo: LocationYamlRepository
    '''

    loc = LocationAggregate(
        name='Pathway_X',
        x=3.5,
        y=7.2,
        is_food_warehouse=False,
        is_obstacle_prone=True,
    )
    location_repo.save(loc)

    result = location_repo.get('Pathway_X')
    assert result.name == 'Pathway_X'
    assert result.x == 3.5
    assert result.y == 7.2
    assert result.is_food_warehouse is False
    assert result.is_obstacle_prone is True
