'''FOODIE Item Domain Model'''

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
    Represents a single food item consumed by FOODIE_BAGGER and order planning.
    '''

    # * attribute: name
    name: str = Field(
        ...,
        description='Item name or description.',
    )

    # * attribute: size
    size: Literal['large', 'medium', 'small'] = Field(
        ...,
        description='Item size determining bagging priority.',
    )

    # * attribute: is_frozen
    is_frozen: bool = Field(
        default=False,
        description='Routes item to freezer bags.',
    )

    # * attribute: is_fragile
    is_fragile: bool = Field(
        default=False,
        description='Forces a new bag to prevent crushing.',
    )

    # * attribute: quantity
    quantity: int = Field(
        default=1,
        ge=1,
        description='Number of identical items.',
    )

    # * method: format_for_bagger
    def format_for_bagger(self) -> str:
        '''
        Format the item for bagger display.

        :return: Formatted string with quantity, name, flags, and size.
        :rtype: str
        '''

        # Build the flags list.
        flags = []
        if self.is_frozen:
            flags.append('frozen')
        if self.is_fragile:
            flags.append('fragile')

        # Build the flag annotation.
        flag_str = f' ({", ".join(flags)})' if flags else ''

        # Return the formatted string.
        return f'{self.quantity}x {self.name}{flag_str} [{self.size}]'
