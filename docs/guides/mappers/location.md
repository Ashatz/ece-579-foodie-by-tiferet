# Location Mappers

**File:** `src/mappers/location.py`
**Persistence Format:** YAML (`campus.yml`)

## Overview

`LocationAggregate` and `LocationYamlObject` provide the mapper layer for the `Location` domain model. Locations are flat models (no nested domain objects) representing nodes in the campus terrain graph used by A* route planning (Goal A).

- **LocationAggregate** — Mutable extension for validated coordinate updates.
- **LocationYamlObject** — YAML serialization with role-based field control.

## LocationAggregate

**Extends:** `Location`, `tiferet.mappers.Aggregate`

Inherits all `Location` domain behavior (including `distance_to` and `format_for_trace`) and adds validated mutation via `set_attribute`.

### Mutation Methods

#### `update_coordinates(x: float, y: float) -> None`

Updates both `x` and `y` coordinates. Calls `set_attribute` for each, ensuring Pydantic field validation on every mutation.

### `set_attribute` Behavior

Inherited from `Aggregate`. Rejects unknown attribute names with `TiferetError` and triggers Pydantic field validation on every mutation.

## LocationYamlObject

**Extends:** `Location`, `tiferet.mappers.TransferObject`

### Roles (`_ROLES`)

| Role | Config | Purpose |
|------|--------|---------|
| `to_model` | `{}` | No exclusions — all fields included when mapping to aggregate. |
| `to_data.yaml` | `{'exclude': {'name'}}` | Excludes `name` because it serves as the YAML dict key. |

### Methods

#### `map(target=None, **overrides) -> LocationAggregate`

Maps the transfer object to a `LocationAggregate`. Defaults to `LocationAggregate` if no target is specified.

#### `from_data(data, **overrides) -> LocationYamlObject`

Creates a `LocationYamlObject` from a raw YAML dict. Merges `overrides` (e.g., `name` from the dict key) into `data` before validation.

#### `from_model(location, **overrides) -> LocationYamlObject`

Creates a `LocationYamlObject` from a `Location` domain model or aggregate via `super().from_model()`.

## Usage

### Construction and Mutation

```python
from src.mappers.location import LocationAggregate

loc = LocationAggregate(
    name='Building_A',
    x=3.0,
    y=4.0,
    is_obstacle_prone=True,
)

# Validated mutation
loc.update_coordinates(10.0, 20.0)
assert loc.x == 10.0
assert loc.y == 20.0
```

### YAML Serialization Round-Trip

```python
from src.mappers.location import LocationAggregate, LocationYamlObject

# Aggregate -> YamlObject -> Aggregate
loc = LocationAggregate(name='FW', x=0.0, y=0.0, is_food_warehouse=True)
yaml_obj = LocationYamlObject.from_model(loc)
restored = yaml_obj.map()

assert restored.name == loc.name
assert restored.is_food_warehouse == loc.is_food_warehouse
```

### Loading from Raw YAML

```python
from src.mappers.location import LocationYamlObject

data = {'x': 5.0, 'y': 5.0, 'is_obstacle_prone': True}
yaml_obj = LocationYamlObject.from_data(data, name='Intersection_1')
loc = yaml_obj.map()
```

## Related Components

- **Location** (`src/domain/location.py`) — Domain model with `distance_to()` and `format_for_trace()`.
- **LocationYamlRepository** (`src/repos/location.py`) — Loads locations from `campus.yml` using `LocationYamlObject`.
- **AStarRoutePlanner** (`src/utils/route_planner.py`) — Uses locations for A* pathfinding (Goal A).
