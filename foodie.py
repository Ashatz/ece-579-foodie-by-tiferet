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
from tiferet import App

# ** app
from src.mappers import OrderAggregate, RobotAggregate
from src.repos import (
    ItemYamlRepository,
    LocationYamlRepository,
    OrderSqliteRepository,
    RobotSqliteRepository,
)


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


def seed_robots(robot_repo: RobotSqliteRepository, fw) -> None:
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

    # Seed demo data using direct repo access.
    item_repo = ItemYamlRepository(menu_yaml_file='menu.yml')
    location_repo = LocationYamlRepository(campus_yaml_file='campus.yml')
    order_repo = OrderSqliteRepository(db_path=DB_PATH)
    robot_repo = RobotSqliteRepository(db_path=DB_PATH)

    fw = location_repo.get('FW')
    seed_orders(order_repo, item_repo)
    seed_robots(robot_repo, fw)

    # Initialize the Tiferet application.
    app = App()
    app.load_app_service(app_yaml_file='config.yml')

    # =========================================================================
    # GOAL B: FOODIE_BAGGER — Forward-Chaining Rule-Based Bagging
    # =========================================================================
    print('=' * 70)
    print('=== FOODIE Starting: GOAL B — FOODIE_BAGGER ===')
    print('=' * 70)
    print()

    app.run('foodie', 'admin.bag_order', data=dict(order_id='ORD-101'))

    # =========================================================================
    # GOAL A: Route Optimization — A* Search + Multi-Robot Replanning
    # =========================================================================
    print()
    print('=' * 70)
    print('=== FOODIE Starting: GOAL A — ROUTE OPTIMIZATION ===')
    print('=' * 70)
    print()

    app.run('foodie', 'admin.plan_route')

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
    app.run('foodie', 'admin.select_beverage', data=dict(
        facts={'health_nut': True, 'allergies_citrus': True, 'guest_age': 'adult'},
    ))

    print()
    print('--- Scenario 2: Casual gathering, adult guest ---')
    print()
    app.run('foodie', 'admin.select_beverage', data=dict(
        facts={'occasion': 'casual', 'guest_age': 'adult', 'setting': 'outdoor'},
    ))

    print()
    print('=' * 70)
    print('FOODIE simulation complete.')
    print('=' * 70)
