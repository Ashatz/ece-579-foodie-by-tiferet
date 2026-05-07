# RobotSqliteRepository

**File:** `src/repos/robot.py`
**Implements:** `RobotService` (`src/interfaces/robot.py`)

## Overview

`RobotSqliteRepository` is the concrete SQLite-backed repository for FOODIE's runtime fleet state. It persists robots to the `robots` table in `foodie.db`, handling two nested domain objects through dual JSON TEXT columns: `current_location_json` for the robot's position and `compartments_json` for its loaded bags.

Like the Order repository, the Robot repository manages instance-specific runtime data that changes during simulation.

## Constructor

```python
RobotSqliteRepository(db_path='foodie.db')
```

- `db_path` — Path to the SQLite database file.
- `ensure_table()` is called in the constructor, auto-creating the table if it does not exist.

## Table Schema

```sql
CREATE TABLE IF NOT EXISTS robots (
    robot_id TEXT PRIMARY KEY,
    current_location_json TEXT NOT NULL,
    battery_level REAL NOT NULL,
    compartments_json TEXT NOT NULL,
    status TEXT NOT NULL
);
```

- `robot_id` — String primary key (e.g., `'R1'`).
- `current_location_json` — JSON TEXT column for the nested `Location` object.
- `compartments_json` — JSON TEXT column for the nested `List[Bag]` (each bag contains `List[Item]`).
- `battery_level` — REAL column (no JSON needed for scalars).

## Dual JSON Serialization

Robots contain two nested structures serialized as separate JSON TEXT columns via `RobotSqlObject`:

- **`current_location_json`** — Serializes the `Location` domain object (name, x, y, is_food_warehouse, is_obstacle_prone).
- **`compartments_json`** — Serializes `List[Bag]`, where each bag contains its own `List[Item]`.

This dual-JSON pattern keeps the schema flat while preserving arbitrarily nested domain data.

## Read Pattern

```python
with Sqlite(self.db_path) as db:
    db.execute("SELECT * FROM robots WHERE robot_id = ?", (robot_id,))
    row = db.fetch_one()
    data = self.row_to_dict(db, row)
    return RobotSqlObject.from_data(data).map()
```

## Write Pattern

```python
data = RobotSqlObject.from_model(robot).to_primitive('to_data.sqlite')
with Sqlite(self.db_path, mode='rw') as db:
    db.execute("INSERT OR REPLACE INTO robots (...) VALUES (?, ?, ?, ?, ?)", (...))
```

## Delete Pattern

```python
with Sqlite(self.db_path, mode='rw') as db:
    db.execute("DELETE FROM robots WHERE robot_id = ?", (robot_id,))
```

## Method Reference

- **`ensure_table()`** — `CREATE TABLE IF NOT EXISTS` via `executescript()` with `mode='rwc'`.
- **`row_to_dict(db, row)`** — Converts tuple to dict via `cursor.description`.
- **`exists(robot_id)`** — `SELECT 1` check.
- **`get(robot_id)`** — Full row fetch → `from_data()` → `map()`, or `None`.
- **`list()`** — All rows → iterate → `from_data()` → `map()`.
- **`save(robot)`** — `from_model()` → `to_primitive('to_data.sqlite')` → `INSERT OR REPLACE`.
- **`delete(robot_id)`** — `DELETE` by primary key.

## Round-Trip Flow

`RobotAggregate` → `RobotSqlObject.from_model()` → `to_primitive('to_data.sqlite')` → SQLite row (with dual JSON) → `row_to_dict()` → `RobotSqlObject.from_data()` → `.map()` → `RobotAggregate`

## Integration

- **Domain Events:**
  - `SeedDatabase` — Clears and re-seeds 3 robots at the Food Warehouse.
  - `PlanRoute` — Loads fleet for round-robin assignment, updates state after route execution.
- **Interface:** Satisfies `RobotService` contract from `src/interfaces/robot.py`.

## Comparison with YAML Repositories

- **Persistence type:** SQLite (single `db_path`) vs. YAML (single `yaml_file`).
- **Nested data:** Dual JSON TEXT columns vs. flat YAML dicts.
- **Use case:** Runtime/mutable data vs. universal/config data.
- **Table creation:** `ensure_table()` in constructor vs. no setup needed for YAML.

## Related Components

- **Robot** (`src/domain/robot.py`) — Domain model.
- **RobotAggregate** (`src/mappers/robot.py`) — Aggregate with mutation support.
- **RobotSqlObject** (`src/mappers/robot.py`) — TransferObject for SQLite serialization.
- **RobotService** (`src/interfaces/robot.py`) — Abstract interface this repo implements.
- **Location** (`src/domain/location.py`) — Nested domain model for robot position.
- **Bag** (`src/domain/bag.py`) — Nested domain model for robot compartments.
- **OrderSqliteRepository** (`src/repos/order.py`) — Companion SQLite repository for runtime data.
