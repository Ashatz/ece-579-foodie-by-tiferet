# SelectBeverage

**File:** `src/events/select_beverage.py`
**Extends:** `tiferet.events.DomainEvent`
**Feature:** `admin.select_beverage`

## Overview

`SelectBeverage` is the domain event that orchestrates **Goal C — FOODIE_SPA**. It loads candidate beverages from the repository, parses guest facts from the input (supporting both dict and CLI `key=value` formats), supplies the 15-rule knowledge base from assets, and delegates backward-chaining inference to an injected `BeverageSelectService`. If no rule fires, the event falls back to a safe default (Sparkling Water).

The event handles input parsing, data loading, and fallback logic. The actual inference algorithm lives in the `BackwardChainSelector` utility.

## Injected Dependencies

| Dependency | Type | Purpose |
|------------|------|---------|
| `beverage_service` | `BeverageService` | Load candidate beverages from `menu.yml`. |
| `beverage_select_service` | `BeverageSelectService` | Backward-chaining inference engine. |

## Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `facts` | `dict` or `list[str]` | No | Guest facts for the inference engine. Accepts a dict (programmatic) or a list of `"key=value"` strings (CLI). Defaults to `{}`. |

## Execution Flow

### Step 1 — Load Candidate Beverages

```python
candidates = self.beverage_service.list()
```

All beverages defined in `menu.yml` are loaded as `BeverageAggregate` instances. These become the hypotheses that the backward chainer tests one by one.

### Step 2 — Parse Guest Facts

The event supports two input formats to enable both programmatic and CLI usage:

**Programmatic (dict):**
```python
app.run('foodie', 'admin.select_beverage', data={
    'facts': {'health_nut': True, 'allergies_citrus': True, 'guest_age': 'adult'}
})
```

**CLI (list of key=value strings):**
```bash
python foodie_cli.py admin select-beverage health_nut=True allergies_citrus=True guest_age=adult
```

The CLI passes facts as a list: `['health_nut=True', 'allergies_citrus=True', 'guest_age=adult']`. The event parses each string by splitting on `=` and converting `"True"`/`"False"` to Python booleans:

```python
if isinstance(facts_input, list):
    facts = {}
    for pair in facts_input:
        key, _, val = pair.partition('=')
        if val.lower() == 'true':
            facts[key] = True
        elif val.lower() == 'false':
            facts[key] = False
        else:
            facts[key] = val
```

This parsing lives in the event (not the utility) because it's an input-handling concern — the selector should receive a clean `dict`, regardless of how the user provided it.

### Step 3 — Delegate Backward-Chaining Inference

```python
result = self.beverage_select_service.select(candidates, facts, BEVERAGE_RULES)
```

The event passes three arguments:
- **`candidates`** — All beverages from `menu.yml`.
- **`facts`** — The parsed guest fact dictionary.
- **`BEVERAGE_RULES`** — The 15-rule knowledge base constant from `src/assets/beverage.py`.

The selector iterates through candidates, testing each as a hypothesis via recursive backward chaining, and returns the first match (or `None`).

### Step 4 — Handle Result or Fallback

```python
if result is not None:
    return result

fallback = BeverageAggregate(**FALLBACK_BEVERAGE)
print(f'No perfect match -> using safe fallback.')
print(f'{fallback.format_for_trace()}')
return fallback
```

If backward chaining succeeds, the selected beverage is returned immediately. If no candidate matches any rule chain, the event constructs a fallback Sparkling Water from the `FALLBACK_BEVERAGE` constant and returns it. This two-tier fallback design ensures:

1. **Rule-based fallback** — R15 in the knowledge base has no conditions and matches water-type beverages, so Sparkling Water can be selected through the normal inference path.
2. **Hard-coded fallback** — If even R15 fails (e.g., no water-type beverage in `menu.yml`), the constant provides a guaranteed answer.

### Return Value

Returns a `BeverageAggregate` — either the backward-chaining result or the fallback.

## Design Decisions

### Why load rules from assets instead of config?

The `BEVERAGE_RULES` knowledge base is a Python constant (`src/assets/beverage.py`) rather than a YAML config for several reasons:
- Rules contain tuple-based conditions that map naturally to Python data structures.
- The rule base is part of the expert system's logic, not application configuration.
- Keeping rules in code enables IDE support (autocomplete, type checking) and makes them version-controlled with the same granularity as code changes.

### Why parse facts in the event, not the CLI handler?

Tiferet's `CliBuilder` passes CLI arguments as raw values. The event is the first layer that understands the semantic meaning of facts (booleans vs. strings), so it's the natural place for parsing. This also means the programmatic interface (`foodie.py`) can pass a dict directly without conversion.

### Why a fallback at all?

An expert system that says "I don't know" is unhelpful. Sparkling Water is universally safe — no allergens, no alcohol, suitable for all ages and occasions. The fallback ensures FOODIE_SPA always provides an actionable recommendation.

## Available Fact Keys

These keys can be used as guest facts, matching the conditions in `BEVERAGE_RULES`:

| Fact Key | Type | Example Values | Used By Rules |
|----------|------|----------------|---------------|
| `health_nut` | `bool` | `True`, `False` | R8, R9, R10 |
| `allergies_citrus` | `bool` | `True`, `False` | R9, R10 |
| `guest_age` | `str` | `'adult'`, `'minor'` | R1, R3, R6, R7, R11, R13, R14 |
| `occasion` | `str` | `'celebration'`, `'casual'`, `'new_years_eve'` | R1, R3, R14 |
| `formality` | `str` | `'formal'` | R2, R12 |
| `setting` | `str` | `'outdoor'` | R5 |
| `entree` | `str` | `'steak'`, `'chicken'` | R6, R7 |
| `guest_liked` | `bool` | `True`, `False` | R13 |

## Related Components

- **BackwardChainSelector** (`src/utils/backward_chain_selector.py`) — The concrete inference engine. See [backward chain selector guide](../utils/backward_chain_selector.md).
- **Beverage** (`src/domain/beverage.py`) — Domain model for beverages.
- **BeverageAggregate** (`src/mappers/beverage.py`) — Mutable aggregate type returned by the selector.
- **BEVERAGE_RULES** (`src/assets/beverage.py`) — The 15-rule knowledge base.
- **FALLBACK_BEVERAGE** (`src/assets/beverage.py`) — Hard-coded Sparkling Water fallback.
- **BeverageService** (`src/interfaces/beverage.py`) — Loads candidates from `menu.yml`.
- **BeverageSelectService** (`src/interfaces/beverage_select.py`) — Abstract interface for inference.
- **BeverageYamlRepository** (`src/repos/beverage.py`) — YAML-backed beverage persistence.
