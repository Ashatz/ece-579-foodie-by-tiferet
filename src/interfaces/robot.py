"""
FOODIE Robot Service Interface
"""

# *** imports

# ** core
from abc import abstractmethod
from typing import List

# ** infra
from tiferet.interfaces import Service

# ** app
from ..domain import Robot

# *** interfaces

# ** interface: robot_service
class RobotService(Service):
    '''
    Vertical interface for fleet Robot data.
    '''

    # * method: exists
    @abstractmethod
    def exists(self, robot_id: str) -> bool:
        '''
        Check if a robot exists by ID.

        :param robot_id: The robot identifier.
        :type robot_id: str
        :return: True if the robot exists.
        :rtype: bool
        '''
        raise NotImplementedError()

    # * method: get
    @abstractmethod
    def get(self, robot_id: str) -> Robot:
        '''
        Retrieve a robot by ID.

        :param robot_id: The robot identifier.
        :type robot_id: str
        :return: The robot domain object.
        :rtype: Robot
        '''
        raise NotImplementedError()

    # * method: list
    @abstractmethod
    def list(self) -> List[Robot]:
        '''
        List all robots.

        :return: List of robot domain objects.
        :rtype: List[Robot]
        '''
        raise NotImplementedError()

    # * method: save
    @abstractmethod
    def save(self, robot: Robot) -> None:
        '''
        Persist a robot.

        :param robot: The robot to persist.
        :type robot: Robot
        '''
        raise NotImplementedError()

    # * method: delete
    @abstractmethod
    def delete(self, robot_id: str) -> None:
        '''
        Delete a robot by ID.

        :param robot_id: The robot identifier.
        :type robot_id: str
        '''
        raise NotImplementedError()
