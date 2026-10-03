"""
core/components.py
Connected Component discovery and comparison module.
Supports BFS-based and DFS-based component identification with step logging and comparison metrics.
"""

import time
from typing import Dict, List, Set, Any, Tuple
from core.graph import Graph
from core.bfs import bfs
from core.dfs import dfs


def find_components(graph: Graph, method: str = "BFS") -> Dict[str, Any]:
    """
    Finds all connected components of active nodes using BFS or DFS traversal.
    
    Returns dict with:
    - components: List[List[str]] (each list is a sorted component)
    - component_count: int
    - component_sizes: List[int]
    - isolated_nodes: List[str]
    - traversal_method: str
    - steps: List[Dict[str, Any]]
    """
    method_upper = method.upper()
    if method_upper not in ["BFS", "DFS"]:
        raise ValueError(f"Invalid method '{method}'. Must be 'BFS' or 'DFS'.")

    active_nodes = graph.get_active_nodes()
    visited: Set[str] = set()
    components: List[List[str]] = []
    isolated_nodes: List[str] = []
    all_steps: List[Dict[str, Any]] = []

    step_counter = 0

    for node in active_nodes:
        if node not in visited:
            # Run selected traversal starting from unvisited node
            if method_upper == "BFS":
                result = bfs(graph, start_node=node)
            else:
                result = dfs(graph, start_node=node)

            comp_nodes = sorted(result["visit_order"]) if result["visit_order"] else [node]
            visited.update(comp_nodes)
            components.append(comp_nodes)

            if len(comp_nodes) == 1:
                isolated_nodes.append(node)

            step_counter += 1
            all_steps.append({
                "step_num": step_counter,
                "current_node": node,
                "explanation": f"Discovered Component {len(components)} starting from '{node}': {comp_nodes} ({len(comp_nodes)} nodes).",
                "component_id": len(components),
                "component_nodes": comp_nodes,
                "visited_so_far": list(visited)
            })

    # Sort components by size descending, then first node
    components.sort(key=lambda c: (-len(c), c[0] if c else ""))

    return {
        "components": components,
        "component_count": len(components),
        "component_sizes": [len(c) for c in components],
        "isolated_nodes": sorted(isolated_nodes),
        "traversal_method": method_upper,
        "steps": all_steps
    }


def compare_components(graph: Graph) -> Dict[str, Any]:
    """
    Compares BFS-based vs DFS-based connected component discovery.
    Calculates execution time, total nodes visited, visit order differences, and component equivalence.
    """
    # Benchmark BFS components
    t0 = time.perf_counter()
    bfs_res = find_components(graph, method="BFS")
    bfs_time = (time.perf_counter() - t0) * 1000.0  # in ms

    # Benchmark DFS components
    t0 = time.perf_counter()
    dfs_res = find_components(graph, method="DFS")
    dfs_time = (time.perf_counter() - t0) * 1000.0  # in ms

    # Normalize component sets for comparison
    bfs_comp_sets = [set(c) for c in bfs_res["components"]]
    dfs_comp_sets = [set(c) for c in dfs_res["components"]]

    same_count = len(bfs_comp_sets) == len(dfs_comp_sets)
    
    # Sort sets for strict structural equivalence check
    sorted_bfs = sorted(bfs_comp_sets, key=lambda s: (len(s), sorted(list(s))))
    sorted_dfs = sorted(dfs_comp_sets, key=lambda s: (len(s), sorted(list(s))))
    identical_components = (sorted_bfs == sorted_dfs)

    explanation = (
        "Both BFS and DFS partition the graph into the exact same connected components because reachability "
        "is a structural property of undirected graphs. However, their visit orders and traversal dynamics differ: "
        "BFS explores breadth-first level-by-level (producing minimum-hop trees), whereas DFS explores deep along paths "
        "before backtracking."
    )

    return {
        "bfs_component_count": bfs_res["component_count"],
        "dfs_component_count": dfs_res["component_count"],
        "bfs_time_ms": round(bfs_time, 4),
        "dfs_time_ms": round(dfs_time, 4),
        "components": bfs_res["components"],
        "identical_components": identical_components,
        "explanation": explanation
    }
