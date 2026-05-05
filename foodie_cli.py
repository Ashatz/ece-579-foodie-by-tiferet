#!/usr/bin/env python3
"""
FOODIE CLI - Food Intelligence Electrified by Tiferet
Command-line interface for the FOODIE expert system.

Usage:
  python foodie_cli.py admin bag-order ORD-101
  python foodie_cli.py admin plan-route
  python foodie_cli.py admin select-beverage health_nut=True allergies_citrus=True guest_age=adult
"""

# *** imports

# ** infra
from tiferet import CLI


# *** main

# Create the CLI builder and load the app service.
cli = CLI()
cli.load_app_service(app_yaml_file='config.yml')

if __name__ == '__main__':
    cli.run('foodie_cli')
