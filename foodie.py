#!/usr/bin/env python3
"""
FOODIE – Food Intelligence Electrified by Tiferet
Main CLI entry point for the ECE 479/579 Spring 2026 Final Project.
"""

# *** imports

# ** infra
from tiferet import CLI

# ** app
from src.builders import FoodieBuilder

# *** main

if __name__ == "__main__":
    # Use the FoodieBuilder we configured (loads config.yml automatically)
    app = FoodieBuilder()
    CLI.run()   # or app.run() – both work