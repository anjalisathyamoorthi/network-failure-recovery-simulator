"""
tests/test_graph.py
Unit tests for core Graph data structure, validation rules, and failure state handling.
"""

import pytest
from core.graph import Graph


def test_empty_graph():
    g = Graph()
    assert g.get_all_nodes() == []
    assert g.get_active_nodes() == []
    assert g.get_all_edges() == []


def test_add_and_remove_nodes():
    g = Graph()
    g.add_node("R1")
    g.add_node("R2")
    assert sorted(g.get_all_nodes()) == ["R1", "R2"]

    g.remove_node("R1")
    assert g.get_all_nodes() == ["R2"]

    with pytest.raises(ValueError):
        g.remove_node("NON_EXISTENT")


def test_validation_negative_weight():
    g = Graph()
    with pytest.raises(ValueError, match="cannot be negative"):
        g.add_edge("R1", "R2", -5.0)


def test_validation_self_loop():
    g = Graph()
    with pytest.raises(ValueError, match="Self-loops are not allowed"):
        g.add_edge("R1", "R1", 2.0)


def test_validation_duplicate_edge():
    g = Graph()
    g.add_edge("R1", "R2", 3.0)
    with pytest.raises(ValueError, match="already exists"):
        g.add_edge("R1", "R2", 4.0)


def test_validation_unknown_node():
    g = Graph()
    g.add_node("R1")
    with pytest.raises(ValueError, match="Unknown router"):
        g.add_edge("R1", "R2", 3.0, auto_add_nodes=False)


def test_failure_states_and_undo():
    g = Graph()
    g.add_edge("R1", "R2", 1.0)
    g.add_edge("R2", "R3", 2.0)

    # Node failure
    g.fail_node("R2")
    assert not g.is_node_active("R2")
    assert g.get_active_nodes() == ["R1", "R3"]
    assert g.get_active_neighbors("R1") == []
    assert g.get_active_neighbors("R2") == []

    # Restore node
    g.restore_node("R2")
    assert g.is_node_active("R2")
    assert len(g.get_active_neighbors("R1")) == 1

    # Edge failure
    g.fail_edge("R1", "R2")
    assert not g.is_edge_active("R1", "R2")
    assert g.get_active_neighbors("R1") == []

    # Clear all failures
    g.clear_failures()
    assert g.is_edge_active("R1", "R2")
    assert len(g.get_active_edges()) == 2


def test_serialization_and_csv():
    g = Graph()
    g.add_edge("A", "B", 5.0)
    g.add_edge("B", "C", 10.0)

    # CSV string test
    csv_str = g.to_csv_string()
    g_csv = Graph.from_csv_string(csv_str)
    assert g_csv.get_all_nodes() == ["A", "B", "C"]
    assert len(g_csv.get_all_edges()) == 2

    # Dict test
    d = g.to_dict()
    g_dict = Graph.from_dict(d)
    assert g_dict.get_all_nodes() == ["A", "B", "C"]
    assert len(g_dict.get_all_edges()) == 2
