# RobotService

**File:** `src/interfaces/robot.py`
**Extends:** `Service` (`tiferet.interfaces`)

## Overview

`RobotService` is the abstract data-access contract for FOODIE's runtime fleet state. It defines the CRUD operations that any robot persistence implementation must satisfy, decoupling domain events from the underlying storage mechanism.

Robots represent the campus food-delivery fleet. Each robot has a current location, battery level, compartments (bags), and operational status. Like orders, robots are instance-specific runtime data that changes during simulation and is persisted to SQLite.

## Contract Design

`RobotService` abstracts **SQLite-backed persistence** for the `robots` table in `foodie.db`. The interface exists so that domain events (e.g., `SeedDatabase`, `PlanRoute`) can create, update, and query robot state without coupling to SQL or the database schema.

Key design decisions:
- **ID-based primary key** — Robots are identified by `robot_id` (e.g., `'R1'`), which serves as the SQLite PRIMARY KEY. This differs from the name-based convention used by YAML-backed interfaces.
- **Domain-typed parameters** — Methods accept and return `Robot` domain objects rather than raw dicts or SQL rows, ensuring type safety at the interface boundary.
- **Dual nested data handling** — Robots contain nested `Location` (current position) and `List[Bag]` (compartments), which the concrete repository serializes as separate JSON TEXT columns. The interface abstracts this complexity.
- **Idempotent delete** — `delete(robot_id)` must not raise if the robot does not exist.

## Method Signatures

### `exists(robot_id: str) -> bool`
Check if a robot exists by ID.

### `get(robot_id: str) -> Robot`
Retrieve a robot by ID. Returns `None` if not found.

### `list() -> List[Robot]`
List all robots.

### `save(robot: Robot) -> None`
Persist a robot. If a robot with the same ID already exists, it is replaced (INSERT OR REPLACE).

### `delete(robot_id: str) -> None`
Delete a robot by ID. Idempotent — does not raise if the robot does not exist.

## Primary Key Convention

Robots use `robot_id: str` as the primary key, reflecting the SQLite PRIMARY KEY convention:

```sql
CREATE TABLE IF NOT EXISTS robots (
    robot_id TEXT PRIMARY KEY,
    current_location_json TEXT NOT NULL,
    battery_level REAL NOT NULL,
    compartments_json TEXT NOT NULL,
    status TEXT NOT NULL
);
```

## Integration Points

- **Repository:** `RobotSqliteRepository` (`src/repos/robot.py`) — Concrete SQLite-backed implementation persisting to `foodie.db`.
- **Domain Events:**
  - `SeedDatabase` — Calls `robot_service.list()` to clear existing robots, then `robot_service.save()` to seed 3 demo robots at the Food Warehouse.
  - `PlanRoute` — Calls `robot_service.list()` to load the fleet for round-robin order assignment, then `robot_service.save()` to update robot state after route execution.
- **Domain Model:** `Robot` (`src/domain/robot.py`) — The domain object returned by all read methods.

## Related Components

- **Robot** (`src/domain/robot.py`) — Domain model with `robot_id`, `current_location`, `battery_level`, `compartments`, `status`.
- **RobotAggregate** (`src/mappers/robot.py`) — Aggregate with mutation support.
- **RobotSqlObject** (`src/mappers/robot.py`) — TransferObject for SQLite serialization with dual JSON columns.
- **RobotSqliteRepository** (`src/repos/robot.py`) — Concrete repository implementation.
- **Location** (`src/domain/location.py`) — Nested domain model for robot position.
- **Bag** (`src/domain/bag.py`) — Nested domain model for robot compartments.
- **OrderService** (`src/interfaces/order.py`) — Companion runtime data service for order lifecycle.
