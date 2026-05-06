# Beverage Mappers

**File:** `src/mappers/beverage.py`
**Persistence Format:** YAML (`menu.yml`)

## Overview

`BeverageAggregate` and `BeverageYamlObject` provide the mapper layer for the `Beverage` domain model. Beverages are flat models (no nested domain objects) representing entries in the backward-chaining knowledge base (Goal C).

- **BeverageAggregate** — Mutable extension for validated allergen updates.
- **BeverageYamlObject** — YAML serialization with role-based field control.

## BeverageAggregate

**Extends:** `Beverage`, `tiferet.mappers.Aggregate`

Inherits all `Beverage` domain behavior (including `matches_guest` and `format_for_trace`) and adds validated mutation via `set_attribute`.

### Mutation Methods

#### `update_allergens(new_allergens: str) -> None`

Updates the comma-separated allergen avoidance list. Delegates to `set_attribute('avoids_allergens', new_allergens)`.

### `set_attribute` Behavior

Inherited from `Aggregate`. Rejects unknown attribute names with `TiferetError` and triggers Pydantic field validation on every mutation.

## BeverageYamlObject

**Extends:** `Beverage`, `tiferet.mappers.TransferObject`

### Roles (`_ROLES`)

| Role | Config | Purpose |
|------|--------|---------|
| `to_model` | `{}` | No exclusions — all fields included when mapping to aggregate. |
| `to_data.yaml` | `{'exclude': {'name'}}` | Excludes `name` because it serves as the YAML dict key. |

### Methods

#### `map(target=None, **overrides) -> BeverageAggregate`

Maps the transfer object to a `BeverageAggregate`. Defaults to `BeverageAggregate` if no target is specified.

#### `from_data(data, **overrides) -> BeverageYamlObject`

Creates a `BeverageYamlObject` from a raw YAML dict. Merges `overrides` (e.g., `name` from the dict key) into `data` before validation.

#### `from_model(beverage, **overrides) -> BeverageYamlObject`

Creates a `BeverageYamlObject` from a `Beverage` domain model or aggregate via `super().from_model()`.

## Usage

### Construction and Mutation

```python
from src.mappers.beverage import BeverageAggregate

bev = BeverageAggregate(
    name='FreshRoots Juice',
    beverage_type='juice',
    brand='FreshRoots',
    is_health_friendly=True,
    avoids_allergens='gluten, dairy',
)

# Validated mutation
bev.update_allergens('nuts, soy')
assert bev.avoids_allergens == 'nuts, soy'
```

### YAML Serialization Round-Trip

```python
from src.mappers.beverage import BeverageAggregate, BeverageYamlObject

# Aggregate -> YamlObject -> Aggregate
bev = BeverageAggregate(
    name='Corona',
    beverage_type='beer',
    brand='Corona',
)
yaml_obj = BeverageYamlObject.from_model(bev)
restored = yaml_obj.map()

assert restored.name == bev.name
assert restored.beverage_type == bev.beverage_type
```

### Loading from Raw YAML

```python
from src.mappers.beverage import BeverageYamlObject

data = {'beverage_type': 'water', 'brand': 'Aqua', 'is_health_friendly': True}
yaml_obj = BeverageYamlObject.from_data(data, name='Aqua Water')
bev = yaml_obj.map()
```

## Related Components

- **Beverage** (`src/domain/beverage.py`) — Domain model with `matches_guest()` and `format_for_trace()`.
- **BeverageYamlRepository** (`src/repos/beverage.py`) — Loads beverages from `menu.yml` using `BeverageYamlObject`.
- **BackwardChainSelector** (`src/utils/backward_chain_selector.py`) — Uses beverages for inference (Goal C).
