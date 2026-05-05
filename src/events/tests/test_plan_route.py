"""
FOODIE PlanRoute Domain Event Tests
"""

# *** imports

# ** core
from unittest import mock

# ** infra
import pytest
from tiferet.events import DomainEvent

# ** app
from ...domain import Location, Order, Robot
from ...interfaces import OrderService, RobotService, RoutePlannerService
from ..plan_route import PlanRoute

# *** fixtures

# ** fixture: fw_location
@pytest.fixture
def fw_location() -> Location:
    '''
    Food Warehouse location for robot starting position.

    :return: A Location domain object.
    :rtype: Location
    '''

    return Location(name='FW', x=0.0, y=0.0, is_food_warehouse=True)


# ** fixture: sample_robot
@pytest.fixture
def sample_robot(fw_location: Location) -> Robot:
    '''
    A sample robot at the Food Warehouse.

    :param fw_location: The Food Warehouse location.
    :type fw_location: Location
    :return: A Robot domain object.
    :rtype: Robot
    '''

    return Robot(robot_id='R1', current_location=fw_location, battery_level=100.0, status='idle')


# ** fixture: sample_order
@pytest.fixture
def sample_order() -> Order:
    '''
    A sample order destined for Building_A.

    :return: An Order domain object.
    :rtype: Order
    '''

    return Order(order_id='ORD-1', destination='Building_A', items=[])


# ** fixture: sample_locations
@pytest.fixture
def sample_locations() -> list:
    '''
    Minimal location list for the campus graph.

    :return: List of Location domain objects.
    :rtype: list[Location]
    '''

    return [
        Location(name='FW', x=0.0, y=0.0, is_food_warehouse=True),
        Location(name='Building_A', x=3.0, y=0.0),
    ]


# ** fixture: sample_edges
@pytest.fixture
def sample_edges() -> dict:
    '''
    Simple bidirectional edge list.

    :return: Adjacency dict.
    :rtype: dict
    '''

    return {
        'FW': ['Building_A'],
        'Building_A': ['FW'],
    }


# ** fixture: mock_robot_service
@pytest.fixture
def mock_robot_service(sample_robot: Robot) -> RobotService:
    '''
    Mock RobotService returning one robot.

    :param sample_robot: The sample robot.
    :type sample_robot: Robot
    :return: Mocked service.
    :rtype: RobotService
    '''

    svc = mock.Mock(spec=RobotService)
    svc.list.return_value = [sample_robot]
    return svc


# ** fixture: mock_order_service
@pytest.fixture
def mock_order_service(sample_order: Order) -> OrderService:
    '''
    Mock OrderService returning one order.

    :param sample_order: The sample order.
    :type sample_order: Order
    :return: Mocked service.
    :rtype: OrderService
    '''

    svc = mock.Mock(spec=OrderService)
    svc.list.return_value = [sample_order]
    return svc


# ** fixture: mock_route_planner
@pytest.fixture
def mock_route_planner() -> RoutePlannerService:
    '''
    Mock RoutePlannerService.

    :return: Mocked service.
    :rtype: RoutePlannerService
    '''

    return mock.Mock(spec=RoutePlannerService)


# *** tests

# ** test: plan_route_success
def test_plan_route_success(
    mock_robot_service: RobotService,
    mock_order_service: OrderService,
    mock_route_planner: RoutePlannerService,
    sample_locations: list,
    sample_edges: dict,
) -> None:
    '''
    Test successful route planning with a valid path.

    :param mock_robot_service: Mocked robot service.
    :type mock_robot_service: RobotService
    :param mock_order_service: Mocked order service.
    :type mock_order_service: OrderService
    :param mock_route_planner: Mocked route planner.
    :type mock_route_planner: RoutePlannerService
    :param sample_locations: List of locations.
    :type sample_locations: list
    :param sample_edges: Adjacency list.
    :type sample_edges: dict
    '''

    # Arrange: planner returns a valid path, no replan needed.
    mock_route_planner.find_path.return_value = (['FW', 'Building_A'], 3.0)
    mock_route_planner.detect_and_replan.return_value = (None, 0.0, set())

    # Act.
    result = DomainEvent.handle(
        PlanRoute,
        dependencies={
            'robot_service': mock_robot_service,
            'order_service': mock_order_service,
            'route_planner': mock_route_planner,
        },
        locations=sample_locations,
        edges=sample_edges,
    )

    # Assert.
    assert result['status'] == 'complete'
    assert result['routes_planned'] == 1
    assert result['details'][0]['status'] == 'planned'
    assert result['details'][0]['path'] == ['FW', 'Building_A']
    assert result['details'][0]['distance'] == 3.0
    mock_route_planner.find_path.assert_called_once()
    mock_robot_service.save.assert_called_once()


# ** test: plan_route_no_path
def test_plan_route_no_path(
    mock_robot_service: RobotService,
    mock_order_service: OrderService,
    mock_route_planner: RoutePlannerService,
    sample_locations: list,
    sample_edges: dict,
) -> None:
    '''
    Test route planning when no path exists.

    :param mock_robot_service: Mocked robot service.
    :type mock_robot_service: RobotService
    :param mock_order_service: Mocked order service.
    :type mock_order_service: OrderService
    :param mock_route_planner: Mocked route planner.
    :type mock_route_planner: RoutePlannerService
    :param sample_locations: List of locations.
    :type sample_locations: list
    :param sample_edges: Adjacency list.
    :type sample_edges: dict
    '''

    # Arrange: planner returns no path.
    mock_route_planner.find_path.return_value = (None, 0.0)

    # Act.
    result = DomainEvent.handle(
        PlanRoute,
        dependencies={
            'robot_service': mock_robot_service,
            'order_service': mock_order_service,
            'route_planner': mock_route_planner,
        },
        locations=sample_locations,
        edges=sample_edges,
    )

    # Assert.
    assert result['status'] == 'complete'
    assert result['details'][0]['status'] == 'no_path'
    assert result['total_distance'] == 0.0
    mock_route_planner.detect_and_replan.assert_not_called()
    mock_robot_service.save.assert_not_called()


# ** test: plan_route_replan
def test_plan_route_replan(
    mock_robot_service: RobotService,
    mock_order_service: OrderService,
    mock_route_planner: RoutePlannerService,
    sample_locations: list,
    sample_edges: dict,
) -> None:
    '''
    Test route planning with obstacle detection and replanning.

    :param mock_robot_service: Mocked robot service.
    :type mock_robot_service: RobotService
    :param mock_order_service: Mocked order service.
    :type mock_order_service: OrderService
    :param mock_route_planner: Mocked route planner.
    :type mock_route_planner: RoutePlannerService
    :param sample_locations: List of locations.
    :type sample_locations: list
    :param sample_edges: Adjacency list.
    :type sample_edges: dict
    '''

    # Arrange: initial path found, then replan returns a new path.
    mock_route_planner.find_path.return_value = (['FW', 'Building_A'], 3.0)
    mock_route_planner.detect_and_replan.return_value = (
        ['FW', 'Detour', 'Building_A'], 5.0, {('FW', 'Building_A'), ('Building_A', 'FW')},
    )

    # Act.
    result = DomainEvent.handle(
        PlanRoute,
        dependencies={
            'robot_service': mock_robot_service,
            'order_service': mock_order_service,
            'route_planner': mock_route_planner,
        },
        locations=sample_locations,
        edges=sample_edges,
    )

    # Assert: the replanned path and distance are used.
    assert result['details'][0]['path'] == ['FW', 'Detour', 'Building_A']
    assert result['details'][0]['distance'] == 5.0
    assert result['total_distance'] == 5.0
    mock_route_planner.detect_and_replan.assert_called_once()
