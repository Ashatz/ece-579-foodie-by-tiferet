# Beverage

**File:** `src/domain/beverage.py`
**Extends:** `tiferet.DomainObject` (Pydantic v2)

## Overview

`Beverage` represents a beverage that can be recommended to an unexpected guest. It is the output of the FOODIE_SPA backward-chaining expert system (Goal C), which uses a 15-rule knowledge base to select an appropriate beverage based on guest facts such as health preferences, allergies, occasion, and age.

Beverages are defined in `menu.yml` and loaded via `BeverageYamlRepository`.

## Attributes

| Attribute | Type | Default | Description |
|-----------|------|---------|-------------|
| `name` | `str` | *required* | Display name (e.g., `"Carrot Juice"`, `"Corona"`). |
| `beverage_type` | `Literal['water', 'juice', 'wine', 'beer', 'liquor']` | *required* | High-level category used by inference rules to narrow the search. |
| `brand` | `str` | *required* | Specific brand (e.g., `"FreshRoots"`, `"Corona"`). |
| `is_health_friendly` | `bool` | `False` | Whether the beverage is suitable for health-conscious guests. |
| `avoids_allergens` | `str` | `''` | Comma-separated list of allergens this beverage avoids (e.g., `"citrus, gluten"`). |

## Methods

### `matches_guest(is_health_nut: bool = False, allergies: list[str] | None = None) -> bool`

Backward-chaining helper that checks whether this beverage satisfies guest facts.

**Rules applied:**
1. **Health-nut rule** — If the guest is health-conscious, the beverage must have `is_health_friendly=True`.
2. **Allergy rule** — The beverage must avoid every allergen in the guest's allergy list. The check compares against the comma-separated `avoids_allergens` field.

Returns `True` only if all applicable rules are satisfied.

```python
juice = Beverage(
    name='Carrot Juice',
    beverage_type='juice',
    brand='FreshRoots',
    is_health_friendly=True,
    avoids_allergens='citrus',
)

juice.matches_guest(is_health_nut=True, allergies=['citrus'])  # True
juice.matches_guest(is_health_nut=True, allergies=['gluten'])  # False
```

### `format_for_trace() -> str`

Returns a human-readable string for the backward-chaining simulation trace.

**Example output:**
```
Selected Carrot Juice (FreshRoots) [juice] (health-friendly, avoids: citrus)
Selected Corona (Corona) [beer]
```

## Usage

### Constructing a Beverage

```python
from src.domain import Beverage

carrot_juice = Beverage(
    name='Carrot Juice',
    beverage_type='juice',
    brand='FreshRoots',
    is_health_friendly=True,
    avoids_allergens='citrus',
)
```

### Data Source — menu.yml

Beverages are defined in the `beverages` section of `menu.yml`:

```yaml
beverages:
  "Carrot Juice":
    name: "Carrot Juice"
    beverage_type: "juice"
    brand: "FreshRoots"
    is_health_friendly: true
    avoids_allergens: "citrus"
  "Corona":
    name: "Corona"
    beverage_type: "beer"
    brand: "Corona"
    is_health_friendly: false
    avoids_allergens: ""
```

### Backward Chaining (Goal C)

The FOODIE_SPA expert system uses a 15-rule knowledge base to select a beverage:

1. **Goal decomposition** — The system starts with the goal "CHOOSE a beverage" and works backward through rules to establish intermediate conclusions (e.g., "JUICE is indicated").
2. **Fact matching** — Rules check guest facts like `health_nut`, `allergies_citrus`, `guest_age`, `occasion`, `setting`, and `formality`.
3. **Beverage selection** — Once a rule chain succeeds, the corresponding `Beverage` object is retrieved and returned.
4. **`matches_guest` helper** — Used as a final validation that the selected beverage is appropriate for the guest's constraints.

**Example trace:**
```
Trying to establish CHOOSE Carrot Juice using rule R9
  Trying to establish JUICE is indicated using rule R8
    Fact "health_nut" = True. OK.
  Rule R8 establishes JUICE is indicated.
  Fact "allergies_citrus" = True. OK.
Rule R9 establishes CHOOSE Carrot Juice.
```

## Related Components

- **BeverageAggregate / BeverageYamlObject** (`src/mappers/beverage.py`) — Mapper layer for mutation and YAML serialization.
- **BeverageYamlRepository** (`src/repos/beverage.py`) — Loads beverages from `menu.yml`.
- **BeverageService** (`src/interfaces/beverage.py`) — Service interface for beverage data access.
- **BeverageSelectService** (`src/interfaces/beverage_select.py`) — Service interface for the backward-chaining selection algorithm.
- **BackwardChainSelector** (`src/utils/backward_chain_selector.py`) — The inference engine implementing 15-rule backward chaining.
- **SelectBeverage** (`src/events/select_beverage.py`) — Domain event that orchestrates the beverage selection workflow.
