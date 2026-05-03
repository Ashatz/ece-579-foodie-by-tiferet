"""
FOODIE Order SQLite Repository

Repository for instance-specific Order data (runtime orders, bagging results, etc.).
Uses tiferet.utils.Sqlite and OrderSqlObject.
"""

# *** imports

# ** core
from typing import List

# ** infra
from tiferet.utils import Sqlite

# ** app
from ..interfaces import OrderService
from ..mappers import OrderAggregate, OrderSqlObject

# *** repos

# ** repo: order_sqlite_repository
class OrderSqliteRepository(OrderService):
    '''
    SQLite-backed repository for Order domain objects (runtime data).
    '''

    # * attribute: db_path
    db_path: str

    # * init
    def __init__(self, db_path: str = 'foodie.db') -> None:
        '''
        Initialize the Order SQLite repository.

        :param db_path: Path to the SQLite database file.
        :type db_path: str
        '''
        self.db_path = db_path
        self._ensure_table()

    # * method: _ensure_table (private helper)
    def _ensure_table(self) -> None:
        '''
        Create the orders table if it does not exist.
        '''
        with Sqlite(self.db_path, mode='rw') as db:
            db.executescript('''
                CREATE TABLE IF NOT EXISTS orders (
                    order_id TEXT PRIMARY KEY,
                    destination TEXT NOT NULL,
                    status TEXT NOT NULL,
                    items_json TEXT NOT NULL
                );
            ''')

    # * method: exists
    def exists(self, order_id: str) -> bool:
        with Sqlite(self.db_path) as db:
            row = db.execute("SELECT 1 FROM orders WHERE order_id = ?", (order_id,)).fetch_one()
            return row is not None

    # * method: get
    def get(self, order_id: str) -> OrderAggregate:
        with Sqlite(self.db_path) as db:
            row = db.execute("SELECT * FROM orders WHERE order_id = ?", (order_id,)).fetch_one()
            if not row:
                return None
            return OrderSqlObject.from_data(dict(row)).map()

    # * method: list
    def list(self) -> List[OrderAggregate]:
        with Sqlite(self.db_path) as db:
            rows = db.execute("SELECT * FROM orders").fetch_all()
            return [OrderSqlObject.from_data(dict(row)).map() for row in rows]

    # * method: save
    def save(self, order: OrderAggregate) -> None:
        data = OrderSqlObject.from_model(order).to_primitive('to_data.sqlite')
        with Sqlite(self.db_path, mode='rw') as db:
            db.execute('''
                INSERT OR REPLACE INTO orders (order_id, destination, status, items_json)
                VALUES (?, ?, ?, ?)
            ''', (
                order.order_id,
                order.destination,
                order.status,
                data.get('items_json', '[]')
            ))

    # * method: delete
    def delete(self, order_id: str) -> None:
        with Sqlite(self.db_path, mode='rw') as db:
            db.execute("DELETE FROM orders WHERE order_id = ?", (order_id,))