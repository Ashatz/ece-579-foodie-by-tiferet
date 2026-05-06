# BeverageSelectService

**File:** `src/interfaces/beverage_select.py`
**Extends:** `tiferet.interfaces.Service` (ABC)

## Overview

`BeverageSelectService` defines the abstract contract for FOODIE's backward-chaining beverage selection inference engine (Goal C). It specifies a single method — `select` — that accepts candidate beverages, guest facts, and a rule base, returning the best match or `None` when no rule fires. This interface decouples the `SelectBeverage` domain event from the concrete inference implementation, allowing the chaining strategy and rule base format to evolve independently of event orchestration logic.

## Contract Design

Beverage selection is a computational infrastructure concern: given candidate beverages, a set of known guest facts, and a hierarchical rule base, determine which beverage is appropriate using goal-driven inference. By abstracting this behind a Service contract:

- **Domain events** (`SelectBeverage`) depend only on the interface, not on the backward-chaining implementation.
- **Testing** is simplified — mock the service to test event orchestration without exercising the full inference engine.
- **Swappability** — alternative selection strategies (e.g., forward chaining, decision trees, ML classifiers) can be introduced by implementing the same contract.

## Method Signatures

### `select(candidates, facts, rules) -> BeverageAggregate | None`

Select the best beverage from candidates using backward chaining.

**Parameters:**

- `candidates` (`List[BeverageAggregate]`) — Available beverages to evaluate. Each aggregate carries the beverage's type, brand, and attribute metadata used by rule conditions.
- `facts` (`Dict[str, Any]`) — Known guest facts used as the working memory for inference. Keys include attributes like `health_nut`, `allergies_citrus`, `occasion`, `guest_age`, `entree`, `formality`, and `setting`.
- `rules` (`List[Dict[str, Any]]`) — The backward-chaining rule base. Each rule is a dict with `id`, `conclusion`, `conditions` (list of `(key, value)` tuples), and `beverage_type` fields.

**Returns:**

- `BeverageAggregate | None` — The selected beverage aggregate if a rule fires successfully, or `None` if no rule in the base matches the given facts and candidates.

## Input/Output Types

- **Input:** `BeverageAggregate` (`src/mappers/beverage.py`) — Mutable aggregate with `name`, `beverage_type`, and `brand` attributes.
- **Input:** Facts dict — String-keyed dictionary of guest attributes parsed from user input.
- **Input:** Rules list — Structured rule base from `src/assets/beverage.py` (`BEVERAGE_RULES` constant).
- **Output:** `BeverageAggregate | None` — The matched beverage or `None`.

## Integration Points

- **SelectBeverage** (`src/events/select_beverage.py`) — Domain event that parses guest facts from input, loads candidates and the rule base, and delegates to `BeverageSelectService.select()` for inference.
- **DI Container** (`config.yml`) — The concrete utility is registered as a service and injected into `SelectBeverage` via constructor injection.

## Concrete Implementation

- **BackwardChainSelector** (`src/utils/backward_chain_selector.py`) — Implements recursive backward chaining with a 15-rule knowledge base, two-level rule hierarchy (category → selection), and explainable trace output. See `docs/guides/utils/backward_chain_selector.md` for details.

## Related Components

- **Beverage** (`src/domain/beverage.py`) — Domain model representing a beverage's structure.
- **BeverageAggregate** (`src/mappers/beverage.py`) — Mutable aggregate consumed and produced by the selection contract.
- **BEVERAGE_RULES** (`src/assets/beverage.py`) — The 15-rule knowledge base constant.
- **SelectBeverage** (`src/events/select_beverage.py`) — Domain event that consumes this interface.
- **BackwardChainSelector** (`src/utils/backward_chain_selector.py`) — Concrete implementation.
