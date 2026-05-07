# ItemYamlRepository

**File:** `src/repos/item.py`
**Implements:** `ItemService` (`src/interfaces/item.py`)

## Overview

`ItemYamlRepository` is the concrete YAML-backed repository for the FOODIE item menu catalog. It reads from and writes to the `items` section of `menu.yml`, providing full CRUD operations for `Item` domain objects via the `ItemService` interface.

## Constructor

```python
ItemYamlRepository(menu_yaml_file='menu.yml', encoding='utf-8')
```

**Three-attribute foundation:**
- `yaml_file` — Path to the YAML file (from `menu_yaml_file` param).
- `encoding` — File encoding (default `'utf-8'`).
- `default_role` — Serialization role for writes (`'to_data.yaml'`).

## YAML File Layout

Items are stored as a dict under the `items` key, with the item name as the dict key:

```yaml
items:
  1-gallon water bottle:
    size: large
    is_frozen: false
    is_fragile: false
    quantity: 2
  pint ice cream:
    size: medium
    is_frozen: true
    is_fragile: false
    quantity: 1
```

Note: the `name` field is excluded from the YAML value (via `to_data.yaml` role) because it is the dict key.

## Read Pattern

```python
item_data = Yaml(self.yaml_file, encoding=self.encoding).load(
    start_node=lambda data: data.get('items', {}).get(name)
)
return ItemYamlObject.from_data(item_data, name=name).map()
```

The `start_node` lambda navigates directly to the target item, avoiding full-file parsing overhead.

## Write Pattern

```python
full_data = Yaml(self.yaml_file, encoding=self.encoding).load()
full_data.setdefault('items', {})[item.name] = \
    ItemYamlObject.from_model(item).to_primitive(self.default_role)
Yaml(self.yaml_file, mode='w', encoding=self.encoding).save(data=full_data)
```

Full-file load → update → rewrite ensures other YAML sections (e.g., `beverages`) are preserved.

## Delete Pattern

```python
full_data.get('items', {}).pop(name, None)
```

Idempotent — `pop(name, None)` does not raise if the key is missing.

## Method Reference

- **`exists(name)`** — Loads `items` section, checks `name in items_data`.
- **`get(name)`** — Loads single item via `start_node`, returns `ItemAggregate` or `None`.
- **`list()`** — Loads all items, returns `List[ItemAggregate]`.
- **`save(item)`** — Full-file load, update items dict, rewrite.
- **`delete(name)`** — Full-file load, pop key, rewrite.

## Round-Trip Flow

`ItemAggregate` → `ItemYamlObject.from_model()` → `to_primitive('to_data.yaml')` → YAML file → `Yaml.load()` → `ItemYamlObject.from_data()` → `.map()` → `ItemAggregate`

## Integration

- **Domain Events:** `SeedDatabase` calls `item_service.list()` to load menu items.
- **Interface:** Satisfies `ItemService` contract from `src/interfaces/item.py`.

## Related Components

- **Item** (`src/domain/item.py`) — Domain model.
- **ItemAggregate** (`src/mappers/item.py`) — Aggregate with mutation support.
- **ItemYamlObject** (`src/mappers/item.py`) — TransferObject for YAML serialization.
- **ItemService** (`src/interfaces/item.py`) — Abstract interface this repo implements.
