"""
FOODIE Robot SQLite Repository

Repository for instance-specific Robot data (fleet state, battery, location, compartments).
Used for multi-robot simulation and route planning (Goal A).
Uses tiferet.utils.Sqlite and RobotSqlObject.
"""

# *** imports

# ** core
from typing import List

# ** infra
from tiferet.utils import Sqlite

# ** app
from ..interfaces import RobotService
from ..mappers import RobotAggregate, RobotSqlObject

# *** repos

# ** repo: robot_sqlite_repository
class RobotSqliteRepository(RobotService):
    '''
    SQLite-backed repository for Robot domain objects (runtime fleet data).
    '''

    # * attribute: db_path
    db_path: str

    # * init
    def __init__(self, db_path: str = 'foodie.db') -> None:
        '''
        Initialize the Robot SQLite repository.

        :param db_path: Path to the SQLite database file.
        :type db_path: str
        '''
        self.db_path = db_path
        self._ensure_table()

    # * method: _ensure_table
    def _ensure_table(self) -> None:
        '''
        Create the robots table if it does not exist.
        '''
        with Sqlite(self.db_path, mode='rw') as db:
            db.executescript('''
                CREATE TABLE IF NOT EXISTS robots (
                    robot_id TEXT PRIMARY KEY,
                    current_location_json TEXT NOT NULL,
                    battery_level REAL NOT NULL,
                    compartments_json TEXT NOT NULL,
                    status TEXT NOT NULL
                );
            ''')

    # * method: exists
    def exists(self, robot_id: str) -> bool:
        with Sqlite(self.db_path) as db:
            row = db.execute("SELECT 1 FROM robots WHERE robot_id = ?", (robot_id,)).fetch_one()
            return row is not None

    # * method: get
    def get(self, robot_id: str) -> RobotAggregate:
        with Sqlite(self.db_path) as db:
            row = db.execute("SELECT * FROM robots WHERE robot_id = ?", (robot_id,)).fetch_one()
            if not row:
                return None
            return RobotSqlObject.from_data(dict(row)).map()

    # * method: list
    def list(self) -> List[RobotAggregate]:
        with Sqlite(self.db_path) as db:
            rows = db.execute("SELECT * FROM robots").fetch_all()
            return [RobotSqlObject.from_data(dict(row)).map() for row in rows]

    # * method: save
    def save(self, robot: RobotAggregate) -> None:
        data = RobotSqlObject.from_model(robot).to_primitive('to_data.sqlite')
        with Sqlite(self.db_path, mode='rw') as db:
            db.execute('''
                INSERT OR REPLACE INTO robots 
                (robot_id, current_location_json, battery_level, compartments_json, status)
                VALUES (?, ?, ?, ?, ?)
            ''', (
                robot.robot_id,
                data.get('current_location_json', '{}'),
                robot.battery_level,
                data.get('compartments_json', '[]'),
                robot.status
            ))

    # * method: delete
    def delete(self, robot_id: str) -> None:
        with Sqlite(self.db_path, mode='rw') as db:
            db.execute("DELETE FROM robots WHERE robot_id = ?", (robot_id,))