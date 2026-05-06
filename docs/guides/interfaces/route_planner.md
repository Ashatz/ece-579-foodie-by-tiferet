# RoutePlannerService

**File:** `src/interfaces/route_planner.py`
**Extends:** `tiferet.interfaces.Service` (ABC)

## Overview

`RoutePlannerService` defines the abstract contract for FOODIE's A* route planning and obstacle-aware replanning system (Goal A). It exposes two methods — `find_path` for shortest-path search and `detect_and_replan` for mid-route obstacle handling. This interface decouples the `PlanRoute` domain event from the concrete A* implementation, allowing the search algorithm and heuristic to evolve independently of fleet orchestration logic.

## Contract Design

Route planning is a computational infrastructure concern: given a campus terrain graph with weighted edges and potential obstacles, find optimal paths for delivery robots. By abstracting this behind a Service contract:

- **Domain events** (`PlanRoute`) depend only on the interface, not on the A* implementation details.
- **Testing** is simplified — mock the service to test fleet orchestration without running the full search algorithm.
- **Swappability** — alternative pathfinding algorithms (e.g., Dijkstra's, D* Lite) can be introduced by implementing the same contract.

## Method Signatures

### `find_path(start, goal, loc_map, edges, obstacles) -> Tuple[List[str] | None, float]`

Find the shortest path between two locations using A* search.

**Parameters:**

- `start` (`str`) — Start location name.
- `goal` (`str`) — Goal location name.
- `loc_map` (`Dict[str, LocationAggregate]`) — Location lookup by name. Each `LocationAggregate` provides coordinates for heuristic computation.
- `edges` (`Dict[str, List[str]]`) — Adjacency list as a dict of `{name: [neighbor_name, ...]}`.
- `obstacles` (`Set[Tuple[str, str]]`) — Set of blocked edge tuples. An edge `(A, B)` in the set means travel from A to B is blocked.

**Returns:**

- `Tuple[List[str] | None, float]` — `(path as list of location names, total distance)` or `(None, 0.0)` if no path exists.

### `detect_and_replan(path, goal, loc_map, edges, obstacles) -> Tuple[List[str] | None, float, Set[Tuple[str, str]]]`

Simulate obstacle detection at the midpoint of a path and replan.

**Parameters:**

- `path` (`List[str]`) — The current planned path as a list of location names.
- `goal` (`str`) — Goal location name.
- `loc_map` (`Dict[str, LocationAggregate]`) — Location lookup by name.
- `edges` (`Dict[str, List[str]]`) — Adjacency list.
- `obstacles` (`Set[Tuple[str, str]]`) — Current set of blocked edge tuples (mutated in place when a new obstacle is injected).

**Returns:**

- `Tuple[List[str] | None, float, Set[Tuple[str, str]]]` — `(new_path, new_distance, updated_obstacles)` or `(None, 0.0, obstacles)` if no replan is needed or possible.

## Input/Output Types

- **Input:** `LocationAggregate` (`src/mappers/location.py`) — Mutable aggregate with `name`, `x`, `y`, `is_obstacle` attributes and `distance_to` method for heuristic computation.
- **Output:** Path as `List[str]` (location names in traversal order) and `float` total distance. The `detect_and_replan` method additionally returns the updated obstacles set.

## Integration Points

- **PlanRoute** (`src/events/plan_route.py`) — Domain event that loads the campus graph, assigns orders to robots via round-robin, and delegates to `RoutePlannerService.find_path()` and `detect_and_replan()` for each delivery.
- **DI Container** (`config.yml`) — The concrete utility is registered as a service and injected into `PlanRoute` via constructor injection.

## Concrete Implementation

- **AStarRoutePlanner** (`src/utils/route_planner.py`) — Implements A* search with Manhattan distance heuristic, obstacle-aware edge filtering, and midpoint replanning. See `docs/guides/utils/route_planner.md` for details.

## Related Components

- **Location** (`src/domain/location.py`) — Domain model representing a campus graph node.
- **LocationAggregate** (`src/mappers/location.py`) — Mutable aggregate consumed by the route planner contract.
- **Robot** (`src/domain/robot.py`) — Domain model representing a delivery robot with battery and compartment state.
- **PlanRoute** (`src/events/plan_route.py`) — Domain event that consumes this interface.
- **AStarRoutePlanner** (`src/utils/route_planner.py`) — Concrete implementation.
