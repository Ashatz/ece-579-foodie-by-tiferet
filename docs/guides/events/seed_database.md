# SeedDatabase Domain Event

## Overview

The `SeedDatabase` event is an idempotent database seeding operation that pre-populates the SQLite database with demo orders and robots before the FOODIE simulation runs. It is the prerequisite step for both **Goal A** (route planning) and **Goal B** (bagging).

The event demonstrates Tiferet's multi-service dependency injection pattern, receiving four injected services to coordinate data clearing, catalog loading, and entity creation.

**Module:** `src/events/migrate.py`

## Dependencies

Four services are injected via constructor:

- **`order_service: OrderService`** — Persisting and clearing orders.
- **`robot_service: RobotService`** — Persisting and clearing robots.
- **`item_service: ItemService`** — Loading the menu catalog from `menu.yml`.
- **`location_service: LocationService`** — Loading the Food Warehouse location from `campus.yml`.

## Algorithm

1. **Clear existing orders** — `order_service.list()` → iterate → `order_service.delete(order_id)`.
2. **Clear existing robots** — `robot_service.list()` → iterate → `robot_service.delete(robot_id)`.
3. **Load menu items** — `item_service.list()` returns all items from the catalog.
4. **Load Food Warehouse** — `location_service.get('FW')` returns the FW location.
5. **Seed 3 orders:**
   - `ORD-101` → `Building_A`, loaded with all menu items.
   - `ORD-102` → `Building_B`, empty.
   - `ORD-103` → `Dorm_1`, empty.
6. **Seed 3 robots:**
   - `R1`, `R2`, `R3` — all at the Food Warehouse, default battery (100%), idle status.
7. **Print trace** — Each seeded order and robot is logged to stdout.
8. **Return summary** — `{'orders_seeded': 3, 'robots_seeded': 3, 'status': 'complete'}`.

## Idempotency

Running `SeedDatabase` multiple times produces the same result — existing data is always cleared first via iterate-and-delete before new records are created.

## Seeded Data

### Orders

| Order ID | Destination | Items |
|----------|-------------|-------|
| ORD-101 | Building_A | All menu items (4 items) |
| ORD-102 | Building_B | Empty |
| ORD-103 | Dorm_1 | Empty |

### Robots

| Robot ID | Location | Battery | Status |
|----------|----------|---------|--------|
| R1 | FW (Food Warehouse) | 100% | idle |
| R2 | FW (Food Warehouse) | 100% | idle |
| R3 | FW (Food Warehouse) | 100% | idle |

## Trace Output Example

```
  Seeded order: ORD-101 -> Building_A (4 items)
  Seeded order: ORD-102 -> Building_B (0 items)
  Seeded order: ORD-103 -> Dorm_1 (0 items)
  Seeded robot: R1 at FW
  Seeded robot: R2 at FW
  Seeded robot: R3 at FW
```

## Integration with config.yml

The event is wired as a service in `config.yml`:

```yaml
services:
  seed_database_evt:
    module_path: src.events.migrate
    class_name: SeedDatabase
```

And exposed as a feature:

```yaml
features:
  admin:
    seed_database:
      name: Seed Database
      description: Pre-seed the database with demo orders and robots
      commands:
        - attribute_id: seed_database_evt
          name: Seed demo data
```

## Related Components

- **OrderService** — `src/interfaces/order.py`
- **RobotService** — `src/interfaces/robot.py`
- **ItemService** — `src/interfaces/item.py`
- **LocationService** — `src/interfaces/location.py`
- **OrderAggregate** — `src/mappers/order.py`
- **RobotAggregate** — `src/mappers/robot.py`
