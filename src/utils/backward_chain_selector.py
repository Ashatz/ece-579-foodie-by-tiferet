"""
FOODIE Backward-Chain Selector Utility

Concrete implementation of BeverageSelectService.
Encapsulates the rule-based backward-chaining inference engine for
beverage selection (Goal C of the project spec).
"""

# *** imports

# ** core
from typing import Dict, List, Any

# ** app
from ..mappers.beverage import BeverageAggregate
from ..interfaces.beverage_select import BeverageSelectService

# *** utils

# ** util: backward_chain_selector
class BackwardChainSelector(BeverageSelectService):
    '''
    Backward-chaining inference engine for beverage selection.

    Evaluates each candidate beverage as a hypothesis, chaining
    backward through the supplied rule base to find the first
    candidate whose CHOOSE conclusion can be established from
    the given guest facts.
    '''

    # * method: select
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

        print('FOODIE_SPA backward-chaining inference started...')
        print(f'Known facts: {facts}')
        print()

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

        # No candidate matched any rule.
        return None

    # * method: _backward_chain
    def _backward_chain(
        self,
        goal: str,
        beverage: BeverageAggregate,
        facts: Dict[str, Any],
        rules: List[Dict[str, Any]],
        depth: int = 0,
    ) -> bool:
        '''
        Backward chain to establish the given goal.

        :param goal: The goal to establish (e.g., "CHOOSE Carrot Juice").
        :type goal: str
        :param beverage: The candidate beverage being tested.
        :type beverage: BeverageAggregate
        :param facts: Known facts.
        :type facts: Dict[str, Any]
        :param rules: The rule base.
        :type rules: List[Dict[str, Any]]
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
