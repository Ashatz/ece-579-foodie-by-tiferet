"""
FOODIE Item Domain Model

Represents a single food item in an order (used by FOODIE_BAGGER and route planning).
"""

# *** imports

# ** core
from tiferet import DomainObject, StringType, BooleanType, IntType

# *** models

# ** model: item
class Item(DomainObject):
    '''
    A food item for bagging, delivery, and inventory.

    Used by the rule-based production system (Goal B) and order planning (Goal A).
    '''

    # * attribute: name
    name = StringType(required=True, metadata={'description': 'Item name or description'})

    # * attribute: size
    size = StringType(
        required=True,
        choices=['large', 'medium', 'small'],
        metadata={'description': 'Size category for bagging priority'}
    )

    # * attribute: is_frozen
    is_frozen = BooleanType(default=False)

    # * attribute: is_fragile
    is_fragile = BooleanType(default=False)

    # * attribute: quantity
    quantity = IntType(default=1, min_value=1)

    # * method: new (static)
    @staticmethod
    def new(name: str, size: str, is_frozen: bool = False, is_fragile: bool = False, quantity: int = 1, **kwargs):
        '''
        Factory for creating a new Item (Tiferet DomainObject pattern).

        :param name: Item name.
        :type name: str
        :param size: Size category (large/medium/small).
        :type size: str
        :param is_frozen: Whether the item requires a freezer bag.
        :type is_frozen: bool
        :param is_fragile: Whether the item must not be crushed.
        :type is_fragile: bool
        :param quantity: Number of identical items.
        :type quantity: int
        '''
        return DomainObject.new(
            model_type=Item,
            name=name,
            size=size,
            is_frozen=is_frozen,
            is_fragile=is_fragile,
            quantity=quantity,
            **kwargs
        )

    # * method: format_for_bagger
    def format_for_bagger(self) -> str:
        '''
        Human-readable string for simulation trace (Goal B).

        :return: Formatted description for rule-firing trace.
        :rtype: str
        '''
        flags = []
        if self.is_frozen:
            flags.append("frozen")
        if self.is_fragile:
            flags.append("fragile")
        flag_str = f" ({', '.join(flags)})" if flags else ""
        return f"{self.quantity}x {self.name}{flag_str} [{self.size}]"