# BeverageYamlRepository

**File:** `src/repos/beverage.py`
**Implements:** `BeverageService` (`src/interfaces/beverage.py`)

## Overview

`BeverageYamlRepository` is the concrete YAML-backed repository for the FOODIE beverage knowledge base. It reads from and writes to the `beverages` section of `menu.yml`, providing full CRUD operations for `Beverage` domain objects via the `BeverageService` interface.

## Constructor

```python
BeverageYamlRepository(menu_yaml_file='menu.yml', encoding='utf-8')
```

**Three-attribute foundation:**
- `yaml_file` — Path to the YAML file (from `menu_yaml_file` param).
- `encoding` — File encoding (default `'utf-8'`).
- `default_role` — Serialization role for writes (`'to_data.yaml'`).

## YAML File Layout

Beverages are stored as a dict under the `beverages` key, with the beverage name as the dict key:

```yaml
beverages:
  Carrot Juice:
    beverage_type: juice
    brand: FreshRoots
    is_health_friendly: true
    avoids_allergens: citrus
  Corona Beer:
    beverage_type: beer
    brand: Corona
    is_health_friendly: false
```

Note: the `name` field is excluded from the YAML value (via `to_data.yaml` role) because it is the dict key.

## Read Pattern

```python
beverage_data = Yaml(self.yaml_file, encoding=self.encoding).load(
    start_node=lambda data: data.get('beverages', {}).get(name)
)
return BeverageYamlObject.from_data(beverage_data, name=name).map()
```

## Write Pattern

```python
full_data = Yaml(self.yaml_file, encoding=self.encoding).load()
full_data.setdefault('beverages', {})[beverage.name] = \
    BeverageYamlObject.from_model(beverage).to_primitive(self.default_role)
Yaml(self.yaml_file, mode='w', encoding=self.encoding).save(data=full_data)
```

Full-file load → update → rewrite ensures other YAML sections (e.g., `items`) are preserved.

## Delete Pattern

```python
full_data.get('beverages', {}).pop(name, None)
```

Idempotent — `pop(name, None)` does not raise if the key is missing.

## Method Reference

- **`exists(name)`** — Loads `beverages` section, checks `name in beverages_data`.
- **`get(name)`** — Loads single beverage via `start_node`, returns `BeverageAggregate` or `None`.
- **`list()`** — Loads all beverages, returns `List[BeverageAggregate]`.
- **`save(beverage)`** — Full-file load, update beverages dict, rewrite.
- **`delete(name)`** — Full-file load, pop key, rewrite.

## Round-Trip Flow

`BeverageAggregate` → `BeverageYamlObject.from_model()` → `to_primitive('to_data.yaml')` → YAML file → `Yaml.load()` → `BeverageYamlObject.from_data()` → `.map()` → `BeverageAggregate`

## Integration

- **Domain Events:** `SelectBeverage` calls `beverage_service.get(name)` after backward-chaining inference.
- **Interface:** Satisfies `BeverageService` contract from `src/interfaces/beverage.py`.

## Related Components

- **Beverage** (`src/domain/beverage.py`) — Domain model.
- **BeverageAggregate** (`src/mappers/beverage.py`) — Aggregate with mutation support.
- **BeverageYamlObject** (`src/mappers/beverage.py`) — TransferObject for YAML serialization.
- **BeverageService** (`src/interfaces/beverage.py`) — Abstract interface this repo implements.
