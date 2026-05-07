"""
FOODIE Beverage YAML Repository

Repository for beverage knowledge base data.
Uses tiferet.utils.Yaml and BeverageYamlObject.
"""

# *** imports

# ** core
from typing import List

# ** infra
from tiferet.utils import Yaml

# ** app
from ..interfaces import BeverageService
from ..mappers.beverage import BeverageAggregate, BeverageYamlObject

# *** repos

# ** repo: beverage_yaml_repository
class BeverageYamlRepository(BeverageService):
    '''
    YAML-backed repository for Beverage domain objects (knowledge base).
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
        Initialize the Beverage YAML repository.

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
        Check if a beverage exists by name.

        :param name: The beverage name.
        :type name: str
        :return: True if the beverage exists.
        :rtype: bool
        '''

        beverages_data = Yaml(
            self.yaml_file,
            encoding=self.encoding,
        ).load(
            start_node=lambda data: data.get('beverages', {})
        )
        return name in beverages_data

    # * method: get
    def get(self, name: str) -> BeverageAggregate:
        '''
        Retrieve a beverage by name.

        :param name: The beverage name.
        :type name: str
        :return: The beverage aggregate, or None if not found.
        :rtype: BeverageAggregate
        '''

        beverage_data = Yaml(
            self.yaml_file,
            encoding=self.encoding,
        ).load(
            start_node=lambda data: data.get('beverages', {}).get(name)
        )
        if not beverage_data:
            return None
        return BeverageYamlObject.from_data(beverage_data, name=name).map()

    # * method: list
    def list(self) -> List[BeverageAggregate]:
        '''
        List all configured beverages.

        :return: List of beverage aggregates.
        :rtype: List[BeverageAggregate]
        '''

        beverages_data = Yaml(
            self.yaml_file,
            encoding=self.encoding,
        ).load(
            start_node=lambda data: data.get('beverages', {})
        )
        return [
            BeverageYamlObject.from_data(data, name=name).map()
            for name, data in beverages_data.items()
        ]

    # * method: save
    def save(self, beverage: BeverageAggregate) -> None:
        '''
        Persist a beverage (insert or replace).

        :param beverage: The beverage aggregate to persist.
        :type beverage: BeverageAggregate
        '''

        full_data = Yaml(self.yaml_file, encoding=self.encoding).load()
        full_data.setdefault('beverages', {})[beverage.name] = \
            BeverageYamlObject.from_model(beverage).to_primitive(self.default_role)
        Yaml(self.yaml_file, mode='w', encoding=self.encoding).save(data=full_data)

    # * method: delete
    def delete(self, name: str) -> None:
        '''
        Delete a beverage by name (idempotent).

        :param name: The beverage name.
        :type name: str
        '''

        full_data = Yaml(self.yaml_file, encoding=self.encoding).load()
        full_data.get('beverages', {}).pop(name, None)
        Yaml(self.yaml_file, mode='w', encoding=self.encoding).save(data=full_data)
