"""
core/dijkstra.py
Hand-crafted Dijkstra's Shortest Path algorithm using Python's heapq (min-heap).
Calculates minimum cost routes on non-negative weighted graphs and logs step-by-step state.
"""

import heapq
from typing import Dict, List, Optional, Any, Set, Tuple
from core.graph import Graph


def dijkstra(graph: Graph, start_node: str, target_node: Optional[str] = None) -> Dict[str, Any]:
    """
    Computes shortest paths from start_node using Dijkstra's algorithm on the active graph.
    
    Returns dict with:
    - distances: Dict[str, float]
    - total_cost: Optional[float] (if target specified)
    - path: List[str] (if target specified)
    - reachable: bool
    - steps: List[Dict[str, Any]]
    """
    start = str(start_node).strip()
    target = str(target_node).strip() if target_node is not None else None

    steps: List[Dict[str, Any]] = []

    if not graph.is_node_active(start):
        steps.append({
            "step_num": 1,
            "current_node": None,
            "explanation": f"Start router '{start}' is failed or does not exist in active network.",
            "heap": [],
            "distances": {},
            "visited": [],
            "parent_map": {},
            "highlight_edge": None
        })
        return {
            "distances": {},
            "total_cost": None,
            "path": [],
            "reachable": False,
            "steps": steps
        }

    active_nodes = graph.get_active_nodes()
    distances: Dict[str, float] = {node: float("inf") for node in active_nodes}
    distances[start] = 0.0

    parent_map: Dict[str, Optional[str]] = {node: None for node in active_nodes}
    visited: Set[str] = set()

    # Min-heap storing tuples: (current_distance, node_id)
    min_heap: List[Tuple[float, str]] = [(0.0, start)]

    step_counter = 1
    steps.append({
        "step_num": step_counter,
        "current_node": start,
        "explanation": f"Initialized Dijkstra: Distance to start router '{start}' set to 0. All other active routers set to infinity.",
        "heap": [(d, n) for d, n in min_heap],
        "distances": dict(distances),
        "visited": list(visited),
        "parent_map": dict(parent_map),
        "highlight_edge": None
    })

    while min_heap:
        curr_dist, curr_node = heapq.heappop(min_heap)

        if curr_node in visited:
            continue

        if curr_dist > distances[curr_node]:
            continue

        visited.add(curr_node)

        step_counter += 1
        cost_str = "0" if curr_dist == 0 else f"{curr_dist:.2f}"
        steps.append({
            "step_num": step_counter,
            "current_node": curr_node,
            "explanation": f"Picked node '{curr_node}' with cost {cost_str} because it is the cheapest unexplored node.",
            "heap": [(d, n) for d, n in min_heap],
            "distances": dict(distances),
            "visited": list(visited),
            "parent_map": dict(parent_map),
            "highlight_edge": None
        })

        if target is not None and curr_node == target:
            # Target reached; shortest path guaranteed
            break

        active_neighbors = graph.get_active_neighbors(curr_node)
        for neighbor, weight in active_neighbors:
            if neighbor in visited:
                continue

            new_dist = curr_dist + weight
            if new_dist < distances[neighbor]:
                old_dist = distances[neighbor]
                distances[neighbor] = new_dist
                parent_map[neighbor] = curr_node
                heapq.heappush(min_heap, (new_dist, neighbor))

                step_counter += 1
                old_str = "inf" if old_dist == float("inf") else f"{old_dist:.2f}"
                steps.append({
                    "step_num": step_counter,
                    "current_node": curr_node,
                    "explanation": f"Relaxed edge ({curr_node} -> {neighbor}, weight={weight}): updated distance of '{neighbor}' from {old_str} to {new_dist:.2f}.",
                    "heap": [(d, n) for d, n in min_heap],
                    "distances": dict(distances),
                    "visited": list(visited),
                    "parent_map": dict(parent_map),
                    "highlight_edge": (curr_node, neighbor)
                })

    # Path reconstruction
    path: List[str] = []
    total_cost: Optional[float] = None
    reachable = False

    if target is not None:
        if graph.is_node_active(target) and distances.get(target, float("inf")) < float("inf"):
            reachable = True
            total_cost = distances[target]
            curr_path = target
            path_reversed = []
            while curr_path is not None:
                path_reversed.append(curr_path)
                curr_path = parent_map.get(curr_path)
            path = list(reversed(path_reversed))
        else:
            reachable = False
            total_cost = None
            path = []
    else:
        reachable = True

    step_counter += 1
    if target is not None:
        if reachable:
            expl = f"Dijkstra completed! Shortest path to '{target}' found with total cost {total_cost:.2f}: {' -> '.join(path)}."
        else:
            expl = f"Dijkstra completed! No route exists to router '{target}'."
    else:
        expl = f"Dijkstra completed! Shortest distances computed to all reachable routers."

    steps.append({
        "step_num": step_counter,
        "current_node": None,
        "explanation": expl,
        "heap": [],
        "distances": dict(distances),
        "visited": list(visited),
        "parent_map": dict(parent_map),
        "highlight_edge": None
    })

    return {
        "distances": distances,
        "total_cost": total_cost,
        "path": path,
        "reachable": reachable,
        "steps": steps
    }
