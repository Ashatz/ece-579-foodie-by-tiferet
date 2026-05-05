# AGENTS.md — FOODIE (v0.1.0)

## Project Overview

**FOODIE** (Food Intelligence Electrified) is an AI expert system for campus food-delivery robots, built on the **Tiferet** framework (v2.0.0b1, Pydantic v2). It implements three AI techniques: A* search, forward chaining, and backward chaining.

- **Repository:** https://github.com/ashatz/ece-579-foodie-by-tiferet
- **Branch:** `v1.0-proto`
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
├── interfaces/        # Service ABCs (BaggingService, BeverageService, LocationService, etc.)
├── mappers/           # Aggregates + TransferObjects
├── repos/             # YAML and SQLite repository implementations
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

## Testing

- **Framework:** pytest
- **Repository tests:** `src/repos/tests/`
- **Run:** `pytest src/` from project root (with venv activated).

## Contributing

- Follow Tiferet structured code style.
- Include `Co-Authored-By: Oz <oz-agent@warp.dev>` when collaborating with AI agents.
