"""
FOODIE Bag SQLite Repository

Repository for instance-specific Bag data (bagging sessions from FOODIE_BAGGER).
Uses tiferet.utils.Sqlite and BagSqlObject.
"""

# *** imports

# ** core
from typing import List

# ** infra
from tiferet.utils import Sqlite

# ** app
from ..interfaces import BagService
from ..mappers import BagAggregate, BagSqlObject

# *** repos

# ** repo: bag_sqlite_repository
class BagSqliteRepository(BagService):
    '''
    SQLite-backed repository for Bag domain objects (runtime bagging data).
    '''

    # * attribute: db_path
    db_path: str

    # * init
    def __init__(self, db_path: str = 'foodie.db') -> None:
        '''
        Initialize the Bag SQLite repository.

        :param db_path: Path to the SQLite database file.
        :type db_path: str
        '''
        self.db_path = db_path
        self._ensure_table()

    # * method: _ensure_table
    def _ensure_table(self) -> None:
        '''
        Create the bags table if it does not exist.
        '''
        with Sqlite(self.db_path, mode='rw') as db:
            db.executescript('''
                CREATE TABLE IF NOT EXISTS bags (
                    bag_id TEXT PRIMARY KEY,
                    bag_type TEXT NOT NULL,
                    items_json TEXT NOT NULL
                );
            ''')

    # * method: exists
    def exists(self, bag_id: str) -> bool:
        with Sqlite(self.db_path) as db:
            row = db.execute("SELECT 1 FROM bags WHERE bag_id = ?", (bag_id,)).fetch_one()
            return row is not None

    # * method: get
    def get(self, bag_id: str) -> BagAggregate:
        with Sqlite(self.db_path) as db:
            row = db.execute("SELECT * FROM bags WHERE bag_id = ?", (bag_id,)).fetch_one()
            if not row:
                return None
            return BagSqlObject.from_data(dict(row)).map()

    # * method: list
    def list(self) -> List[BagAggregate]:
        with Sqlite(self.db_path) as db:
            rows = db.execute("SELECT * FROM bags").fetch_all()
            return [BagSqlObject.from_data(dict(row)).map() for row in rows]

    # * method: save
    def save(self, bag: BagAggregate) -> None:
        data = BagSqlObject.from_model(bag).to_primitive('to_data.sqlite')
        with Sqlite(self.db_path, mode='rw') as db:
            db.execute('''
                INSERT OR REPLACE INTO bags (bag_id, bag_type, items_json)
                VALUES (?, ?, ?)
            ''', (
                bag.bag_id,
                bag.bag_type,
                data.get('items_json', '[]')
            ))

    # * method: delete
    def delete(self, bag_id: str) -> None:
        with Sqlite(self.db_path, mode='rw') as db:
            db.execute("DELETE FROM bags WHERE bag_id = ?", (bag_id,))