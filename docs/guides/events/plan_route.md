# Robot Lifecycle Events (Goal A — Route Optimization)

## Overview

The robot lifecycle events in `src/events/robot.py` model the complete delivery cycle: **bag → route → deliver → return → charge**. Each event enforces domain rules about the robot's state (location, bags, battery) and operates on a per-robot basis.

`ViewFleet` provides a read-only real-time status display of the entire fleet.

**Module:** `src/events/robot.py`

## Robot Lifecycle

```
idle @ FW → [BagOrder] → idle @ FW (with bags)
         → [PlanRoute] → en_route @ destination
         → [DeliverOrder] → idle @ destination (no bags)
         → [ReturnToWarehouse] → idle @ FW
         → [ChargeRobot] → idle @ FW (100% battery)
```

## Events

### PlanRoute

Plan an A* route for a loaded robot to an order's destination.

**Required params:** `robot_id`, `order_id`
**Services:** `RobotService`, `OrderService`, `RoutePlannerService`, `LocationService`

**Preconditions:**
- Robot exists and has bags loaded (`ROBOT_NO_BAGS` if empty)
- Order exists

**Behavior:**
1. Build campus graph from `LocationService`
2. A* search from robot's current location to order destination
3. Attempt obstacle detection and replanning
4. Simulate energy consumption for the final path
5. **Low-battery check:** if `robot.is_low_battery()` (≤ 20%), abort delivery — plan emergency return to FW, consume return energy, update location to FW, set status `'idle'`, return `status: 'low_battery_return'` (order stays `'bagged'` for re-dispatch)
6. Otherwise: update robot location to destination, set status `'en_route'`

**Returns (normal):** `{robot_id, order_id, path, distance, status: 'complete'}`
**Returns (low battery):** `{robot_id, order_id, path, distance, return_path, return_distance, status: 'low_battery_return'}`

### DeliverOrder

Deliver bags at the destination.

**Required params:** `robot_id`, `order_id`
**Services:** `RobotService`, `OrderService`

**Preconditions:**
- Robot is at the order's destination (`ROBOT_NOT_AT_DESTINATION`)
- Robot has bags (`ROBOT_NO_BAGS`)

**Behavior:**
1. Clear robot compartments (bags delivered)
2. Set robot status to `'idle'`
3. Set order status to `'delivered'`
4. Persist both

**Returns:** `{robot_id, order_id, bags_delivered, status}`

### ReturnToWarehouse

Route a robot back to the Food Warehouse.

**Required params:** `robot_id`
**Services:** `RobotService`, `RoutePlannerService`, `LocationService`

**Preconditions:**
- Robot is NOT at the Food Warehouse (`ROBOT_ALREADY_AT_WAREHOUSE`)

**Behavior:**
1. Build campus graph, find FW
2. A* search from current location back to FW
3. Simulate energy consumption, update location to FW
4. Set status to `'idle'`

**Returns:** `{robot_id, path, distance, status}`

### ChargeRobot

Charge a robot at the Food Warehouse.

**Required params:** `robot_id`
**Services:** `RobotService`

**Preconditions:**
- Robot is at the Food Warehouse (`ROBOT_NOT_AT_WAREHOUSE`)

**Behavior:**
1. Reset battery to 100%
2. Set status to `'idle'`

**Returns:** `{robot_id, previous_battery, battery_level, status}`

### ViewFleet

Read-only real-time fleet status display.

**Required params:** none
**Services:** `RobotService` only

**Behavior:**
1. Load all robots via `robot_service.list()`
2. Print `format_for_trace()` for each robot
3. Return structured payload — never calls `save()`

**Returns:** `{robot_count, robots: [{robot_id, location, battery_level, status, bags}, ...]}`

## Error Codes

| Code | Trigger |
|------|---------|
| `ROBOT_NOT_FOUND` | Robot ID does not exist |
| `ROBOT_NO_BAGS` | Robot has empty compartments |
| `ORDER_NOT_FOUND` | Order ID does not exist |
| `ROBOT_NOT_AT_DESTINATION` | Robot not at order's destination (DeliverOrder) |
| `ROBOT_ALREADY_AT_WAREHOUSE` | Robot already at FW (ReturnToWarehouse) |
| `ROBOT_NOT_AT_WAREHOUSE` | Robot not at FW (ChargeRobot, BagOrder) |

## Related Components

- **RoutePlannerService** — `src/interfaces/route_planner.py`
- **AStarRoutePlanner** — `src/utils/route_planner.py`
- **LocationAggregate** — `src/mappers/location.py`
- **RobotAggregate** — `src/mappers/robot.py`
- **BagOrder** — Same module (`src/events/robot.py`)
