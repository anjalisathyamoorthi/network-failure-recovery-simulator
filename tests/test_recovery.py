"""
tests/test_recovery.py
Unit tests for failure recovery analysis.
"""

from core.graph import Graph
from core.recovery import analyze_failure_recovery


def test_failure_recovery_rerouting():
    g = Graph()
    g.add_edge("A", "B", 2.0)
    g.add_edge("B", "C", 2.0)
    g.add_edge("A", "X", 3.0)
    g.add_edge("X", "C", 3.0)

    # Primary route A -> B -> C (cost 4)
    res_healthy = analyze_failure_recovery(g, source_node="A", target_node="C")
    assert res_healthy["status"] == "UNAFFECTED"
    assert res_healthy["primary_cost"] == 4.0

    # Fail router B
    g.fail_node("B")
    res_failed = analyze_failure_recovery(g, source_node="A", target_node="C")
    assert res_failed["status"] == "RECOVERED_REROUTED"
    assert res_failed["alternate_route"] == ["A", "X", "C"]
    assert res_failed["alternate_cost"] == 6.0
    assert res_failed["cost_increase"] == 2.0


def test_failure_recovery_disconnected():
    g = Graph()
    g.add_edge("A", "B", 1.0)
    g.add_edge("B", "C", 1.0)

    g.fail_edge("B", "C")
    res = analyze_failure_recovery(g, source_node="A", target_node="C")
    assert res["status"] == "DISCONNECTED"
    assert res["alternate_reachable"] is False
    assert "C" in res["lost_reachable_nodes"]
