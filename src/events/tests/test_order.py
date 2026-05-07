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
from ...domain import Location, Order
from ...interfaces.order import OrderService
from ...interfaces.robot import RobotService
from ...interfaces.beverage import BeverageService
from ...interfaces.beverage_select import BeverageSelectService
from ...mappers.robot import RobotAggregate
from ...mappers.beverage import BeverageAggregate
from ...mappers.bag import BagAggregate
from ..order import SelectBeverage

# *** constants

# ** constant: food_warehouse
FOOD_WAREHOUSE = Location(name='FW', x=0.0, y=0.0, is_food_warehouse=True)

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
