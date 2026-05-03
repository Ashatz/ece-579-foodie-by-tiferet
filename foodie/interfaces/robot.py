"""
FOODIE Robot Service Interface (SQLite-backed)
"""

# *** imports

# ** infra
from tiferet.interfaces import Service
from typing import List

# ** app
from ..mappers import RobotAggregate

# *** interfaces

# ** interface: robot_service
class RobotService(Service):
    '''
    Vertical interface for fleet Robot data.
    '''

    # * method: exists
    def exists(self, robot_id: str) -> bool: ...

    # * method: get
    def get(self, robot_id: str) -> RobotAggregate: ...

    # * method: list
    def list(self) -> List[RobotAggregate]: ...

    # * method: save
    def save(self, robot: RobotAggregate) -> None: ...

    # * method: delete
    def delete(self, robot_id: str) -> None: ...