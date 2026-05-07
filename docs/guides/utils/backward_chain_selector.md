# BackwardChainSelector

**File:** `src/utils/backward_chain_selector.py`
**Implements:** `BeverageSelectService` (`src/interfaces/beverage_select.py`)

## Overview

`BackwardChainSelector` is the concrete computational utility that implements the FOODIE_SPA backward-chaining inference engine. Given a set of candidate beverages, a dictionary of guest facts, and a rule base, it determines which beverage is appropriate for an unexpected guest by recursively chaining backward from a hypothesis ("CHOOSE X") through intermediate conclusions to verifiable facts. This utility powers **Goal C — FOODIE_SPA** of the FOODIE project.

The selector is stateless — all candidates, facts, and rules are passed in per call.

## Why Backward Chaining?

Beverage selection is a **goal-driven** problem: we have a specific question to answer ("What beverage should we serve this guest?") and need to determine whether the available facts support a particular answer. Two inference strategies were considered:

| Strategy | Direction | Driven by | Best for |
|----------|-----------|-----------|----------|
| **Forward chaining** | Data → conclusions | Known facts trigger rules | Situations where all facts are available and we want all derivable conclusions. |
| **Backward chaining** | Goal → supporting facts | Hypothesis to verify | Situations where we have a specific goal and want to find facts that support it. |

Backward chaining was chosen because:

1. **Goal-directed** — We need to answer one specific question ("Which beverage?"), not derive all possible conclusions from the facts. Backward chaining focuses only on rules relevant to the current hypothesis.
2. **Efficient pruning** — Rules unrelated to the current beverage type are skipped entirely. Forward chaining would evaluate every rule against every fact, most of which are irrelevant.
3. **Natural rule structure** — Beverage rules naturally decompose into layers: "CHOOSE Carrot Juice" depends on "JUICE is indicated", which depends on "health_nut = True". This hierarchical structure maps directly to recursive backward chaining.
4. **Explainable trace** — The recursive descent produces a natural explanation trace showing *why* a beverage was selected, which is valuable for an expert system.
5. **Missing fact handling** — When a required fact is not in the knowledge base, backward chaining can gracefully report it as "unknown" and move to the next candidate, rather than silently producing an incomplete result.

## Knowledge Base: The 15-Rule Rule Base

The rule base is defined in `src/assets/beverage.py` as the `BEVERAGE_RULES` constant. Each rule is a dictionary with:

- **`id`** — Rule identifier (R1–R15) for trace output.
- **`conclusion`** — What this rule establishes (e.g., `"CHOOSE Carrot Juice"`, `"JUICE is indicated"`).
- **`conditions`** — List of `(key, value)` tuples that must all be satisfied. A condition key ending in `"is indicated"` triggers recursive backward chaining; all other keys are checked directly against the facts dictionary.
- **`beverage_type`** — The beverage category this rule applies to, used to filter rules during inference.

### Rule Hierarchy

The rules form a two-level hierarchy:

**Level 1 — Category rules** establish that a beverage type is appropriate:

| Rule | Conclusion | Conditions | Type |
|------|------------|------------|------|
| R1 | LIQUOR is indicated | occasion=celebration, guest_age=adult | liquor |
| R3 | BEER is indicated | occasion=casual, guest_age=adult | beer |
| R6 | WINE is indicated | entree=steak, guest_age=adult | wine |
| R7 | WINE is indicated | entree=chicken, guest_age=adult | wine |
| R8 | JUICE is indicated | health_nut=True | juice |
| R11 | WATER is indicated | guest_age=minor | water |

**Level 2 — Selection rules** choose a specific beverage within a category:

| Rule | Conclusion | Conditions | Type |
|------|------------|------------|------|
| R2 | CHOOSE Polish Vodka | LIQUOR is indicated, formality=formal | liquor |
| R4 | CHOOSE Dos Equis | BEER is indicated | beer |
| R5 | CHOOSE Corona Beer | BEER is indicated, setting=outdoor | beer |
| R9 | CHOOSE Carrot Juice | JUICE is indicated, allergies_citrus=True | juice |
| R10 | CHOOSE Orange Juice | JUICE is indicated, allergies_citrus=False | juice |
| R12 | CHOOSE Sparkling Water | WATER is indicated, formality=formal | water |
| R13 | CHOOSE Cheap Beer | guest_liked=False, guest_age=adult | beer |
| R14 | CHOOSE Champagne | occasion=new_years_eve, guest_age=adult | liquor |
| R15 | CHOOSE Sparkling Water | *(no conditions)* | water |

R15 acts as a **default/fallback** rule — it has no conditions and matches any water-type beverage, ensuring the system always has an answer.

### Rule Filtering by Beverage Type

A critical optimization: when evaluating a candidate beverage, the engine only considers rules whose `beverage_type` matches the candidate's type. This prevents, for example, beer rules from firing when evaluating a juice candidate. This filtering happens at both the CHOOSE level and the intermediate "is indicated" level.

## Algorithm: `select`

### Outer Loop — Hypothesis Generation

The `select` method iterates through candidate beverages and tests each one as a hypothesis:

1. For each candidate beverage, form the hypothesis `"CHOOSE {beverage.name}"`.
2. Call `_backward_chain(hypothesis, beverage, facts, rules)`.
3. If the chain succeeds, return that beverage immediately (first match wins).
4. If no candidate matches, return `None`.

The ordering of candidates matters — the first beverage whose CHOOSE rule can be established is selected. Candidates are provided by the `BeverageYamlRepository` in the order they appear in `menu.yml`.

### Inner Loop — Recursive Backward Chaining

The `_backward_chain` method implements the core inference algorithm:

```
_backward_chain(goal, beverage, facts, rules, depth=0)
```

**Step-by-step:**

1. **Find matching rules** — Filter `rules` to those whose `conclusion` equals the current goal AND whose `beverage_type` matches the candidate beverage's type.

2. **For each matching rule**, check all conditions:
   a. If a condition key ends with `"is indicated"` — it's an intermediate conclusion. **Recurse**: call `_backward_chain(condition_key, beverage, facts, rules, depth+1)`. If recursion fails, this rule fails.
   b. Otherwise — it's a leaf fact. Look it up in the `facts` dictionary:
      - If the key is missing: print "unknown — assuming False" and fail this condition.
      - If the value doesn't match: print the mismatch and fail this condition.
      - If the value matches: print "OK" and continue to the next condition.

3. If **all conditions** of a rule are satisfied, the rule **establishes** the goal. Return `True`.

4. If **no matching rule** succeeds, return `False`.

### Trace Output

The recursive descent produces indented trace output showing the inference chain:

```
Trying to establish CHOOSE Carrot Juice using rule R9
  Trying to establish JUICE is indicated using rule R8
    Fact "health_nut" = True. OK.
  Rule R8 establishes JUICE is indicated.
  Fact "allergies_citrus" = True. OK.
Rule R9 establishes CHOOSE Carrot Juice.

CHOOSE Carrot Juice is True.
Selected Carrot Juice (FreshRoots) [juice] (health-friendly, avoids:citrus)
Backward chaining successful -> beverage selected.
```

The indentation depth corresponds to the recursion depth, making the chain of reasoning visually clear.

## Example Walkthrough

**Facts:** `{health_nut: True, allergies_citrus: True, guest_age: 'adult'}`

**Candidates (from menu.yml):** Carrot Juice (juice), Orange Juice (juice), Corona (beer), ...

### Attempt 1: Carrot Juice

1. Hypothesis: `CHOOSE Carrot Juice`
2. Find rules with conclusion `CHOOSE Carrot Juice` and type `juice` → **R9**
3. R9 conditions: `[('JUICE is indicated', True), ('allergies_citrus', True)]`
4. Condition 1: `JUICE is indicated` ends with "is indicated" → **recurse**
   - Find rules with conclusion `JUICE is indicated` and type `juice` → **R8**
   - R8 conditions: `[('health_nut', True)]`
   - Condition: `facts['health_nut']` = `True` ✓
   - R8 establishes `JUICE is indicated` → return True
5. Condition 2: `facts['allergies_citrus']` = `True` ✓
6. R9 establishes `CHOOSE Carrot Juice` → return True
7. **Selected: Carrot Juice**

If Carrot Juice had failed (e.g., `allergies_citrus=False`), the engine would move to the next candidate and try its CHOOSE rules.

## Comparison: Forward vs. Backward Chaining in FOODIE

FOODIE uses both inference strategies, each where it fits best:

| Aspect | ForwardChainBagger (Goal B) | BackwardChainSelector (Goal C) |
|--------|----------------------------|-------------------------------|
| **Problem type** | Data-driven (all items known) | Goal-driven (which beverage?) |
| **Direction** | Facts → bag assignments | Hypothesis → supporting facts |
| **Rule base** | 5 procedural rules in code | 15 declarative rules in data |
| **Output** | Multiple bags (all conclusions) | One beverage (first match) |
| **Trace style** | Sequential rule firing | Recursive proof tree |
| **Missing facts** | N/A (all items provided) | Gracefully handled ("unknown") |

This dual-strategy design demonstrates that the choice of inference direction depends on the problem structure, not a universal preference for one approach.

## Fallback Behavior

If no candidate beverage can be established through backward chaining, the `SelectBeverage` domain event falls back to Sparkling Water (defined in `src/assets/beverage.py` as `FALLBACK_BEVERAGE`). This ensures the system always provides a recommendation, even with unusual or incomplete guest facts.

Note that R15 in the rule base also has empty conditions and matches water-type beverages, providing a rule-based fallback path before the hard-coded fallback is needed.

## Integration with the Domain Event

The `SelectBeverage` domain event (`src/events/select_beverage.py`) orchestrates the workflow:

1. Loads candidate beverages from `BeverageService`.
2. Parses guest facts from kwargs (supports both dict and CLI `key=value` list formats).
3. Calls `beverage_select_service.select(candidates, facts, BEVERAGE_RULES)`.
4. If a match is found, returns the selected `BeverageAggregate`.
5. If no match, constructs and returns the fallback Sparkling Water.

The selector itself has no knowledge of repositories, YAML files, or CLI parsing — it operates purely on candidates, facts, and rules.

## Related Components

- **Beverage** (`src/domain/beverage.py`) — The domain model with `matches_guest` validation helper.
- **BeverageAggregate** (`src/mappers/beverage.py`) — The mutable aggregate type consumed and returned by the selector.
- **BEVERAGE_RULES** (`src/assets/beverage.py`) — The 15-rule knowledge base constant.
- **FALLBACK_BEVERAGE** (`src/assets/beverage.py`) — Hard-coded Sparkling Water fallback data.
- **BeverageSelectService** (`src/interfaces/beverage_select.py`) — Abstract interface satisfied by this utility.
- **BeverageService** (`src/interfaces/beverage.py`) — Provides candidate beverages from the repository.
- **SelectBeverage** (`src/events/select_beverage.py`) — Domain event that orchestrates the beverage selection workflow.
- **BeverageYamlRepository** (`src/repos/beverage.py`) — Loads beverage candidates from `menu.yml`.
