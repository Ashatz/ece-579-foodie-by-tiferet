# LocationService

**File:** `src/interfaces/location.py`
**Extends:** `Service` (`tiferet.interfaces`)

## Overview

`LocationService` is the abstract data-access contract for the FOODIE campus terrain graph. It defines the CRUD operations for location nodes plus a `get_edges()` method for the graph adjacency list, decoupling the A* route planning system (Goal A) from the underlying storage mechanism.

Locations represent named nodes on the campus map — buildings, dormitories, intersections, and the Food Warehouse. The terrain graph is universal/config data — it is loaded from configuration (YAML) and used by the `AStarRoutePlanner` to compute delivery routes.

## Contract Design

`LocationService` abstracts **YAML-backed persistence** for the `locations` and `edges` sections of `campus.yml`. The interface exists so that domain events (e.g., `SeedDatabase`, `PlanRoute`) can load location data and the graph adjacency list without coupling to the YAML file format.

Key design decisions:
- **Name-based primary key** — Locations are identified by their `name` field, which serves as the YAML dict key. This is consistent with the YAML-backed convention used by `ItemService` and `BeverageService`.
- **Dual-section data model** — Unlike `ItemService` and `BeverageService` which read from a single YAML section, `LocationService` spans two sections: `locations` (node attributes) and `edges` (adjacency list).
- **Extra method: `get_edges()`** — Returns the campus graph adjacency list as `Dict[str, List[str]]`, enabling A* search without loading individual locations.
- **Domain-typed parameters** — Methods accept and return `Location` domain objects rather than raw dicts, ensuring type safety at the interface boundary.
- **Idempotent delete** — `delete(name)` must not raise if the location does not exist.

## Method Signatures

### `exists(name: str) -> bool`
Check if a location exists by name.

### `get(name: str) -> Location`
Retrieve a location by name. Returns `None` if not found.

### `list() -> List[Location]`
List all locations on the campus map.

### `save(location: Location) -> None`
Persist a location. If a location with the same name already exists, it is replaced.

### `delete(name: str) -> None`
Delete a location by name. Idempotent — does not raise if the location does not exist.

### `get_edges() -> Dict[str, List[str]]`
Retrieve the campus graph adjacency list. Returns a dict mapping each location name to a list of its neighbor names. This bidirectional adjacency list is used by the A* route planner to traverse the campus graph.

## Primary Key Convention

Locations use `name: str` as the primary key, reflecting the YAML dict-key convention:

```yaml
locations:
  FW:                       # <-- name is the dict key
    x: 0
    y: 0
    is_obstacle: false
  Building_A:
    x: 3
    y: 4
    is_obstacle: false
```

The edges section defines the adjacency list separately:

```yaml
edges:
  FW: [Int_1, Int_2]
  Int_1: [FW, Building_A]
  ...
```

## Integration Points

- **Repository:** `LocationYamlRepository` (`src/repos/location.py`) — Concrete YAML-backed implementation reading from `campus.yml`.
- **Domain Events:**
  - `SeedDatabase` — Calls `location_service.get('FW')` to load the Food Warehouse as the starting location for seeded robots.
  - `PlanRoute` — Calls `location_service.list()` and `location_service.get_edges()` to build the campus graph for A* search.
- **Domain Model:** `Location` (`src/domain/location.py`) — The domain object returned by all read methods.

## Related Components

- **Location** (`src/domain/location.py`) — Domain model with `name`, `x`, `y`, `is_obstacle`.
- **LocationAggregate** (`src/mappers/location.py`) — Aggregate with mutation support.
- **LocationYamlObject** (`src/mappers/location.py`) — TransferObject for YAML serialization.
- **LocationYamlRepository** (`src/repos/location.py`) — Concrete repository implementation.
- **RoutePlannerService** (`src/interfaces/route_planner.py`) — A* planning contract that consumes location data.
- **AStarRoutePlanner** (`src/utils/route_planner.py`) — Utility that implements A* search over the campus graph.
