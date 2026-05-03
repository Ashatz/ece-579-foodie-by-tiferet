"""
FOODIE Builder – High-level CLI orchestrator for the Food Intelligence Electrified
expert system (ECE 479/579 Spring 2026 Final Project).

Loads everything from the single root config.yml (Tiferet v2.0 style).
"""

# *** imports

# ** app
from tiferet.builders import CliBuilder

# *** builders

# ** builder: foodie_builder
class FoodieBuilder(CliBuilder):
    '''
    Builder for the FOODIE AI expert system.

    Loads all services, features, and CLI commands from config.yml.
    '''

    # * init
    def __init__(self, name: str = 'FoodieBuilder'):
        '''
        Initialize the FoodieBuilder.
        '''
        super().__init__(name=name)

    # * method: load_interface
    def load_interface(self, interface_id: str = 'foodie') -> 'FoodieContext':
        '''
        Load the main FOODIE context using the single config.yml.
        '''
        # Let Tiferet load everything from config.yml
        app = super().load_app_service(app_yaml_file="config.yml")
        return app.load_interface(interface_id)

    # * method: run (convenience)
    def run(self, interface_id: str = 'foodie', argv: list = None) -> Any:
        '''
        High-level entry point for CLI execution.
        '''
        return super().run(interface_id=interface_id, argv=argv)