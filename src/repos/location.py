"""
FOODIE Location YAML Repository

Repository for campus terrain Location data (graph nodes and edges).
Uses tiferet.utils.Yaml and LocationYamlObject.
"""

# *** imports

# ** core
from typing import Dict, List

# ** infra
from tiferet.utils import Yaml

# ** app
from ..interfaces import LocationService
from ..mappers import LocationAggregate, LocationYamlObject

# *** repos

# ** repo: location_yaml_repository
class LocationYamlRepository(LocationService):
    '''
    YAML-backed repository for Location domain objects (campus terrain graph).
    '''

    # * attribute: yaml_file
    yaml_file: str

    # * attribute: encoding
    encoding: str

    # * attribute: default_role
    default_role: str

    # * init
    def __init__(self, campus_yaml_file: str = 'campus.yml', encoding: str = 'utf-8') -> None:
        '''
        Initialize the Location YAML repository.

        :param campus_yaml_file: Path to the campus configuration file.
        :type campus_yaml_file: str
        :param encoding: File encoding.
        :type encoding: str
        '''

        self.yaml_file = campus_yaml_file
        self.encoding = encoding
        self.default_role = 'to_data.yaml'

    # * method: exists
    def exists(self, name: str) -> bool:
        '''
        Check if a location exists by name.

        :param name: The location name.
        :type name: str
        :return: True if the location exists.
        :rtype: bool
        '''

        locations_data = Yaml(
            self.yaml_file,
            encoding=self.encoding,
        ).load(
            start_node=lambda data: data.get('locations', {})
        )
        return name in locations_data

    # * method: get
    def get(self, name: str) -> LocationAggregate:
        '''
        Retrieve a location by name.

        :param name: The location name.
        :type name: str
        :return: The location aggregate, or None if not found.
        :rtype: LocationAggregate
        '''

        location_data = Yaml(
            self.yaml_file,
            encoding=self.encoding,
        ).load(
            start_node=lambda data: data.get('locations', {}).get(name)
        )
        if not location_data:
            return None
        return LocationYamlObject.from_data(location_data, name=name).map()

    # * method: list
    def list(self) -> List[LocationAggregate]:
        '''
        List all locations.

        :return: List of location aggregates.
        :rtype: List[LocationAggregate]
        '''

        locations_data = Yaml(
            self.yaml_file,
            encoding=self.encoding,
        ).load(
            start_node=lambda data: data.get('locations', {})
        )
        return [
            LocationYamlObject.from_data(data, name=name).map()
            for name, data in locations_data.items()
        ]

    # * method: save
    def save(self, location: LocationAggregate) -> None:
        '''
        Persist a location (insert or replace).

        :param location: The location aggregate to persist.
        :type location: LocationAggregate
        '''

        full_data = Yaml(self.yaml_file, encoding=self.encoding).load()
        full_data.setdefault('locations', {})[location.name] = \
            LocationYamlObject.from_model(location).to_primitive(self.default_role)
        Yaml(self.yaml_file, mode='w', encoding=self.encoding).save(data=full_data)

    # * method: delete
    def delete(self, name: str) -> None:
        '''
        Delete a location by name (idempotent).

        :param name: The location name.
        :type name: str
        '''

        full_data = Yaml(self.yaml_file, encoding=self.encoding).load()
        full_data.get('locations', {}).pop(name, None)
        Yaml(self.yaml_file, mode='w', encoding=self.encoding).save(data=full_data)

    # * method: get_edges
    def get_edges(self) -> Dict[str, List[str]]:
        '''
        Retrieve the campus graph adjacency list.

        :return: Dict mapping location names to lists of neighbor names.
        :rtype: Dict[str, List[str]]
        '''

        return Yaml(
            self.yaml_file,
            encoding=self.encoding,
        ).load(
            start_node=lambda data: data.get('edges', {})
        )
