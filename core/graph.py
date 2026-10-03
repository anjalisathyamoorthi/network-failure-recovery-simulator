"""
core/graph.py
Undirected weighted graph representation with failure state management and strict validation.
"""

from typing import Dict, Set, List, Tuple, Optional, Any
import json
import csv
import io


class Graph:
    """
    Undirected weighted graph stored as an adjacency list dictionary:
    self._adj[node] = {neighbor: weight}
    
    Supports non-destructive failure simulation (failed nodes and failed edges).
    """

    def __init__(self):
        # Master graph structures
        self._adj: Dict[str, Dict[str, float]] = {}
        self._nodes: Set[str] = set()

        # Failure states
        self._failed_nodes: Set[str] = set()
        self._failed_edges: Set[Tuple[str, str]] = set()  # Normalized sorted tuple (min(u,v), max(u,v))

    # ------------------------------------------------------------------
    # Graph Modification & Validation
    # ------------------------------------------------------------------

    def add_node(self, node_id: Any) -> str:
        """Adds a router/node to the graph."""
        node_str = str(node_id).strip()
        if not node_str:
            raise ValueError("Router ID cannot be empty.")
        if node_str not in self._nodes:
            self._nodes.add(node_str)
            self._adj[node_str] = {}
        return node_str

    def remove_node(self, node_id: Any) -> None:
        """Permanently removes a node and all associated edges from the graph."""
        node_str = str(node_id).strip()
        if node_str not in self._nodes:
            raise ValueError(f"Router '{node_str}' does not exist.")
        
        # Remove all connected edges
        for neighbor in list(self._adj[node_str].keys()):
            del self._adj[neighbor][node_str]
        
        del self._adj[node_str]
        self._nodes.remove(node_str)
        self._failed_nodes.discard(node_str)

        # Remove any failed edge associated with this node
        edges_to_remove = {e for e in self._failed_edges if node_str in e}
        self._failed_edges -= edges_to_remove

    def add_edge(self, u: Any, v: Any, weight: float, auto_add_nodes: bool = True) -> None:
        """
        Adds an undirected edge between u and v with a non-negative weight.
        Raises ValueError on validation failure.
        """
        u_str = str(u).strip()
        v_str = str(v).strip()

        if u_str == v_str:
            raise ValueError(f"Self-loops are not allowed (Router '{u_str}' to itself).")

        try:
            w = float(weight)
        except (ValueError, TypeError):
            raise ValueError(f"Link weight must be a valid number, got '{weight}'.")

        if w < 0:
            raise ValueError(f"Link weight cannot be negative ({w}).")

        if not auto_add_nodes:
            if u_str not in self._nodes:
                raise ValueError(f"Unknown router '{u_str}'. Add node first.")
            if v_str not in self._nodes:
                raise ValueError(f"Unknown router '{v_str}'. Add node first.")
        else:
            self.add_node(u_str)
            self.add_node(v_str)

        if v_str in self._adj[u_str]:
            raise ValueError(f"Link between '{u_str}' and '{v_str}' already exists.")

        self._adj[u_str][v_str] = w
        self._adj[v_str][u_str] = w

    def remove_edge(self, u: Any, v: Any) -> None:
        """Permanently removes an edge between u and v."""
        u_str = str(u).strip()
        v_str = str(v).strip()

        if u_str not in self._nodes or v_str not in self._nodes or v_str not in self._adj[u_str]:
            raise ValueError(f"Link between '{u_str}' and '{v_str}' does not exist.")

        del self._adj[u_str][v_str]
        del self._adj[v_str][u_str]
        self._failed_edges.discard(self._normalize_edge(u_str, v_str))

    # ------------------------------------------------------------------
    # Failure Management
    # ------------------------------------------------------------------

    @staticmethod
    def _normalize_edge(u: str, v: str) -> Tuple[str, str]:
        return (u, v) if u < v else (v, u)

    def fail_node(self, node_id: Any) -> None:
        node_str = str(node_id).strip()
        if node_str not in self._nodes:
            raise ValueError(f"Cannot fail unknown router '{node_str}'.")
        self._failed_nodes.add(node_str)

    def restore_node(self, node_id: Any) -> None:
        node_str = str(node_id).strip()
        self._failed_nodes.discard(node_str)

    def fail_edge(self, u: Any, v: Any) -> None:
        u_str = str(u).strip()
        v_str = str(v).strip()
        if u_str not in self._nodes or v_str not in self._nodes or v_str not in self._adj[u_str]:
            raise ValueError(f"Cannot fail non-existent link between '{u_str}' and '{v_str}'.")
        self._failed_edges.add(self._normalize_edge(u_str, v_str))

    def restore_edge(self, u: Any, v: Any) -> None:
        u_str = str(u).strip()
        v_str = str(v).strip()
        self._failed_edges.discard(self._normalize_edge(u_str, v_str))

    def clear_failures(self) -> None:
        """Restores all failed nodes and links."""
        self._failed_nodes.clear()
        self._failed_edges.clear()

    # ------------------------------------------------------------------
    # Query Active Graph State
    # ------------------------------------------------------------------

    def is_node_active(self, node_id: Any) -> bool:
        node_str = str(node_id).strip()
        return node_str in self._nodes and node_str not in self._failed_nodes

    def is_edge_active(self, u: Any, v: Any) -> bool:
        u_str = str(u).strip()
        v_str = str(v).strip()
        if not self.is_node_active(u_str) or not self.is_node_active(v_str):
            return False
        if v_str not in self._adj.get(u_str, {}):
            return False
        return self._normalize_edge(u_str, v_str) not in self._failed_edges

    def get_all_nodes(self) -> List[str]:
        return sorted(list(self._nodes))

    def get_active_nodes(self) -> List[str]:
        return sorted([n for n in self._nodes if n not in self._failed_nodes])

    def get_failed_nodes(self) -> Set[str]:
        return set(self._failed_nodes)

    def get_all_edges(self) -> List[Tuple[str, str, float]]:
        """Returns sorted list of unique edges (u, v, weight) with u < v."""
        edges = []
        for u in self._nodes:
            for v, weight in self._adj[u].items():
                if u < v:
                    edges.append((u, v, weight))
        return sorted(edges, key=lambda e: (e[0], e[1]))

    def get_active_edges(self) -> List[Tuple[str, str, float]]:
        """Returns sorted list of active unique edges (u, v, weight)."""
        edges = []
        for u in self.get_active_nodes():
            for v, weight in self._adj[u].items():
                if u < v and self.is_edge_active(u, v):
                    edges.append((u, v, weight))
        return sorted(edges, key=lambda e: (e[0], e[1]))

    def get_failed_edges(self) -> Set[Tuple[str, str]]:
        return set(self._failed_edges)

    def get_active_neighbors(self, node_id: Any) -> List[Tuple[str, float]]:
        """
        Returns list of (neighbor, weight) for active links connected to an active node.
        Sorted by neighbor ID for deterministic traversal.
        """
        node_str = str(node_id).strip()
        if not self.is_node_active(node_str):
            return []

        neighbors = []
        for neighbor, weight in self._adj[node_str].items():
            if self.is_edge_active(node_str, neighbor):
                neighbors.append((neighbor, weight))
        return sorted(neighbors, key=lambda item: item[0])

    def get_edge_weight(self, u: Any, v: Any) -> Optional[float]:
        u_str = str(u).strip()
        v_str = str(v).strip()
        return self._adj.get(u_str, {}).get(v_str)

    # ------------------------------------------------------------------
    # Serialization / Import / Export
    # ------------------------------------------------------------------

    def clone(self) -> "Graph":
        g = Graph()
        for node in self._nodes:
            g.add_node(node)
        for u, v, w in self.get_all_edges():
            g.add_edge(u, v, w)
        g._failed_nodes = set(self._failed_nodes)
        g._failed_edges = set(self._failed_edges)
        return g

    def to_dict(self) -> Dict[str, Any]:
        return {
            "nodes": sorted(list(self._nodes)),
            "edges": [{"source": u, "target": v, "weight": w} for u, v, w in self.get_all_edges()],
            "failed_nodes": sorted(list(self._failed_nodes)),
            "failed_edges": [{"source": u, "target": v} for u, v in self._failed_edges]
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Graph":
        g = cls()
        for node in data.get("nodes", []):
            g.add_node(node)
        for edge in data.get("edges", []):
            g.add_edge(edge["source"], edge["target"], float(edge["weight"]))
        for fn in data.get("failed_nodes", []):
            g.fail_node(fn)
        for fe in data.get("failed_edges", []):
            g.fail_edge(fe["source"], fe["target"])
        return g

    def to_csv_string(self) -> str:
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(["source", "target", "weight"])
        for u, v, w in self.get_all_edges():
            writer.writerow([u, v, w])
        return output.getvalue()

    @classmethod
    def from_csv_string(cls, csv_content: str) -> "Graph":
        g = cls()
        reader = csv.reader(io.StringIO(csv_content.strip()))
        header = True
        for row in reader:
            if not row or len(row) < 2:
                continue
            if header and (row[0].strip().lower() in ["source", "node1", "from", "u"]):
                header = False
                continue
            header = False
            u = row[0].strip()
            v = row[1].strip()
            w = float(row[2].strip()) if len(row) >= 3 else 1.0
            g.add_edge(u, v, w)
        return g
