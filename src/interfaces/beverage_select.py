"""
FOODIE Beverage Select Service Interface
"""

# *** imports

# ** core
from abc import abstractmethod
from typing import Dict, List, Any

# ** infra
from tiferet.interfaces import Service

# ** app
from ..mappers.beverage import BeverageAggregate

# *** interfaces

# ** interface: beverage_select_service
class BeverageSelectService(Service):
    '''
    Vertical interface for backward-chaining beverage selection.

    Accepts candidate beverages, guest facts, and a rule base;
    returns the best match or None when no rule fires.
    '''

    # * method: select
    @abstractmethod
    def select(
        self,
        candidates: List[BeverageAggregate],
        facts: Dict[str, Any],
        rules: List[Dict[str, Any]],
    ) -> BeverageAggregate | None:
        '''
        Select the best beverage from candidates using backward chaining.

        :param candidates: Available beverages to evaluate.
        :type candidates: List[BeverageAggregate]
        :param facts: Known guest facts (e.g., health_nut, allergies, occasion).
        :type facts: Dict[str, Any]
        :param rules: The backward-chaining rule base.
        :type rules: List[Dict[str, Any]]
        :return: The selected beverage, or None if no rule fires.
        :rtype: BeverageAggregate | None
        '''
        raise NotImplementedError()
