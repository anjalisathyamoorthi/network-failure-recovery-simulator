"""
core/presets.py
Pre-packaged topology generators and random graph creation utility for network testing.
"""

import random
from typing import Dict, Any
from core.graph import Graph


def get_campus_network_preset() -> Graph:
    """
    Creates a realistic multi-tier Campus Enterprise Network topology:
    - Core Routers: CORE1, CORE2
    - Distribution Routers: DIST1, DIST2, DIST3
    - Access Routers: ACC1, ACC2, ACC3, ACC4, ACC5
    - Server Farm: SVR1, SVR2
    """
    g = Graph()

    # Core Layer (High bandwidth interconnect)
    g.add_edge("CORE1", "CORE2", 1.0)
    
    # Distribution Layer connected to Core
    g.add_edge("CORE1", "DIST1", 2.0)
    g.add_edge("CORE1", "DIST2", 2.0)
    g.add_edge("CORE2", "DIST2", 2.0)
    g.add_edge("CORE2", "DIST3", 3.0)

    # Cross-distribution redundancy
    g.add_edge("DIST1", "DIST2", 3.0)
    g.add_edge("DIST2", "DIST3", 4.0)

    # Access Layer connected to Distribution
    g.add_edge("DIST1", "ACC1", 5.0)
    g.add_edge("DIST1", "ACC2", 5.0)
    g.add_edge("DIST2", "ACC3", 4.0)
    g.add_edge("DIST3", "ACC4", 6.0)
    g.add_edge("DIST3", "ACC5", 6.0)

    # Redundant access links
    g.add_edge("DIST2", "ACC2", 6.0)
    g.add_edge("DIST3", "ACC3", 5.0)

    # Server Farm connected to Core & Distribution
    g.add_edge("CORE1", "SVR1", 2.0)
    g.add_edge("CORE2", "SVR2", 2.0)
    g.add_edge("SVR1", "SVR2", 1.0)

    return g


def get_ring_topology_preset(num_nodes: int = 8) -> Graph:
    """Creates a ring topology with N routers."""
    g = Graph()
    nodes = [f"R{i+1}" for i in range(num_nodes)]
    for i in range(num_nodes):
        u = nodes[i]
        v = nodes[(i + 1) % num_nodes]
        g.add_edge(u, v, weight=float(random.randint(2, 10)))
    return g


def get_star_topology_preset(num_spokes: int = 7) -> Graph:
    """Creates a star topology with a central HUB router."""
    g = Graph()
    hub = "HUB"
    g.add_node(hub)
    for i in range(1, num_spokes + 1):
        spoke = f"SPOKE_{i}"
        g.add_edge(hub, spoke, weight=float(i * 2))
    return g


def get_core_router_failure_preset() -> Graph:
    """
    Creates a bottleneck topology specifically showcasing critical connections:
    Left cluster (A1, A2, A3) connected to Central Router (CORE_GW),
    which connects to Right cluster (B1, B2, B3).
    CORE_GW is a single point of failure (articulation point).
    """
    g = Graph()
    
    # Left Cluster
    g.add_edge("A1", "A2", 2.0)
    g.add_edge("A2", "A3", 2.0)
    g.add_edge("A3", "A1", 3.0)

    # Right Cluster
    g.add_edge("B1", "B2", 2.0)
    g.add_edge("B2", "B3", 2.0)
    g.add_edge("B3", "B1", 3.0)

    # Central Bottleneck Router & Bridges
    g.add_edge("A1", "CORE_GW", 4.0)
    g.add_edge("CORE_GW", "B1", 4.0)

    return g


def generate_random_graph(num_nodes: int = 15, edge_density: float = 0.2, seed: int = 42) -> Graph:
    """
    Generates a random graph given node count and edge probability density.
    Guarantees initial connectivity by building a random spanning tree first.
    """
    rng = random.Random(seed)
    g = Graph()

    nodes = [f"R{i+1}" for i in range(max(1, num_nodes))]
    for n in nodes:
        g.add_node(n)

    if len(nodes) <= 1:
        return g

    # Build spanning tree to ensure basic connectivity
    unvisited = list(nodes)
    visited = [unvisited.pop(rng.randint(0, len(unvisited) - 1))]

    while unvisited:
        u = rng.choice(visited)
        v = unvisited.pop(rng.randint(0, len(unvisited) - 1))
        weight = float(rng.randint(1, 15))
        g.add_edge(u, v, weight)
        visited.append(v)

    # Add extra random edges based on density
    max_extra_edges = int(0.5 * len(nodes) * (len(nodes) - 1) * max(0.0, min(1.0, edge_density)))
    added = 0
    attempts = 0

    while added < max_extra_edges and attempts < max_extra_edges * 5:
        attempts += 1
        u = rng.choice(nodes)
        v = rng.choice(nodes)
        if u != v and g.get_edge_weight(u, v) is None:
            weight = float(rng.randint(1, 20))
            g.add_edge(u, v, weight)
            added += 1

    return g
