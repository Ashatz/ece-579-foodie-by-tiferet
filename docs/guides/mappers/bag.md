# Bag Mapper

**File:** `src/mappers/bag.py`
**Persistence:** None (aggregate-only; embedded in `RobotSqlObject.compartments_json`)

## Overview

`BagAggregate` is a unique aggregate-only mapper with no accompanying TransferObject. Bags are runtime-only constructs — created in-memory by the `ForwardChainBagger` utility during forward-chaining (Goal B) and loaded into `Robot.compartments` — but never persisted independently. Instead, bags are serialized as part of `RobotSqlObject.compartments_json` when the robot state is saved to SQLite.

The aggregate provides three static factory methods that encapsulate bag-type derivation logic, replacing the need for conditional construction in the bagger utility.

## BagAggregate

**Extends:** `Bag`, `tiferet.mappers.Aggregate`

### Factory Methods

#### `new_freezer_bag(bag_number: int) -> BagAggregate` (static)

Creates a freezer bag for frozen items.
- `bag_id`: `freezer_bag_{bag_number}`
- `bag_type`: `'freezer'`
- `items`: `[]` (default)
- `max_capacity`: `10` (default)

#### `new_fragile_bag(bag_number: int) -> BagAggregate` (static)

Creates a paper bag designated for a single fragile item.
- `bag_id`: `bag_{bag_number}`
- `bag_type`: `'paper'`

#### `new_regular_bag(bag_number: int) -> BagAggregate` (static)

Creates a standard paper bag for regular (non-frozen, non-fragile) items.
- `bag_id`: `bag_{bag_number}`
- `bag_type`: `'paper'`

### Naming Convention

| Bag Type | ID Pattern | `bag_type` |
|----------|------------|------------|
| Freezer | `freezer_bag_{n}` | `'freezer'` |
| Fragile | `bag_{n}` | `'paper'` |
| Regular | `bag_{n}` | `'paper'` |

## Design Rationale

No `BagYamlObject` or `BagSqlObject` exists because:
- Bags are created at runtime by `ForwardChainBagger` during order bagging.
- Bags are embedded inside `Robot.compartments` and serialized as part of `RobotSqlObject.compartments_json`.
- There is no independent persistence format for bags.

## Usage

### Creating Bags

```python
from src.mappers.bag import BagAggregate

freezer = BagAggregate.new_freezer_bag(1)
fragile = BagAggregate.new_fragile_bag(2)
regular = BagAggregate.new_regular_bag(3)
```

### Adding Items via Domain Methods

```python
from src.domain import Item

item = Item(name='Ice Cream', size='medium', is_frozen=True)
freezer.add_item(item)

print(freezer.format_trace())
# Bag freezer_bag_1 (freezer) contains: 1x Ice Cream (frozen) [medium] (1/10)
```

## Related Components

- **Bag** (`src/domain/bag.py`) — Domain model with `can_accept_item()`, `add_item()`, `format_trace()`.
- **ForwardChainBagger** (`src/utils/bagger.py`) — Creates bags via factory methods during forward-chaining (Goal B).
- **Robot** (`src/domain/robot.py`) — Contains `compartments: List[Bag]` for delivery.
- **RobotSqlObject** (`src/mappers/robot.py`) — Serializes bags as `compartments_json`.
