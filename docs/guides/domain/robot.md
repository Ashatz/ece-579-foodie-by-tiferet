# Robot

**File:** `src/domain/robot.py`
**Extends:** `tiferet.DomainObject` (Pydantic v2)

## Overview

`Robot` represents an autonomous food-delivery robot in the campus fleet. It tracks the robot's physical state — current location, battery level, loaded compartments (bags), and operational status — and provides methods for energy simulation and bag loading. Robots are the mobile agents in Goal A (route optimization) and carry the bagged orders produced by Goal B.

Robots are persisted in SQLite via `RobotSqliteRepository` and seeded with demo data by the `SeedDatabase` event.

## Attributes

| Attribute | Type | Default | Description |
|-----------|------|---------|-------------|
| `robot_id` | `str` | *required* | Unique identifier (e.g., `"R1"`, `"R2"`). |
| `current_location` | `Location` | *required* | Current position on the campus graph. |
| `battery_level` | `float` | `100.0` | Battery percentage (0.0–100.0). |
| `compartments` | `List[Bag]` | `[]` | Bags loaded in the robot's cargo area. |
| `status` | `Literal['idle', 'charging', 'en_route', 'delivering', 'returning']` | `'idle'` | Current operational status. |

### Robot Lifecycle

A robot transitions through these statuses during a delivery cycle:

1. **`idle`** — Parked at the Food Warehouse, available for assignment.
2. **`charging`** — Battery is being recharged at the Food Warehouse.
3. **`en_route`** — Traveling along an A*-planned path toward a delivery destination.
4. **`delivering`** — Arrived at destination, unloading bags.
5. **`returning`** — Heading back to the Food Warehouse after delivery.

## Methods

### `load_bag(bag: Bag) -> bool`

Loads a completed bag into a compartment (simulates the robotic arm). Returns `False` if the robot is currently `en_route` or `delivering` — bags can only be loaded while the robot is stationary.

```python
robot.load_bag(bag)  # True if idle/charging/returning
```

### `consume_energy(distance: float, energy_per_meter: float = 0.12) -> None`

Updates the battery level based on distance traveled. The default consumption rate is 0.12% per meter. Battery is clamped to a minimum of 0.0%.

```python
robot.consume_energy(50.0)       # Consumes 6.0% battery
robot.consume_energy(50.0, 0.2)  # Consumes 10.0% battery
```

### `is_low_battery(threshold: float = 20.0) -> bool`

Returns `True` if the battery is at or below the threshold, indicating the robot should return to the Food Warehouse for recharging.

### `format_for_trace() -> str`

Returns a human-readable status line for simulation and fleet monitoring.

**Example output:**
```
Robot R1 | Loc: FW (Food Warehouse) @ (0.0, 0.0) | Battery: 98.0% | Status: en_route | Bags: 2
```

## Usage

### Constructing a Robot

```python
from src.domain import Robot, Location

fw = Location(name='FW', x=0.0, y=0.0, is_food_warehouse=True)

robot = Robot(
    robot_id='R1',
    current_location=fw,
    battery_level=100.0,
    status='idle',
)
```

### Loading Bags and Simulating Travel

```python
from src.domain import Bag, Item

bag = Bag(bag_id='bag_1', bag_type='paper')
bag.add_item(Item(name='water bottle', size='large'))

robot.load_bag(bag)            # True
robot.status = 'en_route'
robot.consume_energy(25.0)     # Battery: 97.0%
robot.is_low_battery()         # False
```

### Data Source — SQLite

Robots are stored in SQLite and managed by `RobotSqliteRepository`. The `SeedDatabase` event pre-populates a fleet of three robots (R1, R2, R3), all starting at the Food Warehouse with full battery.

### Role in A* Route Planning (Goal A)

1. **Fleet assignment** — The `PlanRoute` event assigns pending orders to available robots.
2. **Path execution** — As a robot traverses each edge in the A*-planned path, `consume_energy` updates its battery.
3. **Low-battery replanning** — If `is_low_battery()` returns `True` mid-route, the robot is rerouted to the Food Warehouse for recharging.
4. **Obstacle replanning** — When an obstacle is detected on the current path, A* replans from the robot's `current_location`.

## Related Components

- **Location** (`src/domain/location.py`) — The `current_location` attribute type; provides `distance_to` for the A* heuristic.
- **Bag** (`src/domain/bag.py`) — Loaded into compartments via `load_bag`.
- **RobotAggregate / RobotSqlObject** (`src/mappers/robot.py`) — Mapper layer for mutation and SQLite serialization.
- **RobotSqliteRepository** (`src/repos/robot.py`) — SQLite-backed persistence.
- **RobotService** (`src/interfaces/robot.py`) — Service interface for robot CRUD operations.
- **AStarRoutePlanner** (`src/utils/route_planner.py`) — Plans delivery routes across the campus graph.
- **PlanRoute** (`src/events/plan_route.py`) — Domain event that orchestrates multi-robot route planning.
