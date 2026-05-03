"""
FOODIE Beverage Domain Model

Represents a beverage that can be added to an order.
Used by the backward-chaining FOODIE_SPA expert module (Goal C).
"""

# *** imports

# ** core
from tiferet import DomainObject, StringType, BooleanType

# *** models

# ** model: beverage
class Beverage(DomainObject):
    '''
    A beverage recommendation for unexpected guests (Goal C).

    Supports backward chaining: guest facts (health nut, allergies)
    → appropriate beverage type and brand.
    '''

    # * attribute: name
    name = StringType(required=True, metadata={'description': 'Display name of the beverage'})

    # * attribute: beverage_type
    beverage_type = StringType(
        required=True,
        choices=['water', 'juice', 'wine', 'beer', 'liquor'],
        metadata={'description': 'High-level category used by inference rules'}
    )

    # * attribute: brand
    brand = StringType(required=True, metadata={'description': 'Specific brand (e.g., Corona, carrot juice)'})

    # * attribute: is_health_friendly
    is_health_friendly = BooleanType(default=False, metadata={'description': 'Suitable for health-conscious guests'})

    # * attribute: avoids_allergens
    avoids_allergens = StringType(
        default='',
        metadata={'description': 'Comma-separated list of allergens this beverage avoids (e.g., citrus, gluten)'}
    )

    # * method: new (static)
    @staticmethod
    def new(name: str, beverage_type: str, brand: str,
            is_health_friendly: bool = False, avoids_allergens: str = '', **kwargs):
        '''
        Factory for creating a new Beverage (Tiferet DomainObject pattern).

        :param name: Display name.
        :type name: str
        :param beverage_type: Category (water/juice/wine/beer/liquor).
        :type beverage_type: str
        :param brand: Specific brand.
        :type brand: str
        '''
        return DomainObject.new(
            model_type=Beverage,
            name=name,
            beverage_type=beverage_type,
            brand=brand,
            is_health_friendly=is_health_friendly,
            avoids_allergens=avoids_allergens,
            **kwargs
        )

    # * method: matches_guest
    def matches_guest(self, is_health_nut: bool = False, allergies: list[str] = None) -> bool:
        '''
        Backward-chaining helper: checks if this beverage satisfies guest facts.

        :return: True if the beverage is appropriate for the guest.
        :rtype: bool
        '''
        allergies = allergies or []
        # Health-nut rule
        if is_health_nut and not self.is_health_friendly:
            return False
        # Allergy rule
        for allergen in allergies:
            if allergen.lower() in self.avoids_allergens.lower():
                return False
        return True

    # * method: format_for_trace
    def format_for_trace(self) -> str:
        '''
        Human-readable string for backward-chaining simulation trace (Goal C).

        :return: Formatted recommendation line.
        :rtype: str
        '''
        flags = []
        if self.is_health_friendly:
            flags.append("health-friendly")
        if self.avoids_allergens:
            flags.append(f"avoids:{self.avoids_allergens}")
        flag_str = f" ({', '.join(flags)})" if flags else ""
        return f"Selected {self.name} ({self.brand}) [{self.beverage_type}]{flag_str}"