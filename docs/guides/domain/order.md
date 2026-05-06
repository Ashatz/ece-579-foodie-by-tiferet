# Order

**File:** `src/domain/order.py`
**Extends:** `tiferet.DomainObject` (Pydantic v2)

## Overview

`Order` represents a customer food order containing multiple `Item` objects, a delivery destination, and a lifecycle status. It is the central "fact" in the production system (Goal B) that drives bagging rules, and it provides the delivery targets for route optimization (Goal A).

Orders are persisted in SQLite via `OrderSqliteRepository` and seeded with demo data by the `SeedDatabase` event.

## Attributes

| Attribute | Type | Default | Description |
|-----------|------|---------|-------------|
| `order_id` | `str` | *required* | Unique order identifier (e.g., `"ORD-101"`). |
| `items` | `List[Item]` | `[]` | List of food items in this order. |
| `destination` | `str` | *required* | Delivery location on campus (e.g., `"Building_A"`). |
| `status` | `Literal['pending', 'bagged', 'en_route', 'delivered']` | `'pending'` | Current order lifecycle status. |

### Order Lifecycle

An order progresses through these statuses:

1. **`pending`** — Order has been placed but not yet processed.
2. **`bagged`** — Items have been packed into bags by FOODIE_BAGGER.
3. **`en_route`** — A robot is delivering the order.
4. **`delivered`** — Order has arrived at its destination.

## Methods

### `total_items() -> int`

Returns the total number of individual items in the order by summing the `quantity` of each `Item`.

### `format_for_bagger() -> str`

Returns a human-readable summary for the FOODIE_BAGGER simulation trace.

**Example output:**
```
Order ORD-101 -> Building_A | Items: 2x 1-gallon water bottle [large], 1x pint ice cream (frozen) [medium] (total: 3)
```

## Usage

### Constructing an Order

```python
from src.domain import Order, Item

order = Order(
    order_id='ORD-101',
    destination='Building_A',
    items=[
        Item(name='1-gallon water bottle', size='large', quantity=2),
        Item(name='pint ice cream', size='medium', is_frozen=True),
    ],
)

print(order.total_items())       # 3
print(order.format_for_bagger()) # Order ORD-101 -> Building_A | Items: ...
```

### Data Source — SQLite

Orders are stored in SQLite and managed by `OrderSqliteRepository`. The `SeedDatabase` event pre-populates demo orders:

```python
# Seeded by SeedDatabase event
# ORD-101 -> Building_A (4 items)
# ORD-102 -> Building_B
# ORD-103 -> Dorm_1
```

### Integration with Goals

- **Goal B (Bagging):** The `BagOrder` event retrieves an order by ID, extracts its items, and passes them to the `ForwardChainBagger` for rule-based packing.
- **Goal A (Routing):** The `PlanRoute` event reads all pending orders and uses their `destination` fields to plan multi-robot delivery routes via A* search.

## Related Components

- **Item** (`src/domain/item.py`) — The objects contained within an order.
- **Robot** (`src/domain/robot.py`) — Delivers bagged orders to their destinations.
- **OrderAggregate / OrderSqlObject** (`src/mappers/order.py`) — Mapper layer for mutation and SQLite serialization.
- **OrderSqliteRepository** (`src/repos/order.py`) — SQLite-backed persistence.
- **OrderService** (`src/interfaces/order.py`) — Service interface for order CRUD operations.
- **SeedDatabase** (`src/events/seed_database.py`) — Pre-seeds demo orders into SQLite.
- **BagOrder** (`src/events/bag_order.py`) — Retrieves and bags an order's items.
