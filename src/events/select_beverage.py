"""
FOODIE SelectBeverage Domain Event

Implements backward-chaining inference for beverage selection (Goal C).
"""

# *** imports

# ** core
from typing import List

# ** infra
from tiferet.events import DomainEvent

# ** app
from ..interfaces import BeverageService
from ..domain import Beverage

# *** events

# ** event: select_beverage
class SelectBeverage(DomainEvent):
    '''
    Backward-chaining event for FOODIE_SPA beverage selection (Goal C).
    '''

    # * attribute: beverage_service
    beverage_service: BeverageService

    # * init
    def __init__(self, beverage_service: BeverageService):
        self.beverage_service = beverage_service

    # * method: execute
    @DomainEvent.parameters_required(['is_health_nut', 'allergies'])
    def execute(self, **kwargs) -> Beverage:
        '''
        Select the best beverage using backward chaining on guest facts.
        '''
        is_health_nut: bool = kwargs['is_health_nut']
        allergies: List[str] = kwargs.get('allergies', [])

        print("FOODIE_SPA backward-chaining inference started...")
        print(f"Goal: Find suitable beverage for guest (health_nut={is_health_nut}, allergies={allergies})")

        candidates = self.beverage_service.list()

        for bev in candidates:
            if bev.matches_guest(is_health_nut=is_health_nut, allergies=allergies):
                print(bev.format_for_trace())
                print("Backward chaining successful → beverage selected.")
                return bev

        # Fallback
        fallback = Beverage.new(name="Sparkling Water", beverage_type="water", brand="San Pellegrino")
        print(fallback.format_for_trace())
        print("No perfect match → using safe fallback.")
        return fallback