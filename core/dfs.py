"""
core/dfs.py
Hand-crafted Depth-First Search (DFS) implementation using an explicit stack (frame-based iterative DFS).
Guarantees stack-safety on large graphs and records discovery/finish times and step-by-step logs.
"""

from typing import Dict, List, Optional, Any, Set, Tuple
from core.graph import Graph


def dfs(graph: Graph, start_node: str, target_node: Optional[str] = None) -> Dict[str, Any]:
    """
    Performs DFS traversal starting from start_node on the active graph using an explicit stack.
    
    Returns dict with:
    - visit_order: List[str]
    - discovery_time: Dict[str, int]
    - finish_time: Dict[str, int]
    - path: List[str]
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
            "explanation": f"Start router '{start}' is failed or does not exist in the active graph.",
            "stack": [],
            "visited": [],
            "discovery_time": {},
            "finish_time": {},
            "parent_map": {},
            "highlight_edge": None
        })
        return {
            "visit_order": [],
            "discovery_time": {},
            "finish_time": {},
            "path": [],
            "reachable": False,
            "steps": steps
        }

    # Frame-based stack: ('ENTER'|'EXIT', node, parent)
    stack: List[Tuple[str, str, Optional[str]]] = [("ENTER", start, None)]
    visited: Set[str] = set()
    visit_order: List[str] = []
    discovery_time: Dict[str, int] = {}
    finish_time: Dict[str, int] = {}
    parent_map: Dict[str, Optional[str]] = {}

    timer = 0
    step_counter = 1

    steps.append({
        "step_num": step_counter,
        "current_node": start,
        "explanation": f"Initialize DFS stack with start router '{start}'.",
        "stack": [item[1] for item in stack if item[0] == "ENTER"],
        "visited": list(visited),
        "discovery_time": dict(discovery_time),
        "finish_time": dict(finish_time),
        "parent_map": dict(parent_map),
        "highlight_edge": None
    })

    target_found = False

    while stack:
        action, curr, parent = stack.pop()

        if action == "ENTER":
            if curr in visited:
                continue

            visited.add(curr)
            visit_order.append(curr)
            timer += 1
            discovery_time[curr] = timer
            parent_map[curr] = parent

            step_counter += 1
            highlight = (parent, curr) if parent else None
            expl = f"Entered router '{curr}' (discovery time = {timer})." if not parent else f"Traversed link ({parent} -> {curr}), entered router '{curr}' (discovery time = {timer})."
            steps.append({
                "step_num": step_counter,
                "current_node": curr,
                "explanation": expl,
                "stack": [item[1] for item in stack if item[0] == "ENTER"],
                "visited": list(visited),
                "discovery_time": dict(discovery_time),
                "finish_time": dict(finish_time),
                "parent_map": dict(parent_map),
                "highlight_edge": highlight
            })

            if curr == target:
                target_found = True
                # Record finish time for target and break early if searching for path
                timer += 1
                finish_time[curr] = timer
                break

            # Push EXIT frame for current node
            stack.append(("EXIT", curr, parent))

            # Push active neighbors in reverse sorted order so they are processed in order
            active_neighbors = graph.get_active_neighbors(curr)
            for neighbor, _ in reversed(active_neighbors):
                if neighbor not in visited:
                    stack.append(("ENTER", neighbor, curr))

        elif action == "EXIT":
            timer += 1
            finish_time[curr] = timer
            step_counter += 1
            steps.append({
                "step_num": step_counter,
                "current_node": curr,
                "explanation": f"Finished processing all neighbors of router '{curr}' (finish time = {timer}). Backtracking...",
                "stack": [item[1] for item in stack if item[0] == "ENTER"],
                "visited": list(visited),
                "discovery_time": dict(discovery_time),
                "finish_time": dict(finish_time),
                "parent_map": dict(parent_map),
                "highlight_edge": None
            })

    # Reconstruct path if target requested
    path: List[str] = []
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
        else:
            reachable = False
            path = []
    else:
        reachable = True

    step_counter += 1
    if target is not None:
        if reachable:
            expl = f"DFS completed! Path to target '{target}' found: {' -> '.join(path)}."
        else:
            expl = f"DFS completed! Target '{target}' is unreachable from '{start}'."
    else:
        expl = f"DFS traversal completed! Visited {len(visit_order)} active routers."

    steps.append({
        "step_num": step_counter,
        "current_node": None,
        "explanation": expl,
        "stack": [],
        "visited": list(visited),
        "discovery_time": dict(discovery_time),
        "finish_time": dict(finish_time),
        "parent_map": dict(parent_map),
        "highlight_edge": None
    })

    return {
        "visit_order": visit_order,
        "discovery_time": discovery_time,
        "finish_time": finish_time,
        "path": path,
        "reachable": reachable,
        "steps": steps
    }
