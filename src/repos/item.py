"""
FOODIE Item YAML Repository

Repository for menu catalog Item data.
Uses tiferet.utils.Yaml and ItemYamlObject.
"""

# *** imports

# ** core
from typing import List

# ** infra
from tiferet.utils import Yaml

# ** app
from ..interfaces import ItemService
from ..mappers.item import ItemAggregate, ItemYamlObject

# *** repos

# ** repo: item_yaml_repository
class ItemYamlRepository(ItemService):
    '''
    YAML-backed repository for Item domain objects (menu catalog).
    '''

    # * attribute: yaml_file
    yaml_file: str

    # * attribute: encoding
    encoding: str

    # * attribute: default_role
    default_role: str

    # * init
    def __init__(self, menu_yaml_file: str = 'menu.yml', encoding: str = 'utf-8') -> None:
        '''
        Initialize the Item YAML repository.

        :param menu_yaml_file: Path to the menu configuration file.
        :type menu_yaml_file: str
        :param encoding: File encoding.
        :type encoding: str
        '''

        self.yaml_file = menu_yaml_file
        self.encoding = encoding
        self.default_role = 'to_data.yaml'

    # * method: exists
    def exists(self, name: str) -> bool:
        '''
        Check if an item exists by name.

        :param name: The item name.
        :type name: str
        :return: True if the item exists.
        :rtype: bool
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

        :param name: The item name.
        :type name: str
        :return: The item aggregate, or None if not found.
        :rtype: ItemAggregate
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

        :return: List of item aggregates.
        :rtype: List[ItemAggregate]
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
        Persist an item (insert or replace).

        :param item: The item aggregate to persist.
        :type item: ItemAggregate
        '''

        full_data = Yaml(self.yaml_file, encoding=self.encoding).load()
        full_data.setdefault('items', {})[item.name] = \
            ItemYamlObject.from_model(item).to_primitive(self.default_role)
        Yaml(self.yaml_file, mode='w', encoding=self.encoding).save(data=full_data)

    # * method: delete
    def delete(self, name: str) -> None:
        '''
        Delete an item by name (idempotent).

        :param name: The item name.
        :type name: str
        '''

        full_data = Yaml(self.yaml_file, encoding=self.encoding).load()
        full_data.get('items', {}).pop(name, None)
        Yaml(self.yaml_file, mode='w', encoding=self.encoding).save(data=full_data)
