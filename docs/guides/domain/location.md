# Location

**File:** `src/domain/location.py`
**Extends:** `tiferet.DomainObject` (Pydantic v2)

## Overview

`Location` represents a node in the campus terrain graph — a building, pathway, or the Food Warehouse (FW). It provides the spatial data used by the A* route-planning algorithm (Goal A), including coordinates for the Manhattan distance heuristic, a warehouse flag for the start/recharge point, and an obstacle-prone flag for dynamic replanning.

Locations are defined in `campus.yml` (with edges) and `locations.yml` (standalone), loaded via `LocationYamlRepository`.

## Attributes

| Attribute | Type | Default | Description |
|-----------|------|---------|-------------|
| `name` | `str` | *required* | Unique location identifier (e.g., `"FW"`, `"Building_A"`, `"Pathway_3"`). |
| `x` | `float` | *required* | X coordinate for distance heuristics. |
| `y` | `float` | *required* | Y coordinate for distance heuristics. |
| `is_food_warehouse` | `bool` | `False` | Whether this location is the Food Warehouse (robot start/recharge point). |
| `is_obstacle_prone` | `bool` | `False` | Whether this location may become blocked dynamically during route execution. |

## Methods

### `distance_to(other: Location) -> float`

Computes the Manhattan distance heuristic between this location and another. Manhattan distance (`|Δx| + |Δy|`) is used because campus pathways form a grid-like structure, making it an admissible and consistent heuristic for A*.

```python
fw = Location(name='FW', x=0.0, y=0.0, is_food_warehouse=True)
building_a = Location(name='Building_A', x=5.0, y=8.0)

fw.distance_to(building_a)  # 13.0
```

### `format_for_trace() -> str`

Returns a human-readable string for simulation and route trace output.

**Example output:**
```
FW (Food Warehouse) @ (0.0, 0.0)
Building_A @ (5.0, 8.0)
```

## Usage

### Constructing a Location

```python
from src.domain import Location

fw = Location(
    name='FW',
    x=0.0,
    y=0.0,
    is_food_warehouse=True,
)

pathway = Location(
    name='Pathway_3',
    x=3.0,
    y=4.0,
    is_obstacle_prone=True,
)
```

### Data Source — campus.yml

Locations and their edge graph are defined in `campus.yml`:

```yaml
locations:
  FW:
    name: FW
    x: 0.0
    y: 0.0
    is_food_warehouse: true
  Building_A:
    name: Building_A
    x: 5.0
    y: 8.0

edges:
  FW: [Pathway_1]
  Pathway_1: [FW, Pathway_2, Pathway_4]
  # ...
```

The `edges` section defines the bidirectional adjacency list used by the A* algorithm. Each location lists its direct neighbors.

### Role in A* Search (Goal A)

1. **Graph nodes** — Each `Location` is a node in the search graph.
2. **Heuristic function** — `distance_to` provides the `h(n)` value for A*. The Manhattan distance is admissible (never overestimates) on grid-like campus pathways.
3. **Obstacle detection** — Locations with `is_obstacle_prone=True` may become blocked mid-route, triggering replanning.
4. **Start node** — The Food Warehouse (`is_food_warehouse=True`) is the origin for all delivery routes and the recharge destination.

## Related Components

- **Robot** (`src/domain/robot.py`) — Has a `current_location` attribute of type `Location`.
- **LocationAggregate / LocationYamlObject** (`src/mappers/location.py`) — Mapper layer for mutation and YAML serialization.
- **LocationYamlRepository** (`src/repos/location.py`) — Loads locations and edges from `campus.yml`.
- **LocationService** (`src/interfaces/location.py`) — Service interface including `get_edges` for adjacency lookup.
- **AStarRoutePlanner** (`src/utils/route_planner.py`) — Consumes locations and edges to compute optimal delivery paths.
- **PlanRoute** (`src/events/plan_route.py`) — Domain event that orchestrates multi-robot route planning.
