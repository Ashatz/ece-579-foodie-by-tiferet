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
from typing import List, Dict, Any

# ** infra
from tiferet.events import DomainEvent

# ** app
from ..domain import Beverage

# *** events

# ** event: select_beverage
class SelectBeverage(DomainEvent):
    '''
    Backward-chaining event for FOODIE_SPA beverage selection (Goal C).

    Implements a rule-based backward chaining system (max 15 rules)
    that selects the right beverage for unexpected guests.
    '''

    # * method: execute
    def execute(self, **kwargs) -> Beverage:
        '''
        Select the best beverage using backward chaining on guest facts.

        :param candidates: List of available Beverage objects.
        :type candidates: list[Beverage]
        :param facts: Dict of known guest facts (e.g., health_nut, allergies, occasion, etc.).
        :type facts: dict
        :return: The selected beverage.
        :rtype: Beverage
        '''

        candidates: List[Beverage] = kwargs['candidates']
        facts: Dict[str, Any] = kwargs.get('facts', {})

        print('FOODIE_SPA backward-chaining inference started...')
        print(f'Known facts: {facts}')
        print()

        # Build the rule base (max 15 rules per spec).
        rules = self._build_rule_base()

        # Try each candidate beverage as a hypothesis.
        for bev in candidates:
            hypothesis = f'CHOOSE {bev.name}'
            print(f'Trying to establish {hypothesis} using rules...')

            if self._backward_chain(hypothesis, bev, facts, rules):
                print(f'\n{hypothesis} is True.')
                print(f'{bev.format_for_trace()}')
                print('Backward chaining successful -> beverage selected.')
                return bev

            print()

        # Fallback: Sparkling Water is always safe.
        fallback = Beverage(
            name='Sparkling Water',
            beverage_type='water',
            brand='San Pellegrino',
            is_health_friendly=True,
        )
        print(f'No perfect match -> using safe fallback.')
        print(f'{fallback.format_for_trace()}')
        return fallback

    # * method: _build_rule_base
    def _build_rule_base(self) -> List[Dict[str, Any]]:
        '''
        Build the rule base for backward chaining (max 15 rules per spec).

        Each rule has:
        - id: rule identifier
        - conclusion: what this rule establishes
        - conditions: list of (fact_key, expected_value) pairs
        - beverage_type: which beverage category this rule applies to

        :return: List of rule dictionaries.
        :rtype: list[dict]
        '''

        return [
            # R1: Liquor rules
            {'id': 'R1', 'conclusion': 'LIQUOR is indicated',
             'conditions': [('occasion', 'celebration'), ('guest_age', 'adult')],
             'beverage_type': 'liquor'},

            # R2: Specific liquor - Polish Vodka for formal celebration
            {'id': 'R2', 'conclusion': 'CHOOSE Polish Vodka',
             'conditions': [('LIQUOR is indicated', True), ('formality', 'formal')],
             'beverage_type': 'liquor'},

            # R3: Beer rules
            {'id': 'R3', 'conclusion': 'BEER is indicated',
             'conditions': [('occasion', 'casual'), ('guest_age', 'adult')],
             'beverage_type': 'beer'},

            # R4: Specific beer - Dos Equis for casual adult gathering
            {'id': 'R4', 'conclusion': 'CHOOSE Dos Equis',
             'conditions': [('BEER is indicated', True)],
             'beverage_type': 'beer'},

            # R5: Specific beer - Corona for summer/outdoor
            {'id': 'R5', 'conclusion': 'CHOOSE Corona Beer',
             'conditions': [('BEER is indicated', True), ('setting', 'outdoor')],
             'beverage_type': 'beer'},

            # R6: Wine rules
            {'id': 'R6', 'conclusion': 'WINE is indicated',
             'conditions': [('entree', 'steak'), ('guest_age', 'adult')],
             'beverage_type': 'wine'},

            # R7: Wine for chicken dinner
            {'id': 'R7', 'conclusion': 'WINE is indicated',
             'conditions': [('entree', 'chicken'), ('guest_age', 'adult')],
             'beverage_type': 'wine'},

            # R8: Health-nut juice selection
            {'id': 'R8', 'conclusion': 'JUICE is indicated',
             'conditions': [('health_nut', True)],
             'beverage_type': 'juice'},

            # R9: Carrot juice for health nut with citrus allergy
            {'id': 'R9', 'conclusion': 'CHOOSE Carrot Juice',
             'conditions': [('JUICE is indicated', True), ('allergies_citrus', True)],
             'beverage_type': 'juice'},

            # R10: Orange juice for health nut without citrus allergy
            {'id': 'R10', 'conclusion': 'CHOOSE Orange Juice',
             'conditions': [('JUICE is indicated', True), ('allergies_citrus', False)],
             'beverage_type': 'juice'},

            # R11: Water as universal safe option
            {'id': 'R11', 'conclusion': 'WATER is indicated',
             'conditions': [('guest_age', 'minor')],
             'beverage_type': 'water'},

            # R12: Sparkling water for formal setting
            {'id': 'R12', 'conclusion': 'CHOOSE Sparkling Water',
             'conditions': [('WATER is indicated', True), ('formality', 'formal')],
             'beverage_type': 'water'},

            # R13: Guest not well liked -> cheap beer
            {'id': 'R13', 'conclusion': 'CHOOSE Cheap Beer',
             'conditions': [('guest_liked', False), ('guest_age', 'adult')],
             'beverage_type': 'beer'},

            # R14: New Year's Eve celebration -> champagne
            {'id': 'R14', 'conclusion': 'CHOOSE Champagne',
             'conditions': [('occasion', "new_years_eve"), ('guest_age', 'adult')],
             'beverage_type': 'liquor'},

            # R15: Default water for any remaining case
            {'id': 'R15', 'conclusion': 'CHOOSE Sparkling Water',
             'conditions': [],
             'beverage_type': 'water'},
        ]

    # * method: _backward_chain
    def _backward_chain(
        self,
        goal: str,
        beverage: Beverage,
        facts: Dict[str, Any],
        rules: List[Dict[str, Any]],
        depth: int = 0,
    ) -> bool:
        '''
        Backward chain to establish the given goal.

        :param goal: The goal to establish (e.g., "CHOOSE Carrot Juice").
        :type goal: str
        :param beverage: The candidate beverage being tested.
        :type beverage: Beverage
        :param facts: Known facts.
        :type facts: dict
        :param rules: The rule base.
        :type rules: list[dict]
        :param depth: Current recursion depth for indentation.
        :type depth: int
        :return: True if the goal can be established.
        :rtype: bool
        '''

        indent = '  ' * depth

        # Find rules whose conclusion matches this goal.
        matching_rules = [r for r in rules if r['conclusion'] == goal]

        for rule in matching_rules:

            # Skip rules that don't match the beverage type.
            if rule['beverage_type'] != beverage.beverage_type:
                continue

            print(f'{indent}Trying to establish {goal} using rule {rule["id"]}')

            # Check all conditions.
            all_satisfied = True
            for cond_key, cond_val in rule['conditions']:

                # If the condition is itself a conclusion, recurse.
                if cond_key.endswith('is indicated'):
                    if not self._backward_chain(cond_key, beverage, facts, rules, depth + 1):
                        print(f'{indent}  Rule {rule["id"]} fails to establish {cond_key}.')
                        all_satisfied = False
                        break
                else:
                    # Check against known facts.
                    if cond_key not in facts:
                        print(f'{indent}  Fact "{cond_key}" unknown — assuming False.')
                        all_satisfied = False
                        break

                    if facts[cond_key] != cond_val:
                        print(f'{indent}  Fact "{cond_key}" = {facts[cond_key]}, need {cond_val}. Failed.')
                        all_satisfied = False
                        break

                    print(f'{indent}  Fact "{cond_key}" = {cond_val}. OK.')

            if all_satisfied:
                print(f'{indent}Rule {rule["id"]} establishes {goal}.')
                return True

        return False
