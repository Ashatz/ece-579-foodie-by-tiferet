"""
FOODIE BeverageContext (Goal C)

Low-level context for the backward-chaining FOODIE_SPA expert module.
Selects the right beverage for unexpected guests based on facts
(health nut, allergies, etc.).
"""

# *** imports

# ** core
from typing import List, Dict, Any

# ** app
from tiferet.contexts import AppInterfaceContext
from ..domain import Beverage

# *** contexts

# ** context: beverage_context
class BeverageContext(AppInterfaceContext):
    '''
    Low-level context for FOODIE_SPA backward-chaining inference (Goal C).

    Implements predicate-logic backward chaining (Lectures 9–10):
    - Goal: find suitable beverage
    - Facts: guest attributes (health_nut, allergies)
    - Rules: match against Beverage domain objects
    '''

    # * init
    def __init__(self, **kwargs):
        '''
        Initialize the BeverageContext.
        '''
        super().__init__(**kwargs)

    # * method: select_beverage
    def select_beverage(self, is_health_nut: bool = False, allergies: List[str] = None) -> Beverage:
        '''
        Main backward-chaining entry point for beverage selection.

        Produces the exact inference trace required by the project spec.

        :param is_health_nut: Guest is health-conscious.
        :type is_health_nut: bool
        :param allergies: List of allergens to avoid (e.g., ['citrus']).
        :type allergies: list[str]
        :return: Recommended Beverage.
        :rtype: Beverage
        '''
        allergies = allergies or []
        print("FOODIE_SPA backward-chaining inference started...")
        print(f"Goal: Find suitable beverage for guest (health_nut={is_health_nut}, allergies={allergies})")

        # Sample knowledge base (expandable via repo later)
        candidates = [
            Beverage.new(name="Carrot Juice", beverage_type="juice", brand="FreshRoots",
                         is_health_friendly=True, avoids_allergens="citrus"),
            Beverage.new(name="Corona Beer", beverage_type="beer", brand="Corona",
                         is_health_friendly=False, avoids_allergens=""),
            Beverage.new(name="Sparkling Water", beverage_type="water", brand="San Pellegrino",
                         is_health_friendly=True, avoids_allergens="citrus, gluten"),
            Beverage.new(name="Red Wine", beverage_type="wine", brand="Cabernet",
                         is_health_friendly=False, avoids_allergens=""),
        ]

        print("Rule: Check health-friendly requirement...")
        if is_health_nut:
            print("Fact: Guest is health nut → filter to health_friendly=True")

        print("Rule: Check allergy constraints...")
        for allergen in allergies:
            print(f"Fact: Avoid {allergen} → filter beverages that avoid it")

        # Backward chaining match
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

    # * method: simulate_sample_guest
    def simulate_sample_guest(self) -> Beverage:
        '''
        Convenience method for the exact example in the project spec.
        (health nut with citrus allergy)
        '''
        print("=== FOODIE_SPA Sample Guest Simulation ===")
        return self.select_beverage(
            is_health_nut=True,
            allergies=["citrus"]
        )