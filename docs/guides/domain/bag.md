# Bag

**File:** `src/domain/bag.py`
**Extends:** `tiferet.DomainObject` (Pydantic v2)

## Overview

`Bag` represents a physical bag (paper or freezer) that holds `Item` objects. It is the primary output of the FOODIE_BAGGER forward-chaining production system (Goal B) and is loaded into `Robot` compartments for delivery (Goal A).

The `Bag` model enforces the project's bagging rules: size-priority ordering, frozen-item isolation, fragile-item protection, and per-bag capacity limits.

## Attributes

| Attribute | Type | Default | Description |
|-----------|------|---------|-------------|
| `bag_id` | `str` | *required* | Unique identifier (e.g., `"bag_1"`, `"freezer_bag_2"`). |
| `bag_type` | `Literal['paper', 'freezer']` | `'paper'` | Paper for normal items, freezer for frozen items. |
| `items` | `List[Item]` | `[]` | Items currently in this bag. |
| `max_capacity` | `int` | `10` | Maximum number of items per bag. |

## Methods

### `can_accept_item(item: Item) -> bool`

Checks whether the bag can safely accept the given item without violating rules.

**Rules enforced:**
1. **Capacity** — The bag must not already be at `max_capacity`.
2. **Fragile no-crush** — A fragile item cannot be added to a bag that already contains items (fragile items always start a new bag).

Returns `True` if the item can be added.

### `add_item(item: Item) -> bool`

Attempts to add an item to the bag. Calls `can_accept_item` first, then appends the item via list reassignment (required for Pydantic validation). Returns `True` if the item was successfully added.

### `format_trace() -> str`

Returns the exact format required by the project spec for simulation trace output.

**Example output:**
```
Bag bag_1 (paper) contains: 1x 1-gallon water bottle, 1x 1-gallon water bottle (2/10)
Bag freezer_bag_2 (freezer) contains: 1x pint ice cream (1/10)
```

## Usage

### Constructing a Bag

```python
from src.domain import Bag, Item

bag = Bag(bag_id='bag_1', bag_type='paper')

water = Item(name='1-gallon water bottle', size='large')
bag.add_item(water)  # True

fragile = Item(name='granola box', size='small', is_fragile=True)
bag.add_item(fragile)  # False — fragile items start a new bag
```

### Freezer Bags

Frozen items are routed to freezer bags by the `ForwardChainBagger`:

```python
freezer = Bag(bag_id='freezer_bag_1', bag_type='freezer')
ice_cream = Item(name='pint ice cream', size='medium', is_frozen=True)
freezer.add_item(ice_cream)  # True
```

### Bagging Rule Summary (Goal B)

The forward-chaining production system applies these rules in order:

1. **Size priority** — Large items first, then medium, then small.
2. **Frozen isolation** — Frozen items go into `freezer` bags.
3. **Fragile protection** — Fragile items always start a new bag (prevents crushing).
4. **Capacity limit** — No bag exceeds `max_capacity` items.

The `Bag` model encodes rules 3 and 4 directly in `can_accept_item`. Rules 1 and 2 are enforced by the `ForwardChainBagger` utility.

## Related Components

- **Item** (`src/domain/item.py`) — The objects stored inside bags.
- **Robot** (`src/domain/robot.py`) — Loads completed bags into compartments via `load_bag`.
- **BagAggregate** (`src/mappers/bag.py`) — Aggregate extension for mutation operations.
- **ForwardChainBagger** (`src/utils/bagger.py`) — The production system that creates and fills bags.
- **BagOrder** (`src/events/bag_order.py`) — Domain event that orchestrates the bagging workflow.
