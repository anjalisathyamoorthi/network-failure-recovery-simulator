"""
tests/test_dijkstra.py
Unit tests for Dijkstra's shortest path algorithm including edge cases and NetworkX cross-checks.
"""

import pytest
import networkx as nx
from core.graph import Graph
from core.dijkstra import dijkstra


def test_dijkstra_basic_shortest_path():
    g = Graph()
    g.add_edge("A", "B", 4.0)
    g.add_edge("A", "C", 2.0)
    g.add_edge("C", "B", 1.0)
    g.add_edge("B", "D", 5.0)
    g.add_edge("C", "D", 8.0)

    res = dijkstra(g, start_node="A", target_node="D")
    assert res["reachable"] is True
    # Path should be A -> C -> B -> D with cost 2 + 1 + 5 = 8.0
    assert res["path"] == ["A", "C", "B", "D"]
    assert res["total_cost"] == 8.0


def test_dijkstra_zero_weight_edges():
    g = Graph()
    g.add_edge("A", "B", 0.0)
    g.add_edge("B", "C", 0.0)
    g.add_edge("C", "D", 5.0)

    res = dijkstra(g, start_node="A", target_node="D")
    assert res["reachable"] is True
    assert res["total_cost"] == 5.0
    assert res["path"] == ["A", "B", "C", "D"]


def test_dijkstra_source_equals_target():
    g = Graph()
    g.add_node("A")
    res = dijkstra(g, start_node="A", target_node="A")
    assert res["reachable"] is True
    assert res["total_cost"] == 0.0
    assert res["path"] == ["A"]


def test_dijkstra_unreachable_target():
    g = Graph()
    g.add_node("A")
    g.add_node("B")
    res = dijkstra(g, start_node="A", target_node="B")
    assert res["reachable"] is False
    assert res["total_cost"] is None
    assert res["path"] == []


def test_dijkstra_failed_source_or_target():
    g = Graph()
    g.add_edge("A", "B", 3.0)
    g.fail_node("A")

    res = dijkstra(g, start_node="A", target_node="B")
    assert res["reachable"] is False

    g.clear_failures()
    g.fail_node("B")
    res = dijkstra(g, start_node="A", target_node="B")
    assert res["reachable"] is False


def test_dijkstra_graph_with_cycles():
    g = Graph()
    g.add_edge("A", "B", 1.0)
    g.add_edge("B", "C", 2.0)
    g.add_edge("C", "A", 4.0)

    res = dijkstra(g, start_node="A", target_node="C")
    assert res["reachable"] is True
    assert res["path"] == ["A", "B", "C"]
    assert res["total_cost"] == 3.0


def test_dijkstra_tree_graph():
    g = Graph()
    g.add_edge("ROOT", "L1", 10.0)
    g.add_edge("ROOT", "R1", 5.0)
    g.add_edge("R1", "R2", 2.0)

    res = dijkstra(g, start_node="ROOT", target_node="R2")
    assert res["reachable"] is True
    assert res["path"] == ["ROOT", "R1", "R2"]
    assert res["total_cost"] == 7.0


def test_networkx_crosscheck_dijkstra():
    g = Graph()
    g.add_edge("R1", "R2", 3.0)
    g.add_edge("R2", "R3", 4.0)
    g.add_edge("R1", "R3", 10.0)

    # Build networkx graph
    nxg = nx.Graph()
    for u, v, w in g.get_all_edges():
        nxg.add_edge(u, v, weight=w)

    nx_path = nx.dijkstra_path(nxg, "R1", "R3")
    nx_cost = nx.dijkstra_path_length(nxg, "R1", "R3")

    our_res = dijkstra(g, start_node="R1", target_node="R3")
    assert our_res["path"] == nx_path
    assert our_res["total_cost"] == nx_cost
