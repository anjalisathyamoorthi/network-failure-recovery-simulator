"""
tests/test_critical.py
Unit tests for Tarjan's Critical Connections algorithm (bridges and articulation points)
with NetworkX cross-checks and large graph performance checks.
"""

import networkx as nx
from core.graph import Graph
from core.critical import find_critical_connections
from core.presets import generate_random_graph, get_star_topology_preset, get_ring_topology_preset


def test_tree_graph_all_edges_are_bridges():
    g = Graph()
    g.add_edge("R", "A", 1.0)
    g.add_edge("R", "B", 1.0)
    g.add_edge("A", "A1", 1.0)

    res = find_critical_connections(g)
    assert len(res["bridges"]) == 3
    assert "R" in res["articulation_points"]
    assert "A" in res["articulation_points"]


def test_ring_graph_no_bridges_or_ap():
    g = get_ring_topology_preset(num_nodes=5)
    res = find_critical_connections(g)
    assert len(res["bridges"]) == 0
    assert len(res["articulation_points"]) == 0


def test_star_graph_hub_is_articulation_point():
    g = get_star_topology_preset(num_spokes=4)
    res = find_critical_connections(g)
    assert res["articulation_points"] == ["HUB"]
    assert len(res["bridges"]) == 4


def test_networkx_crosscheck_tarjan():
    g = Graph()
    # Bottleneck graph: Left triangle A-B-C connected via bridge C-D to Right triangle D-E-F
    g.add_edge("A", "B", 1.0)
    g.add_edge("B", "C", 1.0)
    g.add_edge("C", "A", 1.0)
    g.add_edge("C", "D", 2.0)
    g.add_edge("D", "E", 1.0)
    g.add_edge("E", "F", 1.0)
    g.add_edge("F", "D", 1.0)

    res = find_critical_connections(g)

    # NetworkX cross-check
    nxg = nx.Graph()
    for u, v, w in g.get_all_edges():
        nxg.add_edge(u, v)

    nx_bridges = sorted([tuple(sorted(e)) for e in nx.bridges(nxg)])
    nx_aps = sorted(list(nx.articulation_points(nxg)))

    assert res["bridges"] == nx_bridges
    assert res["articulation_points"] == nx_aps


def test_large_graph_1000_nodes_performance():
    """Verifies that Tarjan's algorithm handles a 1000-node graph quickly without recursion error."""
    g = generate_random_graph(num_nodes=1000, edge_density=0.01, seed=42)
    res = find_critical_connections(g)
    assert isinstance(res["bridges"], list)
    assert isinstance(res["articulation_points"], list)
