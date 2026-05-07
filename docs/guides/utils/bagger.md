# ForwardChainBagger

**File:** `src/utils/bagger.py`
**Implements:** `BaggingService` (`src/interfaces/bagging.py`)

## Overview

`ForwardChainBagger` is the concrete computational utility that implements the FOODIE_BAGGER rule-based production system. It uses **forward chaining** (data-driven inference) to assign food items to bags according to a defined set of bagging rules. This utility powers **Goal B — FOODIE_BAGGER** of the FOODIE project.

The bagger is stateless — it receives a flat list of items and returns a list of completed bags, producing a human-readable rule-firing trace as a side effect.

## Why Forward Chaining?

Bagging is a **data-driven** problem: we start with a known set of items (facts) and need to derive the correct bag assignments (conclusions). Two inference strategies were considered:

| Strategy | Direction | Driven by | Best for |
|----------|-----------|-----------|----------|
| **Forward chaining** | Data → conclusions | Known facts trigger rules | Situations where all facts are available upfront and we want all derivable conclusions. |
| **Backward chaining** | Goal → supporting facts | Hypothesis to verify | Situations where we have a specific goal and want to find facts that support it. |

Forward chaining was chosen because:

1. **All facts are known** — The complete list of items is available before bagging begins. There is no need to hypothesize or ask for missing information.
2. **Multiple outputs** — Bagging produces multiple bags (conclusions), not a single yes/no answer. Forward chaining naturally accumulates all results.
3. **Deterministic priority** — Rules fire in a defined order (large → medium → small), making the trace predictable and reproducible.
4. **Production system fit** — The bagging problem maps directly to the classic production system model from AI (Lecture 1): a database of facts (unbagged items), a set of operators (bagging rules), and a control strategy (priority ordering).

## Production System Architecture

The forward-chaining bagger follows the three-component production system model:

### 1. Database (Working Memory)

The "database" is the current state of bags and the remaining unbagged items. At each step:
- Items are consumed from the sorted input list.
- Bags are created and filled as rules fire.
- The `current_bag` pointer tracks the active bag for regular items.

### 2. Operators (Rule Base)

The rules are encoded directly in the `bag_items` method's control flow. Each rule has a condition (IF) and an action (THEN):

| Rule | Condition (IF) | Action (THEN) |
|------|----------------|---------------|
| **Phase announcement** | Item size changes from previous | Print phase header ("Bag large items", "Bag medium items", "Bag small items"). |
| **Frozen rule** | `item.is_frozen == True` | Create a new freezer bag, add the item to it. Frozen items always get their own freezer bag. |
| **Fragile rule** | `item.is_fragile == True` | Create a new paper bag, add the fragile item, then force `current_bag = None` so the next item starts yet another bag. This prevents any item from being placed on top of a fragile item. |
| **Capacity rule** | Current bag is full (`len(items) >= max_capacity`) or no bag exists | Create a new paper bag. |
| **Default placement** | None of the above | Add the item to the current bag. |

### 3. Control Strategy

The control strategy determines **which rule fires when** — this is the key design decision in any production system.

**Size-priority ordering** is enforced by sorting all items before rule evaluation:

```python
size_priority = {'large': 0, 'medium': 1, 'small': 2}
sorted_items = sorted(items, key=lambda i: size_priority[i.size])
```

This ensures:
1. **Large items** are placed first — they form the base of each bag.
2. **Medium items** follow — they fill the middle.
3. **Small items** are placed last — they fill remaining space without crushing risk.

Within each size group, rules are evaluated in priority order: frozen > fragile > capacity > default. This is a **conflict resolution strategy** — when multiple rules could fire, the most specific rule takes precedence.

## Algorithm: `bag_items`

### Input

A pre-expanded list of `Item` objects where each physical item has `quantity=1`. The `BagOrder` event handles expansion before calling the bagger:

```python
# 2x water bottle becomes two separate Item(quantity=1) entries
expanded_items = [Item(name='water bottle', size='large', quantity=1),
                  Item(name='water bottle', size='large', quantity=1)]
```

### Step-by-Step Execution

1. **Sort** items by size priority (large=0, medium=1, small=2).
2. **Iterate** through sorted items. For each item:
   a. If the size group changed, print a phase announcement rule.
   b. If `is_frozen`: create a new freezer bag → add item → continue.
   c. If `is_fragile`: create a new paper bag → add item → set `current_bag = None` → continue.
   d. If no current bag or current bag is full: create a new paper bag.
   e. Add item to the current bag.
3. **Return** the list of all created bags.

### Rule-Firing Trace

Each rule application prints a numbered trace line:

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

The rule counter increments monotonically across all phases, providing a complete audit trail of the inference process.

### Bag Type Selection

The bagger delegates bag creation to `BagAggregate` factory methods:

| Factory Method | When Used | Bag ID Pattern |
|----------------|-----------|----------------|
| `BagAggregate.new_freezer_bag(n)` | Item is frozen | `freezer_bag_N` |
| `BagAggregate.new_fragile_bag(n)` | Item is fragile | `bag_N` (paper, one item only) |
| `BagAggregate.new_regular_bag(n)` | Default | `bag_N` (paper, up to 10 items) |

### Why Not a Rete Network?

The Rete algorithm is the classic optimization for production systems with large rule bases — it builds a discrimination network to avoid re-evaluating unchanged conditions. FOODIE uses a simpler sequential approach because:

- The rule base is small (5 rules).
- Items are processed exactly once in sorted order.
- No rules interact with each other (no chained triggers).
- The sequential approach is transparent and produces a clean trace.

For a production system with hundreds of interdependent rules, Rete would be essential. For FOODIE_BAGGER, the overhead would exceed the benefit.

## Integration with the Domain Event

The `BagOrder` domain event (`src/events/bag_order.py`) orchestrates the workflow:

1. Loads the order from `OrderService` by ID.
2. Expands items by quantity (e.g., `quantity=2` → two separate `Item(quantity=1)` entries).
3. Calls `bagging_service.bag_items(expanded_items)`.
4. Updates the order status to `'bagged'` and persists it.
5. Prints a summary of all completed bags.

The bagger itself has no knowledge of orders, services, or persistence — it operates purely on a list of items, keeping the infrastructure concern cleanly separated from domain orchestration.

## Related Components

- **Item** (`src/domain/item.py`) — The input objects processed by bagging rules.
- **Bag** (`src/domain/bag.py`) — The domain model with `can_accept_item` and `add_item` rule enforcement.
- **BagAggregate** (`src/mappers/bag.py`) — Provides `new_freezer_bag`, `new_fragile_bag`, `new_regular_bag` factory methods.
- **BaggingService** (`src/interfaces/bagging.py`) — Abstract interface satisfied by this utility.
- **BagOrder** (`src/events/bag_order.py`) — Domain event that orchestrates the bagging workflow.
- **OrderService** (`src/interfaces/order.py`) — Provides the order whose items are bagged.
