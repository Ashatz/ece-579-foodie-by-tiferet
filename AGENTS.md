# AGENTS.md — FOODIE (v1.1.0)

## Project Overview

**FOODIE** (Food Intelligence Electrified) is an AI expert system for campus food-delivery robots, built on the **Tiferet** framework (v2.0.0b1, Pydantic v2). It implements three AI techniques: A* search, forward chaining, and backward chaining.

- **Repository:** https://github.com/ashatz/ece-579-foodie-by-tiferet
- **Branch:** `master`
- **Python:** ≥ 3.10
- **Framework:** Tiferet 2.0.0b1

## Architecture

FOODIE follows Tiferet's Domain-Driven Design with a unified `config.yml` configuration:

```
foodie.py              # Demo script (AppBuilder) — runs all 3 goals end-to-end
foodie_cli.py          # CLI entry point (CliBuilder + argparse)
config.yml             # Unified Tiferet v2 config (interfaces, services, features, cli, errors)
menu.yml               # Item catalog + beverage knowledge base (YAML)
campus.yml             # Campus terrain: locations + edge graph (YAML)
src/
├── domain/            # Pydantic v2 domain models (Item, Bag, Order, Location, Robot, Beverage)
├── events/            # Domain events — 10 events across 3 modules
│   ├── migrate.py     # SeedDatabase (database seeding)
│   ├── robot.py       # BagOrder, PlanRoute, DeliverOrder, ReturnToWarehouse, ChargeRobot, DispatchFleet
│   └── order.py       # PlaceItemOrder, PlaceBeverageOrder, SelectBeverage
├── interfaces/        # Service ABCs — 5 data-access + 3 utility contracts
├── mappers/           # Aggregates + TransferObjects (item, bag, beverage, location, order, robot)
├── repos/             # YAML-backed (Item, Beverage, Location) and SQLite-backed (Order, Robot) repositories
├── utils/             # Computational utilities (AStarRoutePlanner, ForwardChainBagger, BackwardChainSelector)
└── assets/            # Constants — beverage rule base (BEVERAGE_RULES) and fallback data (FALLBACK_BEVERAGE)
```

### Runtime Flow

1. `App()` loads `config.yml` via `load_app_service(app_yaml_file='config.yml')`.
2. `app.run(interface_id, feature_id, data={})` resolves the interface and dispatches to `FeatureContext`.
3. `FeatureContext` loads the feature steps from config, resolves each event from the DI container, and executes sequentially.
4. Each event receives injected services (repos, utils) via constructor injection and performs domain logic.

### Key Interfaces

- `foodie` — Default interface for programmatic use via `AppBuilder`.
- `foodie_cli` — CLI interface for argparse-based dispatch via `CliBuilder`.

### Features

Features are grouped into three domains:

**admin** — Setup operations:
- `admin.seed_database` — Pre-seed SQLite database with demo orders and robots.

**robot** — Robot lifecycle operations (bag → route → deliver → return → charge):
- `robot.bag_order` — Forward-chaining bagging onto a robot (Goal B).
- `robot.plan_route` — A* route planning for a single robot delivery (Goal A).
- `robot.deliver_order` — Deliver bags at the destination and clear robot compartments.
- `robot.return_to_warehouse` — Route a robot back to the Food Warehouse.
- `robot.charge_robot` — Charge a robot to full battery at the warehouse.
- `robot.dispatch_fleet` — Round-robin fleet dispatch with A* routing (Goal A).

**order** — Order-level operations:
- `order.new_item` — Create an item order from menu catalog items.
- `order.new_beverage` — Create a beverage order for downstream selection.
- `order.select_beverage` — Backward-chaining beverage selection (Goal C).

### Domain Events

10 domain events organized by responsibility:

- **`SeedDatabase`** (`src/events/migrate.py`) — Idempotent database seeding (robots only). Injects `OrderService`, `RobotService`, `ItemService`, `LocationService`.
- **`BagOrder`** (`src/events/robot.py`) — Robot-centric bagging (Goal B). Injects `OrderService`, `RobotService`, `BaggingService`.
- **`PlanRoute`** (`src/events/robot.py`) — A* routing to order destination (Goal A). Injects `RobotService`, `OrderService`, `RoutePlannerService`, `LocationService`.
- **`DeliverOrder`** (`src/events/robot.py`) — Deliver bags at destination. Injects `RobotService`, `OrderService`.
- **`ReturnToWarehouse`** (`src/events/robot.py`) — Route back to FW. Injects `RobotService`, `RoutePlannerService`, `LocationService`.
- **`ChargeRobot`** (`src/events/robot.py`) — Charge battery at FW. Injects `RobotService`.
- **`DispatchFleet`** (`src/events/robot.py`) — Fleet-level round-robin dispatch (Goal A). Injects `RobotService`, `OrderService`, `RoutePlannerService`, `LocationService`.
- **`PlaceItemOrder`** (`src/events/order.py`) — Create item orders from menu catalog. Injects `OrderService`, `ItemService`.
- **`PlaceBeverageOrder`** (`src/events/order.py`) — Create beverage orders. Injects `OrderService`.
- **`SelectBeverage`** (`src/events/order.py`) — Backward-chaining beverage selection (Goal C). Injects `OrderService`, `RobotService`, `BeverageService`, `BeverageSelectService`.

All events extend `DomainEvent` from `tiferet.events`, use `@DomainEvent.parameters_required([...])` for input validation, and `self.verify()` for domain rules.

### Assets

`src/assets/beverage.py` provides:
- `BEVERAGE_RULES` — 15-rule knowledge base for backward-chaining inference (Goal C).
- `FALLBACK_BEVERAGE` — Safe default (Sparkling Water) when no rule fires.

## Structured Code Style

All code follows Tiferet's artifact comment hierarchy:

- `# *** <section>` — Top-level: `imports`, `exports`, `events`, `interfaces`, `mappers`, `repos`, `utils`
- `# ** <category>: <name>` — Mid-level: `core`, `infra`, `app` (imports); `event: <name>`, etc.
- `# * <component>` — Low-level: `attribute: <name>`, `init`, `method: <name>`

### Spacing

- One empty line between `# ***` and first `# **`.
- One empty line between each `# *` section.
- One empty line after docstrings and between code snippets.

### Docstrings

RST format with `:param`, `:type`, `:return`, `:rtype`.

## Services (DI Container)

All services are defined in `config.yml` under `services:` with `module_path`, `class_name`, and optional `params`. The DI container resolves constructor dependencies by matching parameter names to service IDs.

## Configuration

Single `config.yml` at project root with sections:
- `interfaces` — App (`foodie`) and CLI (`foodie_cli`) interface definitions.
- `services` — DI container entries (events, repos, utils).
- `features` — Feature workflows grouped by domain (`admin`, `robot`, `order`).
- `cli` — CLI command definitions with argparse arguments.
- `errors` — Application-specific error definitions (9 error codes).

## Data Files

- `menu.yml` — Item catalog (4 items) and beverage knowledge base (10 beverages).
- `campus.yml` — Campus terrain graph (10 locations + edge adjacency list).
- `foodie.db` — SQLite database for runtime order/robot state (auto-created by `SeedDatabase`).

## Documentation

Guide documents are in `docs/guides/`:

### Domain Model Guides (`docs/guides/domain/`)

- `item.md` — Item domain model (size, frozen, fragile, quantity; used by FOODIE_BAGGER).
- `bag.md` — Bag domain model (paper/freezer/beverage, capacity rules, crush prevention).
- `order.md` — Order domain model (items, destination, lifecycle statuses, order type).
- `location.md` — Location domain model (campus graph node, A* heuristic, obstacle flag).
- `robot.md` — Robot domain model (battery, compartments, energy simulation).
- `beverage.md` — Beverage domain model (type, brand, health/allergy matching for backward chaining).

### Data-Access Interface Guides (`docs/guides/interfaces/`)

- `item.md` — ItemService (CRUD contract for menu catalog items; YAML-backed).
- `beverage.md` — BeverageService (CRUD contract for beverage knowledge base; YAML-backed).
- `location.md` — LocationService (CRUD + `get_edges()` for campus terrain; YAML-backed).
- `order.md` — OrderService (CRUD contract for runtime orders; SQLite-backed).
- `robot.md` — RobotService (CRUD contract for fleet state; SQLite-backed).

### Utility Interface Guides (`docs/guides/interfaces/`)

- `bagging.md` — BaggingService (forward-chaining bagging contract; Goal B).
- `route_planner.md` — RoutePlannerService (A* route planning and replanning contract; Goal A).
- `beverage_select.md` — BeverageSelectService (backward-chaining beverage selection contract; Goal C).

### Repository Guides (`docs/guides/repos/`)

- `item.md` — ItemYamlRepository (YAML-backed item persistence, `menu.yml`).
- `beverage.md` — BeverageYamlRepository (YAML-backed beverage persistence, `menu.yml`).
- `location.md` — LocationYamlRepository (YAML-backed location persistence, `campus.yml`).
- `order.md` — OrderSqliteRepository (SQLite-backed order persistence, JSON items column).
- `robot.md` — RobotSqliteRepository (SQLite-backed robot persistence, dual JSON columns).

### Utility Guides (`docs/guides/utils/`)

- `route_planner.md` — AStarRoutePlanner (A* search, Manhattan heuristic, obstacle replanning; Goal A).
- `bagger.md` — ForwardChainBagger (forward-chaining production system, rule priority; Goal B).
- `backward_chain_selector.md` — BackwardChainSelector (backward-chaining inference, 15-rule knowledge base; Goal C).

### Mapper Guides (`docs/guides/mappers/`)

- `item.md` — ItemAggregate and ItemYamlObject (flat YAML serialization for menu items).
- `location.md` — LocationAggregate and LocationYamlObject (flat YAML serialization for campus nodes).
- `beverage.md` — BeverageAggregate and BeverageYamlObject (flat YAML serialization for knowledge base).
- `bag.md` — BagAggregate (aggregate-only with static factory methods; no TransferObject).
- `order.md` — OrderAggregate and OrderSqlObject (nested items JSON serialization for SQLite).
- `robot.md` — RobotAggregate and RobotSqlObject (dual nested JSON serialization for SQLite).

### Domain Event Guides (`docs/guides/events/`)

- `seed_database.md` — SeedDatabase (idempotent database seeding, robots only).
- `place_order.md` — PlaceItemOrder and PlaceBeverageOrder (order creation from menu catalog).
- `bag_order.md` — BagOrder (robot-centric bagging with forward-chaining delegation; Goal B).
- `plan_route.md` — Robot Lifecycle Events: PlanRoute, DeliverOrder, ReturnToWarehouse, ChargeRobot, DispatchFleet (Goal A).
- `select_beverage.md` — SelectBeverage (backward-chaining inference with order-type separation; Goal C).

## Testing

- **Framework:** pytest
- **Domain tests:** `src/domain/tests/`
- **Mapper tests:** `src/mappers/tests/`
- **Repository tests:** `src/repos/tests/`
- **Utility tests:** `src/utils/tests/`
- **Event tests:** `src/events/tests/`
- **Total:** 190 tests
- **Run all:** `pytest src/` from project root (with venv activated).
- **Run by layer:**
  - `pytest src/domain/` — domain model tests
  - `pytest src/mappers/` — mapper tests
  - `pytest src/repos/` — repository tests
  - `pytest src/utils/` — utility tests
  - `pytest src/events/` — event tests

## Contributing

- Follow Tiferet structured code style.
- Include `Co-Authored-By: Oz <oz-agent@warp.dev>` when collaborating with AI agents.
