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
from ...domain import Item, Location, Order, Robot
from ...interfaces import ItemService, LocationService, OrderService, RobotService
from ..seed_database import SeedDatabase

# *** fixtures

# ** fixture: fw_location
@pytest.fixture
def fw_location() -> Location:
    '''
    Food Warehouse location used as starting position for all seeded robots.

    :return: A Location domain object.
    :rtype: Location
    '''

    return Location(name='FW', x=0.0, y=0.0, is_food_warehouse=True)


# ** fixture: sample_items
@pytest.fixture
def sample_items() -> list:
    '''
    Sample menu items returned by the item service.

    :return: List of Item domain objects.
    :rtype: list[Item]
    '''

    return [
        Item(name='Sandwich', size='medium', quantity=1),
        Item(name='Apple', size='small', quantity=2),
    ]


# ** fixture: mock_order_service
@pytest.fixture
def mock_order_service() -> OrderService:
    '''
    Mock OrderService with no existing orders.

    :return: Mocked service.
    :rtype: OrderService
    '''

    svc = mock.Mock(spec=OrderService)
    svc.list.return_value = []
    return svc


# ** fixture: mock_robot_service
@pytest.fixture
def mock_robot_service() -> RobotService:
    '''
    Mock RobotService with no existing robots.

    :return: Mocked service.
    :rtype: RobotService
    '''

    svc = mock.Mock(spec=RobotService)
    svc.list.return_value = []
    return svc


# ** fixture: mock_item_service
@pytest.fixture
def mock_item_service(sample_items: list) -> ItemService:
    '''
    Mock ItemService returning sample menu items.

    :param sample_items: The sample items.
    :type sample_items: list
    :return: Mocked service.
    :rtype: ItemService
    '''

    svc = mock.Mock(spec=ItemService)
    svc.list.return_value = sample_items
    return svc


# ** fixture: mock_location_service
@pytest.fixture
def mock_location_service(fw_location: Location) -> LocationService:
    '''
    Mock LocationService returning the Food Warehouse.

    :param fw_location: The Food Warehouse location.
    :type fw_location: Location
    :return: Mocked service.
    :rtype: LocationService
    '''

    svc = mock.Mock(spec=LocationService)
    svc.get.return_value = fw_location
    return svc


# *** tests

# ** test: seed_database_success
def test_seed_database_success(
    mock_order_service: OrderService,
    mock_robot_service: RobotService,
    mock_item_service: ItemService,
    mock_location_service: LocationService,
) -> None:
    '''
    Test that SeedDatabase creates 3 orders and 3 robots on a fresh database.

    :param mock_order_service: Mocked order service.
    :type mock_order_service: OrderService
    :param mock_robot_service: Mocked robot service.
    :type mock_robot_service: RobotService
    :param mock_item_service: Mocked item service.
    :type mock_item_service: ItemService
    :param mock_location_service: Mocked location service.
    :type mock_location_service: LocationService
    '''

    # Act.
    result = DomainEvent.handle(
        SeedDatabase,
        dependencies={
            'order_service': mock_order_service,
            'robot_service': mock_robot_service,
            'item_service': mock_item_service,
            'location_service': mock_location_service,
        },
    )

    # Assert: return summary.
    assert result['orders_seeded'] == 3
    assert result['robots_seeded'] == 3
    assert result['status'] == 'complete'

    # Assert: 3 orders saved (ORD-101, ORD-102, ORD-103).
    assert mock_order_service.save.call_count == 3
    saved_order_ids = [
        call.args[0].order_id
        for call in mock_order_service.save.call_args_list
    ]
    assert saved_order_ids == ['ORD-101', 'ORD-102', 'ORD-103']

    # Assert: 3 robots saved (R1, R2, R3).
    assert mock_robot_service.save.call_count == 3
    saved_robot_ids = [
        call.args[0].robot_id
        for call in mock_robot_service.save.call_args_list
    ]
    assert saved_robot_ids == ['R1', 'R2', 'R3']

    # Assert: item_service.list and location_service.get('FW') called.
    mock_item_service.list.assert_called_once()
    mock_location_service.get.assert_called_once_with('FW')


# ** test: seed_database_clears_existing
def test_seed_database_clears_existing(
    mock_item_service: ItemService,
    mock_location_service: LocationService,
) -> None:
    '''
    Test that SeedDatabase clears existing orders and robots before seeding.

    :param mock_item_service: Mocked item service.
    :type mock_item_service: ItemService
    :param mock_location_service: Mocked location service.
    :type mock_location_service: LocationService
    '''

    # Arrange: services return pre-existing data.
    fw = Location(name='FW', x=0.0, y=0.0, is_food_warehouse=True)

    order_svc = mock.Mock(spec=OrderService)
    order_svc.list.return_value = [
        Order(order_id='OLD-1', destination='Building_A'),
        Order(order_id='OLD-2', destination='Building_B'),
    ]

    robot_svc = mock.Mock(spec=RobotService)
    robot_svc.list.return_value = [
        Robot(robot_id='OLD-R1', current_location=fw),
    ]

    # Act.
    result = DomainEvent.handle(
        SeedDatabase,
        dependencies={
            'order_service': order_svc,
            'robot_service': robot_svc,
            'item_service': mock_item_service,
            'location_service': mock_location_service,
        },
    )

    # Assert: existing data was deleted.
    assert order_svc.delete.call_count == 2
    order_svc.delete.assert_any_call('OLD-1')
    order_svc.delete.assert_any_call('OLD-2')

    assert robot_svc.delete.call_count == 1
    robot_svc.delete.assert_called_once_with('OLD-R1')

    # Assert: new data was still seeded.
    assert result['orders_seeded'] == 3
    assert result['robots_seeded'] == 3


# ** test: seed_database_first_order_has_items
def test_seed_database_first_order_has_items(
    mock_order_service: OrderService,
    mock_robot_service: RobotService,
    mock_item_service: ItemService,
    mock_location_service: LocationService,
    sample_items: list,
) -> None:
    '''
    Test that ORD-101 is seeded with all menu items while others are empty.

    :param mock_order_service: Mocked order service.
    :type mock_order_service: OrderService
    :param mock_robot_service: Mocked robot service.
    :type mock_robot_service: RobotService
    :param mock_item_service: Mocked item service.
    :type mock_item_service: ItemService
    :param mock_location_service: Mocked location service.
    :type mock_location_service: LocationService
    :param sample_items: The sample items from the item service.
    :type sample_items: list
    '''

    # Act.
    DomainEvent.handle(
        SeedDatabase,
        dependencies={
            'order_service': mock_order_service,
            'robot_service': mock_robot_service,
            'item_service': mock_item_service,
            'location_service': mock_location_service,
        },
    )

    # Assert: first order has items, others are empty.
    saved_orders = [
        call.args[0]
        for call in mock_order_service.save.call_args_list
    ]
    assert len(saved_orders[0].items) == len(sample_items)
    assert len(saved_orders[1].items) == 0
    assert len(saved_orders[2].items) == 0
