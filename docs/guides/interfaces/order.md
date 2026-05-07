# OrderService

**File:** `src/interfaces/order.py`
**Extends:** `Service` (`tiferet.interfaces`)

## Overview

`OrderService` is the abstract data-access contract for FOODIE's runtime order lifecycle. It defines the CRUD operations that any order persistence implementation must satisfy, decoupling domain events from the underlying storage mechanism.

Orders represent customer food delivery requests that progress through a lifecycle: `pending` → `bagged` → `en_route` → `delivered`. Unlike the YAML-backed item and beverage catalogs, orders are instance-specific runtime data that changes frequently during simulation and is persisted to SQLite.

## Contract Design

`OrderService` abstracts **SQLite-backed persistence** for the `orders` table in `foodie.db`. The interface exists so that domain events (e.g., `SeedDatabase`, `BagOrder`, `PlanRoute`) can create, update, and query orders without coupling to SQL or the database schema.

Key design decisions:
- **ID-based primary key** — Orders are identified by `order_id` (e.g., `'ORD-101'`), which serves as the SQLite PRIMARY KEY. This differs from the name-based convention used by YAML-backed interfaces.
- **Domain-typed parameters** — Methods accept and return `Order` domain objects rather than raw dicts or SQL rows, ensuring type safety at the interface boundary.
- **Nested data handling** — Orders contain a list of `Item` objects, which the concrete repository serializes as JSON in a TEXT column. The interface abstracts this complexity.
- **Idempotent delete** — `delete(order_id)` must not raise if the order does not exist.

## Method Signatures

### `exists(order_id: str) -> bool`
Check if an order exists by ID.

### `get(order_id: str) -> Order`
Retrieve an order by ID. Returns `None` if not found.

### `list() -> List[Order]`
List all orders.

### `save(order: Order) -> None`
Persist an order. If an order with the same ID already exists, it is replaced (INSERT OR REPLACE).

### `delete(order_id: str) -> None`
Delete an order by ID. Idempotent — does not raise if the order does not exist.

## Primary Key Convention

Orders use `order_id: str` as the primary key, reflecting the SQLite PRIMARY KEY convention:

```sql
CREATE TABLE IF NOT EXISTS orders (
    order_id TEXT PRIMARY KEY,
    destination TEXT NOT NULL,
    status TEXT NOT NULL,
    items_json TEXT NOT NULL
);
```

## Integration Points

- **Repository:** `OrderSqliteRepository` (`src/repos/order.py`) — Concrete SQLite-backed implementation persisting to `foodie.db`.
- **Domain Events:**
  - `SeedDatabase` — Calls `order_service.list()` to clear existing orders, then `order_service.save()` to seed demo orders.
  - `BagOrder` — Calls `order_service.get(order_id)` to load the order, then `order_service.save()` to update status to `'bagged'`.
  - `PlanRoute` — Calls `order_service.list()` to load pending orders for route assignment.
- **Domain Model:** `Order` (`src/domain/order.py`) — The domain object returned by all read methods.

## Related Components

- **Order** (`src/domain/order.py`) — Domain model with `order_id`, `destination`, `status`, `items`.
- **OrderAggregate** (`src/mappers/order.py`) — Aggregate with mutation support.
- **OrderSqlObject** (`src/mappers/order.py`) — TransferObject for SQLite serialization with JSON items column.
- **OrderSqliteRepository** (`src/repos/order.py`) — Concrete repository implementation.
- **Item** (`src/domain/item.py`) — Nested domain model within orders.
- **RobotService** (`src/interfaces/robot.py`) — Companion runtime data service for fleet state.
