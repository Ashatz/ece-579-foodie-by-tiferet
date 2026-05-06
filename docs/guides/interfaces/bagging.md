# BaggingService

**File:** `src/interfaces/bagging.py`
**Extends:** `tiferet.interfaces.Service` (ABC)

## Overview

`BaggingService` defines the abstract contract for FOODIE's forward-chaining bagging production system (Goal B). It specifies a single method — `bag_items` — that accepts a pre-expanded list of items and returns a list of completed bags. This interface decouples the `BagOrder` domain event from the concrete bagging implementation, allowing the production system rules to evolve independently of the event orchestration logic.

## Contract Design

The bagging process is a computational infrastructure concern: given a set of items with known attributes (size, frozen, fragile), apply a deterministic rule-based system to produce bag assignments. By abstracting this behind a Service contract:

- **Domain events** (`BagOrder`) depend only on the interface, not on the forward-chaining implementation.
- **Testing** is simplified — mock the service to test event orchestration without exercising the full rule engine.
- **Swappability** — alternative bagging strategies (e.g., bin-packing, ML-based) can be introduced by implementing the same contract.

## Method Signatures

### `bag_items(items: List[Item]) -> List[BagAggregate]`

Apply bagging rules to a flat, pre-expanded list of items. Implementations handle size-priority sorting, frozen/fragile/capacity logic, and rule-firing trace output.

**Parameters:**

- `items` (`List[Item]`) — Pre-expanded list of `Item` domain objects. Each item has `quantity=1`; the caller is responsible for expanding multi-quantity items into individual entries before invoking this method.

**Returns:**

- `List[BagAggregate]` — Completed list of bags with items assigned. Each `BagAggregate` contains the bag type (paper or freezer), the assigned items, and capacity state.

## Input/Output Types

- **Input:** `Item` (`src/domain/item.py`) — Domain model with `name`, `size`, `is_frozen`, `is_fragile`, and `quantity` attributes.
- **Output:** `BagAggregate` (`src/mappers/bag.py`) — Mutable aggregate with `bag_type`, `items`, and `max_capacity` attributes plus `add_item` and `is_full` methods.

## Integration Points

- **BagOrder** (`src/events/bag_order.py`) — Domain event that loads an order, expands items by quantity, and delegates to `BaggingService.bag_items()` for rule-based assignment.
- **DI Container** (`config.yml`) — The concrete utility is registered as a service and injected into `BagOrder` via constructor injection.

## Concrete Implementation

- **ForwardChainBagger** (`src/utils/bagger.py`) — Implements the forward-chaining production system with size-priority sorting, frozen/fragile rules, and capacity enforcement. See `docs/guides/utils/bagger.md` for details.

## Related Components

- **Item** (`src/domain/item.py`) — Domain model consumed by the bagging contract.
- **Bag** (`src/domain/bag.py`) — Domain model representing a bag's structure.
- **BagAggregate** (`src/mappers/bag.py`) — Mutable aggregate produced by the bagging contract.
- **BagOrder** (`src/events/bag_order.py`) — Domain event that consumes this interface.
- **ForwardChainBagger** (`src/utils/bagger.py`) — Concrete implementation.
