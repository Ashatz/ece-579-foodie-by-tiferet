"""
FOODIE AStarRoutePlanner Utility Tests
"""

# *** imports

# ** infra
import pytest

# ** app
from ...mappers.location import LocationAggregate
from ..route_planner import AStarRoutePlanner

# *** fixtures

# ** fixture: planner
@pytest.fixture
def planner() -> AStarRoutePlanner:
    '''
    Create an AStarRoutePlanner instance.

    :return: The route planner.
    :rtype: AStarRoutePlanner
    '''

    return AStarRoutePlanner()


# ** fixture: loc_map
@pytest.fixture
def loc_map() -> dict:
    '''
    Build a simple 4-node grid graph for testing.

    Layout (Manhattan distances):
        A(0,0) -- B(1,0)
        |         |
        C(0,1) -- D(1,1)

    :return: Location lookup by name.
    :rtype: dict
    '''

    return {
        'A': LocationAggregate(name='A', x=0.0, y=0.0),
        'B': LocationAggregate(name='B', x=1.0, y=0.0),
        'C': LocationAggregate(name='C', x=0.0, y=1.0),
        'D': LocationAggregate(name='D', x=1.0, y=1.0),
    }


# ** fixture: edges
@pytest.fixture
def edges() -> dict:
    '''
    Adjacency list for the 4-node grid (bidirectional).

    :return: Adjacency dict.
    :rtype: dict
    '''

    return {
        'A': ['B', 'C'],
        'B': ['A', 'D'],
        'C': ['A', 'D'],
        'D': ['B', 'C'],
    }


# ** fixture: long_loc_map
@pytest.fixture
def long_loc_map() -> dict:
    '''
    Build a 5-node linear graph for obstacle detection tests.

    Layout: A(0,0) -- B(1,0) -- C(2,0) -- D(3,0) -- E(4,0)
    With bypass: B -- F(1,1) -- D

    :return: Location lookup by name.
    :rtype: dict
    '''

    return {
        'A': LocationAggregate(name='A', x=0.0, y=0.0),
        'B': LocationAggregate(name='B', x=1.0, y=0.0),
        'C': LocationAggregate(name='C', x=2.0, y=0.0),
        'D': LocationAggregate(name='D', x=3.0, y=0.0),
        'E': LocationAggregate(name='E', x=4.0, y=0.0),
        'F': LocationAggregate(name='F', x=1.0, y=1.0),
    }


# ** fixture: long_edges
@pytest.fixture
def long_edges() -> dict:
    '''
    Adjacency list for the 5-node linear graph with bypass.

    :return: Adjacency dict.
    :rtype: dict
    '''

    return {
        'A': ['B'],
        'B': ['A', 'C', 'F'],
        'C': ['B', 'D'],
        'D': ['C', 'E', 'F'],
        'E': ['D'],
        'F': ['B', 'D'],
    }


# *** tests

# ** test: find_path_direct_neighbor
def test_find_path_direct_neighbor(planner: AStarRoutePlanner, loc_map: dict, edges: dict) -> None:
    '''
    Test A* finds a direct neighbor path.

    :param planner: The route planner.
    :type planner: AStarRoutePlanner
    :param loc_map: Location lookup.
    :type loc_map: dict
    :param edges: Adjacency list.
    :type edges: dict
    '''

    path, dist = planner.find_path('A', 'B', loc_map, edges, set())

    assert path == ['A', 'B']
    assert dist == pytest.approx(1.0)


# ** test: find_path_multi_hop
def test_find_path_multi_hop(planner: AStarRoutePlanner, loc_map: dict, edges: dict) -> None:
    '''
    Test A* finds a multi-hop path through intermediate nodes.

    :param planner: The route planner.
    :type planner: AStarRoutePlanner
    :param loc_map: Location lookup.
    :type loc_map: dict
    :param edges: Adjacency list.
    :type edges: dict
    '''

    path, dist = planner.find_path('A', 'D', loc_map, edges, set())

    # Optimal path is A->B->D or A->C->D (both cost 2.0).
    assert path is not None
    assert path[0] == 'A'
    assert path[-1] == 'D'
    assert dist == pytest.approx(2.0)


# ** test: find_path_no_route
def test_find_path_no_route(planner: AStarRoutePlanner) -> None:
    '''
    Test A* returns None for a disconnected graph.

    :param planner: The route planner.
    :type planner: AStarRoutePlanner
    '''

    loc_map = {
        'X': LocationAggregate(name='X', x=0.0, y=0.0),
        'Y': LocationAggregate(name='Y', x=5.0, y=5.0),
    }
    edges = {'X': [], 'Y': []}

    path, dist = planner.find_path('X', 'Y', loc_map, edges, set())

    assert path is None
    assert dist == 0.0


# ** test: find_path_with_obstacle
def test_find_path_with_obstacle(planner: AStarRoutePlanner, loc_map: dict, edges: dict) -> None:
    '''
    Test A* routes around a blocked edge.

    :param planner: The route planner.
    :type planner: AStarRoutePlanner
    :param loc_map: Location lookup.
    :type loc_map: dict
    :param edges: Adjacency list.
    :type edges: dict
    '''

    # Block A->B in both directions.
    obstacles = {('A', 'B'), ('B', 'A')}

    path, dist = planner.find_path('A', 'D', loc_map, edges, obstacles)

    # Must go A->C->D.
    assert path == ['A', 'C', 'D']
    assert dist == pytest.approx(2.0)


# ** test: find_path_unknown_start_or_goal
def test_find_path_unknown_start_or_goal(planner: AStarRoutePlanner, loc_map: dict, edges: dict) -> None:
    '''
    Test A* returns None when start or goal is not in the graph.

    :param planner: The route planner.
    :type planner: AStarRoutePlanner
    :param loc_map: Location lookup.
    :type loc_map: dict
    :param edges: Adjacency list.
    :type edges: dict
    '''

    path1, dist1 = planner.find_path('UNKNOWN', 'A', loc_map, edges, set())
    path2, dist2 = planner.find_path('A', 'UNKNOWN', loc_map, edges, set())

    assert path1 is None and dist1 == 0.0
    assert path2 is None and dist2 == 0.0


# ** test: detect_and_replan_success
def test_detect_and_replan_success(
    planner: AStarRoutePlanner,
    long_loc_map: dict,
    long_edges: dict,
) -> None:
    '''
    Test obstacle detection and successful replanning on a long path.

    :param planner: The route planner.
    :type planner: AStarRoutePlanner
    :param long_loc_map: Location lookup for the long graph.
    :type long_loc_map: dict
    :param long_edges: Adjacency list for the long graph.
    :type long_edges: dict
    '''

    # Original path: A -> B -> C -> D -> E (5 nodes, midpoint idx=2, blocks C->D).
    original_path = ['A', 'B', 'C', 'D', 'E']
    obstacles = set()

    new_path, new_dist, updated_obs = planner.detect_and_replan(
        original_path, 'E', long_loc_map, long_edges, obstacles,
    )

    # Should have replanned around C->D.
    assert new_path is not None
    assert new_path[0] == 'A'
    assert new_path[-1] == 'E'
    assert ('C', 'D') in updated_obs
    assert ('D', 'C') in updated_obs
    assert new_dist > 0.0


# ** test: detect_and_replan_no_alternative
def test_detect_and_replan_no_alternative(planner: AStarRoutePlanner) -> None:
    '''
    Test replanning when no alternative route exists after obstacle injection.

    :param planner: The route planner.
    :type planner: AStarRoutePlanner
    '''

    # Linear graph with no bypass: A -- B -- C -- D -- E.
    loc_map = {
        'A': LocationAggregate(name='A', x=0.0, y=0.0),
        'B': LocationAggregate(name='B', x=1.0, y=0.0),
        'C': LocationAggregate(name='C', x=2.0, y=0.0),
        'D': LocationAggregate(name='D', x=3.0, y=0.0),
        'E': LocationAggregate(name='E', x=4.0, y=0.0),
    }
    edges = {
        'A': ['B'], 'B': ['A', 'C'], 'C': ['B', 'D'],
        'D': ['C', 'E'], 'E': ['D'],
    }
    original_path = ['A', 'B', 'C', 'D', 'E']

    new_path, new_dist, _ = planner.detect_and_replan(
        original_path, 'E', loc_map, edges, set(),
    )

    # Blocking C->D with no bypass means replan fails.
    assert new_path is None
    assert new_dist == 0.0


# ** test: detect_and_replan_short_path_no_obstacle
def test_detect_and_replan_short_path_no_obstacle(
    planner: AStarRoutePlanner,
    loc_map: dict,
    edges: dict,
) -> None:
    '''
    Test that short paths (<=3 nodes) do not trigger obstacle injection.

    :param planner: The route planner.
    :type planner: AStarRoutePlanner
    :param loc_map: Location lookup.
    :type loc_map: dict
    :param edges: Adjacency list.
    :type edges: dict
    '''

    short_path = ['A', 'B', 'D']
    obstacles = set()

    new_path, new_dist, updated_obs = planner.detect_and_replan(
        short_path, 'D', loc_map, edges, obstacles,
    )

    # No obstacle should be injected.
    assert new_path is None
    assert new_dist == 0.0
    assert len(updated_obs) == 0
