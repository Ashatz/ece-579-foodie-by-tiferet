"""
FOODIE Robot SQLite Repository

Repository for instance-specific Robot data (fleet state, battery, location, compartments).
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
        self.ensure_table()

    # * method: ensure_table
    def ensure_table(self) -> None:
        '''
        Create the robots table if it does not exist.
        '''

        with Sqlite(self.db_path, mode='rwc') as db:
            db.executescript('''
                CREATE TABLE IF NOT EXISTS robots (
                    robot_id TEXT PRIMARY KEY,
                    current_location_json TEXT NOT NULL,
                    battery_level REAL NOT NULL,
                    compartments_json TEXT NOT NULL,
                    status TEXT NOT NULL
                );
            ''')

    # * method: row_to_dict
    def row_to_dict(self, db: Sqlite, row: tuple) -> dict:
        '''
        Convert a tuple row to a dict using cursor column descriptions.

        :param db: The Sqlite client with an active cursor.
        :type db: Sqlite
        :param row: The raw tuple row from fetch.
        :type row: tuple
        :return: A dict keyed by column name.
        :rtype: dict
        '''

        columns = [desc[0] for desc in db.cursor.description]
        return dict(zip(columns, row))

    # * method: exists
    def exists(self, robot_id: str) -> bool:
        '''
        Check if a robot exists by ID.

        :param robot_id: The robot identifier.
        :type robot_id: str
        :return: True if the robot exists.
        :rtype: bool
        '''

        with Sqlite(self.db_path) as db:
            db.execute("SELECT 1 FROM robots WHERE robot_id = ?", (robot_id,))
            return db.fetch_one() is not None

    # * method: get
    def get(self, robot_id: str) -> RobotAggregate:
        '''
        Retrieve a robot by ID.

        :param robot_id: The robot identifier.
        :type robot_id: str
        :return: The robot aggregate, or None if not found.
        :rtype: RobotAggregate
        '''

        with Sqlite(self.db_path) as db:
            db.execute("SELECT * FROM robots WHERE robot_id = ?", (robot_id,))
            row = db.fetch_one()
            if not row:
                return None
            data = self.row_to_dict(db, row)
            return RobotSqlObject.from_data(data).map()

    # * method: list
    def list(self) -> List[RobotAggregate]:
        '''
        List all robots.

        :return: List of robot aggregates.
        :rtype: List[RobotAggregate]
        '''

        with Sqlite(self.db_path) as db:
            db.execute("SELECT * FROM robots")
            rows = db.fetch_all()
            results = []
            for row in rows:
                data = self.row_to_dict(db, row)
                results.append(RobotSqlObject.from_data(data).map())
            return results

    # * method: save
    def save(self, robot: RobotAggregate) -> None:
        '''
        Persist a robot (insert or replace).

        :param robot: The robot aggregate to persist.
        :type robot: RobotAggregate
        '''

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
                robot.status,
            ))

    # * method: delete
    def delete(self, robot_id: str) -> None:
        '''
        Delete a robot by ID.

        :param robot_id: The robot identifier.
        :type robot_id: str
        '''

        with Sqlite(self.db_path, mode='rw') as db:
            db.execute("DELETE FROM robots WHERE robot_id = ?", (robot_id,))
