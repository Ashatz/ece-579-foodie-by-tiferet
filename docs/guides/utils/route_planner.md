# AStarRoutePlanner

**File:** `src/utils/route_planner.py`
**Implements:** `RoutePlannerService` (`src/interfaces/route_planner.py`)

## Overview

`AStarRoutePlanner` is the concrete computational utility that performs shortest-path search on the campus terrain graph. It implements the A* search algorithm with a Manhattan distance heuristic, supports dynamic obstacle detection, and provides mid-route replanning. This utility powers **Goal A — Route Optimization** of the FOODIE project.

The planner is stateless: all graph data (locations, edges, obstacles) is passed in per call, making it injectable, testable, and reusable across different graph configurations.

## Why A* Search?

The FOODIE campus terrain is modeled as a weighted graph where locations are nodes and pathways are edges. Several search algorithms were considered:

| Algorithm | Optimal? | Complete? | Time | Space | Why not? |
|-----------|----------|-----------|------|-------|----------|
| **BFS** | Yes (unweighted) | Yes | O(b^d) | O(b^d) | Edge costs are not uniform — Manhattan distances vary per edge. |
| **Dijkstra's** | Yes | Yes | O((V+E) log V) | O(V) | Optimal, but explores nodes in all directions without guidance toward the goal. |
| **Greedy Best-First** | No | Yes | O(b^d) | O(b^d) | Fast but not optimal — can miss shorter paths that initially head away from the goal. |
| **A\*** | Yes | Yes | O((V+E) log V) | O(V) | **Combines Dijkstra's optimality with greedy's goal-directed search.** |

A* was chosen because:

1. **Optimality** — A* with an admissible heuristic guarantees the shortest path, which is critical for energy-constrained delivery robots.
2. **Efficiency** — The heuristic prunes large portions of the search space compared to Dijkstra's, which explores uniformly in all directions.
3. **Campus fit** — The grid-like pathway structure of a campus makes Manhattan distance a natural, admissible, and consistent heuristic.
4. **Dynamic replanning** — When obstacles block an edge mid-route, A* can efficiently recompute from the current position to the goal without starting over from scratch.

## Algorithm: `find_path`

### The A* Evaluation Function

A* evaluates each node using:

```
f(n) = g(n) + h(n)
```

Where:
- **g(n)** = actual cost from the start node to node n (accumulated edge distances).
- **h(n)** = heuristic estimate from node n to the goal (Manhattan distance).
- **f(n)** = estimated total cost of the cheapest path through n.

The node with the lowest f(n) is always expanded next.

### Heuristic: Manhattan Distance

The heuristic function is `Location.distance_to(other)`:

```
h(n) = |x_n - x_goal| + |y_n - y_goal|
```

**Why Manhattan distance?**

- **Admissible** — Manhattan distance never overestimates the true cost on a grid-like campus graph where robots travel along axis-aligned pathways. This guarantees A* finds the optimal path.
- **Consistent (monotone)** — For any edge (n, n'), `h(n) ≤ cost(n, n') + h(n')`. This means A* never needs to re-open closed nodes, improving efficiency.
- **Computationally trivial** — Two subtractions and two absolute values per evaluation.

Euclidean distance (`√(Δx² + Δy²)`) would also be admissible but would underestimate more aggressively on the grid, causing A* to explore more nodes before converging.

### Data Structures

- **Open set** — Python `heapq` min-heap of `(f_score, node_name)` tuples. The heap ensures the node with the lowest f-score is always dequeued first in O(log n).
- **came_from** — `Dict[str, str]` mapping each node to its predecessor for path reconstruction.
- **g_score** — `Dict[str, float]` tracking the best-known cost from start to each node.
- **loc_map** — `Dict[str, LocationAggregate]` providing O(1) coordinate lookups for heuristic evaluation.
- **edges** — `Dict[str, List[str]]` adjacency list representation of the campus graph.
- **obstacles** — `Set[Tuple[str, str]]` of blocked directed edges, checked in O(1) during neighbor expansion.

### Step-by-Step Execution

1. Initialize the open set with `(0.0, start)` and set `g_score[start] = 0.0`.
2. Pop the node with the lowest f-score from the heap.
3. If it's the goal, reconstruct the path by following `came_from` links backward and return `(path, g_score[goal])`.
4. For each neighbor of the current node:
   a. Skip if the edge `(current, neighbor)` is in the obstacle set.
   b. Compute `tentative_g = g_score[current] + edge_cost(current, neighbor)`.
   c. If `tentative_g < g_score[neighbor]` (or neighbor is unseen), update `came_from`, `g_score`, and push `(f_score, neighbor)` onto the heap.
5. If the heap empties without reaching the goal, return `(None, 0.0)`.

### Complexity

- **Time:** O((V + E) log V) where V = number of locations and E = number of edges. Each node is pushed/popped from the heap at most once (due to consistency), and each edge is examined once.
- **Space:** O(V) for the g_score map, came_from map, and heap.

On the default campus graph (10 locations, ~20 edges), A* typically expands only 4–6 nodes to find a path, compared to Dijkstra's which would expand all reachable nodes.

## Algorithm: `detect_and_replan`

### Dynamic Obstacle Handling

Real-world campus environments have unpredictable obstacles (construction, crowds, weather). The `detect_and_replan` method simulates this by:

1. **Obstacle injection** — At the midpoint of the current path, the method blocks the edge in both directions by adding `(from, to)` and `(to, from)` to the obstacle set. This only triggers on paths longer than 3 nodes to avoid trivially short routes.
2. **Partial replanning** — Rather than replanning the entire route from FW, A* is re-invoked only from the obstacle point to the goal. This is more efficient and realistic — the robot has already traveled the prefix.
3. **Path splicing** — The original prefix (start → obstacle point) is concatenated with the new tail (obstacle point → goal), and the total distance is recomputed.

### Why Midpoint Injection?

The midpoint is chosen as a simulation heuristic: it represents the "worst case" timing — the robot discovers the obstacle after committing to half the route, maximizing the impact on the remaining path. In a production system, obstacle detection would come from real-time sensors.

### Example Walkthrough

Given the default campus graph and a route from FW to Building_A:

```
Original: FW -> Pathway_1 -> Pathway_2 -> Pathway_3 -> Pathway_6 -> Building_A
                                          ^^^^^^^^^^^^^^^^^^^^^^^^^^^
                                          Midpoint edge blocked!

Obstacle injected: (Pathway_3, Pathway_6) and (Pathway_6, Pathway_3)

Replan from Pathway_3 to Building_A:
  Pathway_3 -> Building_B -> Pathway_4 -> ... -> Building_A

Spliced: FW -> Pathway_1 -> Pathway_2 -> [new tail from Pathway_3]
```

The replanned path avoids the blocked edge while preserving the already-traveled prefix.

## Campus Graph Structure

The planner operates on the graph defined in `campus.yml`:

```
FW (0,0) ── Pathway_1 (2,0) ── Pathway_4 (4,0) ── Building_B (6,3)
  │                │                   │                  │
  │           Pathway_2 (2,3) ── Pathway_3 (4,3) ─────────┘
  │                │                   │
Dorm_1 (0,5)  Pathway_5 (2,6) ── Pathway_6 (4,6) ── Building_A (5,8)
```

- **10 locations** with (x, y) coordinates.
- **Bidirectional edges** defined in the `edges` section.
- **Pathway_3** is marked `is_obstacle_prone: true` — it's the likely candidate for dynamic blocking.
- **FW** (`is_food_warehouse: true`) is the start/recharge point for all robots.

## Integration with the Domain Event

The `PlanRoute` domain event (`src/events/plan_route.py`) orchestrates the full workflow:

1. Loads robots, orders, and the campus graph from their respective services.
2. Assigns orders to robots via round-robin.
3. Calls `route_planner.find_path(start, goal, loc_map, edges, obstacles)` for each order.
4. Calls `route_planner.detect_and_replan(path, goal, loc_map, edges, obstacles)` to simulate obstacle handling.
5. Updates robot energy via `robot.consume_energy(distance)` and persists state.

The planner itself has no knowledge of robots, orders, or services — it operates purely on graph primitives, keeping the infrastructure concern cleanly separated from domain orchestration.

## Related Components

- **Location** (`src/domain/location.py`) — Provides `distance_to` (Manhattan heuristic) used by the planner.
- **LocationAggregate** (`src/mappers/location.py`) — The concrete node type consumed by `find_path` and `detect_and_replan`.
- **Robot** (`src/domain/robot.py`) — Consumes route distances via `consume_energy` for battery simulation.
- **RoutePlannerService** (`src/interfaces/route_planner.py`) — Abstract interface satisfied by this utility.
- **PlanRoute** (`src/events/plan_route.py`) — Domain event that orchestrates multi-robot route planning.
- **LocationYamlRepository** (`src/repos/location.py`) — Loads the campus graph from `campus.yml`.
