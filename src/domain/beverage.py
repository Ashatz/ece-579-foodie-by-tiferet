'''FOODIE Beverage Domain Model'''

# *** imports

# ** core
from typing import Literal

# ** infra
from pydantic import Field
from tiferet import DomainObject


# *** models

# ** model: beverage
class Beverage(DomainObject):
    '''
    Represents a beverage recommendation for the FOODIE_SPA backward-chaining expert system.
    '''

    # * attribute: name
    name: str = Field(
        ...,
        description='Display name.',
    )

    # * attribute: beverage_type
    beverage_type: Literal['water', 'juice', 'wine', 'beer', 'liquor'] = Field(
        ...,
        description='Category for inference rules.',
    )

    # * attribute: brand
    brand: str = Field(
        ...,
        description='Specific brand.',
    )

    # * attribute: is_health_friendly
    is_health_friendly: bool = Field(
        default=False,
        description='Whether the beverage is health-friendly.',
    )

    # * attribute: avoids_allergens
    avoids_allergens: str = Field(
        default='',
        description='Comma-separated allergen list.',
    )

    # * method: matches_guest
    def matches_guest(self, is_health_nut: bool, allergies: list[str] | None) -> bool:
        '''
        Check health-nut and allergy rules for guest compatibility.

        :param is_health_nut: Whether the guest requires health-friendly options.
        :type is_health_nut: bool
        :param allergies: List of guest allergens to avoid, or None.
        :type allergies: list[str] | None
        :return: True if beverage satisfies all guest constraints.
        :rtype: bool
        '''

        # Reject if guest is a health nut and beverage is not health-friendly.
        if is_health_nut and not self.is_health_friendly:
            return False

        # Check allergy constraints if any.
        if allergies:

            # Parse the beverage's avoided allergens.
            avoided = {a.strip().lower() for a in self.avoids_allergens.split(',') if a.strip()}

            # Reject if any guest allergy is not in the avoided set.
            for allergy in allergies:
                if allergy.strip().lower() not in avoided:
                    return False

        # All constraints satisfied.
        return True

    # * method: format_for_trace
    def format_for_trace(self) -> str:
        '''
        Format the beverage for trace display.

        :return: Formatted string with name, brand, type, and optional flag annotations.
        :rtype: str
        '''

        # Build the flags list.
        flags = []
        if self.is_health_friendly:
            flags.append('health-friendly')
        if self.avoids_allergens:
            flags.append(f'avoids: {self.avoids_allergens}')

        # Build the flag annotation.
        flag_str = f' ({", ".join(flags)})' if flags else ''

        # Return the formatted string.
        return f'Selected {self.name} ({self.brand}) [{self.beverage_type}]{flag_str}'
