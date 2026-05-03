"""
FOODIE Item YAML Repository

Repository for universal/config Item data (menu, rules, etc.).
Uses tiferet.utils.Yaml and ItemYamlObject.
"""

# *** imports

# ** core
from typing import List

# ** infra
from tiferet.utils import Yaml

# ** app
from ..interfaces import ItemService
from ..mappers import ItemAggregate, ItemYamlObject

# *** repos

# ** repo: item_yaml_repository
class ItemYamlRepository(ItemService):
    '''
    YAML-backed repository for Item domain objects.

    Items are universal/config data (not instance-specific), so YAML is appropriate.
    '''

    # * attribute: yaml_file
    yaml_file: str

    # * attribute: encoding
    encoding: str

    # * attribute: default_role
    default_role: str

    # * init
    def __init__(self, item_yaml_file: str, encoding: str = 'utf-8') -> None:
        '''
        Initialize the Item YAML repository.

        :param item_yaml_file: Path to the items configuration file.
        :type item_yaml_file: str
        '''
        self.yaml_file = item_yaml_file
        self.encoding = encoding
        self.default_role = 'to_data.yaml'

    # * method: exists
    def exists(self, name: str) -> bool:
        '''
        Check if an item exists by name.
        '''
        items_data = Yaml(
            self.yaml_file,
            encoding=self.encoding,
        ).load(
            start_node=lambda data: data.get('items', {})
        )
        return name in items_data

    # * method: get
    def get(self, name: str) -> ItemAggregate:
        '''
        Retrieve an item by name.
        '''
        item_data = Yaml(
            self.yaml_file,
            encoding=self.encoding,
        ).load(
            start_node=lambda data: data.get('items', {}).get(name)
        )
        if not item_data:
            return None
        return ItemYamlObject.from_data(item_data, name=name).map()

    # * method: list
    def list(self) -> List[ItemAggregate]:
        '''
        List all configured items.
        '''
        items_data = Yaml(
            self.yaml_file,
            encoding=self.encoding,
        ).load(
            start_node=lambda data: data.get('items', {})
        )
        return [
            ItemYamlObject.from_data(data, name=name).map()
            for name, data in items_data.items()
        ]

    # * method: save
    def save(self, item: ItemAggregate) -> None:
        '''
        Save an item to the YAML configuration.
        '''
        full_data = Yaml(self.yaml_file, encoding=self.encoding).load()
        full_data.setdefault('items', {})[item.name] = ItemYamlObject.from_model(item).to_primitive(self.default_role)
        Yaml(self.yaml_file, mode='w', encoding=self.encoding).save(data=full_data)

    # * method: delete
    def delete(self, name: str) -> None:
        '''
        Delete an item (idempotent).
        '''
        full_data = Yaml(self.yaml_file, encoding=self.encoding).load()
        full_data.get('items', {}).pop(name, None)
        Yaml(self.yaml_file, mode='w', encoding=self.encoding).save(data=full_data)