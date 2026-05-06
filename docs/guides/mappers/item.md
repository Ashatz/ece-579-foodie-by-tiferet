# Item Mappers

**File:** `src/mappers/item.py`
**Persistence Format:** YAML (`menu.yml`)

## Overview

`ItemAggregate` and `ItemYamlObject` provide the mapper layer for the `Item` domain model. Items are flat models (no nested domain objects), making these the simplest mappers in the FOODIE system.

- **ItemAggregate** — Mutable extension for validated field updates.
- **ItemYamlObject** — YAML serialization with role-based field control.

## ItemAggregate

**Extends:** `Item`, `tiferet.mappers.Aggregate`

Inherits all `Item` domain behavior and adds validated mutation via `set_attribute` (inherited from `Aggregate`).

### Mutation Methods

#### `update_quantity(new_quantity: int) -> None`

Updates the item quantity. Delegates to `set_attribute('quantity', new_quantity)`. Pydantic's `validate_assignment=True` enforces the `ge=1` constraint from the domain model — attempting to set `quantity=0` raises `ValidationError`.

### `set_attribute` Behavior

Inherited from `Aggregate`. Rejects unknown attribute names with `TiferetError` and triggers Pydantic field validation on every mutation.

## ItemYamlObject

**Extends:** `Item`, `tiferet.mappers.TransferObject`

### Roles (`_ROLES`)

| Role | Config | Purpose |
|------|--------|---------|
| `to_model` | `{}` | No exclusions — all fields included when mapping to aggregate. |
| `to_data.yaml` | `{'exclude': {'name'}}` | Excludes `name` because it serves as the YAML dict key. |

### Methods

#### `map(target=None, **overrides) -> ItemAggregate`

Maps the transfer object to an `ItemAggregate`. Defaults to `ItemAggregate` if no target is specified.

#### `from_data(data, **overrides) -> ItemYamlObject`

Creates an `ItemYamlObject` from a raw YAML dict. Merges `overrides` (e.g., `name` from the dict key) into `data` before validation.

#### `from_model(item, **overrides) -> ItemYamlObject`

Creates an `ItemYamlObject` from an `Item` domain model or aggregate via `super().from_model()`.

## Usage

### Construction and Mutation

```python
from src.mappers.item import ItemAggregate

item = ItemAggregate(
    name='Water Bottle',
    size='large',
    quantity=2,
)

# Validated mutation
item.update_quantity(5)
assert item.quantity == 5
```

### YAML Serialization Round-Trip

```python
from src.mappers.item import ItemAggregate, ItemYamlObject

# Aggregate -> YamlObject -> Aggregate
item = ItemAggregate(name='Ice Cream', size='medium', is_frozen=True)
yaml_obj = ItemYamlObject.from_model(item)
restored = yaml_obj.map()

assert restored.name == item.name
assert restored.is_frozen == item.is_frozen
```

### Loading from Raw YAML

```python
from src.mappers.item import ItemYamlObject

data = {'size': 'small', 'is_fragile': True, 'quantity': 1}
yaml_obj = ItemYamlObject.from_data(data, name='Granola Box')
item = yaml_obj.map()
```

## Related Components

- **Item** (`src/domain/item.py`) — Domain model with `format_for_bagger()`.
- **ItemYamlRepository** (`src/repos/item.py`) — Loads items from `menu.yml` using `ItemYamlObject`.
- **ForwardChainBagger** (`src/utils/bagger.py`) — Consumes items for bagging rules (Goal B).
