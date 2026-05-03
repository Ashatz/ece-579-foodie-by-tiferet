**Here is the corrected and final README.md**

```markdown
# FOODIE – Food Intelligence Electrified by Tiferet

**ECE 479/579 Principles of Artificial Intelligence**  
**Spring 2026 Final Project/Exam**  
**Due: May 8th, 2026 via D2L**

---

### 1. What is FOODIE?

**FOODIE** (Food Intelligence Electrified by Tiferet) is a complete AI expert system designed to autonomously manage a fleet of food-delivery robots on a university campus.  

It was built using the **Tiferet** framework and directly implements the core AI concepts from the course syllabus:
- Production Systems & forward chaining (Goal B)
- State-space search, heuristic search (A*), and replanning (Goal A)
- Predicate logic and backward chaining (Goal C)

### 2. What It Does (Project Goals)

| Goal | Feature              | Description |
|------|----------------------|-------------|
| **A** | Route Optimization   | Multi-robot A* path planning with energy/time minimization and dynamic replanning for obstacles |
| **B** | FOODIE_BAGGER        | Rule-based forward-chaining production system for bagging orders (large → medium → small, frozen bags, fragile rules, capacity) |
| **C** | FOODIE_SPA           | Backward-chaining expert that selects the right beverage for unexpected guests based on health/allergy facts |

**Hybrid Persistence**:
- YAML (`configs/menu.yml`) for universal/config data (items, beverages)
- SQLite (`foodie.db`) for runtime/instance-specific data (orders, bags, robots, locations)

### 3. How to Use It

#### Quick Start
```bash
# 1. Activate environment
python3 -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate

# 2. Install dependencies
pip install tiferet

# 3. Seed the system with sample data
python -m foodie seed-data

# 4. Run the three main goals
python -m foodie bag-order
python -m foodie plan-routes
python -m foodie select-beverage --health-nut --allergies citrus
```

#### All Available Commands
```bash
python -m foodie --help
```

### 4. Expected Outputs

#### FOODIE_BAGGER (Goal B)
```bash
=== FOODIE Starting: BAG.ORDER ===
FOODIE_BAGGER forward-chaining production system started...
Rule Ri says:   Bag large items.
Rule Rk says:   Put 2x 1-gallon water bottle [large] in bag_1.
...
Bagging complete.
Bag bag_1 (paper) contains: 2x 1-gallon water bottle [large] (2/10)
```

#### Route Planning + Fleet Monitoring (Goal A)
```bash
=== FOODIE Starting: PLAN.ROUTES ===
RoutePlannerContext: A* search + multi-robot replanning started...
Obstacle detected on Pathway 3! Replanning with A*...
New path found (heuristic h(n) = Manhattan + obstacle penalty).

=== Current Fleet Status ===
Robot R1 | Loc: FW (Food Warehouse) @ (0.0, 0.0) | Battery: 85.6% | Status: en_route | Bags: 2
```

#### FOODIE_SPA (Goal C)
```bash
=== FOODIE Starting: SELECT.BEVERAGE ===
FOODIE_SPA backward-chaining inference started...
Selected Carrot Juice (FreshRoots) [juice] (health-friendly, avoids:citrus)
Backward chaining successful → beverage selected.
```

### 5. Architecture Overview

- Built on the **Tiferet** framework (builders, contexts, domain events, mappers, hybrid repositories)
- Clean separation of concerns following Domain-Driven Design
- Real-time simulation traces for all goals (exactly as required by the project specification)

### 6. Submission Files

1. **Project Report** (includes this README + architecture + sample outputs)
2. **Code** – entire `foodie/` package
3. **Instructions to run your system** – see section 3 above

---

**Developed by:**  
Andrew Shatz

**AI Tutor & Architectural Guidance:**  
Grok (xAI) – Assisted with Tiferet framework implementation, domain modeling, repository design, and iterative refinement of the entire codebase.

This project was built step-by-step in close collaboration with Grok, strictly following the Tiferet architecture and the ECE 479/579 syllabus.