"""
FOODIE Robot Domain Event Tests
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
from ...interfaces.robot import RobotService
from ...interfaces.bagging import BaggingService
from ...mappers.robot import RobotAggregate
from ...mappers.bag import BagAggregate
from ..robot import BagOrder

# *** constants

# ** constant: food_warehouse
FOOD_WAREHOUSE = Location(name='FW', x=0.0, y=0.0, is_food_warehouse=True)

# ** constant: sample_items
SAMPLE_ITEMS = [
    Item(name='1-gallon water bottle', size='large', quantity=2),
    Item(name='pint ice cream', size='medium', is_frozen=True, quantity=1),
    Item(name='granola box', size='medium', is_fragile=True, quantity=1),
    Item(name='loaf of bread', size='medium', quantity=1),
]

# *** fixtures

# ** fixture: mock_order_service
@pytest.fixture
def mock_order_service() -> OrderService:
    '''
    Mock OrderService returning a sample order with items.
    '''
    svc = mock.Mock(spec=OrderService)
    svc.get.return_value = Order(
        order_id='ORD-101',
        destination='Building_A',
        items=list(SAMPLE_ITEMS),
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
        robot_id='R1',
        current_location=FOOD_WAREHOUSE,
    )
    return svc

# ** fixture: sample_bags
@pytest.fixture
def sample_bags() -> list:
    '''
    Sample bags returned by the bagging service.
    '''
    bag1 = BagAggregate(bag_id='bag_1', bag_type='paper')
    bag1.add_item(Item(name='1-gallon water bottle', size='large', quantity=1))

    bag2 = BagAggregate(bag_id='freezer_bag_2', bag_type='freezer')
    bag2.add_item(Item(name='pint ice cream', size='medium', is_frozen=True, quantity=1))

    return [bag1, bag2]

# ** fixture: mock_bagging_service
@pytest.fixture
def mock_bagging_service(sample_bags) -> BaggingService:
    '''
    Mock BaggingService returning sample bags.
    '''
    svc = mock.Mock(spec=BaggingService)
    svc.bag_items.return_value = sample_bags
    return svc

# ** fixture: dependencies
@pytest.fixture
def dependencies(
    mock_order_service,
    mock_robot_service,
    mock_bagging_service,
) -> dict:
    '''
    Dependency dict for DomainEvent.handle.
    '''
    return {
        'order_service': mock_order_service,
        'robot_service': mock_robot_service,
        'bagging_service': mock_bagging_service,
    }

# *** tests

# ** test: bag_order_success
def test_bag_order_success(
    dependencies,
    mock_order_service,
    mock_robot_service,
    mock_bagging_service,
    sample_bags,
):
    '''
    Test successful bagging: bags loaded onto robot, order status updated, both saved.

    :param dependencies: The injected service dependencies.
    :type dependencies: dict
    :param mock_order_service: The mock order service.
    :type mock_order_service: OrderService
    :param mock_robot_service: The mock robot service.
    :type mock_robot_service: RobotService
    :param mock_bagging_service: The mock bagging service.
    :type mock_bagging_service: BaggingService
    :param sample_bags: The sample bags from the bagging service.
    :type sample_bags: list
    '''

    # Execute the event.
    result = DomainEvent.handle(
        BagOrder,
        dependencies=dependencies,
        robot_id='R1',
        order_id='ORD-101',
    )

    # Verify the return summary.
    assert result['robot_id'] == 'R1'
    assert result['order_id'] == 'ORD-101'
    assert result['bags_packed'] == 2
    assert result['status'] == 'complete'

    # Verify bagging_service received expanded items (quantity=1 each).
    call_args = mock_bagging_service.bag_items.call_args
    expanded = call_args.args[0]
    assert all(item.quantity == 1 for item in expanded)
    assert len(expanded) == 5  # 2 water + 1 ice cream + 1 granola + 1 bread

    # Verify order status was updated and saved.
    saved_order = mock_order_service.save.call_args.args[0]
    assert saved_order.status == 'bagged'

    # Verify robot was saved with bags loaded.
    mock_robot_service.save.assert_called_once()


# ** test: bag_order_order_not_found
def test_bag_order_order_not_found(dependencies, mock_order_service):
    '''
    Test that a missing order raises TiferetError with ORDER_NOT_FOUND.

    :param dependencies: The injected service dependencies.
    :type dependencies: dict
    :param mock_order_service: The mock order service.
    :type mock_order_service: OrderService
    '''

    # Mock order_service.get to return None.
    mock_order_service.get.return_value = None

    # Execute and expect TiferetError.
    with pytest.raises(TiferetError) as exc_info:
        DomainEvent.handle(
            BagOrder,
            dependencies=dependencies,
            robot_id='R1',
            order_id='ORD-999',
        )

    assert exc_info.value.error_code == 'ORDER_NOT_FOUND'


# ** test: bag_order_robot_not_at_warehouse
def test_bag_order_robot_not_at_warehouse(dependencies, mock_robot_service):
    '''
    Test that a robot not at the Food Warehouse raises ROBOT_NOT_AT_WAREHOUSE.

    :param dependencies: The injected service dependencies.
    :type dependencies: dict
    :param mock_robot_service: The mock robot service.
    :type mock_robot_service: RobotService
    '''

    # Place the robot at a non-warehouse location.
    mock_robot_service.get.return_value = RobotAggregate(
        robot_id='R1',
        current_location=Location(name='Building_A', x=5.0, y=8.0),
    )

    # Execute and expect TiferetError.
    with pytest.raises(TiferetError) as exc_info:
        DomainEvent.handle(
            BagOrder,
            dependencies=dependencies,
            robot_id='R1',
            order_id='ORD-101',
        )

    assert exc_info.value.error_code == 'ROBOT_NOT_AT_WAREHOUSE'


# ** test: bag_order_robot_not_found
def test_bag_order_robot_not_found(dependencies, mock_robot_service):
    '''
    Test that a missing robot raises TiferetError with ROBOT_NOT_FOUND.

    :param dependencies: The injected service dependencies.
    :type dependencies: dict
    :param mock_robot_service: The mock robot service.
    :type mock_robot_service: RobotService
    '''

    # Mock robot_service.get to return None.
    mock_robot_service.get.return_value = None

    # Execute and expect TiferetError.
    with pytest.raises(TiferetError) as exc_info:
        DomainEvent.handle(
            BagOrder,
            dependencies=dependencies,
            robot_id='RX-999',
            order_id='ORD-101',
        )

    assert exc_info.value.error_code == 'ROBOT_NOT_FOUND'
