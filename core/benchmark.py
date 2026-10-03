"""
core/benchmark.py
Performance benchmarking engine for graph algorithms.
Measures execution times across varying node sizes (50 to 800+ nodes).
"""

import time
import pandas as pd
from typing import List, Dict, Any
from core.presets import generate_random_graph
from core.bfs import bfs
from core.dfs import dfs
from core.dijkstra import dijkstra
from core.components import find_components
from core.critical import find_critical_connections


def run_algorithm_benchmarks(
    sizes: List[int] = [50, 100, 200, 400, 800],
    edge_density: float = 0.1,
    seed: int = 42
) -> pd.DataFrame:
    """
    Executes benchmark runs for BFS, DFS, Dijkstra, Connected Components,
    and Tarjan's Critical Connections across specified graph node counts.
    
    Returns pandas DataFrame containing execution times in milliseconds.
    """
    results: List[Dict[str, Any]] = []

    for idx, v_count in enumerate(sizes):
        g = generate_random_graph(num_nodes=v_count, edge_density=edge_density, seed=seed + idx)
        start_node = "R1"
        target_node = f"R{v_count}"

        # 1. BFS Benchmark
        t0 = time.perf_counter()
        bfs(g, start_node=start_node, target_node=target_node)
        bfs_ms = (time.perf_counter() - t0) * 1000.0

        # 2. DFS Benchmark
        t0 = time.perf_counter()
        dfs(g, start_node=start_node, target_node=target_node)
        dfs_ms = (time.perf_counter() - t0) * 1000.0

        # 3. Dijkstra Benchmark
        t0 = time.perf_counter()
        dijkstra(g, start_node=start_node, target_node=target_node)
        dijkstra_ms = (time.perf_counter() - t0) * 1000.0

        # 4. Connected Components Benchmark
        t0 = time.perf_counter()
        find_components(g, method="BFS")
        comp_ms = (time.perf_counter() - t0) * 1000.0

        # 5. Tarjan Critical Connections Benchmark
        t0 = time.perf_counter()
        find_critical_connections(g)
        tarjan_ms = (time.perf_counter() - t0) * 1000.0

        results.append({
            "Graph Size (V)": v_count,
            "Edge Count (E)": len(g.get_all_edges()),
            "BFS (ms)": round(bfs_ms, 3),
            "DFS (ms)": round(dfs_ms, 3),
            "Dijkstra (ms)": round(dijkstra_ms, 3),
            "Components (ms)": round(comp_ms, 3),
            "Tarjan (ms)": round(tarjan_ms, 3)
        })

    return pd.DataFrame(results)
