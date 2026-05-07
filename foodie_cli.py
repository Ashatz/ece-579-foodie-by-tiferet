"""
FOODIE CLI — Command-Line Interface

Argparse-based CLI for individual FOODIE feature execution.
Uses Tiferet's CliBuilder for command dispatch.

Usage:
  python foodie_cli.py admin seed-database
  python foodie_cli.py robot bag-order R1 ORD-101
  python foodie_cli.py robot plan-route R1 ORD-101
  python foodie_cli.py robot deliver-order R1 ORD-101
  python foodie_cli.py robot return-to-warehouse R1
  python foodie_cli.py robot charge-robot R1
  python foodie_cli.py robot dispatch-fleet
  python foodie_cli.py order select-beverage R2 ORD-102 --facts health_nut=True allergies_citrus=True guest_age=adult
"""

# *** imports

# ** infra
from tiferet import App

# *** main

# Create new app instance.
app = App()

# Load configuration.
app.load_app_service(app_yaml_file='config.yml')

# Load the CLI interface.
cli = app.load_interface('foodie_cli')

# Run the CLI app.
if __name__ == '__main__':
    cli.run()
