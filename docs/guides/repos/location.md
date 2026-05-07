# LocationYamlRepository

**File:** `src/repos/location.py`
**Implements:** `LocationService` (`src/interfaces/location.py`)

## Overview

`LocationYamlRepository` is the concrete YAML-backed repository for the FOODIE campus terrain graph. It reads from and writes to the `locations` and `edges` sections of `campus.yml`, providing full CRUD operations for `Location` domain objects plus the graph adjacency list via the `LocationService` interface.

## Constructor

```python
LocationYamlRepository(campus_yaml_file='campus.yml', encoding='utf-8')
```

**Three-attribute foundation:**
- `yaml_file` — Path to the YAML file (from `campus_yaml_file` param).
- `encoding` — File encoding (default `'utf-8'`).
- `default_role` — Serialization role for writes (`'to_data.yaml'`).

## YAML File Layout

The campus file has two sections — `locations` for node attributes and `edges` for the adjacency list:

```yaml
locations:
  FW:
    x: 0.0
    y: 0.0
    is_food_warehouse: true
    is_obstacle_prone: false
  Building_A:
    x: 3.0
    y: 4.0

edges:
  FW: [Pathway_1, Pathway_2]
  Pathway_1: [FW, Building_A]
  Building_A: [Pathway_1]
```

Note: the `name` field is excluded from the YAML value (via `to_data.yaml` role) because it is the dict key.

## Read Pattern

```python
location_data = Yaml(self.yaml_file, encoding=self.encoding).load(
    start_node=lambda data: data.get('locations', {}).get(name)
)
return LocationYamlObject.from_data(location_data, name=name).map()
```

## Write Pattern

```python
full_data = Yaml(self.yaml_file, encoding=self.encoding).load()
full_data.setdefault('locations', {})[location.name] = \
    LocationYamlObject.from_model(location).to_primitive(self.default_role)
Yaml(self.yaml_file, mode='w', encoding=self.encoding).save(data=full_data)
```

Full-file load → update → rewrite ensures both `locations` and `edges` sections are preserved.

## Delete Pattern

```python
full_data.get('locations', {}).pop(name, None)
```

Idempotent — `pop(name, None)` does not raise if the key is missing.

## Graph Loading: `get_edges()`

```python
return Yaml(self.yaml_file, encoding=self.encoding).load(
    start_node=lambda data: data.get('edges', {})
)
```

Returns `Dict[str, List[str]]` — the bidirectional adjacency list used by the A* route planner.

## Method Reference

- **`exists(name)`** — Loads `locations` section, checks `name in locations_data`.
- **`get(name)`** — Loads single location via `start_node`, returns `LocationAggregate` or `None`.
- **`list()`** — Loads all locations, returns `List[LocationAggregate]`.
- **`save(location)`** — Full-file load, update locations dict, rewrite.
- **`delete(name)`** — Full-file load, pop key, rewrite.
- **`get_edges()`** — Loads `edges` section, returns adjacency list dict.

## Round-Trip Flow

`LocationAggregate` → `LocationYamlObject.from_model()` → `to_primitive('to_data.yaml')` → YAML file → `Yaml.load()` → `LocationYamlObject.from_data()` → `.map()` → `LocationAggregate`

## Integration

- **Domain Events:**
  - `SeedDatabase` calls `location_service.get('FW')` to load the Food Warehouse.
  - `PlanRoute` calls `location_service.list()` and `location_service.get_edges()` to build the graph.
- **Interface:** Satisfies `LocationService` contract from `src/interfaces/location.py`.

## Related Components

- **Location** (`src/domain/location.py`) — Domain model.
- **LocationAggregate** (`src/mappers/location.py`) — Aggregate with mutation support.
- **LocationYamlObject** (`src/mappers/location.py`) — TransferObject for YAML serialization.
- **LocationService** (`src/interfaces/location.py`) — Abstract interface this repo implements.
- **AStarRoutePlanner** (`src/utils/route_planner.py`) — Consumes the graph via `get_edges()`.
