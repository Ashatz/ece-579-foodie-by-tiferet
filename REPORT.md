# FOODIE — Food Intelligence Electrified

**Course:** ECE 479/579 — Fundamentals of AI, Spring 2026
**Author:** Andrew J. Shatz
**Date:** May 8, 2026

---

## Table of Contents
1. [Introduction](#1-introduction)
2. [Assumptions](#2-assumptions)
   - [Instructor's Assumptions (Adopted)](#instructors-assumptions-adopted)
   - [Additional Assumptions (Our Refinements)](#additional-assumptions-our-refinements)
3. [Requirements Summary](#3-requirements-summary)
4. [System Architecture](#4-system-architecture)
   - [4.1 High-Level Design](#41-high-level-design)
   - [4.2 Configuration-Driven Design and the Production System Model](#42-configuration-driven-design-and-the-production-system-model)
   - [4.3 Data Flow](#43-data-flow)
5. [Algorithms and Methods](#5-algorithms-and-methods)
   - [5.1 Goal A — A\* Search Route Optimization](#51-goal-a--a-search-route-optimization)
   - [5.2 Goal B — FOODIE_BAGGER (Forward Chaining)](#52-goal-b--foodie_bagger-forward-chaining)
   - [5.3 Goal C — FOODIE_SPA (Backward Chaining)](#53-goal-c--foodie_spa-backward-chaining)
6. [Goal D — STRIPS Rules for Robotic Arm Loading](#6-goal-d--strips-rules-for-robotic-arm-loading)
   - [6.1 Overview](#61-overview)
   - [6.2 State Representation](#62-state-representation)
   - [6.3 STRIPS Operators](#63-strips-operators)
   - [6.4 Loading Sequence for a Typical Order](#64-loading-sequence-for-a-typical-order)
   - [6.5 Handling Last-Minute Changes (Unexpected Guests)](#65-handling-last-minute-changes-unexpected-guests)
7. [Campus Terrain Graph](#7-campus-terrain-graph)
8. [Use of AI Tools](#8-use-of-ai-tools)
9. [Instructions to Run the System](#9-instructions-to-run-the-system)
   - [Prerequisites](#prerequisites)
   - [Setup](#setup)
   - [Running the Demo](#running-the-demo)
   - [Running Individual Features via CLI](#running-individual-features-via-cli)
   - [Running Tests](#running-tests)
- [Appendix A — Sample Run: Goal A](#appendix-a--sample-run-goal-a-a-route-planning)
- [Appendix B — Sample Run: Goal B](#appendix-b--sample-run-goal-b-foodie_bagger-forward-chaining)
- [Appendix C — Sample Run: Goal C](#appendix-c--sample-run-goal-c-foodie_spa-backward-chaining)

---

## 1. Introduction

FOODIE (Food Intelligence Electrified) is an AI expert system designed to manage a network of autonomous food-delivery robots operating across a university campus. The system is implemented in Python and demonstrates three canonical AI techniques — A\* search, forward chaining, and backward chaining — applied to a realistic, multi-agent delivery domain. A fourth technique, STRIPS-based planning, is included as a formal design specification for robotic arm loading.

Beyond satisfying the assignment's functional goals, FOODIE was deliberately constructed using the **Tiferet framework** — a Python framework for Domain-Driven Design (DDD) — for reasons that are both architectural and conceptual. The choice of Tiferet is motivated by its ability to faithfully model the structural components of an AI production system. In classical AI, a production system is characterized by three elements: a **database** (working memory that holds the current state of the world), a set of **operators** (rules or actions that transform that state), and a **control strategy** (the mechanism that determines which operator to apply next). Tiferet's layered architecture maps directly onto this decomposition. The repository and persistence layer — backed by YAML and SQLite — serves as the working memory database, storing the current state of robots, orders, campus locations, and the beverage knowledge base. Domain events serve as the operators: focused, injectable units of computation that read from and write to the working memory in well-defined ways. Finally, Tiferet's feature context, which resolves and sequences domain events from a configuration-driven dependency injection container, serves as the control strategy that governs execution flow.

This alignment between Tiferet's architecture and the classical production system model is not coincidental. Eric Evans, in *Domain-Driven Design: Tackling Complexity in the Heart of Software* (2003), argues that effective software must center its design around the domain it models, with domain logic expressed through a rich, explicit model rather than scattered across infrastructure code. Robert C. Martin's *Clean Architecture* (2017) extends this principle by prescribing a layered structure in which domain logic is fully independent of frameworks, databases, and delivery mechanisms. Tiferet implements both of these ideas: domain events and models are pure Python objects with no infrastructure coupling, while repositories and utilities implement abstract service contracts that can be swapped without affecting domain logic. The result is a system where each AI technique — A\*, forward chaining, and backward chaining — is implemented as a clean, testable unit of domain logic that is decoupled from persistence, configuration, and delivery concerns. This makes FOODIE not merely a working simulation, but a well-structured example of how DDD and clean architecture principles can be applied to AI systems design.

---

## 2. Assumptions

### Instructor's Assumptions (Adopted)

The project specification provides a set of baseline assumptions that FOODIE adopts directly. The campus is a known, bounded terrain with defined pathways, meaning that the robot fleet operates on a graph structure rather than an open environment. Each robot is equipped with compartments, a robotic arm for bagging and loading, and onboard intelligence sufficient to execute delivery decisions. All robots depart from and return to a central Food Warehouse (FW), which serves as the operational hub for order receipt, bagging, loading, recharging, and fleet management. Robots may deliver multiple orders to multiple destinations before returning, meaning route planning must account for multi-stop itineraries.

### Additional Assumptions (Our Refinements)

Several design decisions were made to give the simulation concrete, implementable form. The campus is represented as a weighted undirected graph with ten nodes — the Food Warehouse, six pathway nodes, two academic buildings, and one dormitory — with bidirectional edges defined in `campus.yml`. Each location is assigned integer grid coordinates to support Manhattan distance calculations. The fleet consists of three robots (R1, R2, R3), each initialized at the Food Warehouse with a full 100% battery charge.

The energy model is intentionally simple but physically motivated: battery consumption is proportional to the Manhattan distance traveled, at a rate of 0.12% per unit distance. Robots are recharged to 100% upon returning to the Food Warehouse. Bag capacity follows the project specification's physical constraints — paper bags hold up to ten items, freezer bags are dedicated to frozen items, and fragile items always begin a new bag with no items added after them. Orders are typed as either `item` orders (processed by FOODIE_BAGGER) or `beverage` orders (processed by FOODIE_SPA), and a robot carries only one order type per delivery run. The beverage knowledge base contains three beverages from `menu.yml` and a fifteen-rule backward-chaining rule base.

Obstacle detection is simulated at the midpoint of any path longer than three nodes, where a blocked edge is injected in both directions and the planner re-routes from that point. When multiple orders are pending, robots are assigned via round-robin for concurrent delivery. Orders and robot state are persisted in a SQLite database (`foodie.db`), while menu items, beverages, and campus graph data are read from YAML configuration files.

---

## 3. Requirements Summary

The following table summarizes the four project goals, the AI technique employed for each, and their implementation status.

| Goal | Requirement | AI Technique | Implemented? |
|------|-------------|--------------|--------------|
| A | Optimize delivery routes, minimize time and energy, handle obstacles | A\* Search | Yes |
| B | Rule-based bagging: large → medium → small, frozen/fragile rules | Forward Chaining | Yes |
| C | Beverage selection for unexpected guests via hypothesis testing | Backward Chaining | Yes |
| D | Robotic arm loading of bags into compartments | STRIPS Planning | Design only |

Goals A, B, and C are fully implemented with complete algorithm implementations, rule bases, and simulation traces. Goal D is formalized as a STRIPS planning specification with operators, preconditions, and effect lists, but is not encoded as running software. Both FOODIE_BAGGER (Goal B) and FOODIE_SPA (Goal C) include detailed inference traces that make the reasoning process explicit.

---

## 4. System Architecture

### 4.1 High-Level Design

FOODIE is built on the Tiferet framework, which enforces a layered Domain-Driven Design architecture:

```
foodie.py              # Demo script — runs all 3 goals end-to-end
foodie_cli.py          # CLI entry point (argparse-based)
config.yml             # Unified configuration (interfaces, services, features, errors)
menu.yml               # Item catalog + beverage knowledge base
campus.yml             # Campus terrain: 10 locations + edge graph
src/
├── domain/            # Pydantic v2 domain models
│   ├── item.py        # Item (name, size, frozen, fragile, quantity)
│   ├── bag.py         # Bag (paper/freezer/beverage, capacity rules)
│   ├── order.py       # Order (items, destination, status, order_type)
│   ├── location.py    # Location (x, y, Manhattan distance heuristic)
│   ├── robot.py       # Robot (battery, compartments, energy model)
│   └── beverage.py    # Beverage (type, brand, health/allergy matching)
├── events/            # Domain events — orchestrate business logic
│   ├── migrate.py     # SeedDatabase (robots only)
│   ├── robot.py       # BagOrder, PlanRoute, DeliverOrder, ReturnToWarehouse, ChargeRobot, ViewFleet
│   └── order.py       # PlaceItemOrder, PlaceBeverageOrder, SelectBeverage
├── interfaces/        # Service ABCs (contracts)
│   ├── item.py        # ItemService
│   ├── order.py       # OrderService
│   ├── robot.py       # RobotService
│   ├── location.py    # LocationService
│   ├── beverage.py    # BeverageService
│   ├── bagging.py     # BaggingService
│   ├── route_planner.py  # RoutePlannerService
│   └── beverage_select.py # BeverageSelectService
├── mappers/           # Aggregates + TransferObjects
├── repos/             # YAML-backed and SQLite-backed repositories
├── utils/             # Computational utilities (AI algorithms)
│   ├── route_planner.py        # AStarRoutePlanner
│   ├── bagger.py               # ForwardChainBagger
│   └── backward_chain_selector.py # BackwardChainSelector
└── assets/
    └── beverage.py    # BEVERAGE_RULES (15 rules) + FALLBACK_BEVERAGE
```

### 4.2 Configuration-Driven Design and the Production System Model

A central design principle of FOODIE is that all services, feature workflows, and error handling are declared declaratively in a single `config.yml` file. The Tiferet framework reads this configuration at startup to wire the dependency injection container, resolve domain events with their required services, and map user-facing operations (such as `robot.bag_order`) to chains of domain event executions.

As described in the introduction, this architecture maps onto the classical AI production system model in a direct and intentional way. The repositories — backed by YAML for static knowledge (items, beverages, campus graph) and SQLite for dynamic state (orders, robots) — constitute the working memory of the system. Domain events, each of which encapsulates a single, well-defined state transformation, serve as the operators. The Tiferet feature context, which resolves the correct sequence of events for a given operation and injects their dependencies at runtime, serves as the control strategy. This decomposition means that swapping a different routing algorithm, bagging rule set, or inference engine requires only substituting the concrete utility class behind its service interface — a direct expression of Evans' principle that domain logic should be insulated from infrastructure decisions, and Martin's principle that inner layers should never depend on outer ones.

### 4.3 Data Flow

At runtime, `App()` loads `config.yml` and initializes the dependency injection container. A call to `app.run(interface_id, feature_id, data={})` dispatches to the appropriate domain event sequence via the feature context. Each domain event receives its required services — repositories, computational utilities — through constructor injection, performs its domain logic, and persists results back to SQLite or returns a summary dictionary. This unidirectional data flow keeps each component independently testable and ensures that the AI algorithms themselves (A\*, forward chaining, backward chaining) are pure computational utilities with no direct dependency on persistence or configuration infrastructure.

---

## 5. Algorithms and Methods

### 5.1 Goal A — A\* Search Route Optimization

**Implementation:** `src/utils/route_planner.py` — `AStarRoutePlanner`

#### Algorithm Design

A\* search is used to find shortest paths on the campus graph. The algorithm combines a true cost function *g(n)* — the cumulative Manhattan distance from the start to node *n* along the path taken so far — with an admissible heuristic *h(n)* that estimates the remaining distance to the goal as the straight-line Manhattan distance |x₁ − x₂| + |y₁ − y₂|. The total estimated cost *f(n) = g(n) + h(n)* determines the order in which nodes are expanded. Because the Manhattan heuristic never overestimates the true remaining distance on a grid-like campus and satisfies the consistency property, A\* is guaranteed to find optimal paths.

The campus graph is represented as an adjacency list loaded from `campus.yml`, with ten nodes and bidirectional edges weighted by the Manhattan distance between connected locations. The implementation uses Python's `heapq` min-heap to maintain the open set ordered by f-score, and a closed set to prevent re-expansion of already-settled nodes.

#### Obstacle Detection and Replanning

One of the key requirements of the project specification is that the system must handle obstacles not known in advance. FOODIE simulates this via the `detect_and_replan()` method. When a planned path contains more than three nodes, an obstacle is injected at the midpoint edge, blocking that edge in both directions. The planner then re-invokes A\* from the obstacle point to the original goal, using the updated blocked-edge set. The new tail segment is spliced onto the original prefix, and the total distance is recomputed. This approach demonstrates dynamic replanning without requiring a full restart from the origin, which is both more efficient and more realistic as a model of en-route obstacle avoidance.

#### Energy Management and Emergency Return

Each robot maintains a battery level that decreases proportionally to the distance traveled, at a rate of 0.12% per unit distance. The `Robot` domain model exposes an `is_low_battery()` method with a threshold of 20%. The `PlanRoute` event checks this threshold immediately after simulating energy consumption for the final planned path — whether that path was the original A\* route or a replanned route following obstacle detection. If the threshold is breached, the event aborts the delivery: it plans an emergency return route to the Food Warehouse using the same planner and campus graph already loaded in the event, consumes the return leg energy, updates the robot's location to FW, and returns a `'low_battery_return'` status instead of `'complete'`. The order remains in `'bagged'` status for re-dispatch once the robot is recharged. If battery remains above the threshold, the event proceeds normally and the robot is updated to the delivery destination.

### 5.2 Goal B — FOODIE_BAGGER (Forward Chaining)

**Implementation:** `src/utils/bagger.py` — `ForwardChainBagger`

#### Production System Design

FOODIE_BAGGER is a forward-chaining production system that decides how each item in an order should be placed into bags. The working memory consists of the item list — expanded to individual units by quantity — and the current bag state. Rules are evaluated in a fixed priority order, and the first matching rule fires for each item. This data-driven, condition-action structure is the defining characteristic of a forward-chaining production system: the system starts from the current state of the world and applies rules until the goal state (all items bagged) is reached.

#### Rule Base

The rule base encodes practical bagging knowledge that mirrors real-world grocery bagging heuristics. Items are sorted from largest to smallest before processing, ensuring that heavy items are placed at the bottom of bags and that the bagging sequence proceeds in a physically sensible order.

The rules fire in the following priority sequence. The phase rule (R-Phase) detects when the item size category changes — from large to medium to small — and announces a new bagging phase. The frozen rule (R-Frozen) fires for any frozen item, placing it in a dedicated freezer bag to maintain temperature isolation; each frozen item receives its own freezer bag. The fragile rule (R-Fragile) fires for fragile items, starting a new paper bag for the item and forcing a new bag for any subsequent item, ensuring that nothing is placed on top of a fragile item. When no current bag exists or the current bag has reached its ten-item capacity, the new-bag rule (R-NewBag) opens a fresh paper bag. Finally, the add rule (R-Add) places any ordinary, non-special item into the current bag.

Every rule firing produces a trace line in the format `Rule Rn says: <action>`, satisfying the project specification's requirement for an explicit, human-readable reasoning trace.

#### Sample Trace

For the demo order (2× 1-gallon water bottle, 1× pint ice cream, 1× granola box, 1× loaf of bread):

```
Rule R1 says:   Bag large items.
Rule R2 says:   Put 1-gallon water bottle in bag_1.
Rule R3 says:   Put 1-gallon water bottle in bag_1.
Rule R4 says:   Bag medium items.
Rule R5 says:   Put pint ice cream in a freezer bag.
Rule R6 says:   Start a new bag (fragile item).
Rule R7 says:   Put granola box in bag_3.
Rule R8 says:   Put loaf of bread in bag_4.
```

### 5.3 Goal C — FOODIE_SPA (Backward Chaining)

**Implementation:** `src/utils/backward_chain_selector.py` — `BackwardChainSelector`
**Rule Base:** `src/assets/beverage.py` — `BEVERAGE_RULES`

#### Backward Chaining Design

FOODIE_SPA uses a goal-driven backward-chaining inference engine to select a beverage for an unexpected guest. Rather than starting from known facts and deriving conclusions (as forward chaining does), FOODIE_SPA begins with a hypothesis — "shall I serve Carrot Juice?" — and works backward through the rule base, attempting to establish the conditions that would make that hypothesis true. This makes backward chaining particularly well-suited to selection problems, where the space of possible conclusions is small and known in advance.

The inference engine iterates over each candidate beverage from the knowledge base. For each candidate, it searches for rules whose conclusion matches `CHOOSE <beverage_name>`. For each such rule, all conditions are checked in turn. When a condition references an intermediate conclusion (such as `JUICE is indicated`), the engine recurses to establish that sub-goal before continuing. If a condition is a simple fact, it is checked against the known guest facts dictionary. The first candidate whose `CHOOSE` conclusion can be fully established by the rule base is selected and returned. If no candidate succeeds, the system falls back to Sparkling Water as a universal default.

#### Rule Base (15 Rules)

The rule base is organized into two levels. The first level contains category rules that establish intermediate conclusions about beverage categories from guest facts. For example, Rule R1 concludes that LIQUOR is indicated when the occasion is a celebration and the guest is an adult. Rule R8 concludes that JUICE is indicated whenever the guest is a health nut. Rule R11 concludes that WATER is indicated for a minor.

The second level contains selection rules that translate category conclusions into specific `CHOOSE` conclusions. Rule R9 concludes `CHOOSE Carrot Juice` when JUICE is indicated and the guest has a citrus allergy, while Rule R10 concludes `CHOOSE Orange Juice` when JUICE is indicated and no citrus allergy is present. Rule R5 concludes `CHOOSE Corona Beer` when BEER is indicated and the setting is outdoor. Rule R15 serves as an unconditional fallback that concludes `CHOOSE Sparkling Water` regardless of guest facts, guaranteeing that the system always returns a result.

#### Sample Trace

**Scenario:** Health-conscious guest with citrus allergy.
**Facts:** `{health_nut: True, allergies_citrus: True, guest_age: adult}`

```
FOODIE_SPA backward-chaining inference started...
Known facts: {'health_nut': True, 'allergies_citrus': True, 'guest_age': 'adult'}

Trying to establish CHOOSE Carrot Juice using rules...
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

---

## 6. Goal D — STRIPS Rules for Robotic Arm Loading

### 6.1 Overview

Goal D specifies the use of STRIPS-style planning operators to model how a robot's robotic arm loads bagged items into its delivery compartment. While this component is not encoded as running software, the formal specification below demonstrates how the state transitions involved in physical loading would be represented within a STRIPS planning framework. The design integrates naturally with the bagging output from FOODIE_BAGGER, using the bag manifest produced by Goal B as the initial state for the loading plan.

### 6.2 State Representation

```
Predicates:
  at(bag, location)         — bag is at a given location (belt, arm, compartment)
  empty(arm)                — robotic arm is free
  compartment_open(robot)   — robot compartment is open and has space
  loaded(bag, robot)        — bag has been loaded into robot
  on_belt(bag)              — bag is on the packing belt (ready for pickup)
  order_complete(order)     — all bags for the order are loaded
  is_frozen(bag)            — bag contains frozen items (must be loaded first)
  is_fragile(bag)           — bag contains fragile items (must be loaded last/on top)
```

### 6.3 STRIPS Operators

#### Operator: PICK_UP_BAG

```
PICK_UP_BAG(bag)
  Preconditions:
    on_belt(bag)
    empty(arm)
  Add List:
    at(bag, arm)
  Delete List:
    on_belt(bag)
    empty(arm)
```

#### Operator: LOAD_BAG

```
LOAD_BAG(bag, robot)
  Preconditions:
    at(bag, arm)
    compartment_open(robot)
  Add List:
    loaded(bag, robot)
    empty(arm)
  Delete List:
    at(bag, arm)
```

#### Operator: OPEN_COMPARTMENT

```
OPEN_COMPARTMENT(robot)
  Preconditions:
    ¬compartment_open(robot)
  Add List:
    compartment_open(robot)
  Delete List:
    (none)
```

#### Operator: CLOSE_COMPARTMENT

```
CLOSE_COMPARTMENT(robot)
  Preconditions:
    compartment_open(robot)
  Add List:
    (none)
  Delete List:
    compartment_open(robot)
```

#### Operator: MARK_ORDER_COMPLETE

```
MARK_ORDER_COMPLETE(order, robot)
  Preconditions:
    ∀ bag ∈ order.bags: loaded(bag, robot)
  Add List:
    order_complete(order)
  Delete List:
    (none)
```

### 6.4 Loading Sequence for a Typical Order

Consider the output of FOODIE_BAGGER for the demo order: four bags on the packing belt (bag_1 containing large items, freezer_bag_2 containing ice cream, bag_3 containing a fragile granola box, and bag_4 containing bread). The robot arm is empty and the compartment is closed. The STRIPS planner would generate the following loading sequence, observing the constraint that frozen items are loaded first (bottom of compartment) and fragile items are loaded last (top, not crushed):

1. `OPEN_COMPARTMENT(R1)`
2. `PICK_UP_BAG(freezer_bag_2)` — frozen items loaded first (bottom)
3. `LOAD_BAG(freezer_bag_2, R1)`
4. `PICK_UP_BAG(bag_1)` — large items next
5. `LOAD_BAG(bag_1, R1)`
6. `PICK_UP_BAG(bag_4)` — bread (non-fragile medium)
7. `LOAD_BAG(bag_4, R1)`
8. `PICK_UP_BAG(bag_3)` — fragile granola box last (on top, not crushed)
9. `LOAD_BAG(bag_3, R1)`
10. `CLOSE_COMPARTMENT(R1)`
11. `MARK_ORDER_COMPLETE(ORD-101, R1)`

### 6.5 Handling Last-Minute Changes (Unexpected Guests)

When a guest arrives unexpectedly and a beverage must be added to an order that has already been loaded, two additional operators are required.

#### Operator: REOPEN_COMPARTMENT

```
REOPEN_COMPARTMENT(robot)
  Preconditions:
    ¬compartment_open(robot)
    ¬at(robot, en_route)      — robot must still be at FW
  Add List:
    compartment_open(robot)
  Delete List:
    order_complete(order)     — order is no longer complete
```

#### Operator: LOAD_BEVERAGE_BAG

```
LOAD_BEVERAGE_BAG(bev_bag, robot)
  Preconditions:
    at(bev_bag, arm)
    compartment_open(robot)
  Add List:
    loaded(bev_bag, robot)
    empty(arm)
  Delete List:
    at(bev_bag, arm)
```

The modified loading plan for a last-minute beverage addition then proceeds as follows:

1. `REOPEN_COMPARTMENT(R1)` — reopens compartment, invalidating `order_complete`
2. `PICK_UP_BAG(bev_bag_ORD-101)` — beverage bag produced by FOODIE_SPA
3. `LOAD_BEVERAGE_BAG(bev_bag_ORD-101, R1)` — load on top for easy access at destination
4. `CLOSE_COMPARTMENT(R1)`
5. `MARK_ORDER_COMPLETE(ORD-101, R1)`

---

## 7. Campus Terrain Graph

The campus is modeled in `campus.yml` as a weighted undirected graph with ten locations. The Food Warehouse at coordinates (0, 0) serves as the origin and terminus for all robot routes. Six pathway nodes represent the navigable corridors between locations, while two buildings and one dormitory serve as delivery destinations.

```
Node             Coordinates    Notes
─────────────    ───────────    ──────────────────────────
FW               (0, 0)         Food Warehouse (start/end)
Pathway_1        (1, 2)
Pathway_2        (3, 2)
Pathway_3        (3, 5)         Obstacle-prone
Pathway_4        (5, 5)
Pathway_5        (6, 1)
Pathway_6        (1, 5)
Building_A       (5, 8)         Delivery destination
Building_B       (6, 3)         Delivery destination
Dorm_1           (0, 5)         Delivery destination
```

The edges of the graph are bidirectional and their weights are computed as the Manhattan distance between connected node coordinates:

```
FW ↔ Pathway_1, Pathway_6
Pathway_1 ↔ Pathway_2, Pathway_6
Pathway_2 ↔ Pathway_3, Pathway_5
Pathway_3 ↔ Pathway_4, Pathway_6
Pathway_4 ↔ Building_A, Pathway_5
Pathway_5 ↔ Building_B
Pathway_6 ↔ Dorm_1
```

---

## 8. Use of AI Tools

### Tools Used

All AI-assisted development in this project was conducted using **Warp AI (Oz Agent)**, an agentic development assistant integrated into the Warp terminal IDE. The agent was used throughout the project lifecycle for iterative design collaboration, code generation, code review, test authoring, and documentation.

### AI-Assisted Components

The following table summarizes the level of AI involvement in each major system component.

| Component | Level of AI Assistance |
|-----------|----------------------|
| System architecture and DDD layering | Collaborative design — AI proposed structure, human refined |
| Domain models (Pydantic v2) | AI-generated from specifications, human-reviewed |
| A\* route planner implementation | AI-generated core algorithm, human-specified heuristic and obstacle logic |
| Forward-chaining bagger | Collaborative — human specified rules, AI implemented production system |
| Backward-chaining selector | Collaborative — human designed rule base, AI implemented inference engine |
| Rule bases (both B and C) | Human-designed rule logic, AI structured into code |
| Domain events (orchestration) | AI-generated from TRDs, human-reviewed and refined |
| Order placement events (v1.1.0) | Human identified gap, AI drafted TRD and implemented |
| Test suite (190 tests) | AI-generated with human-specified test scenarios |
| Configuration files (YAML) | Collaborative — human specified data, AI structured format |
| STRIPS rules (Goal D) | Human-designed, AI assisted with formalization |

### Iteration Process

Development followed an iterative, TRD-driven workflow in which a Technical Requirements Document (TRD) was authored for each component before implementation began. The human collaborator wrote the initial requirements and acceptance criteria; the AI agent helped to refine the scope and generated initial code from the TRD following Tiferet's structured code style (artifact comments, RST docstrings, Pydantic v2 patterns). The human then reviewed all generated code, requested modifications, and approved final implementations before they were merged. AI-generated test suites were similarly reviewed and supplemented with human-specified edge cases. Integration was validated through end-to-end simulation output reviewed by the human collaborator. Each major component was implemented as a GitHub issue with a dedicated feature branch, pull request, and a published collaboration report documenting the AI–human interaction at each decision point.

---

## 9. Instructions to Run the System

### Prerequisites

Python 3.10 or later and `pip` are required. All Python package dependencies are listed in `requirements.txt`.

### Setup

```bash
# Clone the repository
git clone https://github.com/ashatz/ece-579-foodie-by-tiferet.git
cd ece-579-foodie-by-tiferet

# Create and activate a virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### Running the Demo

```bash
# Run the full demo (Goals A, B, and C)
python foodie.py
```

This executes all three implemented goals sequentially. First, the database is seeded with the robot fleet. An item order (ORD-101) and two beverage orders (ORD-102, ORD-103) are then placed. Goal B runs next, bagging ORD-101 via forward chaining and assigning the bags to Robot R1. Goal A then plans and executes an A\* route for R1 to Building_A, delivers the order, returns to the Food Warehouse, and recharges. Goal C follows, selecting beverages for two distinct guest scenarios using backward chaining. Finally, Goal A routes R2 and R3 to deliver the beverage orders to their destinations.

### Running Individual Features via CLI

```bash
# Seed the database (robots)
python foodie_cli.py admin seed-database

# Place an item order from the menu catalog
python foodie_cli.py order new-item ORD-101 Building_A --items "loaf of bread:2" "pint ice cream:1"

# Place a beverage order
python foodie_cli.py order new-beverage ORD-102 Building_B

# Bag an order
python foodie_cli.py robot bag-order R1 ORD-101

# Plan a route
python foodie_cli.py robot plan-route R1 ORD-101

# Select a beverage
python foodie_cli.py order select-beverage R2 ORD-102 --facts health_nut=True allergies_citrus=True guest_age=adult
```

### Running Tests

```bash
# Run all tests (190 tests)
pytest src/

# Run by layer
pytest src/domain/     # Domain model tests
pytest src/mappers/    # Mapper tests
pytest src/repos/      # Repository tests
pytest src/utils/      # Utility tests (A*, bagger, backward chainer)
pytest src/events/     # Domain event tests
```

---

## Appendix A — Sample Run: Goal A (A\* Route Planning)

```
======================================================================
GOAL A — Route Planning: A* Search
======================================================================

  Planning route: Robot R1 from FW to Building_A
  Replanned route: FW -> Pathway_6 -> Pathway_3 -> Pathway_4 -> Building_A (dist: 16.0)
  Route: FW -> Pathway_6 -> Pathway_3 -> Pathway_4 -> Building_A (dist: 16.0)
  Robot R1 battery: 98.1%

  --- Delivering Order ---
  Robot R1 delivered 4 bag(s) for ORD-101 at Building_A

  --- Returning to Warehouse ---
  Robot R1 returning from Building_A to FW
  Route: Building_A -> Pathway_4 -> Pathway_3 -> Pathway_6 -> FW (dist: 16.0)
  Robot R1 returned to FW, battery: 96.2%

  --- Charging Robot ---
  Robot R1 charged: 96.2% -> 100.0%
```

## Appendix B — Sample Run: Goal B (FOODIE_BAGGER Forward Chaining)

```
======================================================================
GOAL B — FOODIE_BAGGER: Forward-Chaining Bagging
======================================================================

  Bagging Order ORD-101 -> Building_A | Items: 2x 1-gallon water bottle [large], 1x pint ice cream (frozen) [medium], 1x granola box (fragile) [medium], 1x loaf of bread [medium] (total: 5)
  Assigned to Robot R1
Rule R1 says:   Bag large items.
Rule R2 says:   Put 1-gallon water bottle in bag_1.
Rule R3 says:   Put 1-gallon water bottle in bag_1.
Rule R4 says:   Bag medium items.
Rule R5 says:   Put pint ice cream in a freezer bag.
Rule R6 says:   Start a new bag (fragile item).
Rule R7 says:   Put granola box in bag_3.
Rule R8 says:   Put loaf of bread in bag_4.

  4 bag(s) packed and loaded onto Robot R1:
    Bag bag_1 (paper) contains: 1x 1-gallon water bottle [large], 1x 1-gallon water bottle [large] (2/10)
    Bag freezer_bag_2 (freezer) contains: 1x pint ice cream (frozen) [medium] (1/10)
    Bag bag_3 (paper) contains: 1x granola box (fragile) [medium] (1/10)
    Bag bag_4 (paper) contains: 1x loaf of bread [medium] (1/10)
```

## Appendix C — Sample Run: Goal C (FOODIE_SPA Backward Chaining)

### Scenario 1: Health-Conscious Guest with Citrus Allergy

```
  --- Scenario 1: Health-Conscious Guest ---

  Selecting beverage for order ORD-102 (Robot R2)
  Guest facts: {'health_nut': True, 'allergies_citrus': True, 'guest_age': 'adult'}
FOODIE_SPA backward-chaining inference started...
Known facts: {'health_nut': True, 'allergies_citrus': True, 'guest_age': 'adult'}

Trying to establish CHOOSE Carrot Juice using rules...
Trying to establish CHOOSE Carrot Juice using rule R9
  Trying to establish JUICE is indicated using rule R8
    Fact "health_nut" = True. OK.
  Rule R8 establishes JUICE is indicated.
  Fact "allergies_citrus" = True. OK.
Rule R9 establishes CHOOSE Carrot Juice.

CHOOSE Carrot Juice is True.
Selected Carrot Juice (FreshRoots) [juice] (health-friendly, avoids:citrus)
Backward chaining successful -> beverage selected.
  Selected: Selected Carrot Juice (FreshRoots) [juice] (health-friendly, avoids:citrus)
  Beverage bag loaded onto Robot R2
```

### Scenario 2: Casual Outdoor Gathering

```
  --- Scenario 2: Casual Outdoor Gathering ---

  Selecting beverage for order ORD-103 (Robot R3)
  Guest facts: {'occasion': 'casual', 'guest_age': 'adult', 'setting': 'outdoor'}
FOODIE_SPA backward-chaining inference started...
Known facts: {'occasion': 'casual', 'guest_age': 'adult', 'setting': 'outdoor'}

Trying to establish CHOOSE Carrot Juice using rules...
Trying to establish CHOOSE Carrot Juice using rule R9
  Trying to establish JUICE is indicated using rule R8
    Fact "health_nut" unknown — assuming False.
  Rule R9 fails to establish JUICE is indicated.

Trying to establish CHOOSE Corona Beer using rules...
Trying to establish CHOOSE Corona Beer using rule R5
  Trying to establish BEER is indicated using rule R3
    Fact "occasion" = casual. OK.
    Fact "guest_age" = adult. OK.
  Rule R3 establishes BEER is indicated.
  Fact "setting" = outdoor. OK.
Rule R5 establishes CHOOSE Corona Beer.

CHOOSE Corona Beer is True.
Selected Corona Beer (Corona) [beer]
Backward chaining successful -> beverage selected.
  Selected: Selected Corona Beer (Corona) [beer]
  Beverage bag loaded onto Robot R3
```
