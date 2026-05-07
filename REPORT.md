# FOODIE — Food Intelligence Electrified

**Course:** ECE 479/579 — Fundamentals of AI, Spring 2026
**Author:** Alex Shatz
**Date:** May 8, 2026

---

## 1. Introduction

FOODIE (Food Intelligence Electrified) is an AI expert system that manages a network of autonomous food-delivery robots on a university campus. The system is built in Python using the Tiferet framework — a Domain-Driven Design (DDD) framework — and demonstrates three core AI techniques:

- **A\* Search** for optimal route planning with dynamic obstacle replanning (Goal A).
- **Forward Chaining** for rule-based order bagging (Goal B — FOODIE_BAGGER).
- **Backward Chaining** for inference-driven beverage selection (Goal C — FOODIE_SPA).

The system also includes STRIPS-based planning rules for robotic arm loading (Goal D, design only).

---

## 2. Assumptions

### Instructor's Assumptions (Adopted)

1. The locale is a known, bounded campus terrain with pathways. Robots may encounter obstacles not known a priori.
2. A finite fleet of robots, each with compartments, a robotic arm for bagging and loading, and onboard intelligence.
3. Robots depart from and return to a Food Warehouse (FW) where they park, recharge, receive orders, bag items, and load compartments.
4. Robots may deliver multiple orders to multiple locations before returning.

### Additional Assumptions (Our Refinements)

1. **Campus graph:** The campus is modeled as a weighted undirected graph with 10 nodes (FW, 6 pathways, 2 buildings, 1 dorm) and bidirectional edges defined in `campus.yml`. Coordinates are integer grid positions.
2. **Fleet size:** 3 robots (R1, R2, R3), each starting at FW with 100% battery.
3. **Energy model:** Battery consumption is proportional to Manhattan distance traveled (0.12% per unit distance). Robots recharge to 100% at FW.
4. **Bag capacity:** Paper bags hold up to 10 items. Freezer bags are dedicated to frozen items. Fragile items always start a new bag and no additional items are added after them.
5. **Order types:** Orders are either `item` (food, processed by FOODIE_BAGGER) or `beverage` (processed by FOODIE_SPA). A robot carries only one type at a time.
6. **Beverage knowledge base:** 3 beverages in `menu.yml` (Carrot Juice, Corona Beer, Sparkling Water) and a 15-rule backward-chaining rule base.
7. **Obstacle detection:** Simulated at the midpoint of any path longer than 3 nodes. The blocked edge is added in both directions and the planner re-routes from the obstacle point.
8. **Round-robin dispatch:** When multiple orders are pending, robots are assigned via round-robin for concurrent delivery.
9. **SQLite persistence:** Orders and robots are persisted in `foodie.db`; menu items, beverages, and campus data are read from YAML files.

---

## 3. Requirements Summary

| Goal | Requirement | AI Technique | Implemented? |
|------|-------------|--------------|--------------|
| A | Optimize delivery routes, minimize time and energy, handle obstacles | A* Search | Yes |
| B | Rule-based bagging: large → medium → small, frozen/fragile rules | Forward Chaining | Yes |
| C | Beverage selection for unexpected guests via hypothesis testing | Backward Chaining | Yes |
| D | Robotic arm loading of bags into compartments | STRIPS Planning | Design only |

Both FOODIE_BAGGER (B) and FOODIE_SPA (C) are fully implemented with rule bases and simulation traces.

---

## 4. System Architecture

### 4.1 High-Level Design

FOODIE is built on the Tiferet framework, which enforces a layered Domain-Driven Design architecture:

```
foodie.py              # Demo script — runs all 3 goals end-to-end
foodie_cli.py          # CLI entry point (argparse-based)
config.yml             # Unified configuration (interfaces, services, features, errors)
menu.yml               # Item catalog + beverage knowledge base
campus.yml             # Campus terrain: 10 locations + edge graph
src/
├── domain/            # Pydantic v2 domain models
│   ├── item.py        # Item (name, size, frozen, fragile, quantity)
│   ├── bag.py         # Bag (paper/freezer/beverage, capacity rules)
│   ├── order.py       # Order (items, destination, status, order_type)
│   ├── location.py    # Location (x, y, Manhattan distance heuristic)
│   ├── robot.py       # Robot (battery, compartments, energy model)
│   └── beverage.py    # Beverage (type, brand, health/allergy matching)
├── events/            # Domain events — orchestrate business logic
│   ├── migrate.py     # SeedDatabase (robots only)
│   ├── robot.py       # BagOrder, PlanRoute, DeliverOrder, ReturnToWarehouse, ChargeRobot, DispatchFleet
│   └── order.py       # PlaceItemOrder, PlaceBeverageOrder, SelectBeverage
├── interfaces/        # Service ABCs (contracts)
│   ├── item.py        # ItemService
│   ├── order.py       # OrderService
│   ├── robot.py       # RobotService
│   ├── location.py    # LocationService
│   ├── beverage.py    # BeverageService
│   ├── bagging.py     # BaggingService
│   ├── route_planner.py  # RoutePlannerService
│   └── beverage_select.py # BeverageSelectService
├── mappers/           # Aggregates + TransferObjects
├── repos/             # YAML-backed and SQLite-backed repositories
├── utils/             # Computational utilities (AI algorithms)
│   ├── route_planner.py        # AStarRoutePlanner
│   ├── bagger.py               # ForwardChainBagger
│   └── backward_chain_selector.py # BackwardChainSelector
└── assets/
    └── beverage.py    # BEVERAGE_RULES (15 rules) + FALLBACK_BEVERAGE
```

### 4.2 Configuration-Driven Design

All services, features, and error handling are declared in a single `config.yml`. The Tiferet framework uses this configuration to:

- **Dependency Injection:** Resolve domain events with their required services at runtime.
- **Feature Workflows:** Map user-facing operations (e.g., `robot.bag_order`) to domain event chains.
- **Error Handling:** Define structured error codes with multilingual messages.

### 4.3 Data Flow

1. `App()` loads `config.yml` and initializes the DI container.
2. `app.run(interface_id, feature_id, data={})` dispatches to the appropriate domain event.
3. Domain events receive injected services (repositories, utilities) and perform domain logic.
4. Results are persisted to SQLite (orders, robots) or returned as summary dicts.

---

## 5. Algorithms and Methods

### 5.1 Goal A — A\* Search Route Optimization

**File:** `src/utils/route_planner.py` — `AStarRoutePlanner`

#### Algorithm

A\* search is used to find the shortest path on the campus graph. It combines:

- **g(n):** Actual cost from start to node n (cumulative Manhattan distance along edges).
- **h(n):** Heuristic estimate from node n to the goal (Manhattan distance: |x₁−x₂| + |y₁−y₂|).
- **f(n) = g(n) + h(n):** Total estimated cost.

The Manhattan distance heuristic is **admissible** (never overestimates) and **consistent** for a grid-like campus layout, guaranteeing optimal paths.

#### Implementation Details

- **Graph representation:** Adjacency list from `campus.yml` with 10 nodes and bidirectional edges.
- **Priority queue:** Python `heapq` min-heap on f-score.
- **Edge cost:** Manhattan distance between connected locations.
- **Obstacle handling:** A set of blocked edge tuples `(from, to)` is maintained. Blocked edges are skipped during neighbor expansion.

#### Obstacle Detection and Replanning

The `detect_and_replan()` method simulates encountering an obstacle mid-route:

1. If the path has more than 3 nodes, an obstacle is injected at the midpoint edge.
2. The edge is blocked in both directions.
3. A\* re-searches from the obstacle point to the goal.
4. The new tail is spliced onto the original prefix, and total distance is recomputed.

This demonstrates the system's ability to handle unknown obstacles dynamically, as required by the project specification.

#### Energy Optimization

Each robot tracks battery level. Energy consumption is proportional to distance traveled (0.12% per unit). The system checks for low battery (≤20%) and returns the robot to FW for recharging before the next dispatch.

#### Fleet Dispatch

The `DispatchFleet` event assigns pending orders to robots via round-robin and plans individual A\* routes for each. Multiple robots operate concurrently, each with independent path planning and obstacle handling.

### 5.2 Goal B — FOODIE_BAGGER (Forward Chaining)

**File:** `src/utils/bagger.py` — `ForwardChainBagger`

#### Production System Design

FOODIE_BAGGER is a forward-chaining production system that decides how to bag each item in an order. The working memory contains the list of items (expanded by quantity) and the current bag state. Rules fire in priority order based on item attributes.

#### Rule Base

The rules fire in this priority sequence:

| Rule | Condition | Action |
|------|-----------|--------|
| R-Phase | Item size changes (large→medium→small) | Announce new bagging phase |
| R-Frozen | Item is frozen | Create a new freezer bag; place item |
| R-Fragile | Item is fragile | Start a new paper bag; place item; force new bag after |
| R-NewBag | No current bag OR current bag is full (≥10 items) | Start a new paper bag |
| R-Add | Current bag has capacity and item is not special | Add item to current bag |

#### Key Bagging Rules in Detail

1. **Size-priority sorting:** Items are sorted large → medium → small before processing. This ensures heavy/large items are bagged first (bottom of bags), matching real-world bagging practice.

2. **Frozen items:** Always placed in a dedicated freezer bag. Each frozen item gets its own freezer bag to maintain temperature isolation.

3. **Fragile items:** Always start a new bag. No additional items are placed after a fragile item in the same bag, preventing crushing. This satisfies the project requirement that "fragile items do not get crushed in a bag."

4. **Capacity limit:** Paper bags hold a maximum of 10 items. When full, a new bag is started.

5. **Trace output:** Every rule firing produces a trace line (e.g., `Rule R3 says: Put 1-gallon water bottle in bag_1.`), matching the project specification format.

#### Sample Trace

For the demo order (2× 1-gallon water bottle, 1× pint ice cream, 1× granola box, 1× loaf of bread):

```
Rule R1 says:   Bag large items.
Rule R2 says:   Put 1-gallon water bottle in bag_1.
Rule R3 says:   Put 1-gallon water bottle in bag_1.
Rule R4 says:   Bag medium items.
Rule R5 says:   Put pint ice cream in a freezer bag.
Rule R6 says:   Start a new bag (fragile item).
Rule R7 says:   Put granola box in bag_3.
Rule R8 says:   Put loaf of bread in bag_4.
```

### 5.3 Goal C — FOODIE_SPA (Backward Chaining)

**File:** `src/utils/backward_chain_selector.py` — `BackwardChainSelector`
**Rule Base:** `src/assets/beverage.py` — `BEVERAGE_RULES`

#### Backward Chaining Design

FOODIE_SPA uses a goal-driven backward-chaining inference engine. Given a hypothesis (e.g., "shall I serve Carrot Juice?"), the engine chains backward through the rule base, checking conditions against known guest facts and recursing into sub-goals as needed.

#### Rule Base (15 Rules)

**Level 1 — Category Rules (establish intermediate conclusions):**

| ID | Conclusion | Conditions |
|----|-----------|------------|
| R1 | LIQUOR is indicated | occasion=celebration, guest_age=adult |
| R3 | BEER is indicated | occasion=casual, guest_age=adult |
| R6 | WINE is indicated | entree=steak, guest_age=adult |
| R7 | WINE is indicated | entree=chicken, guest_age=adult |
| R8 | JUICE is indicated | health_nut=True |
| R11 | WATER is indicated | guest_age=minor |

**Level 2 — Selection Rules (establish CHOOSE conclusions):**

| ID | Conclusion | Conditions |
|----|-----------|------------|
| R2 | CHOOSE Polish Vodka | LIQUOR is indicated, formality=formal |
| R4 | CHOOSE Dos Equis | BEER is indicated |
| R5 | CHOOSE Corona Beer | BEER is indicated, setting=outdoor |
| R9 | CHOOSE Carrot Juice | JUICE is indicated, allergies_citrus=True |
| R10 | CHOOSE Orange Juice | JUICE is indicated, allergies_citrus=False |
| R12 | CHOOSE Sparkling Water | WATER is indicated, formality=formal |
| R13 | CHOOSE Cheap Beer | guest_liked=False, guest_age=adult |
| R14 | CHOOSE Champagne | occasion=new_years_eve, guest_age=adult |
| R15 | CHOOSE Sparkling Water | (universal fallback — no conditions) |

#### Inference Engine Operation

1. Each candidate beverage from the knowledge base is tested as a hypothesis.
2. For each candidate, the engine finds rules whose conclusion matches `CHOOSE <beverage_name>`.
3. For each matching rule, all conditions are checked:
   - If a condition references an intermediate conclusion (e.g., `JUICE is indicated`), the engine **recurses** to establish that sub-goal.
   - If a condition is a simple fact, it is checked against the known guest facts.
4. The first candidate whose CHOOSE conclusion can be fully established is selected.
5. If no rule fires for any candidate, the system falls back to Sparkling Water.

#### Sample Trace

**Scenario:** Health-conscious guest with citrus allergy.
**Facts:** `{health_nut: True, allergies_citrus: True, guest_age: adult}`

```
FOODIE_SPA backward-chaining inference started...
Known facts: {'health_nut': True, 'allergies_citrus': True, 'guest_age': 'adult'}

Trying to establish CHOOSE Carrot Juice using rules...
Trying to establish CHOOSE Carrot Juice using rule R9
  Trying to establish JUICE is indicated using rule R8
    Fact "health_nut" = True. OK.
  Rule R8 establishes JUICE is indicated.
  Fact "allergies_citrus" = True. OK.
Rule R9 establishes CHOOSE Carrot Juice.

CHOOSE Carrot Juice is True.
Selected Carrot Juice (FreshRoots) [juice] (health-friendly, avoids:citrus)
Backward chaining successful -> beverage selected.
```

---

## 6. Goal D — STRIPS Rules for Robotic Arm Loading

### 6.1 Overview

This section describes how a robot's robotic arm would load bags into its compartment using STRIPS-style planning operators. This component is designed but not encoded.

### 6.2 State Representation

```
Predicates:
  at(bag, location)         — bag is at a given location (belt, arm, compartment)
  empty(arm)                — robotic arm is free
  compartment_open(robot)   — robot compartment is open and has space
  loaded(bag, robot)        — bag has been loaded into robot
  on_belt(bag)              — bag is on the packing belt (ready for pickup)
  order_complete(order)     — all bags for the order are loaded
  is_frozen(bag)            — bag contains frozen items (must be loaded first)
  is_fragile(bag)           — bag contains fragile items (must be loaded last/on top)
```

### 6.3 STRIPS Operators

#### Operator: PICK_UP_BAG

```
PICK_UP_BAG(bag)
  Preconditions:
    on_belt(bag)
    empty(arm)
  Add List:
    at(bag, arm)
  Delete List:
    on_belt(bag)
    empty(arm)
```

#### Operator: LOAD_BAG

```
LOAD_BAG(bag, robot)
  Preconditions:
    at(bag, arm)
    compartment_open(robot)
  Add List:
    loaded(bag, robot)
    empty(arm)
  Delete List:
    at(bag, arm)
```

#### Operator: OPEN_COMPARTMENT

```
OPEN_COMPARTMENT(robot)
  Preconditions:
    ¬compartment_open(robot)
  Add List:
    compartment_open(robot)
  Delete List:
    (none)
```

#### Operator: CLOSE_COMPARTMENT

```
CLOSE_COMPARTMENT(robot)
  Preconditions:
    compartment_open(robot)
  Add List:
    (none)
  Delete List:
    compartment_open(robot)
```

#### Operator: MARK_ORDER_COMPLETE

```
MARK_ORDER_COMPLETE(order, robot)
  Preconditions:
    ∀ bag ∈ order.bags: loaded(bag, robot)
  Add List:
    order_complete(order)
  Delete List:
    (none)
```

### 6.4 Loading Sequence for a Typical Order

**Initial state:** 4 bags on the belt (bag_1: large items, freezer_bag_2: ice cream, bag_3: granola box, bag_4: bread), arm empty, compartment closed.

**Plan:**

1. `OPEN_COMPARTMENT(R1)`
2. `PICK_UP_BAG(freezer_bag_2)` — frozen items loaded first (bottom)
3. `LOAD_BAG(freezer_bag_2, R1)`
4. `PICK_UP_BAG(bag_1)` — large items next
5. `LOAD_BAG(bag_1, R1)`
6. `PICK_UP_BAG(bag_4)` — bread (non-fragile medium)
7. `LOAD_BAG(bag_4, R1)`
8. `PICK_UP_BAG(bag_3)` — fragile granola box last (on top, not crushed)
9. `LOAD_BAG(bag_3, R1)`
10. `CLOSE_COMPARTMENT(R1)`
11. `MARK_ORDER_COMPLETE(ORD-101, R1)`

### 6.5 Handling Last-Minute Changes (Unexpected Guests)

When guests arrive unexpectedly and a beverage must be added to an existing order:

#### Operator: REOPEN_COMPARTMENT

```
REOPEN_COMPARTMENT(robot)
  Preconditions:
    ¬compartment_open(robot)
    ¬at(robot, en_route)      — robot must still be at FW
  Add List:
    compartment_open(robot)
  Delete List:
    order_complete(order)     — order is no longer complete
```

#### Operator: LOAD_BEVERAGE_BAG

```
LOAD_BEVERAGE_BAG(bev_bag, robot)
  Preconditions:
    at(bev_bag, arm)
    compartment_open(robot)
  Add List:
    loaded(bev_bag, robot)
    empty(arm)
  Delete List:
    at(bev_bag, arm)
```

**Modified plan for last-minute beverage addition:**

1. `REOPEN_COMPARTMENT(R1)` — reopens, invalidates order_complete
2. `PICK_UP_BAG(bev_bag_ORD-101)` — beverage bag from FOODIE_SPA
3. `LOAD_BEVERAGE_BAG(bev_bag_ORD-101, R1)` — load on top (accessible first)
4. `CLOSE_COMPARTMENT(R1)`
5. `MARK_ORDER_COMPLETE(ORD-101, R1)`

---

## 7. Campus Terrain Graph

The campus is modeled in `campus.yml` with 10 locations:

```
Node             Coordinates    Notes
─────────────    ───────────    ──────────────────────────
FW               (0, 0)         Food Warehouse (start/end)
Pathway_1        (1, 2)
Pathway_2        (3, 2)
Pathway_3        (3, 5)         Obstacle-prone
Pathway_4        (5, 5)
Pathway_5        (6, 1)
Pathway_6        (1, 5)
Building_A       (5, 8)         Delivery destination
Building_B       (6, 3)         Delivery destination
Dorm_1           (0, 5)         Delivery destination
```

Edges (bidirectional):

```
FW ↔ Pathway_1, Pathway_6
Pathway_1 ↔ Pathway_2, Pathway_6
Pathway_2 ↔ Pathway_3, Pathway_5
Pathway_3 ↔ Pathway_4, Pathway_6
Pathway_4 ↔ Building_A, Pathway_5
Pathway_5 ↔ Building_B
Pathway_6 ↔ Dorm_1
```

---

## 8. Use of AI Tools

### Tools Used

- **Warp AI (Oz Agent):** Used extensively for iterative design collaboration, code generation, code review, testing, and documentation within the Warp terminal IDE.

### AI-Assisted Components

| Component | Level of AI Assistance |
|-----------|----------------------|
| System architecture and DDD layering | Collaborative design — AI proposed structure, human refined |
| Domain models (Pydantic v2) | AI-generated from specifications, human-reviewed |
| A* route planner implementation | AI-generated core algorithm, human-specified heuristic and obstacle logic |
| Forward-chaining bagger | Collaborative — human specified rules, AI implemented production system |
| Backward-chaining selector | Collaborative — human designed rule base, AI implemented inference engine |
| Rule bases (both B and C) | Human-designed rule logic, AI structured into code |
| Domain events (orchestration) | AI-generated from TRDs, human-reviewed and refined |
| Order placement events (v1.1.0) | Human identified gap, AI drafted TRD and implemented |
| Test suite (190 tests) | AI-generated with human-specified test scenarios |
| Configuration files (YAML) | Collaborative — human specified data, AI structured format |
| STRIPS rules (Goal D) | Human-designed, AI assisted with formalization |

### Iteration Process

Development followed an iterative TRD-driven workflow:

1. **Requirements definition:** Human wrote Technical Requirements Documents (TRDs) for each component, with AI helping to refine scope and acceptance criteria.
2. **Implementation:** AI generated initial code from TRDs, following Tiferet's structured code style (artifact comments, RST docstrings, Pydantic v2 patterns).
3. **Review and refinement:** Human reviewed all generated code, requested modifications, and approved final implementations.
4. **Testing:** AI generated test suites; human verified coverage and edge cases.
5. **Integration:** AI orchestrated feature integration; human validated end-to-end simulation output.

Each major component was implemented as a GitHub issue with a feature branch, pull request, and collaboration report documenting the AI ↔ human interaction.

---

## 9. Instructions to Run the System

### Prerequisites

- Python ≥ 3.10
- pip (Python package manager)

### Setup

```bash
# Clone the repository
git clone https://github.com/ashatz/ece-579-foodie-by-tiferet.git
cd ece-579-foodie-by-tiferet

# Create and activate a virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### Running the Demo

```bash
# Run the full demo (Goals A, B, and C)
python foodie.py
```

This executes all three goals sequentially:
1. Seeds the database with robots.
2. **Order Placement:** Places an item order (ORD-101) and two beverage orders (ORD-102, ORD-103).
3. **Goal B:** Bags order ORD-101 using forward chaining.
4. **Goal A:** Plans and executes A* route for R1 to Building_A, delivers, returns, recharges.
5. **Goal C:** Selects beverages for two scenarios using backward chaining.
6. **Goal A:** Routes R2 and R3 to deliver beverage orders.

### Running Individual Features via CLI

```bash
# Seed the database (robots)
python foodie_cli.py admin seed-database

# Place an item order from the menu catalog
python foodie_cli.py order new-item ORD-101 Building_A --items "loaf of bread:2" "pint ice cream:1"

# Place a beverage order
python foodie_cli.py order new-beverage ORD-102 Building_B

# Bag an order
python foodie_cli.py robot bag-order R1 ORD-101

# Plan a route
python foodie_cli.py robot plan-route R1 ORD-101

# Select a beverage
python foodie_cli.py order select-beverage R2 ORD-102 --facts health_nut=True allergies_citrus=True guest_age=adult
```

### Running Tests

```bash
# Run all tests (190 tests)
pytest src/

# Run by layer
pytest src/domain/     # Domain model tests
pytest src/mappers/    # Mapper tests
pytest src/repos/      # Repository tests
pytest src/utils/      # Utility tests (A*, bagger, backward chainer)
pytest src/events/     # Domain event tests
```

---

## Appendix A — Sample Run: Goal A (A\* Route Planning)

```
======================================================================
GOAL A — Route Planning: A* Search
======================================================================

  Planning route: Robot R1 from FW to Building_A
  Replanned route: FW -> Pathway_6 -> Pathway_3 -> Pathway_4 -> Building_A (dist: 16.0)
  Route: FW -> Pathway_6 -> Pathway_3 -> Pathway_4 -> Building_A (dist: 16.0)
  Robot R1 battery: 98.1%

  --- Delivering Order ---
  Robot R1 delivered 4 bag(s) for ORD-101 at Building_A

  --- Returning to Warehouse ---
  Robot R1 returning from Building_A to FW
  Route: Building_A -> Pathway_4 -> Pathway_3 -> Pathway_6 -> FW (dist: 16.0)
  Robot R1 returned to FW, battery: 96.2%

  --- Charging Robot ---
  Robot R1 charged: 96.2% -> 100.0%
```

## Appendix B — Sample Run: Goal B (FOODIE_BAGGER Forward Chaining)

```
======================================================================
GOAL B — FOODIE_BAGGER: Forward-Chaining Bagging
======================================================================

  Bagging Order ORD-101 -> Building_A | Items: 2x 1-gallon water bottle [large], 1x pint ice cream (frozen) [medium], 1x granola box (fragile) [medium], 1x loaf of bread [medium] (total: 5)
  Assigned to Robot R1
Rule R1 says:   Bag large items.
Rule R2 says:   Put 1-gallon water bottle in bag_1.
Rule R3 says:   Put 1-gallon water bottle in bag_1.
Rule R4 says:   Bag medium items.
Rule R5 says:   Put pint ice cream in a freezer bag.
Rule R6 says:   Start a new bag (fragile item).
Rule R7 says:   Put granola box in bag_3.
Rule R8 says:   Put loaf of bread in bag_4.

  4 bag(s) packed and loaded onto Robot R1:
    Bag bag_1 (paper) contains: 1x 1-gallon water bottle [large], 1x 1-gallon water bottle [large] (2/10)
    Bag freezer_bag_2 (freezer) contains: 1x pint ice cream (frozen) [medium] (1/10)
    Bag bag_3 (paper) contains: 1x granola box (fragile) [medium] (1/10)
    Bag bag_4 (paper) contains: 1x loaf of bread [medium] (1/10)
```

## Appendix C — Sample Run: Goal C (FOODIE_SPA Backward Chaining)

### Scenario 1: Health-Conscious Guest with Citrus Allergy

```
  --- Scenario 1: Health-Conscious Guest ---

  Selecting beverage for order ORD-102 (Robot R2)
  Guest facts: {'health_nut': True, 'allergies_citrus': True, 'guest_age': 'adult'}
FOODIE_SPA backward-chaining inference started...
Known facts: {'health_nut': True, 'allergies_citrus': True, 'guest_age': 'adult'}

Trying to establish CHOOSE Carrot Juice using rules...
Trying to establish CHOOSE Carrot Juice using rule R9
  Trying to establish JUICE is indicated using rule R8
    Fact "health_nut" = True. OK.
  Rule R8 establishes JUICE is indicated.
  Fact "allergies_citrus" = True. OK.
Rule R9 establishes CHOOSE Carrot Juice.

CHOOSE Carrot Juice is True.
Selected Carrot Juice (FreshRoots) [juice] (health-friendly, avoids:citrus)
Backward chaining successful -> beverage selected.
  Selected: Selected Carrot Juice (FreshRoots) [juice] (health-friendly, avoids:citrus)
  Beverage bag loaded onto Robot R2
```

### Scenario 2: Casual Outdoor Gathering

```
  --- Scenario 2: Casual Outdoor Gathering ---

  Selecting beverage for order ORD-103 (Robot R3)
  Guest facts: {'occasion': 'casual', 'guest_age': 'adult', 'setting': 'outdoor'}
FOODIE_SPA backward-chaining inference started...
Known facts: {'occasion': 'casual', 'guest_age': 'adult', 'setting': 'outdoor'}

Trying to establish CHOOSE Carrot Juice using rules...
Trying to establish CHOOSE Carrot Juice using rule R9
  Trying to establish JUICE is indicated using rule R8
    Fact "health_nut" unknown — assuming False.
  Rule R9 fails to establish JUICE is indicated.

Trying to establish CHOOSE Corona Beer using rules...
Trying to establish CHOOSE Corona Beer using rule R5
  Trying to establish BEER is indicated using rule R3
    Fact "occasion" = casual. OK.
    Fact "guest_age" = adult. OK.
  Rule R3 establishes BEER is indicated.
  Fact "setting" = outdoor. OK.
Rule R5 establishes CHOOSE Corona Beer.

CHOOSE Corona Beer is True.
Selected Corona Beer (Corona) [beer]
Backward chaining successful -> beverage selected.
  Selected: Selected Corona Beer (Corona) [beer]
  Beverage bag loaded onto Robot R3
```
