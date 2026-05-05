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

# ** core
import os

# ** infra
from tiferet.events import DomainEvent
from tiferet.utils import Yaml

# ** app
from src.domain import Item, Order, Bag, Location, Robot, Beverage
from src.mappers import OrderAggregate, RobotAggregate
from src.repos import OrderSqliteRepository, RobotSqliteRepository
from src.events import BagOrder, PlanRoute, SelectBeverage


# *** constants

DB_PATH = 'foodie.db'


# *** helpers

def load_menu(path: str = 'menu.yml') -> dict:
    '''Load item and beverage data from the YAML menu file.'''
    return Yaml(path).load()


def seed_orders(order_repo: OrderSqliteRepository, menu_data: dict) -> None:
    '''Seed the sample order into SQLite from menu.yml data.'''
    items = []
    for name, data in menu_data.get('items', {}).items():
        items.append(Item(
            name=data['name'],
            size=data['size'],
            is_frozen=data.get('is_frozen', False),
            is_fragile=data.get('is_fragile', False),
            quantity=data.get('quantity', 1),
        ))

    orders = [
        OrderAggregate(order_id='ORD-101', items=items, destination='Building_A'),
        OrderAggregate(order_id='ORD-102', items=[], destination='Building_B'),
        OrderAggregate(order_id='ORD-103', items=[], destination='Dorm_1'),
    ]
    for order in orders:
        order_repo.save(order)


def seed_robots(robot_repo: RobotSqliteRepository, fw: Location) -> None:
    '''Seed the robot fleet into SQLite.'''
    robots = [
        RobotAggregate(robot_id='R1', current_location=fw),
        RobotAggregate(robot_id='R2', current_location=fw),
        RobotAggregate(robot_id='R3', current_location=fw),
    ]
    for robot in robots:
        robot_repo.save(robot)


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

    # Clean up any previous database for a fresh demo run.
    if os.path.exists(DB_PATH):
        os.remove(DB_PATH)

    # Initialize repositories.
    order_repo = OrderSqliteRepository(db_path=DB_PATH)
    robot_repo = RobotSqliteRepository(db_path=DB_PATH)

    # Load menu and build campus graph.
    menu_data = load_menu()
    locations, edges, fw = build_campus_graph()

    # Seed data into SQLite.
    seed_orders(order_repo, menu_data)
    seed_robots(robot_repo, fw)

    # =========================================================================
    # GOAL B: FOODIE_BAGGER — Forward-Chaining Rule-Based Bagging
    # =========================================================================
    print('=' * 70)
    print('=== FOODIE Starting: GOAL B — FOODIE_BAGGER ===')
    print('=' * 70)
    print()

    bags = DomainEvent.handle(
        BagOrder,
        dependencies={'order_service': order_repo},
        order_id='ORD-101',
    )

    # =========================================================================
    # GOAL A: Route Optimization — A* Search + Multi-Robot Replanning
    # =========================================================================
    print()
    print('=' * 70)
    print('=== FOODIE Starting: GOAL A — ROUTE OPTIMIZATION ===')
    print('=' * 70)
    print()

    route_result = DomainEvent.handle(
        PlanRoute,
        dependencies={'robot_service': robot_repo, 'order_service': order_repo},
        locations=locations,
        edges=edges,
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
