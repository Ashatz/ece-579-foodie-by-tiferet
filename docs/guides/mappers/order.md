# Order Mappers

**File:** `src/mappers/order.py`
**Persistence Format:** SQLite (`foodie.db`)

## Overview

`OrderAggregate` and `OrderSqlObject` provide the mapper layer for the `Order` domain model. Unlike flat YAML-backed leaf mappers, Order requires custom JSON serialization because `Order.items` is a `List[Item]` — a nested domain object collection stored as a single `items_json` TEXT column in SQLite.

- **OrderAggregate** — Mutable extension for lifecycle status updates.
- **OrderSqlObject** — SQLite serialization with custom `to_primitive` for JSON-encoded items.

## OrderAggregate

**Extends:** `Order`, `tiferet.mappers.Aggregate`

### Mutation Methods

#### `update_status(new_status: str) -> None`

Changes the order lifecycle status (`pending` → `bagged` → `en_route` → `delivered`). Directly assigns `self.status`; Pydantic's `validate_assignment=True` enforces the `Literal` constraint.

## OrderSqlObject

**Extends:** `Order`, `tiferet.mappers.TransferObject`

### Roles (`_ROLES`)

| Role | Config | Purpose |
|------|--------|---------|
| `to_model` | `{'exclude': {'items'}}` | Items passed separately via `map()`. |
| `to_data.sqlite` | `{'exclude': {'items'}}` | Items serialized as `items_json` via custom `to_primitive`. |

### Methods

#### `to_primitive(role=None, **overrides) -> dict`

Overrides base serialization. When `role='to_data.sqlite'`, adds `items_json` — a JSON string produced by `json.dumps([item.model_dump() for item in self.items])`. The `items` field is excluded from the base dict via `_ROLES`.

#### `map(target=None, **overrides) -> OrderAggregate`

Maps to `OrderAggregate`, passing `items=list(self.items)` to preserve deserialized domain objects.

#### `from_data(data, **overrides) -> OrderSqlObject` (classmethod)

Creates from a raw SQLite row dict:
1. Pops `items_json` and deserializes via `json.loads`.
2. Converts each dict to an `Item` domain object.
3. Delegates to `model_validate`.

#### `from_model(order, **overrides) -> OrderSqlObject` (classmethod)

Creates from an `Order` domain model or aggregate via `super().from_model()`.

### Serialization Flow

```
OrderAggregate
    → OrderSqlObject.from_model()
    → .to_primitive(role='to_data.sqlite')
    → SQLite row {order_id, destination, status, items_json}
    → OrderSqlObject.from_data()
    → .map()
    → OrderAggregate
```

## Usage

### Construction and Mutation

```python
from src.domain import Item
from src.mappers.order import OrderAggregate

order = OrderAggregate(
    order_id='ORD-001',
    items=[Item(name='Water Bottle', size='large', quantity=2)],
    destination='Building_A',
    status='pending',
)

order.update_status('bagged')
assert order.status == 'bagged'
```

### SQLite Round-Trip

```python
from src.mappers.order import OrderAggregate, OrderSqlObject

# Serialize to SQLite format
sql_obj = OrderSqlObject.from_model(order)
row = sql_obj.to_primitive(role='to_data.sqlite')
# row = {'order_id': 'ORD-001', 'destination': 'Building_A', 'status': 'bagged', 'items_json': '[...]'}

# Deserialize back
restored = OrderSqlObject.from_data(dict(row)).map()
assert restored.order_id == order.order_id
assert restored.items[0].name == order.items[0].name
```

## Related Components

- **Order** (`src/domain/order.py`) — Domain model with `total_items()` and `format_summary()`.
- **Item** (`src/domain/item.py`) — Nested domain model serialized as JSON.
- **OrderSqliteRepository** (`src/repos/order.py`) — Persists orders using `OrderSqlObject`.
- **BagOrder** (`src/events/bag_order.py`) — Loads orders for forward-chaining bagging (Goal B).
- **PlanRoute** (`src/events/plan_route.py`) — Loads orders for A* route planning (Goal A).
