"""
core/bfs.py
Hand-crafted Breadth-First Search (BFS) implementation using collections.deque.
Returns level-by-level traversal, minimum-hop paths, and a detailed step-by-step log for animation.
"""

from collections import deque
from typing import Dict, List, Optional, Any, Set, Tuple
from core.graph import Graph


def bfs(graph: Graph, start_node: str, target_node: Optional[str] = None) -> Dict[str, Any]:
    """
    Performs BFS traversal starting from start_node on the active graph.
    
    Returns dict with:
    - visit_order: List[str]
    - levels: Dict[str, int]
    - hop_count: Optional[int]
    - path: List[str]
    - reachable: bool
    - steps: List[Dict[str, Any]]
    """
    start = str(start_node).strip()
    target = str(target_node).strip() if target_node is not None else None

    steps: List[Dict[str, Any]] = []

    # Check if start node is active in the graph
    if not graph.is_node_active(start):
        steps.append({
            "step_num": 1,
            "current_node": None,
            "explanation": f"Start router '{start}' is failed or does not exist in the active graph.",
            "queue": [],
            "visited": [],
            "levels": {},
            "parent_map": {},
            "highlight_edge": None
        })
        return {
            "visit_order": [],
            "levels": {},
            "hop_count": None,
            "path": [],
            "reachable": False,
            "steps": steps
        }

    queue: deque = deque([start])
    visited: Set[str] = {start}
    visit_order: List[str] = []
    levels: Dict[str, int] = {start: 0}
    parent_map: Dict[str, Optional[str]] = {start: None}

    step_counter = 1
    steps.append({
        "step_num": step_counter,
        "current_node": start,
        "explanation": f"Initialize BFS queue with start router '{start}'. Set distance level to 0.",
        "queue": list(queue),
        "visited": list(visited),
        "levels": dict(levels),
        "parent_map": dict(parent_map),
        "highlight_edge": None
    })

    target_found = (start == target)

    while queue and not target_found:
        curr = queue.popleft()
        visit_order.append(curr)

        step_counter += 1
        steps.append({
            "step_num": step_counter,
            "current_node": curr,
            "explanation": f"Dequeued router '{curr}' (level {levels[curr]}). Checking active neighbors...",
            "queue": list(queue),
            "visited": list(visited),
            "levels": dict(levels),
            "parent_map": dict(parent_map),
            "highlight_edge": None
        })

        if curr == target:
            target_found = True
            break

        active_neighbors = graph.get_active_neighbors(curr)
        for neighbor, _ in active_neighbors:
            if neighbor not in visited:
                visited.add(neighbor)
                levels[neighbor] = levels[curr] + 1
                parent_map[neighbor] = curr
                queue.append(neighbor)

                step_counter += 1
                steps.append({
                    "step_num": step_counter,
                    "current_node": curr,
                    "explanation": f"Discovered neighbor '{neighbor}' via link ({curr} -> {neighbor}). Assigned level {levels[neighbor]} and enqueued.",
                    "queue": list(queue),
                    "visited": list(visited),
                    "levels": dict(levels),
                    "parent_map": dict(parent_map),
                    "highlight_edge": (curr, neighbor)
                })

                if neighbor == target:
                    target_found = True
                    break

    # If popped loop ended and we didn't add curr to visit_order if target matched early
    if target and target in visited and target not in visit_order:
        # Continue popping if needed or add target
        pass

    # Reconstruct path if target is provided
    path: List[str] = []
    hop_count: Optional[int] = None
    reachable = False

    if target is not None:
        if target in visited and graph.is_node_active(target):
            reachable = True
            curr_path = target
            path_reversed = []
            while curr_path is not None:
                path_reversed.append(curr_path)
                curr_path = parent_map.get(curr_path)
            path = list(reversed(path_reversed))
            hop_count = levels.get(target, len(path) - 1)
        else:
            reachable = False
            path = []
            hop_count = None
    else:
        reachable = True  # General traversal starting from start

    step_counter += 1
    if target is not None:
        if reachable:
            expl = f"BFS completed! Target '{target}' reached with minimum hop count of {hop_count}. Path: {' -> '.join(path)}."
        else:
            expl = f"BFS completed! Target '{target}' is unreachable from '{start}'."
    else:
        expl = f"BFS traversal completed! Visited {len(visit_order)} active routers."

    steps.append({
        "step_num": step_counter,
        "current_node": None,
        "explanation": expl,
        "queue": list(queue),
        "visited": list(visited),
        "levels": dict(levels),
        "parent_map": dict(parent_map),
        "highlight_edge": None
    })

    return {
        "visit_order": visit_order if visit_order else ([start] if start in visited else []),
        "levels": levels,
        "hop_count": hop_count,
        "path": path,
        "reachable": reachable,
        "steps": steps
    }
