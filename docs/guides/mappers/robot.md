# Robot Mappers

**File:** `src/mappers/robot.py`
**Persistence Format:** SQLite (`foodie.db`)

## Overview

`RobotAggregate` and `RobotSqlObject` provide the mapper layer for the `Robot` domain model — the most composite mapper in FOODIE. Robot contains two nested domain objects (`current_location: Location`, `compartments: List[Bag]`) that must each be serialized as separate JSON TEXT columns in SQLite.

This extends the custom serialization pattern established by `OrderSqlObject` (one JSON column) to handle two JSON columns: `current_location_json` and `compartments_json`.

- **RobotAggregate** — Mutable extension for battery, location, and status updates during A* route execution.
- **RobotSqlObject** — SQLite serialization with dual-JSON custom `to_primitive`.

## RobotAggregate

**Extends:** `Robot`, `tiferet.mappers.Aggregate`

### Mutation Methods

#### `update_battery(new_level: float) -> None`

Updates battery percentage. Pydantic's `validate_assignment=True` enforces the `ge=0.0, le=100.0` constraint.

#### `update_location(new_location: Location) -> None`

Changes current location to a new `Location` domain object.

#### `update_status(new_status: str) -> None`

Changes operational status. Pydantic enforces the `Literal['idle', 'charging', 'en_route', 'delivering', 'returning']` constraint.

## RobotSqlObject

**Extends:** `Robot`, `tiferet.mappers.TransferObject`

### Roles (`_ROLES`)

| Role | Config | Purpose |
|------|--------|---------|
| `to_model` | `{'exclude': {'current_location', 'compartments'}}` | Nested objects passed separately via `map()`. |
| `to_data.sqlite` | `{'exclude': {'current_location', 'compartments'}}` | Nested objects serialized as JSON columns. |

### Methods

#### `to_primitive(role=None, **overrides) -> dict`

Overrides base serialization. When `role='to_data.sqlite'`:
- Adds `current_location_json` via `json.dumps(self.current_location.model_dump())`.
- Adds `compartments_json` via `json.dumps([bag.model_dump() for bag in self.compartments])`.

Both `current_location` and `compartments` are excluded from the base dict.

#### `map(target=None, **overrides) -> RobotAggregate`

Maps to `RobotAggregate`, passing nested objects through:
- `current_location=self.current_location`
- `compartments=list(self.compartments)`

#### `from_data(data, **overrides) -> RobotSqlObject` (classmethod)

Creates from a raw SQLite row dict with dual deserialization:
1. Pops `current_location_json` → `Location(**json.loads(...))`.
2. Pops `compartments_json` → `[Bag(**bag_data) for bag_data in json.loads(...)]`.
3. Delegates to `model_validate`.

#### `from_model(robot, **overrides) -> RobotSqlObject` (classmethod)

Creates from a `Robot` domain model or aggregate via `super().from_model()`.

### Serialization Flow

```
RobotAggregate
    → RobotSqlObject.from_model()
    → .to_primitive(role='to_data.sqlite')
    → SQLite row {robot_id, battery_level, status, current_location_json, compartments_json}
    → RobotSqlObject.from_data()
    → .map()
    → RobotAggregate
```

### Comparison with OrderSqlObject

| Aspect | OrderSqlObject | RobotSqlObject |
|--------|---------------|----------------|
| JSON columns | 1 (`items_json`) | 2 (`current_location_json`, `compartments_json`) |
| Nested types | `List[Item]` | `Location` + `List[Bag]` |
| Pattern | Same custom `to_primitive` / `from_data` |  |

## Usage

### Construction and Mutation

```python
from src.domain import Location
from src.mappers.robot import RobotAggregate

robot = RobotAggregate(
    robot_id='R1',
    current_location=Location(name='FW', x=0.0, y=0.0, is_food_warehouse=True),
    battery_level=100.0,
    status='idle',
)

robot.update_battery(85.0)
robot.update_location(Location(name='Building_A', x=3.0, y=4.0))
robot.update_status('en_route')
```

### SQLite Round-Trip

```python
from src.mappers.robot import RobotSqlObject

# Serialize
sql_obj = RobotSqlObject.from_model(robot)
row = sql_obj.to_primitive(role='to_data.sqlite')

# Deserialize
restored = RobotSqlObject.from_data(dict(row)).map()
assert restored.current_location.name == robot.current_location.name
assert restored.compartments == robot.compartments
```

## Related Components

- **Robot** (`src/domain/robot.py`) — Domain model with `has_capacity()`, `energy_cost()`, `format_status()`.
- **Location** (`src/domain/location.py`) — Nested domain model for `current_location`.
- **Bag** (`src/domain/bag.py`) — Nested domain model for `compartments`.
- **RobotSqliteRepository** (`src/repos/robot.py`) — Persists robots using `RobotSqlObject`.
- **PlanRoute** (`src/events/plan_route.py`) — Mutates robot state during A* route execution (Goal A).
