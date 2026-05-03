"""
FOODIE Location SQLite Repository

Repository for instance-specific Location data (campus terrain graph nodes).
Used for route planning and dynamic obstacles (Goal A).
Uses tiferet.utils.Sqlite and LocationSqlObject.
"""

# *** imports

# ** core
from typing import List

# ** infra
from tiferet.utils import Sqlite

# ** app
from ..interfaces import LocationService
from ..mappers import LocationAggregate, LocationSqlObject

# *** repos

# ** repo: location_sqlite_repository
class LocationSqliteRepository(LocationService):
    '''
    SQLite-backed repository for Location domain objects (runtime terrain data).
    '''

    # * attribute: db_path
    db_path: str

    # * init
    def __init__(self, db_path: str = 'foodie.db') -> None:
        '''
        Initialize the Location SQLite repository.

        :param db_path: Path to the SQLite database file.
        :type db_path: str
        '''
        self.db_path = db_path
        self._ensure_table()

    # * method: _ensure_table
    def _ensure_table(self) -> None:
        '''
        Create the locations table if it does not exist.
        '''
        with Sqlite(self.db_path, mode='rw') as db:
            db.executescript('''
                CREATE TABLE IF NOT EXISTS locations (
                    name TEXT PRIMARY KEY,
                    x REAL NOT NULL,
                    y REAL NOT NULL,
                    is_food_warehouse INTEGER NOT NULL,
                    is_obstacle_prone INTEGER NOT NULL
                );
            ''')

    # * method: exists
    def exists(self, name: str) -> bool:
        with Sqlite(self.db_path) as db:
            row = db.execute("SELECT 1 FROM locations WHERE name = ?", (name,)).fetch_one()
            return row is not None

    # * method: get
    def get(self, name: str) -> LocationAggregate:
        with Sqlite(self.db_path) as db:
            row = db.execute("SELECT * FROM locations WHERE name = ?", (name,)).fetch_one()
            if not row:
                return None
            return LocationSqlObject.from_data(dict(row)).map()

    # * method: list
    def list(self) -> List[LocationAggregate]:
        with Sqlite(self.db_path) as db:
            rows = db.execute("SELECT * FROM locations").fetch_all()
            return [LocationSqlObject.from_data(dict(row)).map() for row in rows]

    # * method: save
    def save(self, location: LocationAggregate) -> None:
        with Sqlite(self.db_path, mode='rw') as db:
            db.execute('''
                INSERT OR REPLACE INTO locations 
                (name, x, y, is_food_warehouse, is_obstacle_prone)
                VALUES (?, ?, ?, ?, ?)
            ''', (
                location.name,
                location.x,
                location.y,
                int(location.is_food_warehouse),
                int(location.is_obstacle_prone)
            ))

    # * method: delete
    def delete(self, name: str) -> None:
        with Sqlite(self.db_path, mode='rw') as db:
            db.execute("DELETE FROM locations WHERE name = ?", (name,))