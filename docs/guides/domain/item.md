# Item

**File:** `src/domain/item.py`
**Extends:** `tiferet.DomainObject` (Pydantic v2)

## Overview

`Item` represents a single food item in an order. It is the smallest unit of data consumed by the FOODIE_BAGGER forward-chaining production system (Goal B) and participates in order planning and route optimization (Goal A).

Items are loaded from `menu.yml` via the `ItemYamlRepository` and assembled into `Order` objects stored in SQLite.

## Attributes

| Attribute | Type | Default | Description |
|-----------|------|---------|-------------|
| `name` | `str` | *required* | Item name or description (e.g., `"1-gallon water bottle"`). |
| `size` | `Literal['large', 'medium', 'small']` | *required* | Size category that determines bagging priority — large items are bagged first, then medium, then small. |
| `is_frozen` | `bool` | `False` | Whether the item requires a freezer bag instead of a paper bag. |
| `is_fragile` | `bool` | `False` | Whether the item must not be crushed — fragile items always start a new bag. |
| `quantity` | `int` | `1` | Number of identical items (minimum 1). |

## Methods

### `format_for_bagger() -> str`

Returns a human-readable string for the FOODIE_BAGGER simulation trace. Includes quantity, name, optional flag annotations (frozen/fragile), and size.

**Example output:**
```
2x 1-gallon water bottle [large]
1x pint ice cream (frozen) [medium]
1x granola box (fragile) [small]
```

## Usage

### Constructing an Item

```python
from src.domain import Item

water = Item(
    name='1-gallon water bottle',
    size='large',
    quantity=2,
)

ice_cream = Item(
    name='pint ice cream',
    size='medium',
    is_frozen=True,
)
```

### Data Source — menu.yml

Items are defined in `menu.yml` and loaded via `ItemYamlRepository`:

```yaml
items:
  "1-gallon water bottle":
    name: "1-gallon water bottle"
    size: "large"
    is_frozen: false
    is_fragile: false
    quantity: 2
```

### Bagging Rules (Goal B)

The `size` attribute drives the forward-chaining rule priority:
1. **Large** items are placed first.
2. **Medium** items follow.
3. **Small** items are placed last.

The `is_frozen` flag routes items to freezer bags. The `is_fragile` flag forces a new bag to prevent crushing.

## Related Components

- **Bag** (`src/domain/bag.py`) — Contains a list of `Item` objects and enforces capacity/crush rules.
- **Order** (`src/domain/order.py`) — Contains a list of `Item` objects representing a customer order.
- **ItemAggregate / ItemYamlObject** (`src/mappers/item.py`) — Mapper layer for mutation and YAML serialization.
- **ItemYamlRepository** (`src/repos/item.py`) — Loads items from `menu.yml`.
- **ForwardChainBagger** (`src/utils/bagger.py`) — Consumes items to execute bagging rules.
