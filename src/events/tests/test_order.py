"""
FOODIE Order Domain Event Tests
"""

# *** imports

# ** core
from unittest import mock

# ** infra
import pytest
from tiferet.events import DomainEvent
from tiferet.assets.exceptions import TiferetError

# ** app
from ...domain import Item, Location, Order
from ...interfaces.order import OrderService
from ...interfaces.item import ItemService
from ...interfaces.robot import RobotService
from ...interfaces.beverage import BeverageService
from ...interfaces.beverage_select import BeverageSelectService
from ...mappers.robot import RobotAggregate
from ...mappers.beverage import BeverageAggregate
from ...mappers.bag import BagAggregate
from ..order import PlaceItemOrder, PlaceBeverageOrder, SelectBeverage

# *** constants

# ** constant: food_warehouse
FOOD_WAREHOUSE = Location(name='FW', x=0.0, y=0.0, is_food_warehouse=True)

# ** constant: sample_item_bread
SAMPLE_ITEM_BREAD = Item(name='loaf of bread', size='medium', quantity=1)

# ** constant: sample_item_water
SAMPLE_ITEM_WATER = Item(name='1-gallon water bottle', size='large', quantity=2)

# ** constant: sample_beverage
SAMPLE_BEVERAGE = BeverageAggregate(
    name='Carrot Juice',
    beverage_type='juice',
    brand='FreshRoots',
    is_health_friendly=True,
)

# *** fixtures

# ** fixture: mock_order_service
@pytest.fixture
def mock_order_service() -> OrderService:
    '''
    Mock OrderService returning a beverage order.
    '''
    svc = mock.Mock(spec=OrderService)
    svc.get.return_value = Order(
        order_id='BEV-201',
        order_type='beverage',
        destination='Building_A',
    )
    return svc

# ** fixture: mock_robot_service
@pytest.fixture
def mock_robot_service() -> RobotService:
    '''
    Mock RobotService returning an idle robot at the Food Warehouse.
    '''
    svc = mock.Mock(spec=RobotService)
    svc.get.return_value = RobotAggregate(
        robot_id='R2',
        current_location=FOOD_WAREHOUSE,
    )
    return svc

# ** fixture: mock_beverage_service
@pytest.fixture
def mock_beverage_service() -> BeverageService:
    '''
    Mock BeverageService returning candidate beverages.
    '''
    svc = mock.Mock(spec=BeverageService)
    svc.list.return_value = [SAMPLE_BEVERAGE]
    return svc

# ** fixture: mock_beverage_select_service
@pytest.fixture
def mock_beverage_select_service() -> BeverageSelectService:
    '''
    Mock BeverageSelectService returning a selected beverage.
    '''
    svc = mock.Mock(spec=BeverageSelectService)
    svc.select.return_value = SAMPLE_BEVERAGE
    return svc

# ** fixture: dependencies
@pytest.fixture
def dependencies(
    mock_order_service,
    mock_robot_service,
    mock_beverage_service,
    mock_beverage_select_service,
) -> dict:
    '''
    Dependency dict for DomainEvent.handle.
    '''
    return {
        'order_service': mock_order_service,
        'robot_service': mock_robot_service,
        'beverage_service': mock_beverage_service,
        'beverage_select_service': mock_beverage_select_service,
    }

# *** tests

# ** test: select_beverage_success
def test_select_beverage_success(
    dependencies,
    mock_order_service,
    mock_robot_service,
    mock_beverage_select_service,
):
    '''
    Test successful backward-chaining beverage selection.
    '''

    # Execute the event with guest facts.
    result = DomainEvent.handle(
        SelectBeverage,
        dependencies=dependencies,
        robot_id='R2',
        order_id='BEV-201',
        facts={'health_nut': True, 'allergies_citrus': True, 'guest_age': 'adult'},
    )

    # Verify the return summary.
    assert result['status'] == 'complete'
    assert result['beverage'] == 'Carrot Juice'
    assert result['brand'] == 'FreshRoots'
    assert result['robot_id'] == 'R2'
    assert result['order_id'] == 'BEV-201'

    # Verify backward chaining was called with candidates and rules.
    mock_beverage_select_service.select.assert_called_once()

    # Verify order status updated and both services saved.
    saved_order = mock_order_service.save.call_args.args[0]
    assert saved_order.status == 'bagged'
    mock_robot_service.save.assert_called_once()


# ** test: select_beverage_fallback
def test_select_beverage_fallback(
    dependencies,
    mock_beverage_select_service,
):
    '''
    Test that fallback beverage is returned when no rule fires.
    '''

    # Mock select to return None (no rule matched).
    mock_beverage_select_service.select.return_value = None

    # Execute the event.
    result = DomainEvent.handle(
        SelectBeverage,
        dependencies=dependencies,
        robot_id='R2',
        order_id='BEV-201',
    )

    # Verify fallback beverage.
    assert result['status'] == 'complete'
    assert result['beverage'] == 'Sparkling Water'
    assert result['brand'] == 'San Pellegrino'


# ** test: select_beverage_wrong_order_type
def test_select_beverage_wrong_order_type(
    dependencies,
    mock_order_service,
):
    '''
    Test that an item order raises ORDER_TYPE_MISMATCH.
    '''

    # Mock order_service to return an item order.
    mock_order_service.get.return_value = Order(
        order_id='ORD-101',
        order_type='item',
        destination='Building_A',
    )

    # Execute and expect TiferetError.
    with pytest.raises(TiferetError) as exc_info:
        DomainEvent.handle(
            SelectBeverage,
            dependencies=dependencies,
            robot_id='R2',
            order_id='ORD-101',
        )

    assert exc_info.value.error_code == 'ORDER_TYPE_MISMATCH'


# ** test: select_beverage_cargo_conflict
def test_select_beverage_cargo_conflict(
    dependencies,
    mock_robot_service,
):
    '''
    Test that a robot with item bags raises ROBOT_CARGO_CONFLICT.
    '''

    # Robot at FW with item bags loaded.
    robot = RobotAggregate(robot_id='R2', current_location=FOOD_WAREHOUSE)
    robot.load_bag(BagAggregate(bag_id='bag_1', bag_type='paper'))
    mock_robot_service.get.return_value = robot

    # Execute and expect TiferetError.
    with pytest.raises(TiferetError) as exc_info:
        DomainEvent.handle(
            SelectBeverage,
            dependencies=dependencies,
            robot_id='R2',
            order_id='BEV-201',
        )

    assert exc_info.value.error_code == 'ROBOT_CARGO_CONFLICT'


# *** PlaceItemOrder tests

# ** test: place_item_order_success
def test_place_item_order_success():
    '''
    Test successful item order placement with 2 menu items.
    '''

    # Set up mock services.
    mock_order_service = mock.Mock(spec=OrderService)
    mock_order_service.exists.return_value = False
    mock_item_service = mock.Mock(spec=ItemService)
    mock_item_service.get.side_effect = lambda name: {
        'loaf of bread': SAMPLE_ITEM_BREAD,
        '1-gallon water bottle': SAMPLE_ITEM_WATER,
    }.get(name)

    # Execute the event.
    result = DomainEvent.handle(
        PlaceItemOrder,
        dependencies={
            'order_service': mock_order_service,
            'item_service': mock_item_service,
        },
        order_id='ORD-201',
        destination='Building_A',
        items=[
            {'name': 'loaf of bread', 'quantity': 3},
            {'name': '1-gallon water bottle', 'quantity': 2},
        ],
    )

    # Verify the return summary.
    assert result['status'] == 'complete'
    assert result['order_id'] == 'ORD-201'
    assert result['destination'] == 'Building_A'
    assert result['total_items'] == 5

    # Verify the order was persisted with correct attributes.
    saved_order = mock_order_service.save.call_args.args[0]
    assert saved_order.order_id == 'ORD-201'
    assert saved_order.order_type == 'item'
    assert saved_order.destination == 'Building_A'
    assert len(saved_order.items) == 2
    assert saved_order.items[0].name == 'loaf of bread'
    assert saved_order.items[0].quantity == 3
    assert saved_order.items[1].name == '1-gallon water bottle'
    assert saved_order.items[1].quantity == 2


# ** test: place_item_order_duplicate
def test_place_item_order_duplicate():
    '''
    Test that a duplicate order raises DUPLICATE_ORDER.
    '''

    # Set up mock services with existing order.
    mock_order_service = mock.Mock(spec=OrderService)
    mock_order_service.exists.return_value = True
    mock_item_service = mock.Mock(spec=ItemService)

    # Execute and expect TiferetError.
    with pytest.raises(TiferetError) as exc_info:
        DomainEvent.handle(
            PlaceItemOrder,
            dependencies={
                'order_service': mock_order_service,
                'item_service': mock_item_service,
            },
            order_id='ORD-201',
            destination='Building_A',
            items=[{'name': 'loaf of bread'}],
        )

    assert exc_info.value.error_code == 'DUPLICATE_ORDER'


# ** test: place_item_order_item_not_found
def test_place_item_order_item_not_found():
    '''
    Test that an unknown item raises ITEM_NOT_FOUND.
    '''

    # Set up mock services with item not found.
    mock_order_service = mock.Mock(spec=OrderService)
    mock_order_service.exists.return_value = False
    mock_item_service = mock.Mock(spec=ItemService)
    mock_item_service.get.return_value = None

    # Execute and expect TiferetError.
    with pytest.raises(TiferetError) as exc_info:
        DomainEvent.handle(
            PlaceItemOrder,
            dependencies={
                'order_service': mock_order_service,
                'item_service': mock_item_service,
            },
            order_id='ORD-201',
            destination='Building_A',
            items=[{'name': 'nonexistent item'}],
        )

    assert exc_info.value.error_code == 'ITEM_NOT_FOUND'


# *** PlaceBeverageOrder tests

# ** test: place_beverage_order_success
def test_place_beverage_order_success():
    '''
    Test successful beverage order placement.
    '''

    # Set up mock service.
    mock_order_service = mock.Mock(spec=OrderService)
    mock_order_service.exists.return_value = False

    # Execute the event.
    result = DomainEvent.handle(
        PlaceBeverageOrder,
        dependencies={'order_service': mock_order_service},
        order_id='BEV-301',
        destination='Dorm_1',
    )

    # Verify the return summary.
    assert result['status'] == 'complete'
    assert result['order_id'] == 'BEV-301'
    assert result['destination'] == 'Dorm_1'
    assert result['order_type'] == 'beverage'

    # Verify the order was persisted with correct attributes.
    saved_order = mock_order_service.save.call_args.args[0]
    assert saved_order.order_id == 'BEV-301'
    assert saved_order.order_type == 'beverage'
    assert saved_order.destination == 'Dorm_1'
    assert saved_order.items == []


# ** test: place_beverage_order_duplicate
def test_place_beverage_order_duplicate():
    '''
    Test that a duplicate beverage order raises DUPLICATE_ORDER.
    '''

    # Set up mock service with existing order.
    mock_order_service = mock.Mock(spec=OrderService)
    mock_order_service.exists.return_value = True

    # Execute and expect TiferetError.
    with pytest.raises(TiferetError) as exc_info:
        DomainEvent.handle(
            PlaceBeverageOrder,
            dependencies={'order_service': mock_order_service},
            order_id='BEV-301',
            destination='Dorm_1',
        )

    assert exc_info.value.error_code == 'DUPLICATE_ORDER'
