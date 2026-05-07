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
        self.ensure_table()

    # * method: ensure_table
    def ensure_table(self) -> None:
        '''
        Create the orders table if it does not exist.
        '''

        with Sqlite(self.db_path, mode='rwc') as db:
            db.executescript('''
                CREATE TABLE IF NOT EXISTS orders (
                    order_id TEXT PRIMARY KEY,
                    destination TEXT NOT NULL,
                    status TEXT NOT NULL,
                    items_json TEXT NOT NULL
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
    def exists(self, order_id: str) -> bool:
        '''
        Check if an order exists by ID.

        :param order_id: The order identifier.
        :type order_id: str
        :return: True if the order exists.
        :rtype: bool
        '''

        with Sqlite(self.db_path) as db:
            db.execute("SELECT 1 FROM orders WHERE order_id = ?", (order_id,))
            return db.fetch_one() is not None

    # * method: get
    def get(self, order_id: str) -> OrderAggregate:
        '''
        Retrieve an order by ID.

        :param order_id: The order identifier.
        :type order_id: str
        :return: The order aggregate, or None if not found.
        :rtype: OrderAggregate
        '''

        with Sqlite(self.db_path) as db:
            db.execute("SELECT * FROM orders WHERE order_id = ?", (order_id,))
            row = db.fetch_one()
            if not row:
                return None
            data = self.row_to_dict(db, row)
            return OrderSqlObject.from_data(data).map()

    # * method: list
    def list(self) -> List[OrderAggregate]:
        '''
        List all orders.

        :return: List of order aggregates.
        :rtype: List[OrderAggregate]
        '''

        with Sqlite(self.db_path) as db:
            db.execute("SELECT * FROM orders")
            rows = db.fetch_all()
            results = []
            for row in rows:
                data = self.row_to_dict(db, row)
                results.append(OrderSqlObject.from_data(data).map())
            return results

    # * method: save
    def save(self, order: OrderAggregate) -> None:
        '''
        Persist an order (insert or replace).

        :param order: The order aggregate to persist.
        :type order: OrderAggregate
        '''

        data = OrderSqlObject.from_model(order).to_primitive('to_data.sqlite')

        with Sqlite(self.db_path, mode='rw') as db:
            db.execute('''
                INSERT OR REPLACE INTO orders (order_id, destination, status, items_json)
                VALUES (?, ?, ?, ?)
            ''', (
                order.order_id,
                order.destination,
                order.status,
                data.get('items_json', '[]'),
            ))

    # * method: delete
    def delete(self, order_id: str) -> None:
        '''
        Delete an order by ID.

        :param order_id: The order identifier.
        :type order_id: str
        '''

        with Sqlite(self.db_path, mode='rw') as db:
            db.execute("DELETE FROM orders WHERE order_id = ?", (order_id,))
