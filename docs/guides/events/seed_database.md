# SeedDatabase Domain Event

## Overview

The `SeedDatabase` event is an idempotent database seeding operation that pre-populates the SQLite database with robots before the FOODIE simulation runs. It clears existing orders and robots, then seeds 3 robots at the Food Warehouse.

Order creation is handled separately by `PlaceItemOrder` and `PlaceBeverageOrder` events (see `docs/guides/events/place_order.md`).

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
3. **Load Food Warehouse** — `location_service.get('FW')` returns the FW location.
4. **Seed 3 robots:**
   - `R1`, `R2`, `R3` — all at the Food Warehouse, default battery (100%), idle status.
5. **Print trace** — Each seeded robot is logged to stdout.
6. **Return summary** — `{'robots_seeded': 3, 'status': 'complete'}`.

## Idempotency

Running `SeedDatabase` multiple times produces the same result — existing data is always cleared first via iterate-and-delete before new records are created.

## Seeded Data

### Robots

| Robot ID | Location | Battery | Status |
|----------|----------|---------|--------|
| R1 | FW (Food Warehouse) | 100% | idle |
| R2 | FW (Food Warehouse) | 100% | idle |
| R3 | FW (Food Warehouse) | 100% | idle |

## Trace Output Example

```
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
      description: Pre-seed SQLite database with demo orders and robots
      commands:
        - service_id: seed_database_evt
          name: Seed demo data
```

## Related Components

- **OrderService** — `src/interfaces/order.py`
- **RobotService** — `src/interfaces/robot.py`
- **ItemService** — `src/interfaces/item.py`
- **LocationService** — `src/interfaces/location.py`
- **OrderAggregate** — `src/mappers/order.py`
- **RobotAggregate** — `src/mappers/robot.py`
