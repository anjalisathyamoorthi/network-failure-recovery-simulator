"""
core/critical.py
Hand-crafted iterative implementation of Tarjan's algorithm for finding
Bridges (critical links) and Articulation Points (critical routers) in undirected graphs.
Fully recursion-safe for large graphs (1000+ nodes) and supports disconnected graphs.
"""

from typing import Dict, List, Set, Tuple, Optional, Any
from core.graph import Graph


def find_critical_connections(graph: Graph) -> Dict[str, Any]:
    """
    Finds all bridges and articulation points on the active graph using an iterative Tarjan's DFS.
    
    Returns dict with:
    - bridges: List[Tuple[str, str]] (sorted tuples with u < v)
    - articulation_points: List[str] (sorted list of node IDs)
    - discovery_times: Dict[str, int]
    - low_links: Dict[str, int]
    - steps: List[Dict[str, Any]]
    """
    active_nodes = graph.get_active_nodes()
    disc: Dict[str, int] = {}
    low: Dict[str, int] = {}
    parent_map: Dict[str, Optional[str]] = {}
    children: Dict[str, int] = {}
    is_ap: Set[str] = set()
    bridges: Set[Tuple[str, str]] = set()

    steps: List[Dict[str, Any]] = []
    timer = 0
    step_counter = 0

    step_counter += 1
    steps.append({
        "step_num": step_counter,
        "current_node": None,
        "explanation": "Starting Tarjan's Algorithm to identify critical links (bridges) and critical routers (articulation points).",
        "disc": dict(disc),
        "low": dict(low),
        "bridges": [],
        "articulation_points": [],
        "parent_map": dict(parent_map)
    })

    for root_node in active_nodes:
        if root_node in disc:
            continue

        # Stack frame format: [u, parent, neighbors_list, neighbor_index]
        root_neighbors = [nbr for nbr, _ in graph.get_active_neighbors(root_node)]
        
        timer += 1
        disc[root_node] = low[root_node] = timer
        parent_map[root_node] = None
        children[root_node] = 0

        step_counter += 1
        steps.append({
            "step_num": step_counter,
            "current_node": root_node,
            "explanation": f"Discovered root router '{root_node}' (disc={timer}, low={timer}).",
            "disc": dict(disc),
            "low": dict(low),
            "bridges": sorted(list(bridges)),
            "articulation_points": sorted(list(is_ap)),
            "parent_map": dict(parent_map)
        })

        stack: List[List[Any]] = [[root_node, None, root_neighbors, 0]]

        while stack:
            frame = stack[-1]
            u, p, neighbors, idx = frame[0], frame[1], frame[2], frame[3]

            if idx < len(neighbors):
                v = neighbors[idx]
                frame[3] += 1  # Increment neighbor index for next iteration

                if v == p:
                    # Ignore back edge to direct parent
                    continue

                if v in disc:
                    # Back-edge to an already visited ancestor
                    old_low = low[u]
                    low[u] = min(low[u], disc[v])
                    if low[u] < old_low:
                        step_counter += 1
                        steps.append({
                            "step_num": step_counter,
                            "current_node": u,
                            "explanation": f"Found back-edge ({u} -- {v}). Updated low[{u}] from {old_low} to {low[u]}.",
                            "disc": dict(disc),
                            "low": dict(low),
                            "bridges": sorted(list(bridges)),
                            "articulation_points": sorted(list(is_ap)),
                            "parent_map": dict(parent_map)
                        })
                else:
                    # Tree edge to unvisited child v
                    children[u] += 1
                    timer += 1
                    disc[v] = low[v] = timer
                    parent_map[v] = u
                    children[v] = 0

                    step_counter += 1
                    steps.append({
                        "step_num": step_counter,
                        "current_node": v,
                        "explanation": f"Tree edge ({u} -- {v}). Discovered router '{v}' (disc={timer}, low={timer}).",
                        "disc": dict(disc),
                        "low": dict(low),
                        "bridges": sorted(list(bridges)),
                        "articulation_points": sorted(list(is_ap)),
                        "parent_map": dict(parent_map)
                    })

                    v_neighbors = [nbr for nbr, _ in graph.get_active_neighbors(v)]
                    stack.append([v, u, v_neighbors, 0])

            else:
                # All neighbors of u processed. Post-process u before returning to parent p
                stack.pop()

                if p is not None:
                    old_low_p = low[p]
                    low[p] = min(low[p], low[u])

                    # Check Articulation Point condition for non-root parent p
                    if parent_map[p] is not None and low[u] >= disc[p]:
                        if p not in is_ap:
                            is_ap.add(p)
                            step_counter += 1
                            steps.append({
                                "step_num": step_counter,
                                "current_node": p,
                                "explanation": f"Router '{p}' identified as ARTICULATION POINT (low[{u}]={low[u]} >= disc[{p}]={disc[p]}).",
                                "disc": dict(disc),
                                "low": dict(low),
                                "bridges": sorted(list(bridges)),
                                "articulation_points": sorted(list(is_ap)),
                                "parent_map": dict(parent_map)
                            })

                    # Check Bridge condition for edge (p, u)
                    if low[u] > disc[p]:
                        edge = (min(p, u), max(p, u))
                        if edge not in bridges:
                            bridges.add(edge)
                            step_counter += 1
                            steps.append({
                                "step_num": step_counter,
                                "current_node": u,
                                "explanation": f"Link ({p} -- {u}) identified as BRIDGE / SINGLE POINT OF FAILURE (low[{u}]={low[u]} > disc[{p}]={disc[p]}).",
                                "disc": dict(disc),
                                "low": dict(low),
                                "bridges": sorted(list(bridges)),
                                "articulation_points": sorted(list(is_ap)),
                                "parent_map": dict(parent_map)
                            })

                else:
                    # Root node condition
                    if children[u] >= 2:
                        if u not in is_ap:
                            is_ap.add(u)
                            step_counter += 1
                            steps.append({
                                "step_num": step_counter,
                                "current_node": u,
                                "explanation": f"Root router '{u}' identified as ARTICULATION POINT (has {children[u]} DFS tree children).",
                                "disc": dict(disc),
                                "low": dict(low),
                                "bridges": sorted(list(bridges)),
                                "articulation_points": sorted(list(is_ap)),
                                "parent_map": dict(parent_map)
                            })

    sorted_bridges = sorted(list(bridges), key=lambda e: (e[0], e[1]))
    sorted_ap = sorted(list(is_ap))

    step_counter += 1
    steps.append({
        "step_num": step_counter,
        "current_node": None,
        "explanation": f"Tarjan's analysis complete! Found {len(sorted_bridges)} bridges and {len(sorted_ap)} articulation points.",
        "disc": dict(disc),
        "low": dict(low),
        "bridges": sorted_bridges,
        "articulation_points": sorted_ap,
        "parent_map": dict(parent_map)
    })

    return {
        "bridges": sorted_bridges,
        "articulation_points": sorted_ap,
        "discovery_times": disc,
        "low_links": low,
        "steps": steps
    }
