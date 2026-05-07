"""
FOODIE Item YAML Repository Tests
"""

# *** imports

# ** infra
import pytest

# ** app
from ...mappers.item import ItemAggregate
from ..item import ItemYamlRepository

# *** constants

# ** constant: seed_yaml
SEED_YAML = """\
items:
  1-gallon water bottle:
    name: 1-gallon water bottle
    size: large
    is_frozen: false
    is_fragile: false
    quantity: 2
  pint ice cream:
    name: pint ice cream
    size: medium
    is_frozen: true
    is_fragile: false
    quantity: 1
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


# ** fixture: item_repo
@pytest.fixture
def item_repo(yaml_path) -> ItemYamlRepository:
    '''
    Create an ItemYamlRepository backed by the temporary YAML file.

    :param yaml_path: Path to the temporary YAML file.
    :type yaml_path: str
    :return: The repository instance.
    :rtype: ItemYamlRepository
    '''

    return ItemYamlRepository(menu_yaml_file=yaml_path)


# ** fixture: sample_item
@pytest.fixture
def sample_item() -> ItemAggregate:
    '''
    Build a sample ItemAggregate for testing.

    :return: An item aggregate.
    :rtype: ItemAggregate
    '''

    return ItemAggregate(
        name='granola box',
        size='small',
        is_frozen=False,
        is_fragile=False,
        quantity=3,
    )


# *** tests

# ** test: save_and_get
def test_save_and_get(item_repo: ItemYamlRepository, sample_item: ItemAggregate) -> None:
    '''
    Test that saving an item and retrieving it by name produces matching data.

    :param item_repo: The item repository.
    :type item_repo: ItemYamlRepository
    :param sample_item: The sample item aggregate.
    :type sample_item: ItemAggregate
    '''

    item_repo.save(sample_item)
    result = item_repo.get('granola box')

    assert result is not None
    assert result.name == 'granola box'
    assert result.size == 'small'
    assert result.is_frozen is False
    assert result.is_fragile is False
    assert result.quantity == 3


# ** test: exists_true
def test_exists_true(item_repo: ItemYamlRepository) -> None:
    '''
    Test that exists returns True for a seeded item.

    :param item_repo: The item repository.
    :type item_repo: ItemYamlRepository
    '''

    assert item_repo.exists('1-gallon water bottle') is True


# ** test: exists_false
def test_exists_false(item_repo: ItemYamlRepository) -> None:
    '''
    Test that exists returns False for a non-existent item.

    :param item_repo: The item repository.
    :type item_repo: ItemYamlRepository
    '''

    assert item_repo.exists('NO_SUCH_ITEM') is False


# ** test: get_not_found
def test_get_not_found(item_repo: ItemYamlRepository) -> None:
    '''
    Test that get returns None for a non-existent item.

    :param item_repo: The item repository.
    :type item_repo: ItemYamlRepository
    '''

    assert item_repo.get('NO_SUCH_ITEM') is None


# ** test: list_items
def test_list_items(item_repo: ItemYamlRepository) -> None:
    '''
    Test that list returns all seeded items.

    :param item_repo: The item repository.
    :type item_repo: ItemYamlRepository
    '''

    results = item_repo.list()
    assert len(results) == 2
    names = {item.name for item in results}
    assert names == {'1-gallon water bottle', 'pint ice cream'}


# ** test: save_updates_existing
def test_save_updates_existing(item_repo: ItemYamlRepository) -> None:
    '''
    Test that saving an item with the same name replaces the previous entry.

    :param item_repo: The item repository.
    :type item_repo: ItemYamlRepository
    '''

    updated = ItemAggregate(
        name='1-gallon water bottle',
        size='large',
        is_frozen=False,
        is_fragile=False,
        quantity=5,
    )
    item_repo.save(updated)

    result = item_repo.get('1-gallon water bottle')
    assert result.quantity == 5
    assert len(item_repo.list()) == 2


# ** test: delete_item
def test_delete_item(item_repo: ItemYamlRepository, sample_item: ItemAggregate) -> None:
    '''
    Test that deleting an item removes it from the YAML file.

    :param item_repo: The item repository.
    :type item_repo: ItemYamlRepository
    :param sample_item: The sample item aggregate.
    :type sample_item: ItemAggregate
    '''

    item_repo.save(sample_item)
    item_repo.delete('granola box')

    assert item_repo.exists('granola box') is False
    assert item_repo.get('granola box') is None


# ** test: delete_idempotent
def test_delete_idempotent(item_repo: ItemYamlRepository) -> None:
    '''
    Test that deleting a non-existent item does not raise.

    :param item_repo: The item repository.
    :type item_repo: ItemYamlRepository
    '''

    item_repo.delete('NO_SUCH_ITEM')
