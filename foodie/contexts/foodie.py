"""
FOODIE High-Level Context

Main runtime interface for the entire FOODIE expert system.
Orchestrates all domain events for Goals A, B, and C using services from config.yml.
"""

# *** imports

# ** core
from typing import Any, Dict

# ** app
from tiferet.contexts.app import AppInterfaceContext
from tiferet.events import DomainEvent
from ..events import BagOrder, PlanRoute, SelectBeverage, SeedData

# *** contexts

# ** context: foodie_context
class FoodieContext(AppInterfaceContext):
    '''
    High-level context for the FOODIE AI expert system.

    Delegates to real domain events using services registered in config.yml.
    Provides real-time monitoring output for the grader/demo.
    '''

    # * init
    def __init__(self, interface_id: str = 'foodie', **kwargs):
        '''
        Initialize the main FOODIE context.
        '''
        super().__init__(interface_id=interface_id, **kwargs)

    # * method: run
    def run(self, feature_id: str, headers: Dict[str, str] = None, data: Dict[str, Any] = None) -> Any:
        '''
        Main entry point called by CliBuilder / config.yml features.
        '''
        print(f"\n=== FOODIE Starting: {feature_id.upper()} ===")

        if feature_id == 'bag.order':
            return self.handle_bag_order(data)
        elif feature_id == 'plan.routes':
            return self.handle_plan_routes(data)
        elif feature_id == 'select.beverage':
            return self.handle_select_beverage(data)
        elif feature_id == 'seed.data':
            return self.handle_seed_data()
        else:
            print(f"Unknown feature: {feature_id}")
            return None

    # * method: handle_bag_order
    def handle_bag_order(self, data: Dict[str, Any]) -> Any:
        '''
        Goal B – FOODIE_BAGGER rule-based bagging.
        '''
        result = DomainEvent.handle(
            BagOrder,
            bag_service=self.get_service('bag_service'),
            item_service=self.get_service('item_service'),
            order=data.get('order') if data else None
        )
        return result

    # * method: handle_plan_routes
    def handle_plan_routes(self, data: Dict[str, Any]) -> Any:
        '''
        Goal A – A* route planning and multi-robot simulation.
        '''
        result = DomainEvent.handle(
            PlanRoute,
            robot_service=self.get_service('robot_service'),
            order_service=self.get_service('order_service'),
            location_service=self.get_service('location_service'),
            orders=data.get('orders', []) if data else []
        )
        return result

    # * method: handle_select_beverage
    def handle_select_beverage(self, data: Dict[str, Any]) -> Any:
        '''
        Goal C – FOODIE_SPA backward-chaining beverage selection.
        '''
        result = DomainEvent.handle(
            SelectBeverage,
            beverage_service=self.get_service('beverage_service'),
            is_health_nut=data.get('is_health_nut', False) if data else False,
            allergies=data.get('allergies', []) if data else []
        )
        return result

    # * method: handle_seed_data
    def handle_seed_data(self) -> Any:
        '''
        Seed pre-generated data (Items/Beverages from menu.yml + runtime data in SQLite).
        '''
        result = DomainEvent.handle(
            SeedData,
            item_service=self.get_service('item_service'),
            beverage_service=self.get_service('beverage_service'),
            location_service=self.get_service('location_service'),
            robot_service=self.get_service('robot_service')
        )
        return result

    # * method: print_fleet_status
    def print_fleet_status(self, robots: list) -> None:
        '''
        Real-time monitoring output for multi-robot simulation (Goal A).
        '''
        print("\n=== Current Fleet Status ===")
        for robot in robots:
            print(robot.format_for_trace())
        print("===")