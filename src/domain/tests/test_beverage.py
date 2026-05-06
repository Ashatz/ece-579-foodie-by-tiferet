'''FOODIE Beverage Domain Model Tests'''

# *** imports

# ** infra
import pytest

# ** app
from ..beverage import Beverage


# *** fixtures

# ** fixture: default_beverage
@pytest.fixture
def default_beverage() -> Beverage:
    '''
    Create a Beverage with only required fields, relying on defaults.

    :return: A Beverage instance with default optional values.
    :rtype: Beverage
    '''
    return Beverage(name='Tap Water', beverage_type='water', brand='City Water')


# ** fixture: health_beverage
@pytest.fixture
def health_beverage() -> Beverage:
    '''
    Create a health-friendly Beverage that avoids common allergens.

    :return: A Beverage instance with health-friendly and allergen avoidance.
    :rtype: Beverage
    '''
    return Beverage(
        name='Green Juice',
        beverage_type='juice',
        brand='Organic Co',
        is_health_friendly=True,
        avoids_allergens='gluten, dairy',
    )


# *** tests

# ** test: beverage_instantiation_defaults
def test_beverage_instantiation_defaults(default_beverage: Beverage) -> None:
    '''
    Test that a Beverage created with only required fields has correct defaults.

    :param default_beverage: Beverage fixture with defaults.
    :type default_beverage: Beverage
    '''

    # Assert required fields are set.
    assert default_beverage.name == 'Tap Water'
    assert default_beverage.beverage_type == 'water'
    assert default_beverage.brand == 'City Water'

    # Assert optional fields have correct defaults.
    assert default_beverage.is_health_friendly is False
    assert default_beverage.avoids_allergens == ''


# ** test: beverage_instantiation_all_fields
def test_beverage_instantiation_all_fields(health_beverage: Beverage) -> None:
    '''
    Test that a Beverage created with all fields has correct values.

    :param health_beverage: Beverage fixture with all fields.
    :type health_beverage: Beverage
    '''

    # Assert all fields are set correctly.
    assert health_beverage.name == 'Green Juice'
    assert health_beverage.beverage_type == 'juice'
    assert health_beverage.brand == 'Organic Co'
    assert health_beverage.is_health_friendly is True
    assert health_beverage.avoids_allergens == 'gluten, dairy'


# ** test: beverage_matches_guest_no_constraints
def test_beverage_matches_guest_no_constraints(default_beverage: Beverage) -> None:
    '''
    Test matches_guest with no constraints (not health nut, no allergies).

    :param default_beverage: Beverage fixture with defaults.
    :type default_beverage: Beverage
    '''

    # Assert any beverage matches when there are no constraints.
    assert default_beverage.matches_guest(is_health_nut=False, allergies=None) is True


# ** test: beverage_matches_guest_health_nut_rejects
def test_beverage_matches_guest_health_nut_rejects(default_beverage: Beverage) -> None:
    '''
    Test matches_guest rejects non-health-friendly beverage for health nut.

    :param default_beverage: Beverage fixture (not health-friendly).
    :type default_beverage: Beverage
    '''

    # Assert a non-health-friendly beverage is rejected for a health nut.
    assert default_beverage.matches_guest(is_health_nut=True, allergies=None) is False


# ** test: beverage_matches_guest_health_nut_accepts
def test_beverage_matches_guest_health_nut_accepts(health_beverage: Beverage) -> None:
    '''
    Test matches_guest accepts health-friendly beverage for health nut.

    :param health_beverage: Beverage fixture (health-friendly).
    :type health_beverage: Beverage
    '''

    # Assert a health-friendly beverage is accepted for a health nut.
    assert health_beverage.matches_guest(is_health_nut=True, allergies=None) is True


# ** test: beverage_matches_guest_allergy_satisfied
def test_beverage_matches_guest_allergy_satisfied(health_beverage: Beverage) -> None:
    '''
    Test matches_guest when beverage avoids the guest's allergy.

    :param health_beverage: Beverage fixture avoiding gluten and dairy.
    :type health_beverage: Beverage
    '''

    # Assert the beverage matches when allergy is in the avoided set.
    assert health_beverage.matches_guest(is_health_nut=False, allergies=['gluten']) is True


# ** test: beverage_matches_guest_allergy_not_satisfied
def test_beverage_matches_guest_allergy_not_satisfied(default_beverage: Beverage) -> None:
    '''
    Test matches_guest rejects when beverage does not avoid the guest's allergy.

    :param default_beverage: Beverage fixture with no allergen avoidance.
    :type default_beverage: Beverage
    '''

    # Assert the beverage is rejected when allergy is not in the avoided set.
    assert default_beverage.matches_guest(is_health_nut=False, allergies=['nuts']) is False


# ** test: beverage_matches_guest_multiple_allergies
def test_beverage_matches_guest_multiple_allergies(health_beverage: Beverage) -> None:
    '''
    Test matches_guest with multiple allergies, all satisfied.

    :param health_beverage: Beverage fixture avoiding gluten and dairy.
    :type health_beverage: Beverage
    '''

    # Assert both allergies are satisfied.
    assert health_beverage.matches_guest(is_health_nut=False, allergies=['gluten', 'dairy']) is True


# ** test: beverage_matches_guest_combined_constraints
def test_beverage_matches_guest_combined_constraints(health_beverage: Beverage) -> None:
    '''
    Test matches_guest with both health-nut and allergy constraints.

    :param health_beverage: Beverage fixture (health-friendly, avoids gluten and dairy).
    :type health_beverage: Beverage
    '''

    # Assert beverage satisfies both health-nut and allergy constraints.
    assert health_beverage.matches_guest(is_health_nut=True, allergies=['dairy']) is True


# ** test: beverage_format_for_trace_plain
def test_beverage_format_for_trace_plain(default_beverage: Beverage) -> None:
    '''
    Test format_for_trace with no flags.

    :param default_beverage: Beverage fixture with defaults.
    :type default_beverage: Beverage
    '''

    # Assert the formatted string has no flag annotations.
    assert default_beverage.format_for_trace() == 'Selected Tap Water (City Water) [water]'


# ** test: beverage_format_for_trace_with_flags
def test_beverage_format_for_trace_with_flags(health_beverage: Beverage) -> None:
    '''
    Test format_for_trace with health-friendly and allergen flags.

    :param health_beverage: Beverage fixture with flags.
    :type health_beverage: Beverage
    '''

    # Assert the formatted string includes flag annotations.
    expected = 'Selected Green Juice (Organic Co) [juice] (health-friendly, avoids: gluten, dairy)'
    assert health_beverage.format_for_trace() == expected
