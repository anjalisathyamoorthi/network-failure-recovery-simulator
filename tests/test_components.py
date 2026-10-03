"""
tests/test_components.py
Unit tests for connected component discovery and NetworkX cross-checks.
"""

import networkx as nx
from core.graph import Graph
from core.components import find_components, compare_components


def test_components_empty_graph():
    g = Graph()
    res = find_components(g, method="BFS")
    assert res["component_count"] == 0
    assert res["components"] == []


def test_components_single_node():
    g = Graph()
    g.add_node("A")
    res = find_components(g, method="BFS")
    assert res["component_count"] == 1
    assert res["components"] == [["A"]]
    assert res["isolated_nodes"] == ["A"]


def test_already_disconnected_graph():
    g = Graph()
    g.add_edge("A1", "A2", 1.0)
    g.add_edge("B1", "B2", 1.0)

    res = find_components(g, method="BFS")
    assert res["component_count"] == 2
    comp_sets = [set(c) for c in res["components"]]
    assert {"A1", "A2"} in comp_sets
    assert {"B1", "B2"} in comp_sets


def test_components_after_failure():
    g = Graph()
    g.add_edge("A", "B", 1.0)
    g.add_edge("B", "C", 1.0)

    res_before = find_components(g, method="BFS")
    assert res_before["component_count"] == 1

    g.fail_node("B")
    res_after = find_components(g, method="BFS")
    assert res_after["component_count"] == 2
    assert res_after["isolated_nodes"] == ["A", "C"]


def test_compare_bfs_and_dfs_components():
    g = Graph()
    g.add_edge("1", "2", 1.0)
    g.add_edge("2", "3", 1.0)
    g.add_edge("4", "5", 1.0)

    comp_eval = compare_components(g)
    assert comp_eval["identical_components"] is True
    assert comp_eval["bfs_component_count"] == 2


def test_networkx_crosscheck_components():
    g = Graph()
    g.add_edge("A", "B", 1.0)
    g.add_edge("C", "D", 1.0)
    g.add_node("E")

    nxg = nx.Graph()
    for n in g.get_all_nodes():
        nxg.add_node(n)
    for u, v, w in g.get_all_edges():
        nxg.add_edge(u, v)

    nx_comps = [set(c) for c in nx.connected_components(nxg)]
    our_comps = [set(c) for c in find_components(g)["components"]]

    sorted_nx = sorted(nx_comps, key=lambda s: (len(s), sorted(list(s))))
    sorted_our = sorted(our_comps, key=lambda s: (len(s), sorted(list(s))))
    assert sorted_our == sorted_nx
