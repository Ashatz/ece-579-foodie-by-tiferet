# AGENTS.md — FOODIE (v0.1.0)

## Project Overview

**FOODIE** (Food Intelligence Electrified) is an AI expert system for campus food-delivery robots, built on the **Tiferet** framework (v2.0.0b1, Pydantic v2). It implements three AI techniques: A* search, forward chaining, and backward chaining.

- **Repository:** https://github.com/ashatz/ece-579-foodie-by-tiferet
- **Branch:** `v1.0a4-release`
- **Python:** ≥ 3.10
- **Framework:** Tiferet 2.0.0b1

## Architecture

FOODIE follows Tiferet's Domain-Driven Design with a unified `config.yml` configuration:

```
foodie.py              # Demo script (AppBuilder)
foodie_cli.py          # CLI entry point (CliBuilder)
config.yml             # Unified Tiferet v2 config (interfaces, services, features, cli, errors)
src/
├── domain/            # Pydantic v2 domain models (Item, Bag, Order, Location, Robot, Beverage)
├── events/            # Domain events (SeedDatabase, BagOrder, PlanRoute, SelectBeverage)
├── interfaces/        # Service ABCs — 5 data-access (ItemService, BeverageService, LocationService, OrderService, RobotService) + 3 utility (BaggingService, RoutePlannerService, BeverageSelectService)
├── mappers/           # Aggregates + TransferObjects (item, bag, beverage, location, order, robot)
├── repos/             # YAML-backed (Item, Beverage, Location) and SQLite-backed (Order, Robot) repository implementations
├── utils/             # Computational utilities (AStarRoutePlanner, ForwardChainBagger, BackwardChainSelector)
└── assets/            # Constants (beverage rules, fallback data)
```

### Runtime Flow

1. `App()` / `CLI()` loads `config.yml` via `load_app_service(app_yaml_file='config.yml')`.
2. `app.run(interface_id, feature_id, data={})` resolves the interface and dispatches to `FeatureContext`.
3. `FeatureContext` loads the feature steps from config, resolves each event from the DI container, and executes sequentially.
4. Each event receives injected services (repos, utils) via constructor injection and performs domain logic.

### Key Interfaces

- `foodie` — Default interface for programmatic use via `AppBuilder`.
- `foodie_cli` — CLI interface for argparse-based dispatch via `CliBuilder`.

### Features (admin group)

- `admin.seed_database` — Pre-seed SQLite database with demo orders and robots.
- `admin.bag_order` — Forward-chaining bagging (Goal B).
- `admin.plan_route` — A* route planning with replanning (Goal A).
- `admin.select_beverage` — Backward-chaining beverage selection (Goal C).

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

## Domain Events

- Extend `DomainEvent` from `tiferet.events`.
- Dependencies via constructor injection.
- `execute(**kwargs)` is the entry point.
- `@DomainEvent.parameters_required([...])` for input validation.
- `self.verify(expression, error_code, ...)` for domain rules.

## Services (DI Container)

All services are defined in `config.yml` under `services:` with `module_path`, `class_name`, and optional `params`. The DI container resolves constructor dependencies by matching parameter names to service IDs.

## Configuration

Single `config.yml` at project root with sections:
- `interfaces` — App and CLI interface definitions.
- `services` — DI container entries (events, repos, utils).
- `features` — Feature workflows grouped by domain (admin).
- `cli` — CLI command definitions with argparse arguments.
- `errors` — Application-specific error definitions.

## Data Files

- `menu.yml` — Item catalog and beverage knowledge base.
- `campus.yml` — Campus terrain graph (locations + edges).
- `foodie.db` — SQLite database for runtime order/robot state (auto-created).

## Documentation

Guide documents are in `docs/guides/`:

### Domain Model Guides (`docs/guides/domain/`)

- `item.md` — Item domain model (size, frozen, fragile, quantity; used by FOODIE_BAGGER).
- `bag.md` — Bag domain model (paper/freezer, capacity rules, crush prevention).
- `order.md` — Order domain model (items, destination, lifecycle statuses).
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

- `seed_database.md` — SeedDatabase (idempotent database seeding with demo orders and robots).
- `bag_order.md` — BagOrder (order loading, item expansion, forward-chaining delegation; Goal B).
- `plan_route.md` — PlanRoute (fleet orchestration, round-robin assignment, A* delegation; Goal A).
- `select_beverage.md` — SelectBeverage (fact parsing, backward-chaining delegation, fallback; Goal C).

## Testing

- **Framework:** pytest
- **Domain tests:** `src/domain/tests/`
- **Mapper tests:** `src/mappers/tests/`
- **Repository tests:** `src/repos/tests/`
- **Utility tests:** `src/utils/tests/`
- **Run all:** `pytest src/` from project root (with venv activated).
- **Run repos only:** `pytest src/repos/` from project root.
- **Run mappers only:** `pytest src/mappers/` from project root.
- **Run utils only:** `pytest src/utils/` from project root.

## Contributing

- Follow Tiferet structured code style.
- Include `Co-Authored-By: Oz <oz-agent@warp.dev>` when collaborating with AI agents.
