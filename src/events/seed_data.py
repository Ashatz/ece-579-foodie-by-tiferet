"""
FOODIE SeedData Management Event

Seeds the system with pre-generated data for immediate demo of core goals:
- Items and Beverages from configs/menu.yml (YAML)
- Locations and Robots into SQLite (runtime data)
"""

# *** imports

# ** infra
from tiferet.events import DomainEvent

# ** app
from ..interfaces import (
    ItemService,
    BeverageService,
    LocationService,
    RobotService,
)
from ..domain import Location, Robot

# *** events

# ** event: seed_data
class SeedData(DomainEvent):
    '''
    Seeds the system with pre-generated data so the three main goals
    (BAGGER, route planning, beverage SPA) work immediately.
    '''

    # * attribute: item_service
    item_service: ItemService

    # * attribute: beverage_service
    beverage_service: BeverageService

    # * attribute: location_service
    location_service: LocationService

    # * attribute: robot_service
    robot_service: RobotService

    # * init
    def __init__(self, item_service: ItemService, beverage_service: BeverageService,
                 location_service: LocationService, robot_service: RobotService):
        
        self.item_service = item_service
        self.beverage_service = beverage_service
        self.location_service = location_service
        self.robot_service = robot_service

    # * method: execute
    def execute(self, **kwargs):
        print("=== Seeding FOODIE with pre-generated data ===")

        # 1. Items and Beverages are loaded from YAML (menu.yml)
        print("✓ Items and Beverages loaded from configs/menu.yml")

        # 2. Seed Locations (SQLite)
        fw = Location.new(name="FW", x=0.0, y=0.0, is_food_warehouse=True)
        bldg_a = Location.new(name="Building_A", x=5.0, y=8.0)
        self.location_service.save(fw)
        self.location_service.save(bldg_a)
        print("✓ Locations seeded into SQLite.")

        # 3. Seed Robots (SQLite)
        r1 = Robot.new(robot_id="R1", current_location=fw)
        r2 = Robot.new(robot_id="R2", current_location=fw)
        r3 = Robot.new(robot_id="R3", current_location=fw)
        self.robot_service.save(r1)
        self.robot_service.save(r2)
        self.robot_service.save(r3)
        print("✓ Fleet seeded (3 robots) into SQLite.")

        print("\nSeeding complete. Core behaviors are now ready!")
        print("You can now run:")
        print("  foodie bag-order")
        print("  foodie plan-routes")
        print("  foodie select-beverage")
        print("  foodie seed-data   (to re-seed anytime)")