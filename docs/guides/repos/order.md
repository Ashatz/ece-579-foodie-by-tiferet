# OrderSqliteRepository

**File:** `src/repos/order.py`
**Implements:** `OrderService` (`src/interfaces/order.py`)

## Overview

`OrderSqliteRepository` is the concrete SQLite-backed repository for FOODIE's runtime order lifecycle. It persists orders to the `orders` table in `foodie.db`, handling nested `Item` data through JSON serialization in a TEXT column.

Unlike the YAML-backed repositories (Item, Beverage, Location) which store universal/config data, the Order repository manages instance-specific runtime data that changes frequently during simulation.

## Constructor

```python
OrderSqliteRepository(db_path='foodie.db')
```

- `db_path` — Path to the SQLite database file.
- `ensure_table()` is called in the constructor, auto-creating the table if it does not exist.

## Table Schema

```sql
CREATE TABLE IF NOT EXISTS orders (
    order_id TEXT PRIMARY KEY,
    destination TEXT NOT NULL,
    status TEXT NOT NULL,
    items_json TEXT NOT NULL
);
```

- `order_id` — String primary key (e.g., `'ORD-101'`).
- `items_json` — JSON TEXT column containing the serialized list of `Item` objects.

## JSON Serialization

Orders contain a nested `List[Item]` which is serialized as JSON in the `items_json` TEXT column via `OrderSqlObject`:

- **Write:** `OrderSqlObject.from_model(order).to_primitive('to_data.sqlite')` produces a dict with `items_json` as a JSON string.
- **Read:** `OrderSqlObject.from_data(row_dict).map()` deserializes `items_json` back to `List[Item]` within the `OrderAggregate`.

## Read Pattern

```python
with Sqlite(self.db_path) as db:
    db.execute("SELECT * FROM orders WHERE order_id = ?", (order_id,))
    row = db.fetch_one()
    data = self.row_to_dict(db, row)
    return OrderSqlObject.from_data(data).map()
```

## Write Pattern

```python
data = OrderSqlObject.from_model(order).to_primitive('to_data.sqlite')
with Sqlite(self.db_path, mode='rw') as db:
    db.execute("INSERT OR REPLACE INTO orders (...) VALUES (?, ?, ?, ?)", (...))
```

## Delete Pattern

```python
with Sqlite(self.db_path, mode='rw') as db:
    db.execute("DELETE FROM orders WHERE order_id = ?", (order_id,))
```

## Method Reference

- **`ensure_table()`** — `CREATE TABLE IF NOT EXISTS` via `executescript()` with `mode='rwc'`.
- **`row_to_dict(db, row)`** — Converts tuple to dict via `cursor.description`.
- **`exists(order_id)`** — `SELECT 1` check.
- **`get(order_id)`** — Full row fetch → `from_data()` → `map()`, or `None`.
- **`list()`** — All rows → iterate → `from_data()` → `map()`.
- **`save(order)`** — `from_model()` → `to_primitive('to_data.sqlite')` → `INSERT OR REPLACE`.
- **`delete(order_id)`** — `DELETE` by primary key.

## Round-Trip Flow

`OrderAggregate` → `OrderSqlObject.from_model()` → `to_primitive('to_data.sqlite')` → SQLite row (with `items_json`) → `row_to_dict()` → `OrderSqlObject.from_data()` → `.map()` → `OrderAggregate`

## Integration

- **Domain Events:**
  - `SeedDatabase` — Clears and re-seeds orders.
  - `BagOrder` — Loads order, updates status to `'bagged'`, persists.
  - `PlanRoute` — Loads pending orders for route assignment.
- **Interface:** Satisfies `OrderService` contract from `src/interfaces/order.py`.

## Comparison with YAML Repositories

- **Persistence type:** SQLite (single `db_path`) vs. YAML (single `yaml_file`).
- **Nested data:** JSON TEXT columns vs. flat YAML dicts.
- **Use case:** Runtime/mutable data vs. universal/config data.
- **Table creation:** `ensure_table()` in constructor vs. no setup needed for YAML.

## Related Components

- **Order** (`src/domain/order.py`) — Domain model.
- **OrderAggregate** (`src/mappers/order.py`) — Aggregate with mutation support.
- **OrderSqlObject** (`src/mappers/order.py`) — TransferObject for SQLite serialization.
- **OrderService** (`src/interfaces/order.py`) — Abstract interface this repo implements.
- **Item** (`src/domain/item.py`) — Nested domain model within orders.
