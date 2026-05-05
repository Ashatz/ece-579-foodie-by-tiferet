#!/usr/bin/env python3
"""
FOODIE - Food Intelligence Electrified by Tiferet
Main demo script for the ECE 479/579 Spring 2026 Final Project.

Demonstrates all three project goals:
  A. Route Optimization (A* search + multi-robot replanning)
  B. FOODIE_BAGGER (forward-chaining rule-based bagging)
  C. FOODIE_SPA (backward-chaining beverage selection)
"""

# *** imports

# ** infra
from tiferet.events import DomainEvent
from tiferet.utils import Yaml

# ** app
from src.domain import Item, Order, Bag, Location, Robot, Beverage
from src.events import BagOrder, PlanRoute, SelectBeverage


# *** helpers

def load_menu(path: str = 'menu.yml') -> dict:
    '''Load item and beverage data from the YAML menu file.'''
    return Yaml(path).load()


def build_sample_order(menu_data: dict) -> Order:
    '''Build the sample order from the project spec using menu.yml data.'''
    items = []
    for name, data in menu_data.get('items', {}).items():
        items.append(Item(
            name=data['name'],
            size=data['size'],
            is_frozen=data.get('is_frozen', False),
            is_fragile=data.get('is_fragile', False),
            quantity=data.get('quantity', 1),
        ))
    return Order(order_id='ORD-101', items=items, destination='Building_A')


def build_campus_graph():
    '''Build a small campus terrain graph for A* simulation.'''
    locations = [
        Location(name='FW', x=0.0, y=0.0, is_food_warehouse=True),
        Location(name='Pathway_1', x=2.0, y=0.0),
        Location(name='Pathway_2', x=2.0, y=3.0),
        Location(name='Pathway_3', x=4.0, y=3.0, is_obstacle_prone=True),
        Location(name='Pathway_4', x=4.0, y=0.0),
        Location(name='Pathway_5', x=2.0, y=6.0),
        Location(name='Pathway_6', x=4.0, y=6.0),
        Location(name='Building_A', x=5.0, y=8.0),
        Location(name='Building_B', x=6.0, y=3.0),
        Location(name='Dorm_1', x=0.0, y=5.0),
    ]
    edges = {
        'FW':         ['Pathway_1', 'Dorm_1'],
        'Pathway_1':  ['FW', 'Pathway_2', 'Pathway_4'],
        'Pathway_2':  ['Pathway_1', 'Pathway_3', 'Pathway_5'],
        'Pathway_3':  ['Pathway_2', 'Pathway_4', 'Pathway_6', 'Building_B'],
        'Pathway_4':  ['Pathway_1', 'Pathway_3', 'Building_B'],
        'Pathway_5':  ['Pathway_2', 'Pathway_6', 'Dorm_1'],
        'Pathway_6':  ['Pathway_5', 'Pathway_3', 'Building_A'],
        'Building_A': ['Pathway_6'],
        'Building_B': ['Pathway_3', 'Pathway_4'],
        'Dorm_1':     ['FW', 'Pathway_5'],
    }
    fw = locations[0]
    return locations, edges, fw


def build_beverage_candidates(menu_data: dict) -> list:
    '''Build beverage candidates from menu.yml data.'''
    candidates = []
    for name, data in menu_data.get('beverages', {}).items():
        candidates.append(Beverage(
            name=data['name'],
            beverage_type=data['beverage_type'],
            brand=data['brand'],
            is_health_friendly=data.get('is_health_friendly', False),
            avoids_allergens=data.get('avoids_allergens', ''),
        ))
    return candidates


# *** main

if __name__ == '__main__':

    menu_data = load_menu()

    # =========================================================================
    # GOAL B: FOODIE_BAGGER — Forward-Chaining Rule-Based Bagging
    # =========================================================================
    print('=' * 70)
    print('=== FOODIE Starting: GOAL B — FOODIE_BAGGER ===')
    print('=' * 70)
    print()

    sample_order = build_sample_order(menu_data)
    bags = DomainEvent.handle(BagOrder, order=sample_order)

    # =========================================================================
    # GOAL A: Route Optimization — A* Search + Multi-Robot Replanning
    # =========================================================================
    print()
    print('=' * 70)
    print('=== FOODIE Starting: GOAL A — ROUTE OPTIMIZATION ===')
    print('=' * 70)
    print()

    locations, edges, fw = build_campus_graph()
    robots = [
        Robot(robot_id='R1', current_location=fw),
        Robot(robot_id='R2', current_location=fw),
        Robot(robot_id='R3', current_location=fw),
    ]
    orders = [
        Order(order_id='ORD-101', items=[], destination='Building_A'),
        Order(order_id='ORD-102', items=[], destination='Building_B'),
        Order(order_id='ORD-103', items=[], destination='Dorm_1'),
    ]
    route_result = DomainEvent.handle(
        PlanRoute,
        robots=robots, orders=orders,
        locations=locations, edges=edges,
    )

    # =========================================================================
    # GOAL C: FOODIE_SPA — Backward-Chaining Beverage Selection
    # =========================================================================
    print()
    print('=' * 70)
    print('=== FOODIE Starting: GOAL C — FOODIE_SPA ===')
    print('=' * 70)
    print()

    beverage_candidates = build_beverage_candidates(menu_data)

    print('--- Scenario 1: Health nut with citrus allergy ---')
    print()
    result_1 = DomainEvent.handle(
        SelectBeverage,
        candidates=beverage_candidates,
        facts={'health_nut': True, 'allergies_citrus': True, 'guest_age': 'adult'},
    )

    print()
    print('--- Scenario 2: Casual gathering, adult guest ---')
    print()
    result_2 = DomainEvent.handle(
        SelectBeverage,
        candidates=beverage_candidates,
        facts={'occasion': 'casual', 'guest_age': 'adult', 'setting': 'outdoor'},
    )

    print()
    print('=' * 70)
    print('FOODIE simulation complete.')
    print('=' * 70)
