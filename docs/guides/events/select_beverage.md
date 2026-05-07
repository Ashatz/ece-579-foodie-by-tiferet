# SelectBeverage Domain Event

## Overview

The `SelectBeverage` event is the backward-chaining inference orchestrator for **Goal C — FOODIE_SPA**. It processes beverage orders by loading candidate beverages, parsing guest facts, delegating inference to the `BeverageSelectService`, and loading a beverage bag onto the assigned robot.

The event enforces order type separation — only beverage orders are accepted, and the robot must not have item bags loaded (exclusive transport rule).

**Module:** `src/events/order.py`

## Dependencies

Four services are injected via constructor:

- **`order_service: OrderService`** — Loading and saving orders.
- **`robot_service: RobotService`** — Loading and saving robots.
- **`beverage_service: BeverageService`** — Loading candidate beverages from the knowledge base.
- **`beverage_select_service: BeverageSelectService`** — Backward-chaining inference engine.

**Asset imports:**
- `BEVERAGE_RULES` — 15-rule knowledge base from `src/assets/beverage.py`.
- `FALLBACK_BEVERAGE` — Safe default (Sparkling Water).

## Required Parameters

- **`robot_id: str`** — The robot to load the beverage onto.
- **`order_id: str`** — The beverage order to fulfill.
- **`facts`** (optional kwarg) — Guest facts as a dict or list of `key=value` strings.

## Algorithm

1. **Load robot** → verify exists, at Food Warehouse, no item bags (`ROBOT_CARGO_CONFLICT`).
2. **Load order** → verify exists, `order_type == 'beverage'` (`ORDER_TYPE_MISMATCH`).
3. **Load candidates** — `beverage_service.list()`.
4. **Parse facts** — dict or CLI `key=value` list with boolean conversion.
5. **Backward-chaining inference** — `beverage_select_service.select(candidates, facts, BEVERAGE_RULES)`.
6. **Fallback** — If no rule fires, use `BeverageAggregate(**FALLBACK_BEVERAGE)`.
7. **Create beverage bag** — `BagAggregate(bag_id=f'bev_{order_id}', bag_type='beverage')`.
8. **Load onto robot** — `robot.load_bag(bev_bag)`.
9. **Update order** — `status = 'bagged'`, persist both.

## Order Types and Exclusive Transport

FOODIE distinguishes two order types via `Order.order_type`:
- **`'item'`** — Processed by `BagOrder` (forward chaining). Creates paper/freezer bags.
- **`'beverage'`** — Processed by `SelectBeverage` (backward chaining). Creates beverage bags.

A robot can only carry one type at a time:
- `BagOrder` rejects robots with beverage bags (`ROBOT_CARGO_CONFLICT`).
- `SelectBeverage` rejects robots with item bags (`ROBOT_CARGO_CONFLICT`).
- `PlanRoute` and `DeliverOrder` work for both types — they check `len(compartments) > 0`.

## Error Codes

| Code | Trigger |
|------|---------|
| `ROBOT_NOT_FOUND` | Robot ID does not exist |
| `ROBOT_NOT_AT_WAREHOUSE` | Robot not at FW |
| `ROBOT_CARGO_CONFLICT` | Robot has conflicting cargo type |
| `ORDER_NOT_FOUND` | Order ID does not exist |
| `ORDER_TYPE_MISMATCH` | Order type does not match expected |

## Related Components

- **BeverageSelectService** — `src/interfaces/beverage_select.py`
- **BackwardChainSelector** — `src/utils/backward_chain_selector.py`
- **BeverageService** — `src/interfaces/beverage.py`
- **BEVERAGE_RULES / FALLBACK_BEVERAGE** — `src/assets/beverage.py`
- **BagOrder** — `src/events/robot.py` (item counterpart)
