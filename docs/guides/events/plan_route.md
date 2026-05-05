# PlanRoute

**File:** `src/events/plan_route.py`
**Extends:** `tiferet.events.DomainEvent`
**Feature:** `admin.plan_route`

## Overview

`PlanRoute` is the domain event that orchestrates **Goal A — Route Optimization**. It loads the robot fleet, pending orders, and the campus graph, assigns orders to robots via round-robin, and delegates pathfinding and obstacle replanning to an injected `RoutePlannerService`. After each route is planned, the event simulates robot movement by consuming battery energy and persisting the updated robot state.

The event is the coordinator — it owns the business logic of fleet management (assignment, energy tracking, status updates) while the `AStarRoutePlanner` utility owns the search algorithm.

## Injected Dependencies

| Dependency | Type | Purpose |
|------------|------|---------|
| `robot_service` | `RobotService` | Load and persist robots from/to SQLite. |
| `order_service` | `OrderService` | Load pending orders from SQLite. |
| `route_planner` | `RoutePlannerService` | A* pathfinding and obstacle replanning. |
| `location_service` | `LocationService` | Load campus graph (locations + edges) from YAML. |

## Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `obstacles` | `set` | No | Pre-existing blocked edges. Defaults to an empty set. Passed via `kwargs`. |

## Execution Flow

### Step 1 — Load Fleet and Graph Data

```python
robots = self.robot_service.list()
orders = self.order_service.list()
locations = self.location_service.list()
edges = self.location_service.get_edges()
```

The campus graph is loaded from `campus.yml` through the `LocationService`. Locations are converted to `LocationAggregate` instances and indexed into a `loc_map` dictionary for O(1) lookups during A* search.

### Step 2 — Assign Orders to Robots (Round-Robin)

```python
for i, order in enumerate(orders):
    robot = robots[i % len(robots)]
```

Orders are assigned to robots in round-robin order: `ORD-101` → `R1`, `ORD-102` → `R2`, `ORD-103` → `R3`. This simple strategy ensures even distribution across the fleet. With 3 orders and 3 robots, each robot gets exactly one delivery.

In a production system, assignment could consider robot battery levels, proximity to the order's destination, or compartment capacity. The round-robin approach is sufficient for the demo simulation.

### Step 3 — Delegate A* Pathfinding

```python
path, dist = self.route_planner.find_path(start, goal, loc_map, edges, obstacles)
```

For each order, the event calls the planner with the robot's current location as `start` and the order's `destination` as `goal`. The planner returns the optimal path and its total distance, or `(None, 0.0)` if no path exists.

If no path is found, the order is logged as `'no_path'` and skipped.

### Step 4 — Delegate Obstacle Detection and Replanning

```python
new_path, new_dist, obstacles = self.route_planner.detect_and_replan(
    path, goal, loc_map, edges, obstacles,
)
```

The planner simulates obstacle detection at the path's midpoint and, if an obstacle is injected, replans from the obstacle point to the goal. The obstacles set is mutated in place and carried forward to subsequent orders — once an edge is blocked, it stays blocked for the rest of the simulation.

If replanning produces a new path, it replaces the original.

### Step 5 — Simulate Robot Movement

```python
robot.consume_energy(dist)
robot.status = 'en_route'
self.robot_service.save(robot)
```

The robot's battery is decremented based on the route distance (default: 0.12% per meter), its status is updated to `'en_route'`, and the changes are persisted to SQLite.

### Step 6 — Fleet Status Summary

```
=== Current Fleet Status ===
  Robot R1 | Loc: FW (Food Warehouse) @ (0.0, 0.0) | Battery: 98.0% | Status: en_route
  Robot R2 | Loc: FW (Food Warehouse) @ (0.0, 0.0) | Battery: 98.2% | Status: en_route
  Robot R3 | Loc: FW (Food Warehouse) @ (0.0, 0.0) | Battery: 99.4% | Status: en_route
===
```

### Return Value

```python
{
    'total_distance': 35.2,
    'routes_planned': 3,
    'details': [
        {'order': 'ORD-101', 'robot': 'R1', 'path': [...], 'distance': 17.0, 'status': 'planned'},
        ...
    ],
    'status': 'complete',
}
```

## Design Decisions

### Why round-robin assignment?

The demo uses three robots and three orders — one-to-one assignment is natural. Round-robin is deterministic and predictable, which is important for reproducible simulation traces. A more sophisticated assignment algorithm (e.g., nearest-robot, least-battery-cost) would be an enhancement but adds complexity without improving the A* demonstration.

### Why carry obstacles across orders?

Once an edge is blocked during one robot's route, it remains blocked for all subsequent robots in the same simulation run. This reflects a real-world scenario — an obstacle on campus doesn't disappear when a different robot encounters it. It also demonstrates that A* can work with a growing obstacle set across multiple invocations.

### Why does the event own energy simulation?

Battery management is a domain concern — it depends on business rules (energy per meter, low-battery thresholds, recharge logic) that the route planner shouldn't know about. The planner returns distances; the event decides what to do with them.

## Related Components

- **AStarRoutePlanner** (`src/utils/route_planner.py`) — The concrete A* algorithm. See [route planner guide](../utils/route_planner.md).
- **Robot** (`src/domain/robot.py`) — Tracks battery, compartments, and status.
- **Order** (`src/domain/order.py`) — Provides delivery destinations.
- **Location** (`src/domain/location.py`) — Campus graph nodes with coordinates.
- **LocationAggregate** (`src/mappers/location.py`) — Node type consumed by the planner.
- **RobotService** (`src/interfaces/robot.py`) — Robot CRUD contract.
- **OrderService** (`src/interfaces/order.py`) — Order CRUD contract.
- **LocationService** (`src/interfaces/location.py`) — Graph data access (locations + edges).
- **RoutePlannerService** (`src/interfaces/route_planner.py`) — Abstract interface for pathfinding.
