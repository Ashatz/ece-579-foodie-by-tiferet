# BagOrder

**File:** `src/events/bag_order.py`
**Extends:** `tiferet.events.DomainEvent`
**Feature:** `admin.bag_order`

## Overview

`BagOrder` is the domain event that orchestrates **Goal B — FOODIE_BAGGER**. It loads an order by ID, expands its items by quantity into individual units, and delegates the forward-chaining production system to an injected `BaggingService`. The event itself is concerned with domain orchestration — retrieving data, preparing inputs, persisting status updates — while the actual bagging algorithm lives in the `ForwardChainBagger` utility.

This separation follows Tiferet's architectural pattern: events coordinate, utilities compute.

## Injected Dependencies

| Dependency | Type | Purpose |
|------------|------|---------|
| `order_service` | `OrderService` | Load and persist orders from/to SQLite. |
| `bagging_service` | `BaggingService` | Forward-chaining bagging algorithm. |

## Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `order_id` | `str` | Yes | The order to retrieve and bag. Validated by `@DomainEvent.parameters_required`. |

If `order_id` is missing, empty, or `None`, Tiferet raises a `TiferetError` before the method body runs.

## Execution Flow

### Step 1 — Load and Validate the Order

```python
order = self.order_service.get(order_id)

self.verify(
    expression=order is not None,
    error_code='ORDER_NOT_FOUND',
    order_id=order_id,
)
```

The `verify` call raises a structured `TiferetError` with the `ORDER_NOT_FOUND` code if the order doesn't exist, preventing the bagger from running on invalid input.

### Step 2 — Expand Items by Quantity

Orders store items with a `quantity` field (e.g., `quantity=2` means two identical water bottles). The bagger expects a flat list where each physical item is a separate `Item(quantity=1)` entry:

```python
expanded_items = []
for item in order.items:
    for _ in range(item.quantity):
        expanded_items.append(Item(
            name=item.name,
            size=item.size,
            is_frozen=item.is_frozen,
            is_fragile=item.is_fragile,
            quantity=1,
        ))
```

This expansion is done in the event (not the utility) because it's a domain concern — the bagger shouldn't need to know about the `quantity` concept. It operates on physical items.

### Step 3 — Delegate to the Bagger

```python
bags = self.bagging_service.bag_items(expanded_items)
```

The `ForwardChainBagger` receives the expanded list, sorts by size priority, applies the forward-chaining rules, and returns a list of `BagAggregate` objects. The rule-firing trace is printed to stdout during execution.

### Step 4 — Update Order Status

```python
order.status = 'bagged'
self.order_service.save(order)
```

The order transitions from `'pending'` to `'bagged'`, which is persisted to SQLite. This status is checked by Goal A when determining which orders need delivery.

### Step 5 — Print Summary

```
Bagging complete.
  Bag bag_1 (paper) contains: 1x 1-gallon water bottle, 1x 1-gallon water bottle (2/10)
  Bag freezer_bag_2 (freezer) contains: 1x pint ice cream (1/10)
  Bag bag_3 (paper) contains: 1x granola box (1/10)
  Bag bag_4 (paper) contains: 1x loaf of bread (1/10)
```

### Return Value

Returns the list of `BagAggregate` objects, allowing the calling context to inspect or further process the bags (e.g., loading them into robot compartments).

## Design Decisions

### Why expand items in the event, not the utility?

The `quantity` field is a domain-level abstraction — "2 water bottles" is how a customer thinks about an order. The bagger operates at the physical level — "this water bottle goes in this bag." Converting between these levels is a domain orchestration responsibility, so it belongs in the event.

### Why delegate to a service instead of inlining the rules?

The `BaggingService` interface makes the bagger swappable and testable:
- The event can be tested with a mock bagger that returns predetermined bags.
- Alternative bagging strategies (e.g., weight-based, bin-packing) can be implemented without modifying the event.
- The utility can be tested in isolation with synthetic item lists.

## Related Components

- **ForwardChainBagger** (`src/utils/bagger.py`) — The concrete bagging algorithm. See [bagger guide](../utils/bagger.md).
- **Item** (`src/domain/item.py`) — Domain model for food items.
- **BagAggregate** (`src/mappers/bag.py`) — Mutable bag objects created by the bagger.
- **Order** (`src/domain/order.py`) — The order whose items are bagged.
- **OrderService** (`src/interfaces/order.py`) — Loads and persists orders.
- **BaggingService** (`src/interfaces/bagging.py`) — Abstract interface for the bagging algorithm.
