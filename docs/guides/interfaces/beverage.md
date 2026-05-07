# BeverageService

**File:** `src/interfaces/beverage.py`
**Extends:** `Service` (`tiferet.interfaces`)

## Overview

`BeverageService` is the abstract data-access contract for the FOODIE beverage knowledge base. It defines the CRUD operations that any beverage persistence implementation must satisfy, decoupling the backward-chaining inference system (Goal C) from the underlying storage mechanism.

Beverages represent the drink options available for recommendation. The knowledge base is universal/config data — it is loaded from configuration (YAML) and used by the `BackwardChainSelector` to match inferred beverage names to concrete beverage records.

## Contract Design

`BeverageService` abstracts **YAML-backed persistence** for the `beverages` section of `menu.yml`. The interface exists so that domain events (e.g., `SelectBeverage`) can retrieve beverage records by name after the backward-chaining inference determines which beverage to recommend.

Key design decisions:
- **Name-based primary key** — Beverages are identified by their `name` field, which serves as the YAML dict key. This is consistent with the YAML-backed convention used by `ItemService` and `LocationService`.
- **Domain-typed parameters** — Methods accept and return `Beverage` domain objects rather than raw dicts, ensuring type safety at the interface boundary.
- **Idempotent delete** — `delete(name)` must not raise if the beverage does not exist.

## Method Signatures

### `exists(name: str) -> bool`
Check if a beverage exists by name.

### `get(name: str) -> Beverage`
Retrieve a beverage by name. Returns `None` if not found.

### `list() -> List[Beverage]`
List all configured beverages from the knowledge base.

### `save(beverage: Beverage) -> None`
Persist a beverage. If a beverage with the same name already exists, it is replaced.

### `delete(name: str) -> None`
Delete a beverage by name. Idempotent — does not raise if the beverage does not exist.

## Primary Key Convention

Beverages use `name: str` as the primary key, reflecting the YAML dict-key convention:

```yaml
beverages:
  Carrot Juice:    # <-- name is the dict key
    beverage_type: juice
    brand: FreshRoots
    ...
```

## Integration Points

- **Repository:** `BeverageYamlRepository` (`src/repos/beverage.py`) — Concrete YAML-backed implementation reading from `menu.yml`.
- **Domain Events:**
  - `SelectBeverage` — Calls `beverage_service.get(name)` to retrieve the beverage record after backward-chaining inference.
- **Domain Model:** `Beverage` (`src/domain/beverage.py`) — The domain object returned by all read methods.

## Related Components

- **Beverage** (`src/domain/beverage.py`) — Domain model with `name`, `beverage_type`, `brand`, `is_health_friendly`, `avoids_allergens`.
- **BeverageAggregate** (`src/mappers/beverage.py`) — Aggregate with mutation support.
- **BeverageYamlObject** (`src/mappers/beverage.py`) — TransferObject for YAML serialization.
- **BeverageYamlRepository** (`src/repos/beverage.py`) — Concrete repository implementation.
- **BeverageSelectService** (`src/interfaces/beverage_select.py`) — Backward-chaining inference contract that produces beverage names consumed by this service.
- **BackwardChainSelector** (`src/utils/backward_chain_selector.py`) — Utility that implements the inference logic.
