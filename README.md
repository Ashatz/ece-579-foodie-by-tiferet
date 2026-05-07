# FOODIE – Food Intelligence Electrified by Tiferet

**ECE 479/579 Principles of Artificial Intelligence**  
**Spring 2026 Final Project/Exam**  
**Due: May 8th, 2026 via D2L**

---

## 1. What is FOODIE?

**FOODIE** (Food Intelligence Electrified) is an AI expert system that manages a fleet of food-delivery robots on a university campus. It is built on the **Tiferet** framework (v2.0.0b1, Pydantic v2) and implements three core AI techniques from the course syllabus:

- **Production Systems & forward chaining** (Goal B)
- **State-space search, A\* heuristic search, and replanning** (Goal A)
- **Predicate logic and backward chaining** (Goal C)

## 2. Project Goals

**Goal A – Route Optimization:** Multi-robot A\* path planning on a campus graph with Manhattan-distance heuristic, energy/time minimization, dynamic obstacle detection, and replanning.

**Goal B – FOODIE_BAGGER:** Forward-chaining rule-based production system that bags food orders by size priority (large → medium → small), uses freezer bags for frozen items, prevents crushing of fragile items, and enforces per-bag capacity limits.

**Goal C – FOODIE_SPA:** Backward-chaining expert system (15-rule knowledge base) that selects the appropriate beverage for unexpected guests based on facts such as health preferences, allergies, occasion, and guest age.

## 3. Prerequisites

- Python 3.10+
- pip

## 4. Setup & Installation

```bash
# Clone the repository
git clone https://github.com/ashatz/ece-579-foodie-by-tiferet.git
cd ece-579-foodie-by-tiferet

# Create and activate a virtual environment
python3 -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate

# Install the Tiferet framework
pip install tiferet==2.0.0b1
```

## 5. Running the Simulation

A single command runs the full demo — seeding, bagging, routing, delivery, and beverage selection:

```bash
python foodie.py
```

The script uses the Tiferet `AppBuilder` to execute the complete robot lifecycle:
1. **Setup** — `admin.seed_database` pre-seeds the SQLite database.
2. **Goal B** — `robot.bag_order` bags an order onto Robot R1.
3. **Goal A** — `robot.plan_route` routes R1 to the destination, `robot.deliver_order` delivers the bags, `robot.return_to_warehouse` returns R1, and `robot.charge_robot` charges it.
4. **Goal C** — `order.select_beverage` selects beverages for two guest scenarios.
5. **Goal A** — `robot.plan_route` dispatches R2 and R3 with beverage deliveries.

### CLI Interface

FOODIE also provides a command-line interface via `foodie_cli.py`:

```bash
# Seed the database with demo data (orders + robots)
python foodie_cli.py admin seed-database

# Bag an order onto a robot (Goal B)
python foodie_cli.py robot bag-order R1 ORD-101

# Plan an A* route for a robot delivery (Goal A)
python foodie_cli.py robot plan-route R1 ORD-101

# Deliver bags at the destination
python foodie_cli.py robot deliver-order R1 ORD-101

# Return a robot to the Food Warehouse
python foodie_cli.py robot return-to-warehouse R1

# Charge a robot at the warehouse
python foodie_cli.py robot charge-robot R1

# Round-robin fleet dispatch (Goal A)
python foodie_cli.py robot dispatch-fleet

# Select a beverage (Goal C — pass facts as key=value pairs)
python foodie_cli.py order select-beverage R2 ORD-102 --facts health_nut=True allergies_citrus=True guest_age=adult
```

The CLI uses Tiferet's `CliBuilder` to parse arguments via `argparse` and dispatch to the same features defined in `config.yml`.

## 6. Expected Output

Running `python foodie.py` produces output for each phase of the simulation.

### Database Seeding
```
======================================================================
SETUP — Seeding Database
======================================================================
  Seeded order: ORD-101 -> Building_A (4 items)
  Seeded order: ORD-102 -> Building_B (0 items)
  Seeded order: ORD-103 -> Dorm_1 (0 items)
  Seeded robot: R1 at FW
  Seeded robot: R2 at FW
  Seeded robot: R3 at FW
```

### Goal B – FOODIE_BAGGER (Forward Chaining)
```
======================================================================
GOAL B — FOODIE_BAGGER: Forward-Chaining Bagging
======================================================================

  Bagging Order ORD-101 -> Building_A | Items: ... (total: 5)
  Assigned to Robot R1
  FOODIE_BAGGER forward-chaining production system started...
  Rule R1 says: ...
  ...
  Bagging complete.

  4 bag(s) packed and loaded onto Robot R1:
    Bag bag_1 (paper) contains: ... (2/10)
    Bag freezer_bag_2 (freezer) contains: ... (1/10)
    ...
```

### Goal A – Route Planning, Delivery, Return, Charge
```
======================================================================
GOAL A — Route Planning: A* Search
======================================================================

  Planning route: Robot R1 from FW to Building_A
  Replanned route: FW -> ... -> Building_A (dist: 17.0)
  Route: FW -> ... -> Building_A (dist: 17.0)
  Robot R1 battery: 96.6%

  --- Delivering Order ---
  Robot R1 delivered 4 bag(s) for ORD-101 at Building_A

  --- Returning to Warehouse ---
  Robot R1 returning from Building_A to FW
  Route: Building_A -> ... -> FW (dist: 17.0)
  Robot R1 returned to FW, battery: 93.2%

  --- Charging Robot ---
  Robot R1 charged: 93.2% -> 100.0%
```

### Goal C – FOODIE_SPA (Backward Chaining)
```
======================================================================
GOAL C — FOODIE_SPA: Backward-Chaining Beverage Selection
======================================================================

  --- Scenario 1: Health-Conscious Guest ---
  Selecting beverage for order ORD-102 (Robot R2)
  Guest facts: {'health_nut': True, 'allergies_citrus': True, 'guest_age': 'adult'}
  FOODIE_SPA backward-chaining inference started...
  ...
  Selected: Carrot Juice (FreshRoots) [juice] (health-friendly, avoids:citrus)
  Beverage bag loaded onto Robot R2

  --- Scenario 2: Casual Outdoor Gathering ---
  Selecting beverage for order ORD-103 (Robot R3)
  Guest facts: {'occasion': 'casual', 'guest_age': 'adult', 'setting': 'outdoor'}
  FOODIE_SPA backward-chaining inference started...
  ...
  Selected: Corona (Corona) [beer] (avoids:none)
  Beverage bag loaded onto Robot R3
```

## 7. Project Structure

```
foodie.py                  # Main demo script (runs full lifecycle via AppBuilder)
foodie_cli.py              # CLI entry point (CliBuilder + argparse)
config.yml                 # Unified Tiferet v2 configuration
menu.yml                   # Item & beverage data (YAML)
campus.yml                 # Campus terrain: locations + edge graph (YAML)
locations.yml              # Standalone location definitions (YAML)
README.md                  # This file
AGENTS.md                  # AI agent reference
src/
├── __init__.py            # Package exports
├── domain/                # Pydantic domain models (Tiferet DomainObject)
│   ├── item.py            # Food item (name, size, frozen, fragile, quantity)
│   ├── bag.py             # Bag (paper/freezer/beverage, capacity rules, items list)
│   ├── order.py           # Customer order (items, destination, status, order type)
│   ├── location.py        # Campus graph node (coordinates, warehouse flag)
│   ├── robot.py           # Delivery robot (battery, compartments, status)
│   └── beverage.py        # Beverage (type, brand, health/allergy attributes)
├── interfaces/            # Service interfaces (Tiferet Service ABC)
│   ├── bagging.py         # BaggingService
│   ├── beverage.py        # BeverageService
│   ├── beverage_select.py # BeverageSelectService
│   ├── item.py            # ItemService
│   ├── location.py        # LocationService (CRUD + get_edges)
│   ├── order.py           # OrderService
│   ├── robot.py           # RobotService
│   └── route_planner.py   # RoutePlannerService
├── mappers/               # Aggregates and TransferObjects
│   ├── bag.py             # BagAggregate
│   ├── beverage.py        # BeverageAggregate, BeverageYamlObject
│   ├── item.py            # ItemAggregate, ItemYamlObject
│   ├── location.py        # LocationAggregate, LocationYamlObject
│   ├── order.py           # OrderAggregate, OrderSqlObject
│   └── robot.py           # RobotAggregate, RobotSqlObject
├── repos/                 # Repository implementations
│   ├── beverage.py        # BeverageYamlRepository
│   ├── item.py            # ItemYamlRepository
│   ├── location.py        # LocationYamlRepository (YAML-backed)
│   ├── order.py           # OrderSqliteRepository (SQLite-backed)
│   ├── robot.py           # RobotSqliteRepository (SQLite-backed)
│   └── tests/             # Repository unit tests
├── utils/                 # Infrastructure utilities
│   ├── backward_chain_selector.py  # BackwardChainSelector (Goal C)
│   ├── bagger.py          # ForwardChainBagger (Goal B)
│   └── route_planner.py   # AStarRoutePlanner (Goal A)
├── events/                # Domain events (Tiferet DomainEvent) — 8 events
│   ├── migrate.py         # SeedDatabase (database seeding)
│   ├── robot.py           # BagOrder, PlanRoute, DeliverOrder, ReturnToWarehouse, ChargeRobot, DispatchFleet
│   └── order.py           # SelectBeverage (backward-chaining inference)
└── assets/                # Constants and rule bases
    └── beverage.py        # BEVERAGE_RULES (15 rules), FALLBACK_BEVERAGE
```

## 8. Architecture

FOODIE follows the **Tiferet** framework's Domain-Driven Design architecture:

- **Configuration** (`config.yml`) – Unified Tiferet v2 configuration defining interfaces, DI services, features, CLI commands, and errors. The `AppBuilder` and `CliBuilder` load this file to bootstrap the application.
- **Domain Models** (`src/domain/`) – Pydantic v2 models extending `DomainObject`. Each model uses `Field(...)` for validation, `Literal` for constrained choices, and `List[T]` for nested collections.
- **Domain Events** (`src/events/`) – 8 operation classes extending `DomainEvent` across 3 modules. Each event receives dependencies via constructor injection and exposes an `execute(**kwargs)` method. Events are resolved from `config.yml` services via Tiferet's DI container. The robot module (`robot.py`) contains 6 events modeling the complete delivery lifecycle: bag → route → deliver → return → charge, plus fleet dispatch. The order module (`order.py`) handles beverage selection via backward chaining. The migrate module (`migrate.py`) provides idempotent database seeding.
- **Assets** (`src/assets/`) – Hard-coded constants and rule bases. `beverage.py` provides the 15-rule backward-chaining knowledge base (`BEVERAGE_RULES`) and fallback beverage data (`FALLBACK_BEVERAGE`).
- **Service Interfaces** (`src/interfaces/`) – Abstract service contracts extending `Service`. Eight interfaces: 5 data-access contracts (`ItemService`, `BeverageService`, `LocationService`, `OrderService`, `RobotService`) defining CRUD operations for domain persistence, plus 3 utility-associated contracts (`BaggingService`, `RoutePlannerService`, `BeverageSelectService`) defining computational APIs.
- **Mappers** (`src/mappers/`) – Aggregates provide validated mutation methods (e.g., `update_status`, `update_battery`); TransferObjects provide role-based serialization for persistence. Three patterns exist: flat YAML-backed mappers (`ItemYamlObject`, `LocationYamlObject`, `BeverageYamlObject`), an aggregate-only mapper (`BagAggregate` with static factories), and SQL-backed mappers with custom JSON serialization (`OrderSqlObject` with one JSON column, `RobotSqlObject` with two).
- **Repositories** (`src/repos/`) – Concrete service implementations with two persistence backends. YAML-backed: `ItemYamlRepository`, `BeverageYamlRepository`, `LocationYamlRepository` for universal/config data (`menu.yml`, `campus.yml`). SQLite-backed: `OrderSqliteRepository`, `RobotSqliteRepository` for instance-specific runtime data (`foodie.db`).
- **Utilities** (`src/utils/`) – Concrete computational infrastructure: `AStarRoutePlanner`, `ForwardChainBagger`, `BackwardChainSelector`. Each implements a service interface and is injected via DI.
- **Data** – `menu.yml` (item catalog + beverage knowledge base), `campus.yml` (campus terrain graph with locations and edges).

### AI Techniques Implemented

- **A\* Search** (`plan_route.py`): Uses `heapq` priority queue, Manhattan distance heuristic, and adjacency-list graph representation. Supports dynamic obstacle detection and mid-route replanning.
- **Forward Chaining** (`bag_order.py`): Production system with size-priority ordering, frozen/fragile/capacity rules, and sequential rule-firing trace output.
- **Backward Chaining** (`select_beverage.py`): 15-rule knowledge base with recursive goal decomposition. Rules chain from specific beverages through intermediate conclusions (e.g., "JUICE is indicated") back to guest facts.

## 9. Customizing the Simulation

### Modifying items or beverages
Edit `menu.yml` to add/remove items or beverages. The format is:

```yaml
items:
  "item name":
    name: "item name"
    size: "large"    # large, medium, or small
    is_frozen: false
    is_fragile: false
    quantity: 1

beverages:
  "beverage name":
    name: "beverage name"
    beverage_type: "juice"  # water, juice, wine, beer, or liquor
    brand: "Brand Name"
    is_health_friendly: true
    avoids_allergens: "citrus, gluten"
```

### Modifying the campus graph
Edit `campus.yml` to add, remove, or modify locations and edges. The format is:

```yaml
locations:
  "LocationName":
    name: "LocationName"
    x: 0.0               # X coordinate (used by A* heuristic)
    y: 0.0               # Y coordinate (used by A* heuristic)
    is_food_warehouse: false
    is_obstacle_prone: false

edges:
  "LocationName": ["Neighbor1", "Neighbor2"]
```

The `locations` section defines graph nodes with coordinates for the Manhattan distance heuristic. The `edges` section defines the bidirectional adjacency list — each location must list its neighbors, and the reverse edge should also be present. A standalone `locations.yml` is also provided for location-only definitions without the edge graph.

### Modifying guest scenarios
Edit the `facts` dictionaries in the Goal C section of `foodie.py`. Available fact keys include: `health_nut`, `allergies_citrus`, `guest_age` (adult/minor), `occasion` (casual/celebration/new_years_eve), `setting` (outdoor), `formality` (formal), `entree` (steak/chicken), `guest_liked`.

## 10. Documentation

Guide documents for each layer of the FOODIE codebase are available in `docs/guides/`.

### Domain Model Guides

- [Item](docs/guides/domain/item.md) — Food item (size, frozen, fragile, quantity)
- [Bag](docs/guides/domain/bag.md) — Paper/freezer bag with capacity and crush rules
- [Order](docs/guides/domain/order.md) — Customer order (items, destination, lifecycle status)
- [Location](docs/guides/domain/location.md) — Campus graph node (coordinates, A* heuristic)
- [Robot](docs/guides/domain/robot.md) — Delivery robot (battery, compartments, status)
- [Beverage](docs/guides/domain/beverage.md) — Beverage recommendation (backward chaining)

### Data-Access Interface Guides

- [ItemService](docs/guides/interfaces/item.md) — CRUD contract for menu catalog items (YAML-backed)
- [BeverageService](docs/guides/interfaces/beverage.md) — CRUD contract for beverage knowledge base (YAML-backed)
- [LocationService](docs/guides/interfaces/location.md) — CRUD + `get_edges()` contract for campus terrain (YAML-backed)
- [OrderService](docs/guides/interfaces/order.md) — CRUD contract for runtime orders (SQLite-backed)
- [RobotService](docs/guides/interfaces/robot.md) — CRUD contract for fleet state (SQLite-backed)

### Utility Interface Guides

- [BaggingService](docs/guides/interfaces/bagging.md) — Forward-chaining bagging contract (Goal B)
- [RoutePlannerService](docs/guides/interfaces/route_planner.md) — A* route planning and replanning contract (Goal A)
- [BeverageSelectService](docs/guides/interfaces/beverage_select.md) — Backward-chaining beverage selection contract (Goal C)

### Repository Guides

- [ItemYamlRepository](docs/guides/repos/item.md) — YAML-backed item persistence (`menu.yml`, `items` section)
- [BeverageYamlRepository](docs/guides/repos/beverage.md) — YAML-backed beverage persistence (`menu.yml`, `beverages` section)
- [LocationYamlRepository](docs/guides/repos/location.md) — YAML-backed location persistence (`campus.yml`, `locations` + `edges` sections)
- [OrderSqliteRepository](docs/guides/repos/order.md) — SQLite-backed order persistence (JSON items column)
- [RobotSqliteRepository](docs/guides/repos/robot.md) — SQLite-backed robot persistence (dual JSON columns)

### Utility Guides

- [AStarRoutePlanner](docs/guides/utils/route_planner.md) — A* search algorithm, Manhattan heuristic, obstacle replanning (Goal A)
- [ForwardChainBagger](docs/guides/utils/bagger.md) — Forward-chaining production system, rule priority, bagging logic (Goal B)
- [BackwardChainSelector](docs/guides/utils/backward_chain_selector.md) — Backward-chaining inference engine, 15-rule knowledge base (Goal C)

### Mapper Guides

- [Item Mappers](docs/guides/mappers/item.md) — ItemAggregate and ItemYamlObject (flat YAML serialization)
- [Location Mappers](docs/guides/mappers/location.md) — LocationAggregate and LocationYamlObject (flat YAML serialization)
- [Beverage Mappers](docs/guides/mappers/beverage.md) — BeverageAggregate and BeverageYamlObject (flat YAML serialization)
- [Bag Mapper](docs/guides/mappers/bag.md) — BagAggregate (aggregate-only, static factories)
- [Order Mappers](docs/guides/mappers/order.md) — OrderAggregate and OrderSqlObject (nested JSON serialization)
- [Robot Mappers](docs/guides/mappers/robot.md) — RobotAggregate and RobotSqlObject (dual nested JSON serialization)

### Domain Event Guides

- [SeedDatabase](docs/guides/events/seed_database.md) — Idempotent database seeding with demo orders and robots
- [BagOrder](docs/guides/events/bag_order.md) — Order loading, item expansion, and forward-chaining delegation (Goal B)
- [PlanRoute](docs/guides/events/plan_route.md) — Fleet orchestration, round-robin assignment, and A* delegation (Goal A)
- [SelectBeverage](docs/guides/events/select_beverage.md) — Fact parsing, backward-chaining delegation, and fallback logic (Goal C)

## 11. Running Tests

The full test suite covers all layers: domain models, mappers, repositories, utilities, and domain events (186 tests total).

```bash
# Activate virtual environment
source .venv/bin/activate

# Run all tests (186 tests)
pytest src/

# Run tests by layer
pytest src/domain/       # Domain model tests
pytest src/mappers/      # Mapper tests
pytest src/repos/        # Repository tests
pytest src/utils/        # Utility tests
pytest src/events/       # Domain event tests

# Run a specific test file
pytest src/repos/tests/test_item.py
pytest src/events/tests/test_robot.py
```

## 12. Submission Files

1. **Project Report** – includes architecture, algorithms, rule bases, STRIPS rules, and sample runs
2. **Code** – this repository
3. **Instructions** – this README (Section 4–5)

---

**Developed by:** Andrew Shatz

**AI Tools Used:**
- Grok (xAI) – Initial scaffolding and domain modeling
- Oz (Warp) – Framework upgrade to tiferet 2.0.0b1, Pydantic v2 rewrite, A\* implementation, backward-chaining engine, and full system integration
