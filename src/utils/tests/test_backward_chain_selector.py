"""
FOODIE BackwardChainSelector Utility Tests
"""

# *** imports

# ** infra
import pytest

# ** app
from ...mappers.beverage import BeverageAggregate
from ..backward_chain_selector import BackwardChainSelector

# *** fixtures

# ** fixture: selector
@pytest.fixture
def selector() -> BackwardChainSelector:
    '''
    Create a BackwardChainSelector instance.

    :return: The selector utility.
    :rtype: BackwardChainSelector
    '''

    return BackwardChainSelector()


# ** fixture: sample_rules
@pytest.fixture
def sample_rules():
    '''
    A minimal rule base for testing backward chaining.

    :return: List of rule dictionaries.
    :rtype: list[dict]
    '''

    return [
        {'id': 'R8', 'conclusion': 'JUICE is indicated',
         'conditions': [('health_nut', True)],
         'beverage_type': 'juice'},

        {'id': 'R9', 'conclusion': 'CHOOSE Carrot Juice',
         'conditions': [('JUICE is indicated', True), ('allergies_citrus', True)],
         'beverage_type': 'juice'},

        {'id': 'R10', 'conclusion': 'CHOOSE Orange Juice',
         'conditions': [('JUICE is indicated', True), ('allergies_citrus', False)],
         'beverage_type': 'juice'},

        {'id': 'R3', 'conclusion': 'BEER is indicated',
         'conditions': [('occasion', 'casual'), ('guest_age', 'adult')],
         'beverage_type': 'beer'},

        {'id': 'R5', 'conclusion': 'CHOOSE Corona Beer',
         'conditions': [('BEER is indicated', True), ('setting', 'outdoor')],
         'beverage_type': 'beer'},
    ]


# ** fixture: carrot_juice
@pytest.fixture
def carrot_juice() -> BeverageAggregate:
    '''
    Carrot Juice candidate beverage.

    :return: A BeverageAggregate for Carrot Juice.
    :rtype: BeverageAggregate
    '''

    return BeverageAggregate(
        name='Carrot Juice',
        beverage_type='juice',
        brand='FreshRoots',
        is_health_friendly=True,
        avoids_allergens='citrus',
    )


# ** fixture: corona_beer
@pytest.fixture
def corona_beer() -> BeverageAggregate:
    '''
    Corona Beer candidate beverage.

    :return: A BeverageAggregate for Corona Beer.
    :rtype: BeverageAggregate
    '''

    return BeverageAggregate(
        name='Corona Beer',
        beverage_type='beer',
        brand='Corona',
        is_health_friendly=False,
    )


# *** tests

# ** test: select_exact_match
def test_select_exact_match(
    selector: BackwardChainSelector,
    sample_rules: list,
    carrot_juice: BeverageAggregate,
) -> None:
    '''
    Test that backward chaining selects Carrot Juice for a health nut with citrus allergy.

    :param selector: The selector utility.
    :type selector: BackwardChainSelector
    :param sample_rules: The test rule base.
    :type sample_rules: list
    :param carrot_juice: The Carrot Juice candidate.
    :type carrot_juice: BeverageAggregate
    '''

    facts = {'health_nut': True, 'allergies_citrus': True}
    result = selector.select([carrot_juice], facts, sample_rules)

    assert result is carrot_juice


# ** test: select_rule_chaining
def test_select_rule_chaining(
    selector: BackwardChainSelector,
    sample_rules: list,
    corona_beer: BeverageAggregate,
) -> None:
    '''
    Test that intermediate conclusions chain correctly
    (BEER is indicated -> CHOOSE Corona Beer).

    :param selector: The selector utility.
    :type selector: BackwardChainSelector
    :param sample_rules: The test rule base.
    :type sample_rules: list
    :param corona_beer: The Corona Beer candidate.
    :type corona_beer: BeverageAggregate
    '''

    facts = {'occasion': 'casual', 'guest_age': 'adult', 'setting': 'outdoor'}
    result = selector.select([corona_beer], facts, sample_rules)

    assert result is corona_beer


# ** test: select_no_match_returns_none
def test_select_no_match_returns_none(
    selector: BackwardChainSelector,
    sample_rules: list,
    carrot_juice: BeverageAggregate,
) -> None:
    '''
    Test that select returns None when no rule fires for any candidate.

    :param selector: The selector utility.
    :type selector: BackwardChainSelector
    :param sample_rules: The test rule base.
    :type sample_rules: list
    :param carrot_juice: The Carrot Juice candidate (won't match given facts).
    :type carrot_juice: BeverageAggregate
    '''

    facts = {'occasion': 'formal_dinner'}
    result = selector.select([carrot_juice], facts, sample_rules)

    assert result is None


# ** test: select_empty_candidates
def test_select_empty_candidates(
    selector: BackwardChainSelector,
    sample_rules: list,
) -> None:
    '''
    Test that select returns None when no candidates are provided.

    :param selector: The selector utility.
    :type selector: BackwardChainSelector
    :param sample_rules: The test rule base.
    :type sample_rules: list
    '''

    facts = {'health_nut': True, 'allergies_citrus': True}
    result = selector.select([], facts, sample_rules)

    assert result is None


# ** test: select_first_matching_candidate
def test_select_first_matching_candidate(
    selector: BackwardChainSelector,
    sample_rules: list,
    carrot_juice: BeverageAggregate,
    corona_beer: BeverageAggregate,
) -> None:
    '''
    Test that the first matching candidate is returned when multiple are provided.

    :param selector: The selector utility.
    :type selector: BackwardChainSelector
    :param sample_rules: The test rule base.
    :type sample_rules: list
    :param carrot_juice: The Carrot Juice candidate.
    :type carrot_juice: BeverageAggregate
    :param corona_beer: The Corona Beer candidate.
    :type corona_beer: BeverageAggregate
    '''

    facts = {'health_nut': True, 'allergies_citrus': True}
    result = selector.select([carrot_juice, corona_beer], facts, sample_rules)

    # Carrot Juice is first and matches the facts.
    assert result is carrot_juice
