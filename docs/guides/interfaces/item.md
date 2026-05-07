# ItemService

**File:** `src/interfaces/item.py`
**Extends:** `Service` (`tiferet.interfaces`)

## Overview

`ItemService` is the abstract data-access contract for the FOODIE item menu catalog. It defines the CRUD operations that any item persistence implementation must satisfy, decoupling domain events and contexts from the underlying storage mechanism.

Items represent the food products available for ordering and bagging. The menu catalog is universal/config data — it is loaded once from configuration (YAML) and shared across all orders and simulation runs.

## Contract Design

`ItemService` abstracts **YAML-backed persistence** for the `items` section of `menu.yml`. The interface exists so that domain events (e.g., `SeedDatabase`, `BagOrder`) can load and query items without knowing whether the data comes from YAML, a database, or an in-memory store.

Key design decisions:
- **Name-based primary key** — Items are identified by their `name` field, which serves as the YAML dict key. This is consistent with the YAML-backed convention used by `BeverageService` and `LocationService`.
- **Domain-typed parameters** — Methods accept and return `Item` domain objects rather than raw dicts, ensuring type safety at the interface boundary.
- **Idempotent delete** — `delete(name)` must not raise if the item does not exist.

## Method Signatures

### `exists(name: str) -> bool`
Check if an item exists by name.

### `get(name: str) -> Item`
Retrieve an item by name. Returns `None` if not found.

### `list() -> List[Item]`
List all configured items from the catalog.

### `save(item: Item) -> None`
Persist an item. If an item with the same name already exists, it is replaced.

### `delete(name: str) -> None`
Delete an item by name. Idempotent — does not raise if the item does not exist.

## Primary Key Convention

Items use `name: str` as the primary key, reflecting the YAML dict-key convention:

```yaml
items:
  1-gallon water bottle:    # <-- name is the dict key
    size: large
    is_frozen: false
    ...
```

## Integration Points

- **Repository:** `ItemYamlRepository` (`src/repos/item.py`) — Concrete YAML-backed implementation reading from `menu.yml`.
- **Domain Events:**
  - `SeedDatabase` — Calls `item_service.list()` to load menu items for seeding demo orders.
  - `BagOrder` — Indirectly consumes items loaded into orders.
- **Domain Model:** `Item` (`src/domain/item.py`) — The domain object returned by all read methods.

## Related Components

- **Item** (`src/domain/item.py`) — Domain model with `name`, `size`, `is_frozen`, `is_fragile`, `quantity`.
- **ItemAggregate** (`src/mappers/item.py`) — Aggregate with mutation support.
- **ItemYamlObject** (`src/mappers/item.py`) — TransferObject for YAML serialization.
- **ItemYamlRepository** (`src/repos/item.py`) — Concrete repository implementation.
- **BaggingService** (`src/interfaces/bagging.py`) — Consumes items via the bagging workflow.
