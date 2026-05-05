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

A single command runs all three goals with sample data:

```bash
python foodie.py
```

The script uses the Tiferet `AppBuilder` to first seed the SQLite database (`admin.seed_database`), then execute each goal as a configured feature (`admin.bag_order`, `admin.plan_route`, `admin.select_beverage`).

### CLI Interface

FOODIE also provides a command-line interface via `foodie_cli.py`:

```bash
# Seed the database with demo data (orders + robots)
python foodie_cli.py admin seed-database

# Bag an order
python foodie_cli.py admin bag-order ORD-101

# Plan delivery routes
python foodie_cli.py admin plan-route

# Select a beverage (pass facts as key=value pairs)
python foodie_cli.py admin select-beverage health_nut=True allergies_citrus=True guest_age=adult
```

The CLI uses Tiferet's `CliBuilder` to parse arguments via `argparse` and dispatch to the same features defined in `config.yml`.

## 6. Expected Output

### Database Seeding
```
SeedDatabase: Pre-seeding SQLite database with demo data...

  Seeded order ORD-101 -> Building_A (4 items)
  Seeded order ORD-102 -> Building_B (0 items)
  Seeded order ORD-103 -> Dorm_1 (0 items)

  Seeded robot R1 at FW
  Seeded robot R2 at FW
  Seeded robot R3 at FW

SeedDatabase complete: 3 orders, 3 robots.
```

### Goal B – FOODIE_BAGGER
```
FOODIE_BAGGER forward-chaining production system started...
Rule R1 says:   Bag large items.
Rule R2 says:   Put 1-gallon water bottle in bag_1.
Rule R3 says:   Put 1-gallon water bottle in bag_1.
Rule R4 says:   Bag medium items.
Rule R5 says:   Put pint ice cream in a freezer bag.
Rule R6 says:   Start a new bag (fragile item).
Rule R7 says:   Put granola box in bag_3.
Rule R8 says:   Put loaf of bread in bag_4.

Bagging complete.
  Bag bag_1 (paper) contains: 1x 1-gallon water bottle, 1x 1-gallon water bottle (2/10)
  Bag freezer_bag_2 (freezer) contains: 1x pint ice cream (1/10)
  Bag bag_3 (paper) contains: 1x granola box (1/10)
  Bag bag_4 (paper) contains: 1x loaf of bread (1/10)
```

### Goal A – Route Optimization
```
RoutePlannerContext: A* search + multi-robot replanning started...
Fleet: 3 robots | Orders: 3 | Locations: 10

--- Order ORD-101: FW -> Building_A (Robot R1) ---
  Path: FW -> Pathway_1 -> Pathway_2 -> Pathway_3 -> Pathway_6 -> Building_A (distance: 13.0)
  Obstacle detected on Pathway_3 -> Pathway_6! Replanning with A*...
  New path found (heuristic h(n) = Manhattan + obstacle penalty).
  Replanned: FW -> Pathway_1 -> Pathway_2 -> ... -> Building_A (distance: 17.0)

=== Current Fleet Status ===
  Robot R1 | Loc: FW (Food Warehouse) @ (0.0, 0.0) | Battery: 98.0% | Status: en_route
  Robot R2 | Loc: FW (Food Warehouse) @ (0.0, 0.0) | Battery: 98.2% | Status: en_route
  Robot R3 | Loc: FW (Food Warehouse) @ (0.0, 0.0) | Battery: 99.4% | Status: en_route
```

### Goal C – FOODIE_SPA
```
FOODIE_SPA backward-chaining inference started...
Known facts: {'health_nut': True, 'allergies_citrus': True, 'guest_age': 'adult'}

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

## 7. Project Structure

```
foodie.py                  # Main demo script (runs all 3 goals via AppBuilder)
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
│   ├── bag.py             # Bag (paper/freezer, capacity rules, items list)
│   ├── order.py           # Customer order (items, destination, status)
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
└── events/                # Domain events (Tiferet DomainEvent)
    ├── seed_database.py   # Pre-seed SQLite with demo orders and robots
    ├── bag_order.py       # Goal B: forward-chaining FOODIE_BAGGER
    ├── plan_route.py      # Goal A: A* route planning with replanning
    └── select_beverage.py # Goal C: backward-chaining FOODIE_SPA
```

## 8. Architecture

FOODIE follows the **Tiferet** framework's Domain-Driven Design architecture:

- **Configuration** (`config.yml`) – Unified Tiferet v2 configuration defining interfaces, DI services, features, CLI commands, and errors. The `AppBuilder` and `CliBuilder` load this file to bootstrap the application.
- **Domain Models** (`src/domain/`) – Pydantic v2 models extending `DomainObject`. Each model uses `Field(...)` for validation, `Literal` for constrained choices, and `List[T]` for nested collections.
- **Domain Events** (`src/events/`) – Operation classes extending `DomainEvent`. Each event receives dependencies via constructor injection and exposes an `execute(**kwargs)` method. Events are resolved from `config.yml` services via Tiferet's DI container. The `SeedDatabase` event pre-seeds the SQLite database with demo orders and robots before the simulation begins.
- **Service Interfaces** (`src/interfaces/`) – Abstract service contracts extending `Service`. Define the expected data-access and computational APIs for each domain.
- **Mappers** (`src/mappers/`) – Aggregates (mutation) and TransferObjects (serialization). `LocationYamlObject` handles YAML ↔ domain mapping; `OrderSqlObject`/`RobotSqlObject` handle SQLite ↔ domain mapping.
- **Repositories** (`src/repos/`) – Concrete service implementations. `LocationYamlRepository` persists to YAML; `OrderSqliteRepository`/`RobotSqliteRepository` persist to SQLite.
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

### Utility Guides

- [AStarRoutePlanner](docs/guides/utils/route_planner.md) — A* search algorithm, Manhattan heuristic, obstacle replanning (Goal A)
- [ForwardChainBagger](docs/guides/utils/bagger.md) — Forward-chaining production system, rule priority, bagging logic (Goal B)
- [BackwardChainSelector](docs/guides/utils/backward_chain_selector.md) — Backward-chaining inference engine, 15-rule knowledge base (Goal C)

## 11. Submission Files

1. **Project Report** – includes architecture, algorithms, rule bases, STRIPS rules, and sample runs
2. **Code** – this repository
3. **Instructions** – this README (Section 4–5)

---

**Developed by:** Andrew Shatz

**AI Tools Used:**
- Grok (xAI) – Initial scaffolding and domain modeling
- Oz (Warp) – Framework upgrade to tiferet 2.0.0b1, Pydantic v2 rewrite, A\* implementation, backward-chaining engine, and full system integration
