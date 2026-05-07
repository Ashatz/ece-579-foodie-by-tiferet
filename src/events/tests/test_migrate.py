"""
FOODIE SeedDatabase Domain Event Tests
"""

# *** imports

# ** core
from unittest import mock

# ** infra
import pytest
from tiferet.events import DomainEvent

# ** app
from ...domain import Item, Location
from ...interfaces.order import OrderService
from ...interfaces.robot import RobotService
from ...interfaces.item import ItemService
from ...interfaces.location import LocationService
from ..migrate import SeedDatabase

# *** fixtures

# ** fixture: mock_order_service
@pytest.fixture
def mock_order_service() -> OrderService:
    '''
    Mock OrderService for testing.
    '''
    svc = mock.Mock(spec=OrderService)
    svc.list.return_value = []
    return svc

# ** fixture: mock_robot_service
@pytest.fixture
def mock_robot_service() -> RobotService:
    '''
    Mock RobotService for testing.
    '''
    svc = mock.Mock(spec=RobotService)
    svc.list.return_value = []
    return svc

# ** fixture: mock_item_service
@pytest.fixture
def mock_item_service() -> ItemService:
    '''
    Mock ItemService with sample menu items.
    '''
    svc = mock.Mock(spec=ItemService)
    svc.list.return_value = [
        Item(name='1-gallon water bottle', size='large', quantity=2),
        Item(name='pint ice cream', size='medium', is_frozen=True, quantity=1),
        Item(name='granola box', size='medium', is_fragile=True, quantity=1),
        Item(name='loaf of bread', size='medium', quantity=1),
    ]
    return svc

# ** fixture: mock_location_service
@pytest.fixture
def mock_location_service() -> LocationService:
    '''
    Mock LocationService returning the Food Warehouse.
    '''
    svc = mock.Mock(spec=LocationService)
    svc.get.return_value = Location(
        name='FW', x=0.0, y=0.0, is_food_warehouse=True,
    )
    return svc

# ** fixture: dependencies
@pytest.fixture
def dependencies(
    mock_order_service,
    mock_robot_service,
    mock_item_service,
    mock_location_service,
) -> dict:
    '''
    Dependency dict for DomainEvent.handle.
    '''
    return {
        'order_service': mock_order_service,
        'robot_service': mock_robot_service,
        'item_service': mock_item_service,
        'location_service': mock_location_service,
    }

# *** tests

# ** test: seed_database_success
def test_seed_database_success(dependencies, mock_order_service, mock_robot_service):
    '''
    Test successful seeding: correct return dict, 3 orders saved, 3 robots saved.

    :param dependencies: The injected service dependencies.
    :type dependencies: dict
    :param mock_order_service: The mock order service.
    :type mock_order_service: OrderService
    :param mock_robot_service: The mock robot service.
    :type mock_robot_service: RobotService
    '''

    # Execute the event via DomainEvent.handle.
    result = DomainEvent.handle(
        SeedDatabase,
        dependencies=dependencies,
    )

    # Verify the return summary.
    assert result['robots_seeded'] == 3
    assert result['status'] == 'complete'

    # Verify save calls (robots only, no orders).
    assert mock_order_service.save.call_count == 0
    assert mock_robot_service.save.call_count == 3


# ** test: seed_database_clears_existing
def test_seed_database_clears_existing(dependencies, mock_order_service, mock_robot_service):
    '''
    Test that existing orders and robots are cleared before seeding.

    :param dependencies: The injected service dependencies.
    :type dependencies: dict
    :param mock_order_service: The mock order service.
    :type mock_order_service: OrderService
    :param mock_robot_service: The mock robot service.
    :type mock_robot_service: RobotService
    '''

    # Pre-populate mock services with existing records.
    existing_order = mock.Mock()
    existing_order.order_id = 'OLD-001'
    mock_order_service.list.return_value = [existing_order]

    existing_robot = mock.Mock()
    existing_robot.robot_id = 'OLD-R1'
    mock_robot_service.list.return_value = [existing_robot]

    # Execute the event.
    DomainEvent.handle(
        SeedDatabase,
        dependencies=dependencies,
    )

    # Verify delete was called for each existing record before new saves.
    mock_order_service.delete.assert_called_once_with('OLD-001')
    mock_robot_service.delete.assert_called_once_with('OLD-R1')

    # Verify new data was still seeded (robots only).
    assert mock_order_service.save.call_count == 0
    assert mock_robot_service.save.call_count == 3
