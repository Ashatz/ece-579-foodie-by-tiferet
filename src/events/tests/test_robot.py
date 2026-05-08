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
from ...interfaces.location import LocationService
from ...interfaces.bagging import BaggingService
from ...interfaces.route_planner import RoutePlannerService
from ...mappers.robot import RobotAggregate
from ...mappers.bag import BagAggregate
from ..robot import (
    BagOrder, PlanRoute, DeliverOrder,
    ReturnToWarehouse, ChargeRobot, ViewFleet,
)

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


# ** constant: building_a
BUILDING_A = Location(name='Building_A', x=5.0, y=8.0)


# *** route event fixtures

# ** fixture: mock_location_service
@pytest.fixture
def mock_location_service() -> LocationService:
    '''
    Mock LocationService returning FW and Building_A.
    '''
    svc = mock.Mock(spec=LocationService)
    svc.list.return_value = [FOOD_WAREHOUSE, BUILDING_A]
    svc.get_edges.return_value = {
        'FW': ['Building_A'],
        'Building_A': ['FW'],
    }
    return svc

# ** fixture: mock_route_planner
@pytest.fixture
def mock_route_planner() -> RoutePlannerService:
    '''
    Mock RoutePlannerService returning a simple path.
    '''
    svc = mock.Mock(spec=RoutePlannerService)
    svc.find_path.return_value = (['FW', 'Building_A'], 13.0)
    svc.detect_and_replan.return_value = (None, 0.0, set())
    return svc

# ** fixture: loaded_robot
@pytest.fixture
def loaded_robot(sample_bags) -> RobotAggregate:
    '''
    A robot at FW with bags loaded.
    '''
    robot = RobotAggregate(robot_id='R1', current_location=FOOD_WAREHOUSE)
    for bag in sample_bags:
        robot.load_bag(bag)
    return robot

# ** fixture: route_deps
@pytest.fixture
def route_deps(
    mock_robot_service,
    mock_order_service,
    mock_route_planner,
    mock_location_service,
) -> dict:
    '''
    Dependency dict for route-planning events.
    '''
    return {
        'robot_service': mock_robot_service,
        'order_service': mock_order_service,
        'route_planner': mock_route_planner,
        'location_service': mock_location_service,
    }


# *** plan_route tests

# ** test: plan_route_success
def test_plan_route_success(route_deps, mock_robot_service, loaded_robot, mock_route_planner):
    '''
    Test successful A* route planning for a loaded robot.
    '''

    # Set up the robot with bags.
    mock_robot_service.get.return_value = loaded_robot

    # Execute the event.
    result = DomainEvent.handle(
        PlanRoute,
        dependencies=route_deps,
        robot_id='R1',
        order_id='ORD-101',
    )

    # Verify the return summary.
    assert result['status'] == 'complete'
    assert result['path'] == ['FW', 'Building_A']
    assert result['distance'] == 13.0

    # Verify robot was saved with updated status.
    mock_robot_service.save.assert_called_once()


# ** test: plan_route_no_bags
def test_plan_route_no_bags(route_deps, mock_robot_service):
    '''
    Test that a robot with no bags raises ROBOT_NO_BAGS.
    '''

    # Robot at FW but no bags.
    mock_robot_service.get.return_value = RobotAggregate(
        robot_id='R1', current_location=FOOD_WAREHOUSE,
    )

    with pytest.raises(TiferetError) as exc_info:
        DomainEvent.handle(
            PlanRoute,
            dependencies=route_deps,
            robot_id='R1',
            order_id='ORD-101',
        )

    assert exc_info.value.error_code == 'ROBOT_NO_BAGS'


# ** test: plan_route_no_path
def test_plan_route_no_path(route_deps, mock_robot_service, loaded_robot, mock_route_planner):
    '''
    Test that no_path status is returned when A* finds no route.
    '''

    mock_robot_service.get.return_value = loaded_robot
    mock_route_planner.find_path.return_value = (None, 0.0)

    result = DomainEvent.handle(
        PlanRoute,
        dependencies=route_deps,
        robot_id='R1',
        order_id='ORD-101',
    )

    assert result['status'] == 'no_path'
    assert result['path'] is None


# ** test: plan_route_low_battery_after_route
def test_plan_route_low_battery_after_route(
    route_deps, mock_robot_service, mock_route_planner, sample_bags,
):
    '''
    Test that a robot with insufficient battery after route consumption
    returns to FW instead of completing the delivery.

    A delivery distance of 700 units consumes 84% battery (700 * 0.12),
    leaving 16% — below the 20% threshold. The event should abort the
    delivery and route back to FW.

    :param route_deps: Injected route event dependencies.
    :type route_deps: dict
    :param mock_robot_service: The mock robot service.
    :type mock_robot_service: RobotService
    :param mock_route_planner: The mock route planner.
    :type mock_route_planner: RoutePlannerService
    :param sample_bags: Sample bags loaded onto the robot.
    :type sample_bags: list
    '''

    # Robot at FW with full battery and bags loaded.
    robot = RobotAggregate(robot_id='R1', current_location=FOOD_WAREHOUSE)
    for bag in sample_bags:
        robot.load_bag(bag)
    mock_robot_service.get.return_value = robot

    # Delivery route costs 700 units (84% battery drain); return costs 13 units.
    mock_route_planner.find_path.side_effect = [
        (['FW', 'Building_A'], 700.0),
        (['Building_A', 'FW'], 13.0),
    ]
    mock_route_planner.detect_and_replan.return_value = (None, 0.0, set())

    # Execute the event.
    result = DomainEvent.handle(
        PlanRoute,
        dependencies=route_deps,
        robot_id='R1',
        order_id='ORD-101',
    )

    # Verify low battery return status.
    assert result['status'] == 'low_battery_return'
    assert result['path'] == ['FW', 'Building_A']
    assert result['distance'] == 700.0
    assert result['return_path'] == ['Building_A', 'FW']
    assert result['return_distance'] == 13.0

    # Verify robot was saved at FW in idle state.
    saved_robot = mock_robot_service.save.call_args.args[0]
    assert saved_robot.current_location.is_food_warehouse
    assert saved_robot.status == 'idle'

    # Verify order was NOT updated (remains bagged for re-dispatch).
    mock_robot_service.save.assert_called_once()


# ** test: plan_route_low_battery_after_replan
def test_plan_route_low_battery_after_replan(
    route_deps, mock_robot_service, mock_route_planner, sample_bags,
):
    '''
    Test that a low-battery condition triggered by an obstacle replan
    (which increases the route distance beyond the battery threshold)
    also results in an emergency return to FW.

    The initial route costs 13 units (fine), but after obstacle detection
    the replanned route costs 700 units (84% drain), dropping battery
    below 20%.

    :param route_deps: Injected route event dependencies.
    :type route_deps: dict
    :param mock_robot_service: The mock robot service.
    :type mock_robot_service: RobotService
    :param mock_route_planner: The mock route planner.
    :type mock_route_planner: RoutePlannerService
    :param sample_bags: Sample bags loaded onto the robot.
    :type sample_bags: list
    '''

    # Robot at FW with full battery and bags loaded.
    robot = RobotAggregate(robot_id='R1', current_location=FOOD_WAREHOUSE)
    for bag in sample_bags:
        robot.load_bag(bag)
    mock_robot_service.get.return_value = robot

    # Initial route is short; obstacle forces a 700-unit replan.
    mock_route_planner.find_path.side_effect = [
        (['FW', 'Building_A'], 13.0),         # initial delivery route
        (['Building_A', 'FW'], 13.0),          # emergency return route
    ]
    mock_route_planner.detect_and_replan.return_value = (
        ['FW', 'Pathway_X', 'Building_A'], 700.0, set(),
    )

    # Execute the event.
    result = DomainEvent.handle(
        PlanRoute,
        dependencies=route_deps,
        robot_id='R1',
        order_id='ORD-101',
    )

    # Verify low battery return triggered by the replanned distance.
    assert result['status'] == 'low_battery_return'
    assert result['distance'] == 700.0
    assert result['return_path'] == ['Building_A', 'FW']

    # Verify robot landed at FW.
    saved_robot = mock_robot_service.save.call_args.args[0]
    assert saved_robot.current_location.is_food_warehouse
    assert saved_robot.status == 'idle'


# *** deliver_order tests

# ** test: deliver_order_success
def test_deliver_order_success(mock_robot_service, mock_order_service, sample_bags):
    '''
    Test successful delivery at the destination.
    '''

    # Robot at Building_A with bags.
    robot = RobotAggregate(robot_id='R1', current_location=BUILDING_A)
    for bag in sample_bags:
        robot.load_bag(bag)
    mock_robot_service.get.return_value = robot

    # Order destined for Building_A.
    mock_order_service.get.return_value = Order(
        order_id='ORD-101', destination='Building_A', status='bagged',
    )

    deps = {
        'robot_service': mock_robot_service,
        'order_service': mock_order_service,
    }

    result = DomainEvent.handle(
        DeliverOrder,
        dependencies=deps,
        robot_id='R1',
        order_id='ORD-101',
    )

    assert result['status'] == 'complete'
    assert result['bags_delivered'] == 2

    # Verify order updated to delivered.
    saved_order = mock_order_service.save.call_args.args[0]
    assert saved_order.status == 'delivered'


# ** test: deliver_order_not_at_destination
def test_deliver_order_not_at_destination(mock_robot_service, mock_order_service):
    '''
    Test that a robot not at the destination raises ROBOT_NOT_AT_DESTINATION.
    '''

    # Robot at FW, not at destination.
    robot = RobotAggregate(robot_id='R1', current_location=FOOD_WAREHOUSE)
    robot.compartments = [BagAggregate(bag_id='bag_1', bag_type='paper')]
    mock_robot_service.get.return_value = robot

    mock_order_service.get.return_value = Order(
        order_id='ORD-101', destination='Building_A', status='bagged',
    )

    deps = {
        'robot_service': mock_robot_service,
        'order_service': mock_order_service,
    }

    with pytest.raises(TiferetError) as exc_info:
        DomainEvent.handle(
            DeliverOrder,
            dependencies=deps,
            robot_id='R1',
            order_id='ORD-101',
        )

    assert exc_info.value.error_code == 'ROBOT_NOT_AT_DESTINATION'


# ** test: deliver_order_no_bags
def test_deliver_order_no_bags(mock_robot_service, mock_order_service):
    '''
    Test that a robot at destination but with no bags raises ROBOT_NO_BAGS.
    '''

    # Robot at Building_A, no bags.
    mock_robot_service.get.return_value = RobotAggregate(
        robot_id='R1', current_location=BUILDING_A,
    )

    mock_order_service.get.return_value = Order(
        order_id='ORD-101', destination='Building_A', status='bagged',
    )

    deps = {
        'robot_service': mock_robot_service,
        'order_service': mock_order_service,
    }

    with pytest.raises(TiferetError) as exc_info:
        DomainEvent.handle(
            DeliverOrder,
            dependencies=deps,
            robot_id='R1',
            order_id='ORD-101',
        )

    assert exc_info.value.error_code == 'ROBOT_NO_BAGS'


# *** return_to_warehouse tests

# ** test: return_to_warehouse_success
def test_return_to_warehouse_success(
    mock_robot_service, mock_route_planner, mock_location_service,
):
    '''
    Test successful return to Food Warehouse.
    '''

    # Robot at Building_A.
    mock_robot_service.get.return_value = RobotAggregate(
        robot_id='R1', current_location=BUILDING_A,
    )
    mock_route_planner.find_path.return_value = (['Building_A', 'FW'], 13.0)

    deps = {
        'robot_service': mock_robot_service,
        'route_planner': mock_route_planner,
        'location_service': mock_location_service,
    }

    result = DomainEvent.handle(
        ReturnToWarehouse,
        dependencies=deps,
        robot_id='R1',
    )

    assert result['status'] == 'complete'
    assert result['path'] == ['Building_A', 'FW']
    mock_robot_service.save.assert_called_once()


# ** test: return_to_warehouse_already_at_fw
def test_return_to_warehouse_already_at_fw(mock_robot_service, mock_route_planner, mock_location_service):
    '''
    Test that a robot already at FW raises ROBOT_ALREADY_AT_WAREHOUSE.
    '''

    # Robot already at FW.
    mock_robot_service.get.return_value = RobotAggregate(
        robot_id='R1', current_location=FOOD_WAREHOUSE,
    )

    deps = {
        'robot_service': mock_robot_service,
        'route_planner': mock_route_planner,
        'location_service': mock_location_service,
    }

    with pytest.raises(TiferetError) as exc_info:
        DomainEvent.handle(
            ReturnToWarehouse,
            dependencies=deps,
            robot_id='R1',
        )

    assert exc_info.value.error_code == 'ROBOT_ALREADY_AT_WAREHOUSE'


# *** charge_robot tests

# ** test: charge_robot_success
def test_charge_robot_success(mock_robot_service):
    '''
    Test successful charging at the Food Warehouse.
    '''

    # Robot at FW with low battery.
    robot = RobotAggregate(
        robot_id='R1', current_location=FOOD_WAREHOUSE, battery_level=45.0,
    )
    mock_robot_service.get.return_value = robot

    deps = {'robot_service': mock_robot_service}

    result = DomainEvent.handle(
        ChargeRobot,
        dependencies=deps,
        robot_id='R1',
    )

    assert result['status'] == 'complete'
    assert result['previous_battery'] == 45.0
    assert result['battery_level'] == 100.0
    mock_robot_service.save.assert_called_once()


# ** test: charge_robot_not_at_warehouse
def test_charge_robot_not_at_warehouse(mock_robot_service):
    '''
    Test that charging away from FW raises ROBOT_NOT_AT_WAREHOUSE.
    '''

    mock_robot_service.get.return_value = RobotAggregate(
        robot_id='R1', current_location=BUILDING_A,
    )

    deps = {'robot_service': mock_robot_service}

    with pytest.raises(TiferetError) as exc_info:
        DomainEvent.handle(
            ChargeRobot,
            dependencies=deps,
            robot_id='R1',
        )

    assert exc_info.value.error_code == 'ROBOT_NOT_AT_WAREHOUSE'


# *** view_fleet tests

# ** test: view_fleet_success
def test_view_fleet_success(mock_robot_service, sample_bags):
    '''
    Test that ViewFleet loads all robots, prints their status, and
    returns a correctly structured payload without mutating any state.

    :param mock_robot_service: The mock robot service.
    :type mock_robot_service: RobotService
    :param sample_bags: Sample bags used to give robots non-empty compartments.
    :type sample_bags: list
    '''

    # Two robots at different locations with varying state.
    r1 = RobotAggregate(robot_id='R1', current_location=FOOD_WAREHOUSE, battery_level=100.0)
    r2 = RobotAggregate(robot_id='R2', current_location=BUILDING_A, battery_level=85.0)
    for bag in sample_bags:
        r2.load_bag(bag)
    mock_robot_service.list.return_value = [r1, r2]

    deps = {'robot_service': mock_robot_service}

    # Execute the event.
    result = DomainEvent.handle(ViewFleet, dependencies=deps)

    # Verify payload structure.
    assert result['robot_count'] == 2
    assert len(result['robots']) == 2

    # Verify per-robot fields.
    r1_data = next(r for r in result['robots'] if r['robot_id'] == 'R1')
    assert r1_data['location'] == 'FW'
    assert r1_data['battery_level'] == 100.0
    assert r1_data['status'] == 'idle'
    assert r1_data['bags'] == 0

    r2_data = next(r for r in result['robots'] if r['robot_id'] == 'R2')
    assert r2_data['location'] == 'Building_A'
    assert r2_data['battery_level'] == 85.0
    assert r2_data['bags'] == 2

    # Verify the event is truly read-only — save must never be called.
    mock_robot_service.save.assert_not_called()


# ** test: view_fleet_empty
def test_view_fleet_empty(mock_robot_service):
    '''
    Test that ViewFleet handles an empty fleet gracefully, returning
    robot_count of 0 and an empty robots list.

    :param mock_robot_service: The mock robot service.
    :type mock_robot_service: RobotService
    '''

    # No robots in fleet.
    mock_robot_service.list.return_value = []

    deps = {'robot_service': mock_robot_service}

    result = DomainEvent.handle(ViewFleet, dependencies=deps)

    assert result['robot_count'] == 0
    assert result['robots'] == []
    mock_robot_service.save.assert_not_called()
