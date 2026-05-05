"""
FOODIE SelectBeverage Domain Event

Implements backward-chaining inference for beverage selection (Goal C).

Backward Chaining (Lectures 9-10):
- Goal: determine the best beverage for an unexpected guest
- Rules: if-then knowledge base matching guest facts to beverage categories
- Inference: start from hypothesis, chain backward through rules, ask for missing facts
"""

# *** imports

# ** core
from typing import Dict, Any

# ** infra
from tiferet.events import DomainEvent

# ** app
from ..assets.beverage import BEVERAGE_RULES, FALLBACK_BEVERAGE
from ..mappers.beverage import BeverageAggregate
from ..interfaces import BeverageService
from ..interfaces.beverage_select import BeverageSelectService

# *** events

# ** event: select_beverage
class SelectBeverage(DomainEvent):
    '''
    Backward-chaining event for FOODIE_SPA beverage selection (Goal C).

    Loads candidate beverages, supplies the rule base from assets,
    and delegates inference to an injected BeverageSelectService.
    '''

    # * attribute: beverage_service
    beverage_service: BeverageService

    # * attribute: beverage_select_service
    beverage_select_service: BeverageSelectService

    # * init
    def __init__(self, beverage_service: BeverageService, beverage_select_service: BeverageSelectService):
        '''
        Initialize the SelectBeverage event.

        :param beverage_service: The beverage service for loading beverage candidates.
        :type beverage_service: BeverageService
        :param beverage_select_service: The selection service for backward-chaining inference.
        :type beverage_select_service: BeverageSelectService
        '''

        self.beverage_service = beverage_service
        self.beverage_select_service = beverage_select_service

    # * method: execute
    def execute(self, **kwargs) -> BeverageAggregate:
        '''
        Select the best beverage using backward chaining on guest facts.

        :param facts: Dict of known guest facts (e.g., health_nut, allergies, occasion, etc.).
        :type facts: dict
        :param kwargs: Additional keyword arguments.
        :type kwargs: dict
        :return: The selected beverage.
        :rtype: BeverageAggregate
        '''

        # Load candidate beverages from the service.
        candidates = self.beverage_service.list()

        # Parse facts from kwargs; accept dict or list of key=value strings (CLI).
        facts_input = kwargs.get('facts', {})
        if isinstance(facts_input, list):
            facts: Dict[str, Any] = {}
            for pair in facts_input:
                key, _, val = pair.partition('=')
                if val.lower() == 'true':
                    facts[key] = True
                elif val.lower() == 'false':
                    facts[key] = False
                else:
                    facts[key] = val
        else:
            facts = facts_input

        # Delegate backward-chaining inference to the select service.
        result = self.beverage_select_service.select(candidates, facts, BEVERAGE_RULES)

        # Return the result if a match was found.
        if result is not None:
            return result

        # Fallback: Sparkling Water is always safe.
        fallback = BeverageAggregate(**FALLBACK_BEVERAGE)
        print(f'No perfect match -> using safe fallback.')
        print(f'{fallback.format_for_trace()}')
        return fallback
