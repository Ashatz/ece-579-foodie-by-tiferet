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

# ** app
from src.domain import Item, Order, Bag, Location, Robot, Beverage
from src.mappers import OrderAggregate, RobotAggregate
from src.repos import (
    BeverageYamlRepository,
    ItemYamlRepository,
    LocationYamlRepository,
    OrderSqliteRepository,
    RobotSqliteRepository,
)
from src.events import BagOrder, PlanRoute, SelectBeverage
from src.utils import AStarRoutePlanner


# *** constants

DB_PATH = 'foodie.db'


# *** helpers

def seed_orders(order_repo: OrderSqliteRepository, item_repo: ItemYamlRepository) -> None:
    '''Seed the sample order into SQLite using the item repository.'''

    items = item_repo.list()

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


# *** main

if __name__ == '__main__':

    # Clean up any previous database for a fresh demo run.
    if os.path.exists(DB_PATH):
        os.remove(DB_PATH)

    # Initialize repositories.
    item_repo = ItemYamlRepository(menu_yaml_file='menu.yml')
    beverage_repo = BeverageYamlRepository(menu_yaml_file='menu.yml')
    location_repo = LocationYamlRepository(campus_yaml_file='campus.yml')
    order_repo = OrderSqliteRepository(db_path=DB_PATH)
    robot_repo = RobotSqliteRepository(db_path=DB_PATH)

    # Load campus graph from YAML.
    locations = location_repo.list()
    edges = location_repo.get_edges()
    fw = location_repo.get('FW')

    # Seed data into SQLite.
    seed_orders(order_repo, item_repo)
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
        dependencies={
            'robot_service': robot_repo,
            'order_service': order_repo,
            'route_planner': AStarRoutePlanner(),
        },
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

    print('--- Scenario 1: Health nut with citrus allergy ---')
    print()
    result_1 = DomainEvent.handle(
        SelectBeverage,
        dependencies={'beverage_service': beverage_repo},
        facts={'health_nut': True, 'allergies_citrus': True, 'guest_age': 'adult'},
    )

    print()
    print('--- Scenario 2: Casual gathering, adult guest ---')
    print()
    result_2 = DomainEvent.handle(
        SelectBeverage,
        dependencies={'beverage_service': beverage_repo},
        facts={'occasion': 'casual', 'guest_age': 'adult', 'setting': 'outdoor'},
    )

    print()
    print('=' * 70)
    print('FOODIE simulation complete.')
    print('=' * 70)
