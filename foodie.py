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


# *** constants

DB_PATH = 'foodie.db'


# *** main

if __name__ == '__main__':

    # Clean up any previous database for a fresh demo run.
    if os.path.exists(DB_PATH):
        os.remove(DB_PATH)

    # Initialize the Tiferet application.
    app = App()
    app.load_app_service(app_yaml_file='config.yml')

    # =========================================================================
    # SEED DATABASE — Pre-seed SQLite with demo orders and robots
    # =========================================================================
    print('=' * 70)
    print('=== FOODIE Starting: DATABASE SEEDING ===')
    print('=' * 70)
    print()

    app.run('foodie', 'admin.seed_database')

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
