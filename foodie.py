"""
FOODIE — Food Intelligence Electrified

Main demo script for ECE 479/579 final project.
Demonstrates all three project goals using Tiferet's AppBuilder:

  Goal A — A* route planning with obstacle replanning.
  Goal B — Forward-chaining production system for order bagging.
  Goal C — Backward-chaining inference for beverage selection.
"""

# *** imports

# ** core
import os

# ** infra
from tiferet import App

# *** main

if __name__ == '__main__':

    # Clean up any existing database for a fresh run.
    if os.path.exists('foodie.db'):
        os.remove('foodie.db')

    # Initialize the Tiferet application.
    app = App()
    app.load_app_service(app_yaml_file='config.yml')

    # ======================================================================
    # SETUP — Seed Database
    # ======================================================================
    print('=' * 70)
    print('SETUP — Seeding Database')
    print('=' * 70)

    app.run('foodie', 'admin.seed_database')

    # ======================================================================
    # GOAL B — FOODIE_BAGGER (Forward Chaining)
    # ======================================================================
    print('\n' + '=' * 70)
    print('GOAL B — FOODIE_BAGGER: Forward-Chaining Bagging')
    print('=' * 70)

    app.run('foodie', 'robot.bag_order', data=dict(
        robot_id='R1',
        order_id='ORD-101',
    ))

    # ======================================================================
    # GOAL A — Route Optimization (A* Search)
    # ======================================================================
    print('\n' + '=' * 70)
    print('GOAL A — Route Planning: A* Search')
    print('=' * 70)

    # Plan route for R1 to deliver ORD-101 at Building_A.
    app.run('foodie', 'robot.plan_route', data=dict(
        robot_id='R1',
        order_id='ORD-101',
    ))

    # Deliver the order at the destination.
    print('\n  --- Delivering Order ---')
    app.run('foodie', 'robot.deliver_order', data=dict(
        robot_id='R1',
        order_id='ORD-101',
    ))

    # Return R1 to the Food Warehouse.
    print('\n  --- Returning to Warehouse ---')
    app.run('foodie', 'robot.return_to_warehouse', data=dict(
        robot_id='R1',
    ))

    # Charge R1 at the Food Warehouse.
    print('\n  --- Charging Robot ---')
    app.run('foodie', 'robot.charge_robot', data=dict(
        robot_id='R1',
    ))

    # ======================================================================
    # GOAL C — FOODIE_SPA (Backward Chaining)
    # ======================================================================
    print('\n' + '=' * 70)
    print('GOAL C — FOODIE_SPA: Backward-Chaining Beverage Selection')
    print('=' * 70)

    # Scenario 1: Health-conscious guest with citrus allergy → Carrot Juice.
    print('\n  --- Scenario 1: Health-Conscious Guest ---')
    app.run('foodie', 'order.select_beverage', data=dict(
        robot_id='R2',
        order_id='ORD-102',
        facts={'health_nut': True, 'allergies_citrus': True, 'guest_age': 'adult'},
    ))

    # Scenario 2: Casual outdoor gathering → Corona Beer.
    print('\n  --- Scenario 2: Casual Outdoor Gathering ---')
    app.run('foodie', 'order.select_beverage', data=dict(
        robot_id='R3',
        order_id='ORD-103',
        facts={'occasion': 'casual', 'guest_age': 'adult', 'setting': 'outdoor'},
    ))

    # ======================================================================
    # GOAL A — Fleet Dispatch (Round-Robin A* Routing)
    # ======================================================================
    print('\n' + '=' * 70)
    print('GOAL A — Fleet Dispatch: Round-Robin A* Routing')
    print('=' * 70)

    app.run('foodie', 'robot.dispatch_fleet')

    print('\n' + '=' * 70)
    print('FOODIE Demo Complete')
    print('=' * 70)
