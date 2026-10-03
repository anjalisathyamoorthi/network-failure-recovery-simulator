"""
tests/test_dfs.py
Unit tests for iterative Depth-First Search (DFS) implementation.
"""

from core.graph import Graph
from core.dfs import dfs


def test_dfs_basic_traversal():
    g = Graph()
    g.add_edge("A", "B", 1.0)
    g.add_edge("B", "C", 1.0)

    res = dfs(g, start_node="A", target_node="C")
    assert res["reachable"] is True
    assert res["path"] == ["A", "B", "C"]
    assert "A" in res["discovery_time"]
    assert "C" in res["finish_time"]


def test_dfs_source_equals_target():
    g = Graph()
    g.add_node("A")
    res = dfs(g, start_node="A", target_node="A")
    assert res["reachable"] is True
    assert res["path"] == ["A"]


def test_dfs_unreachable_target():
    g = Graph()
    g.add_node("A")
    g.add_node("B")
    res = dfs(g, start_node="A", target_node="B")
    assert res["reachable"] is False
    assert res["path"] == []


def test_dfs_failing_source():
    g = Graph()
    g.add_edge("A", "B", 1.0)
    g.fail_node("A")

    res = dfs(g, start_node="A", target_node="B")
    assert res["reachable"] is False
    assert res["path"] == []
