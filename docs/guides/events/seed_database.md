# SeedDatabase

**File:** `src/events/seed_database.py`
**Extends:** `tiferet.events.DomainEvent`
**Feature:** `admin.seed_database`

## Overview

`SeedDatabase` is a domain event that prepares the SQLite database with a repeatable set of demo data before the simulation begins. It clears any existing orders and robots, then creates three sample orders and a fleet of three robots stationed at the Food Warehouse. This event is always run first — both `foodie.py` and the CLI's `admin seed-database` command invoke it before Goals A, B, or C.

## Why a Separate Seeding Event?

The seeding step is isolated as its own domain event (rather than embedded in the demo script) for several reasons:

1. **Idempotency** — Running the simulation multiple times produces identical starting conditions. Every invocation clears and re-seeds, so there is no stale state from previous runs.
2. **Testability** — The event can be tested independently of the goal events, verifying that the correct number of orders and robots are persisted.
3. **CLI parity** — The CLI can seed the database as a standalone command (`admin seed-database`) without running the full simulation, useful for debugging individual goals.
4. **Separation of concerns** — Demo data setup is infrastructure, not domain logic. Keeping it in its own event prevents Goals A/B/C from carrying setup responsibilities.

## Injected Dependencies

| Dependency | Type | Purpose |
|------------|------|---------|
| `order_service` | `OrderService` | CRUD operations on orders in SQLite. |
| `robot_service` | `RobotService` | CRUD operations on robots in SQLite. |
| `item_service` | `ItemService` | Loads the item catalog from `menu.yml`. |
| `location_service` | `LocationService` | Loads the Food Warehouse location for robot placement. |

All dependencies are injected via constructor and resolved from `config.yml` services by Tiferet's DI container.

## Execution Flow

### Step 1 — Clear Existing Data

```
existing_orders = order_service.list()
for order in existing_orders:
    order_service.delete(order.order_id)

existing_robots = robot_service.list()
for robot in existing_robots:
    robot_service.delete(robot.robot_id)
```

This ensures a clean slate regardless of how many times the simulation has been run. Deletes are idempotent — deleting a non-existent record is a no-op in the SQLite repositories.

### Step 2 — Load Reference Data

- **Items** — `item_service.list()` returns all items from `menu.yml` (e.g., water bottle, ice cream, granola box, bread).
- **Food Warehouse** — `location_service.get('FW')` returns the Location object for the robot starting point.

### Step 3 — Seed Orders

Three orders are created using `OrderAggregate`:

| Order ID | Destination | Items |
|----------|-------------|-------|
| `ORD-101` | Building_A | All menu items (4 items) |
| `ORD-102` | Building_B | Empty (tests edge case) |
| `ORD-103` | Dorm_1 | Empty (tests edge case) |

`ORD-101` carries the full item catalog so Goal B (bagging) has meaningful data. `ORD-102` and `ORD-103` are empty orders that test route planning without bagging.

### Step 4 — Seed Robots

Three robots are created using `RobotAggregate`, all starting at the Food Warehouse with default `battery_level=100.0` and `status='idle'`:

| Robot ID | Start Location |
|----------|----------------|
| `R1` | FW |
| `R2` | FW |
| `R3` | FW |

Three robots match the three orders, enabling the round-robin assignment in Goal A.

### Return Value

```python
{
    'orders_seeded': 3,
    'robots_seeded': 3,
    'status': 'complete',
}
```

## Trace Output

```
SeedDatabase: Pre-seeding SQLite database with demo data...

  Seeded order ORD-101 -> Building_A (4 items)
  Seeded order ORD-102 -> Building_B (0 items)
  Seeded order ORD-103 -> Dorm_1 (0 items)

  Seeded robot R1 at FW
  Seeded robot R2 at FW
  Seeded robot R3 at FW

SeedDatabase complete: 3 orders, 3 robots.
```

## Related Components

- **OrderAggregate** (`src/mappers/order.py`) — Constructs order objects for persistence.
- **RobotAggregate** (`src/mappers/robot.py`) — Constructs robot objects for persistence.
- **OrderService** (`src/interfaces/order.py`) — Order CRUD contract.
- **RobotService** (`src/interfaces/robot.py`) — Robot CRUD contract.
- **ItemService** (`src/interfaces/item.py`) — Loads menu items from YAML.
- **LocationService** (`src/interfaces/location.py`) — Loads the Food Warehouse location.
- **OrderSqliteRepository** (`src/repos/order.py`) — Concrete SQLite persistence for orders.
- **RobotSqliteRepository** (`src/repos/robot.py`) — Concrete SQLite persistence for robots.
