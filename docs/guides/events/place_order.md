# PlaceItemOrder and PlaceBeverageOrder Domain Events

## Overview

The `PlaceItemOrder` and `PlaceBeverageOrder` events handle order creation, separating item orders from beverage orders. They replace the hardcoded order seeding that was previously part of `SeedDatabase`, enabling user-driven order placement via features and CLI commands.

- **`PlaceItemOrder`** — Looks up items from the menu catalog by name, builds an `Order` with `order_type='item'`, and persists it. Validates item existence and duplicate order IDs.
- **`PlaceBeverageOrder`** — Creates a minimal `Order` with `order_type='beverage'` and no items, ready for downstream `SelectBeverage` inference.

**Module:** `src/events/order.py`

## PlaceItemOrder

### Dependencies

Two services are injected via constructor:

- **`order_service: OrderService`** — Checking existence and persisting orders.
- **`item_service: ItemService`** — Looking up items from the menu catalog.

### Required Parameters

- **`order_id: str`** — Unique order identifier.
- **`destination: str`** — Delivery destination on campus.
- **`items: list`** — List of dicts with `name: str` and optional `quantity: int` (default 1).

### Algorithm

1. **Duplicate check** — `order_service.exists(order_id)` → raise `DUPLICATE_ORDER` if true.
2. **Resolve items** — For each entry, look up via `item_service.get(name)` → raise `ITEM_NOT_FOUND` if not found.
3. **Build Item objects** — Copy catalog attributes, override `quantity` from input.
4. **Create order** — `OrderAggregate(order_type='item', ...)`.
5. **Persist** — `order_service.save(order)`.
6. **Return summary** — `{order_id, destination, total_items, status: 'complete'}`.

### Feature and CLI

- **Feature:** `order.new_item`
- **CLI:** `python foodie_cli.py order new-item ORD-101 Building_A --items "loaf of bread:2" "pint ice cream:1"`

## PlaceBeverageOrder

### Dependencies

One service is injected via constructor:

- **`order_service: OrderService`** — Checking existence and persisting orders.

### Required Parameters

- **`order_id: str`** — Unique order identifier.
- **`destination: str`** — Delivery destination on campus.

### Algorithm

1. **Duplicate check** — `order_service.exists(order_id)` → raise `DUPLICATE_ORDER` if true.
2. **Create order** — `OrderAggregate(order_type='beverage', items=[], ...)`.
3. **Persist** — `order_service.save(order)`.
4. **Return summary** — `{order_id, destination, order_type: 'beverage', status: 'complete'}`.

### Feature and CLI

- **Feature:** `order.new_beverage`
- **CLI:** `python foodie_cli.py order new-beverage BEV-201 Building_B`

## Error Codes

| Code | Trigger |
|------|---------|
| `DUPLICATE_ORDER` | An order with the given ID already exists |
| `ITEM_NOT_FOUND` | Item name not found in the menu catalog |

## Order Lifecycle

These events complete the order lifecycle:

1. **Place** — `order.new_item` or `order.new_beverage` (this event)
2. **Bag/Select** — `robot.bag_order` (items) or `order.select_beverage` (beverages)
3. **Route** — `robot.plan_route`
4. **Deliver** — `robot.deliver_order`
5. **Return** — `robot.return_to_warehouse`
6. **Charge** — `robot.charge_robot`

## Related Components

- **OrderService** — `src/interfaces/order.py`
- **ItemService** — `src/interfaces/item.py`
- **OrderAggregate** — `src/mappers/order.py`
- **BagOrder** — `src/events/robot.py` (downstream for item orders)
- **SelectBeverage** — `src/events/order.py` (downstream for beverage orders)
