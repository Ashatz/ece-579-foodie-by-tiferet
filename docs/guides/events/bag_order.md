# BagOrder Domain Event

## Overview

The `BagOrder` event is the robot-centric order bagging orchestrator for **Goal B — FOODIE_BAGGER**. It loads a specific robot and order, expands items by quantity into individual units, delegates rule-based bagging to the `BaggingService`, then loads the resulting bags into the robot's compartments and updates the order status to `'bagged'`.

This design ties bagging directly to a robot — after bagging completes, the robot is ready to move out with the order's bags loaded in its compartments.

**Module:** `src/events/robot.py`

## Dependencies

Three services are injected via constructor:

- **`order_service: OrderService`** — Loading and saving orders.
- **`robot_service: RobotService`** — Loading and saving robots.
- **`bagging_service: BaggingService`** — Forward-chaining bag assignment.

## Required Parameters

- **`robot_id: str`** — The robot to load bags onto.
- **`order_id: str`** — The order to bag.

Validated via `@DomainEvent.parameters_required(['robot_id', 'order_id'])`.

## Algorithm

1. **Load robot** — `robot_service.get(robot_id)` → verify exists (`ROBOT_NOT_FOUND`).
2. **Load order** — `order_service.get(order_id)` → verify exists (`ORDER_NOT_FOUND`).
3. **Print trace header** — Order summary and robot assignment.
4. **Expand items** — For each item, create `quantity` individual `Item(quantity=1)` instances.
5. **Delegate bagging** — `bagging_service.bag_items(expanded_items)` returns completed bags.
6. **Load bags onto robot** — `robot.load_bag(bag)` for each bag.
7. **Update order status** — Set `order.status = 'bagged'`, persist via `order_service.save()`.
8. **Persist robot** — Save updated robot (now carrying bags) via `robot_service.save()`.
9. **Print summary** — Bag count and contents.
10. **Return summary** — `{'robot_id': ..., 'order_id': ..., 'bags_packed': N, 'status': 'complete'}`.

## Item Expansion

Items in the order have a `quantity` field (e.g., "2x water bottle"). The bagger operates on individual physical units, so the event expands each item into `quantity` separate `Item(quantity=1)` instances before passing them to the bagging service. This keeps the bagger focused on pure rule logic.

## Error Handling

- **`ROBOT_NOT_FOUND`** — Raised when `robot_service.get()` returns `None`.
- **`ORDER_NOT_FOUND`** — Raised when `order_service.get()` returns `None`.

Both use `self.verify()` for domain rule enforcement.

## Trace Output Example

```
  Bagging Order ORD-101 -> Building_A | Items: 2x 1-gallon water bottle [large], ... (total: 5)
  Assigned to Robot R1

  3 bag(s) packed and loaded onto Robot R1:
    Bag bag_1 (paper) contains: 1x 1-gallon water bottle [large], ... (3/10)
    Bag freezer_bag_2 (freezer) contains: 1x pint ice cream (frozen) [medium] (1/10)
    Bag bag_3 (paper) contains: 1x granola box (fragile) [medium] (1/10)
```

## Integration with config.yml

The event is wired as a service in `config.yml`:

```yaml
services:
  bag_order_evt:
    module_path: src.events.robot
    class_name: BagOrder
```

And exposed as a feature:

```yaml
features:
  admin:
    bag_order:
      name: Bag Order
      description: Bag an order and load onto a robot
      commands:
        - attribute_id: bag_order_evt
          name: Bag order items for robot
```

## Related Components

- **OrderService** — `src/interfaces/order.py`
- **RobotService** — `src/interfaces/robot.py`
- **BaggingService** — `src/interfaces/bagging.py`
- **ForwardChainBagger** — `src/utils/bagger.py`
- **BagAggregate** — `src/mappers/bag.py`
- **RobotAggregate** — `src/mappers/robot.py`
