"""
FOODIE Beverage Domain Model

Represents a beverage that can be added to an order.
Used by the backward-chaining FOODIE_SPA expert module (Goal C).
"""

# *** imports

# ** core
from typing import Literal, List

# ** infra
from pydantic import Field
from tiferet import DomainObject

# *** models

# ** model: beverage
class Beverage(DomainObject):
    '''
    A beverage recommendation for unexpected guests (Goal C).

    Supports backward chaining: guest facts (health nut, allergies)
    -> appropriate beverage type and brand.
    '''

    # * attribute: name
    name: str = Field(..., description='Display name of the beverage')

    # * attribute: beverage_type
    beverage_type: Literal['water', 'juice', 'wine', 'beer', 'liquor'] = Field(
        ...,
        description='High-level category used by inference rules',
    )

    # * attribute: brand
    brand: str = Field(..., description='Specific brand (e.g., Corona, FreshRoots)')

    # * attribute: is_health_friendly
    is_health_friendly: bool = Field(default=False, description='Suitable for health-conscious guests')

    # * attribute: avoids_allergens
    avoids_allergens: str = Field(
        default='',
        description='Comma-separated list of allergens this beverage avoids',
    )

    # * method: matches_guest
    def matches_guest(self, is_health_nut: bool = False, allergies: List[str] | None = None) -> bool:
        '''
        Backward-chaining helper: checks if this beverage satisfies guest facts.

        :param is_health_nut: Whether the guest is health-conscious.
        :type is_health_nut: bool
        :param allergies: List of allergens to avoid.
        :type allergies: list[str] | None
        :return: True if the beverage is appropriate for the guest.
        :rtype: bool
        '''

        allergies = allergies or []

        # Health-nut rule.
        if is_health_nut and not self.is_health_friendly:
            return False

        # Allergy rule: beverage must avoid every listed allergen.
        avoided = [a.strip().lower() for a in self.avoids_allergens.split(',') if a.strip()]
        for allergen in allergies:
            if allergen.lower() not in avoided:
                return False

        # All rules satisfied.
        return True

    # * method: format_for_trace
    def format_for_trace(self) -> str:
        '''
        Human-readable string for backward-chaining simulation trace (Goal C).

        :return: Formatted recommendation line.
        :rtype: str
        '''

        # Build optional flag annotations.
        flags = []
        if self.is_health_friendly:
            flags.append('health-friendly')
        if self.avoids_allergens:
            flags.append(f'avoids:{self.avoids_allergens}')
        flag_str = f" ({', '.join(flags)})" if flags else ''

        # Return the formatted string.
        return f'Selected {self.name} ({self.brand}) [{self.beverage_type}]{flag_str}'
