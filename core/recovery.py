"""
core/recovery.py
Failure Recovery Analysis module.
Evaluates network impact when routers or links fail: primary vs. alternate route,
cost metrics, connected component changes, and lost reachability.
"""

from typing import Dict, List, Set, Any, Optional
from core.graph import Graph
from core.dijkstra import dijkstra
from core.components import find_components


def analyze_failure_recovery(
    graph: Graph,
    source_node: str,
    target_node: str
) -> Dict[str, Any]:
    """
    Performs failure recovery analysis for a given source and target router.
    Compares healthy network state vs current active network state.
    """
    src = str(source_node).strip()
    tgt = str(target_node).strip()

    # 1. Analyze Healthy Graph (Failures Cleared)
    healthy_graph = graph.clone()
    healthy_graph.clear_failures()
    
    healthy_dijkstra = dijkstra(healthy_graph, start_node=src, target_node=tgt)
    healthy_components = find_components(healthy_graph, method="BFS")

    # 2. Analyze Active Graph (Failures Applied)
    active_dijkstra = dijkstra(graph, start_node=src, target_node=tgt)
    active_components = find_components(graph, method="BFS")

    # Primary route & cost (Healthy)
    primary_route = healthy_dijkstra["path"]
    primary_cost = healthy_dijkstra["total_cost"]
    primary_reachable = healthy_dijkstra["reachable"]

    # Alternate route & cost (Active)
    alternate_route = active_dijkstra["path"]
    alternate_cost = active_dijkstra["total_cost"]
    alternate_reachable = active_dijkstra["reachable"]

    # Cost metrics calculation
    cost_increase: Optional[float] = None
    cost_increase_pct: Optional[float] = None

    if primary_cost is not None and alternate_cost is not None:
        cost_increase = round(alternate_cost - primary_cost, 4)
        if primary_cost > 0:
            cost_increase_pct = round((cost_increase / primary_cost) * 100.0, 2)
        else:
            cost_increase_pct = 0.0

    # Lost reachability calculation from source router
    healthy_all_dijkstra = dijkstra(healthy_graph, start_node=src, target_node=None)
    active_all_dijkstra = dijkstra(graph, start_node=src, target_node=None)

    healthy_reachable_nodes = {
        node for node, dist in healthy_all_dijkstra["distances"].items() if dist < float("inf")
    }
    active_reachable_nodes = {
        node for node, dist in active_all_dijkstra["distances"].items() if dist < float("inf")
    }

    lost_reachable_nodes = sorted(list(healthy_reachable_nodes - active_reachable_nodes))

    # Detailed status message
    if not graph.is_node_active(src):
        status = "FAILED_SOURCE"
        message = f"Source router '{src}' has failed! No routes can originate from a failed router."
    elif not graph.is_node_active(tgt):
        status = "FAILED_TARGET"
        message = f"Target router '{tgt}' has failed! Target is currently unavailable."
    elif not primary_reachable:
        status = "NO_PRIMARY_ROUTE"
        message = f"No route exists between '{src}' and '{tgt}' even in a fully healthy network."
    elif not alternate_reachable:
        status = "DISCONNECTED"
        message = f"NO ALTERNATE ROUTE EXISTS: Failure has completely disconnected router '{tgt}' from '{src}'."
    elif primary_route == alternate_route:
        status = "UNAFFECTED"
        message = "The primary route remains completely active and unaffected by current failures."
    else:
        status = "RECOVERED_REROUTED"
        message = f"Alternate route established! Cost increased by {cost_increase:.2f} ({cost_increase_pct}% increase)."

    return {
        "status": status,
        "message": message,
        "source": src,
        "target": tgt,
        "primary_route": primary_route,
        "primary_cost": primary_cost,
        "primary_reachable": primary_reachable,
        "alternate_route": alternate_route,
        "alternate_cost": alternate_cost,
        "alternate_reachable": alternate_reachable,
        "cost_increase": cost_increase,
        "cost_increase_pct": cost_increase_pct,
        "healthy_component_count": healthy_components["component_count"],
        "active_component_count": active_components["component_count"],
        "lost_reachable_nodes": lost_reachable_nodes,
        "failed_nodes": sorted(list(graph.get_failed_nodes())),
        "failed_edges": sorted(list(graph.get_failed_edges()))
    }
