"""
tests/test_bfs.py
Unit tests for Breadth-First Search (BFS) implementation.
"""

from core.graph import Graph
from core.bfs import bfs


def test_bfs_basic_path():
    g = Graph()
    g.add_edge("A", "B", 1.0)
    g.add_edge("B", "C", 2.0)
    g.add_edge("A", "C", 5.0)

    res = bfs(g, start_node="A", target_node="C")
    assert res["reachable"] is True
    assert res["hop_count"] == 1  # Direct edge A-C has 1 hop
    assert res["path"] == ["A", "C"]


def test_bfs_source_equals_target():
    g = Graph()
    g.add_node("A")
    res = bfs(g, start_node="A", target_node="A")
    assert res["reachable"] is True
    assert res["hop_count"] == 0
    assert res["path"] == ["A"]


def test_bfs_unreachable_target():
    g = Graph()
    g.add_node("A")
    g.add_node("B")
    res = bfs(g, start_node="A", target_node="B")
    assert res["reachable"] is False
    assert res["path"] == []
    assert res["hop_count"] is None


def test_bfs_failing_source_or_destination():
    g = Graph()
    g.add_edge("A", "B", 1.0)
    g.fail_node("A")

    res = bfs(g, start_node="A", target_node="B")
    assert res["reachable"] is False
    assert res["path"] == []

    g.clear_failures()
    g.fail_node("B")
    res = bfs(g, start_node="A", target_node="B")
    assert res["reachable"] is False
    assert res["path"] == []


def test_bfs_single_node():
    g = Graph()
    g.add_node("X")
    res = bfs(g, start_node="X")
    assert res["visit_order"] == ["X"]
    assert res["levels"] == {"X": 0}
