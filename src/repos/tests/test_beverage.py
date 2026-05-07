"""
FOODIE Beverage YAML Repository Tests
"""

# *** imports

# ** infra
import pytest

# ** app
from ...mappers.beverage import BeverageAggregate
from ..beverage import BeverageYamlRepository

# *** constants

# ** constant: seed_yaml
SEED_YAML = """\
beverages:
  Carrot Juice:
    name: Carrot Juice
    beverage_type: juice
    brand: FreshRoots
    is_health_friendly: true
    avoids_allergens: citrus
  Corona Beer:
    name: Corona Beer
    beverage_type: beer
    brand: Corona
    is_health_friendly: false
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

    path = tmp_path / 'test_menu.yml'
    path.write_text(SEED_YAML, encoding='utf-8')
    return str(path)


# ** fixture: beverage_repo
@pytest.fixture
def beverage_repo(yaml_path) -> BeverageYamlRepository:
    '''
    Create a BeverageYamlRepository backed by the temporary YAML file.

    :param yaml_path: Path to the temporary YAML file.
    :type yaml_path: str
    :return: The repository instance.
    :rtype: BeverageYamlRepository
    '''

    return BeverageYamlRepository(menu_yaml_file=yaml_path)


# ** fixture: sample_beverage
@pytest.fixture
def sample_beverage() -> BeverageAggregate:
    '''
    Build a sample BeverageAggregate for testing.

    :return: A beverage aggregate.
    :rtype: BeverageAggregate
    '''

    return BeverageAggregate(
        name='Green Tea',
        beverage_type='water',
        brand='ZenLeaf',
        is_health_friendly=True,
    )


# *** tests

# ** test: save_and_get
def test_save_and_get(beverage_repo: BeverageYamlRepository, sample_beverage: BeverageAggregate) -> None:
    '''
    Test that saving a beverage and retrieving it by name produces matching data.

    :param beverage_repo: The beverage repository.
    :type beverage_repo: BeverageYamlRepository
    :param sample_beverage: The sample beverage aggregate.
    :type sample_beverage: BeverageAggregate
    '''

    beverage_repo.save(sample_beverage)
    result = beverage_repo.get('Green Tea')

    assert result is not None
    assert result.name == 'Green Tea'
    assert result.beverage_type == 'water'
    assert result.brand == 'ZenLeaf'
    assert result.is_health_friendly is True


# ** test: exists_true
def test_exists_true(beverage_repo: BeverageYamlRepository) -> None:
    '''
    Test that exists returns True for a seeded beverage.

    :param beverage_repo: The beverage repository.
    :type beverage_repo: BeverageYamlRepository
    '''

    assert beverage_repo.exists('Carrot Juice') is True


# ** test: exists_false
def test_exists_false(beverage_repo: BeverageYamlRepository) -> None:
    '''
    Test that exists returns False for a non-existent beverage.

    :param beverage_repo: The beverage repository.
    :type beverage_repo: BeverageYamlRepository
    '''

    assert beverage_repo.exists('NO_SUCH_BEVERAGE') is False


# ** test: get_not_found
def test_get_not_found(beverage_repo: BeverageYamlRepository) -> None:
    '''
    Test that get returns None for a non-existent beverage.

    :param beverage_repo: The beverage repository.
    :type beverage_repo: BeverageYamlRepository
    '''

    assert beverage_repo.get('NO_SUCH_BEVERAGE') is None


# ** test: list_beverages
def test_list_beverages(beverage_repo: BeverageYamlRepository) -> None:
    '''
    Test that list returns all seeded beverages.

    :param beverage_repo: The beverage repository.
    :type beverage_repo: BeverageYamlRepository
    '''

    results = beverage_repo.list()
    assert len(results) == 2
    names = {bev.name for bev in results}
    assert names == {'Carrot Juice', 'Corona Beer'}


# ** test: save_updates_existing
def test_save_updates_existing(beverage_repo: BeverageYamlRepository) -> None:
    '''
    Test that saving a beverage with the same name replaces the previous entry.

    :param beverage_repo: The beverage repository.
    :type beverage_repo: BeverageYamlRepository
    '''

    updated = BeverageAggregate(
        name='Carrot Juice',
        beverage_type='juice',
        brand='OrganicRoots',
        is_health_friendly=True,
        avoids_allergens='citrus',
    )
    beverage_repo.save(updated)

    result = beverage_repo.get('Carrot Juice')
    assert result.brand == 'OrganicRoots'
    assert len(beverage_repo.list()) == 2


# ** test: delete_beverage
def test_delete_beverage(beverage_repo: BeverageYamlRepository, sample_beverage: BeverageAggregate) -> None:
    '''
    Test that deleting a beverage removes it from the YAML file.

    :param beverage_repo: The beverage repository.
    :type beverage_repo: BeverageYamlRepository
    :param sample_beverage: The sample beverage aggregate.
    :type sample_beverage: BeverageAggregate
    '''

    beverage_repo.save(sample_beverage)
    beverage_repo.delete('Green Tea')

    assert beverage_repo.exists('Green Tea') is False
    assert beverage_repo.get('Green Tea') is None


# ** test: delete_idempotent
def test_delete_idempotent(beverage_repo: BeverageYamlRepository) -> None:
    '''
    Test that deleting a non-existent beverage does not raise.

    :param beverage_repo: The beverage repository.
    :type beverage_repo: BeverageYamlRepository
    '''

    beverage_repo.delete('NO_SUCH_BEVERAGE')
