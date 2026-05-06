"""
FOODIE Item Domain Model

Represents a single food item in an order (used by FOODIE_BAGGER and route planning).
"""

# *** imports

# ** core
from typing import Literal

# ** infra
from pydantic import Field
from tiferet import DomainObject

# *** models

# ** model: item
class Item(DomainObject):
    '''
    A food item for bagging, delivery, and inventory.

    Used by the rule-based production system (Goal B) and order planning (Goal A).
    '''

    # * attribute: name
    name: str = Field(..., description='Item name or description')

    # * attribute: size
    size: Literal['large', 'medium', 'small'] = Field(
        ...,
        description='Size category for bagging priority',
    )

    # * attribute: is_frozen
    is_frozen: bool = Field(default=False, description='Whether the item requires a freezer bag')

    # * attribute: is_fragile
    is_fragile: bool = Field(default=False, description='Whether the item must not be crushed')

    # * attribute: quantity
    quantity: int = Field(default=1, ge=1, description='Number of identical items')

    # * method: format_for_bagger
    def format_for_bagger(self) -> str:
        '''
        Human-readable string for simulation trace (Goal B).

        :return: Formatted description for rule-firing trace.
        :rtype: str
        '''

        # Build optional flag annotations.
        flags = []
        if self.is_frozen:
            flags.append('frozen')
        if self.is_fragile:
            flags.append('fragile')
        flag_str = f" ({', '.join(flags)})" if flags else ''

        # Return the formatted string.
        return f'{self.quantity}x {self.name}{flag_str} [{self.size}]'
