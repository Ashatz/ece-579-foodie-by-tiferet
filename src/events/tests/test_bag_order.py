"""
FOODIE BagOrder Domain Event Tests
"""

# *** imports

# ** core
from unittest import mock

# ** infra
import pytest
from tiferet.events import DomainEvent
from tiferet.assets.exceptions import TiferetError

# ** app
from ...domain import Item, Order
from ...mappers.bag import BagAggregate
from ...interfaces import OrderService
from ...interfaces.bagging import BaggingService
from ..bag_order import BagOrder

# *** fixtures

# ** fixture: sample_order
@pytest.fixture
def sample_order() -> Order:
    '''
    A sample order with mixed items for bagging.

    :return: An Order domain object.
    :rtype: Order
    '''

    return Order(
        order_id='ORD-BAG-1',
        destination='Building_A',
        items=[
            Item(name='Apple', size='small', quantity=2),
            Item(name='Ice Cream', size='medium', is_frozen=True, quantity=1),
        ],
    )


# ** fixture: mock_order_service
@pytest.fixture
def mock_order_service(sample_order: Order) -> OrderService:
    '''
    Mock OrderService returning the sample order.

    :param sample_order: The sample order.
    :type sample_order: Order
    :return: Mocked service.
    :rtype: OrderService
    '''

    svc = mock.Mock(spec=OrderService)
    svc.get.return_value = sample_order
    return svc


# ** fixture: mock_bagging_service
@pytest.fixture
def mock_bagging_service() -> BaggingService:
    '''
    Mock BaggingService returning pre-built bags.

    :return: Mocked service.
    :rtype: BaggingService
    '''

    svc = mock.Mock(spec=BaggingService)
    svc.bag_items.return_value = [
        BagAggregate.new_regular_bag(1),
        BagAggregate.new_freezer_bag(2),
    ]
    return svc


# *** tests

# ** test: bag_order_success
def test_bag_order_success(
    mock_order_service: OrderService,
    mock_bagging_service: BaggingService,
    sample_order: Order,
) -> None:
    '''
    Test successful bagging delegates to bagging_service and updates order status.

    :param mock_order_service: Mocked order service.
    :type mock_order_service: OrderService
    :param mock_bagging_service: Mocked bagging service.
    :type mock_bagging_service: BaggingService
    :param sample_order: The sample order.
    :type sample_order: Order
    '''

    # Act.
    result = DomainEvent.handle(
        BagOrder,
        dependencies={
            'order_service': mock_order_service,
            'bagging_service': mock_bagging_service,
        },
        order_id='ORD-BAG-1',
    )

    # Assert: bags returned from bagging service.
    assert len(result) == 2

    # Assert: bagging_service.bag_items was called with expanded items.
    mock_bagging_service.bag_items.assert_called_once()
    expanded_items = mock_bagging_service.bag_items.call_args[0][0]
    # 2 Apples + 1 Ice Cream = 3 expanded items.
    assert len(expanded_items) == 3

    # Assert: order status updated and saved.
    assert sample_order.status == 'bagged'
    mock_order_service.save.assert_called_once_with(sample_order)


# ** test: bag_order_not_found
def test_bag_order_not_found(
    mock_bagging_service: BaggingService,
) -> None:
    '''
    Test that a missing order raises ORDER_NOT_FOUND.

    :param mock_bagging_service: Mocked bagging service.
    :type mock_bagging_service: BaggingService
    '''

    # Arrange: order_service returns None.
    svc = mock.Mock(spec=OrderService)
    svc.get.return_value = None

    # Act / Assert.
    with pytest.raises(TiferetError) as exc_info:
        DomainEvent.handle(
            BagOrder,
            dependencies={
                'order_service': svc,
                'bagging_service': mock_bagging_service,
            },
            order_id='MISSING',
        )

    assert exc_info.value.error_code == 'ORDER_NOT_FOUND'
