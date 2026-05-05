"""
FOODIE Beverage Domain Model Tests
"""

# *** imports

# ** infra
import pytest

# ** app
from ..beverage import Beverage

# *** fixtures

# ** fixture: health_beverage
@pytest.fixture
def health_beverage() -> Beverage:
    '''
    A health-friendly beverage that avoids gluten.

    :return: A health-friendly Beverage instance.
    :rtype: Beverage
    '''

    return Beverage(
        name='FreshRoots Juice',
        beverage_type='juice',
        brand='FreshRoots',
        is_health_friendly=True,
        avoids_allergens='gluten, dairy',
    )


# ** fixture: regular_beverage
@pytest.fixture
def regular_beverage() -> Beverage:
    '''
    A regular beverage with no special properties.

    :return: A regular Beverage instance.
    :rtype: Beverage
    '''

    return Beverage(
        name='Corona',
        beverage_type='beer',
        brand='Corona',
    )


# *** tests

# ** test: instantiation_defaults
def test_instantiation_defaults(regular_beverage: Beverage) -> None:
    '''
    Test that default field values are applied correctly.

    :param regular_beverage: A regular Beverage instance.
    :type regular_beverage: Beverage
    '''

    assert regular_beverage.name == 'Corona'
    assert regular_beverage.beverage_type == 'beer'
    assert regular_beverage.brand == 'Corona'
    assert regular_beverage.is_health_friendly is False
    assert regular_beverage.avoids_allergens == ''


# ** test: instantiation_all_fields
def test_instantiation_all_fields(health_beverage: Beverage) -> None:
    '''
    Test that all fields can be set explicitly.

    :param health_beverage: A health-friendly Beverage instance.
    :type health_beverage: Beverage
    '''

    assert health_beverage.name == 'FreshRoots Juice'
    assert health_beverage.beverage_type == 'juice'
    assert health_beverage.brand == 'FreshRoots'
    assert health_beverage.is_health_friendly is True
    assert health_beverage.avoids_allergens == 'gluten, dairy'


# ** test: matches_guest_no_constraints
def test_matches_guest_no_constraints(regular_beverage: Beverage) -> None:
    '''
    Test that a regular beverage matches a guest with no constraints.

    :param regular_beverage: A regular Beverage instance.
    :type regular_beverage: Beverage
    '''

    assert regular_beverage.matches_guest() is True


# ** test: matches_guest_health_nut_rejects
def test_matches_guest_health_nut_rejects(regular_beverage: Beverage) -> None:
    '''
    Test that a non-health-friendly beverage is rejected for health-nut guests.

    :param regular_beverage: A regular Beverage instance.
    :type regular_beverage: Beverage
    '''

    assert regular_beverage.matches_guest(is_health_nut=True) is False


# ** test: matches_guest_health_nut_accepts
def test_matches_guest_health_nut_accepts(health_beverage: Beverage) -> None:
    '''
    Test that a health-friendly beverage is accepted for health-nut guests.

    :param health_beverage: A health-friendly Beverage instance.
    :type health_beverage: Beverage
    '''

    assert health_beverage.matches_guest(is_health_nut=True) is True


# ** test: matches_guest_allergy_satisfied
def test_matches_guest_allergy_satisfied(health_beverage: Beverage) -> None:
    '''
    Test that a beverage matching allergen avoidance satisfies allergy constraints.

    :param health_beverage: A health-friendly Beverage instance.
    :type health_beverage: Beverage
    '''

    assert health_beverage.matches_guest(allergies=['gluten']) is True


# ** test: matches_guest_allergy_not_satisfied
def test_matches_guest_allergy_not_satisfied(health_beverage: Beverage) -> None:
    '''
    Test that a beverage is rejected when it does not avoid the required allergen.

    :param health_beverage: A health-friendly Beverage instance.
    :type health_beverage: Beverage
    '''

    assert health_beverage.matches_guest(allergies=['nuts']) is False


# ** test: matches_guest_multiple_allergies
def test_matches_guest_multiple_allergies(health_beverage: Beverage) -> None:
    '''
    Test matching with multiple allergies (all must be avoided).

    :param health_beverage: A health-friendly Beverage instance.
    :type health_beverage: Beverage
    '''

    assert health_beverage.matches_guest(allergies=['gluten', 'dairy']) is True
    assert health_beverage.matches_guest(allergies=['gluten', 'nuts']) is False


# ** test: matches_guest_combined_constraints
def test_matches_guest_combined_constraints(health_beverage: Beverage) -> None:
    '''
    Test matching with both health-nut and allergy constraints combined.

    :param health_beverage: A health-friendly Beverage instance.
    :type health_beverage: Beverage
    '''

    assert health_beverage.matches_guest(is_health_nut=True, allergies=['gluten']) is True
    assert health_beverage.matches_guest(is_health_nut=True, allergies=['nuts']) is False


# ** test: format_for_trace_plain
def test_format_for_trace_plain(regular_beverage: Beverage) -> None:
    '''
    Test format_for_trace with no flags.

    :param regular_beverage: A regular Beverage instance.
    :type regular_beverage: Beverage
    '''

    result = regular_beverage.format_for_trace()

    assert result == 'Selected Corona (Corona) [beer]'


# ** test: format_for_trace_with_flags
def test_format_for_trace_with_flags(health_beverage: Beverage) -> None:
    '''
    Test format_for_trace with health-friendly and allergen flags.

    :param health_beverage: A health-friendly Beverage instance.
    :type health_beverage: Beverage
    '''

    result = health_beverage.format_for_trace()

    assert result == 'Selected FreshRoots Juice (FreshRoots) [juice] (health-friendly, avoids:gluten, dairy)'
