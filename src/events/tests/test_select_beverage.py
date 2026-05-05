"""
FOODIE SelectBeverage Domain Event Tests
"""

# *** imports

# ** core
from unittest import mock

# ** infra
import pytest
from tiferet.events import DomainEvent

# ** app
from ...mappers.beverage import BeverageAggregate
from ...interfaces import BeverageService
from ...interfaces.beverage_select import BeverageSelectService
from ..select_beverage import SelectBeverage

# *** fixtures

# ** fixture: sample_carrot_juice
@pytest.fixture
def sample_carrot_juice() -> BeverageAggregate:
    '''
    A sample BeverageAggregate for Carrot Juice.

    :return: BeverageAggregate instance.
    :rtype: BeverageAggregate
    '''

    return BeverageAggregate(
        name='Carrot Juice',
        beverage_type='juice',
        brand='FreshRoots',
        is_health_friendly=True,
        avoids_allergens='citrus',
    )


# ** fixture: mock_beverage_service
@pytest.fixture
def mock_beverage_service(sample_carrot_juice: BeverageAggregate) -> BeverageService:
    '''
    Mock BeverageService returning a list with the sample beverage.

    :param sample_carrot_juice: The sample beverage.
    :type sample_carrot_juice: BeverageAggregate
    :return: Mocked service.
    :rtype: BeverageService
    '''

    svc = mock.Mock(spec=BeverageService)
    svc.list.return_value = [sample_carrot_juice]
    return svc


# ** fixture: mock_select_service_match
@pytest.fixture
def mock_select_service_match(sample_carrot_juice: BeverageAggregate) -> BeverageSelectService:
    '''
    Mock BeverageSelectService that returns a matching beverage.

    :param sample_carrot_juice: The sample beverage to return.
    :type sample_carrot_juice: BeverageAggregate
    :return: Mocked service.
    :rtype: BeverageSelectService
    '''

    svc = mock.Mock(spec=BeverageSelectService)
    svc.select.return_value = sample_carrot_juice
    return svc


# ** fixture: mock_select_service_no_match
@pytest.fixture
def mock_select_service_no_match() -> BeverageSelectService:
    '''
    Mock BeverageSelectService that returns None (no match).

    :return: Mocked service.
    :rtype: BeverageSelectService
    '''

    svc = mock.Mock(spec=BeverageSelectService)
    svc.select.return_value = None
    return svc


# *** tests

# ** test: select_beverage_success
def test_select_beverage_success(
    mock_beverage_service: BeverageService,
    mock_select_service_match: BeverageSelectService,
    sample_carrot_juice: BeverageAggregate,
) -> None:
    '''
    Test successful beverage selection delegates to BeverageSelectService.

    :param mock_beverage_service: Mocked beverage service.
    :type mock_beverage_service: BeverageService
    :param mock_select_service_match: Mocked select service returning a match.
    :type mock_select_service_match: BeverageSelectService
    :param sample_carrot_juice: Expected result.
    :type sample_carrot_juice: BeverageAggregate
    '''

    # Act.
    result = DomainEvent.handle(
        SelectBeverage,
        dependencies={
            'beverage_service': mock_beverage_service,
            'beverage_select_service': mock_select_service_match,
        },
        facts={'health_nut': True, 'allergies_citrus': True},
    )

    # Assert: result is the matched beverage.
    assert result is sample_carrot_juice

    # Assert: beverage_service.list was called.
    mock_beverage_service.list.assert_called_once()

    # Assert: select was called with candidates, facts, and rules.
    mock_select_service_match.select.assert_called_once()
    call_args = mock_select_service_match.select.call_args
    assert call_args[0][0] == [sample_carrot_juice]  # candidates
    assert call_args[0][1] == {'health_nut': True, 'allergies_citrus': True}  # facts
    assert isinstance(call_args[0][2], list)  # rules


# ** test: select_beverage_fallback
def test_select_beverage_fallback(
    mock_beverage_service: BeverageService,
    mock_select_service_no_match: BeverageSelectService,
) -> None:
    '''
    Test fallback path when BeverageSelectService returns None.

    :param mock_beverage_service: Mocked beverage service.
    :type mock_beverage_service: BeverageService
    :param mock_select_service_no_match: Mocked select service returning None.
    :type mock_select_service_no_match: BeverageSelectService
    '''

    # Act.
    result = DomainEvent.handle(
        SelectBeverage,
        dependencies={
            'beverage_service': mock_beverage_service,
            'beverage_select_service': mock_select_service_no_match,
        },
        facts={'unknown_fact': 'value'},
    )

    # Assert: fallback is Sparkling Water.
    assert result.name == 'Sparkling Water'
    assert result.beverage_type == 'water'
    assert result.brand == 'San Pellegrino'
    assert result.is_health_friendly is True
    assert isinstance(result, BeverageAggregate)
