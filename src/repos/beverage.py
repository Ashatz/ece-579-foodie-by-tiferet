"""
FOODIE Beverage YAML Repository

Repository for universal/config Beverage data (knowledge base for Goal C).
Uses tiferet.utils.Yaml and BeverageYamlObject.
"""

# *** imports

# ** core
from typing import List

# ** infra
from tiferet.utils import Yaml

# ** app
from ..interfaces import BeverageService
from ..mappers import BeverageAggregate, BeverageYamlObject

# *** repos

# ** repo: beverage_yaml_repository
class BeverageYamlRepository(BeverageService):
    '''
    YAML-backed repository for Beverage domain objects (universal knowledge base).
    '''

    # * attribute: yaml_file
    yaml_file: str

    # * attribute: encoding
    encoding: str

    # * attribute: default_role
    default_role: str

    # * init
    def __init__(self, menu_yaml_file: str = 'configs/menu.yml', encoding: str = 'utf-8') -> None:
        '''
        Initialize the Beverage YAML repository.

        :param menu_yaml_file: Path to the menu configuration file.
        :type menu_yaml_file: str
        '''
        self.yaml_file = menu_yaml_file
        self.encoding = encoding
        self.default_role = 'to_data.yaml'

    # * method: exists
    def exists(self, name: str) -> bool:
        beverages_data = Yaml(
            self.yaml_file,
            encoding=self.encoding,
        ).load(
            start_node=lambda data: data.get('beverages', {})
        )
        return name in beverages_data

    # * method: get
    def get(self, name: str) -> BeverageAggregate:
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
        full_data = Yaml(self.yaml_file, encoding=self.encoding).load()
        full_data.setdefault('beverages', {})[beverage.name] = BeverageYamlObject.from_model(beverage).to_primitive(self.default_role)
        Yaml(self.yaml_file, mode='w', encoding=self.encoding).save(data=full_data)

    # * method: delete
    def delete(self, name: str) -> None:
        full_data = Yaml(self.yaml_file, encoding=self.encoding).load()
        full_data.get('beverages', {}).pop(name, None)
        Yaml(self.yaml_file, mode='w', encoding=self.encoding).save(data=full_data)