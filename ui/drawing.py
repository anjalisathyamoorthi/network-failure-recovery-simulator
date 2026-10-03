"""
ui/drawing.py
Plotly graph renderer for network visualization.
Uses networkx solely for 2D node layout positioning.
Supports color-coding for failed routers/links, shortest paths, bridges, articulation points, and animation steps.
"""

from typing import Dict, List, Set, Tuple, Optional, Any
import plotly.graph_objects as go
import networkx as nx
from core.graph import Graph


def compute_node_positions(graph: Graph, seed: int = 42) -> Dict[str, Tuple[float, float]]:
    """
    Computes 2D spatial layout coordinates using NetworkX spring layout algorithm.
    Uses fixed random seed for layout stability when failures occur.
    """
    all_nodes = graph.get_all_nodes()
    if not all_nodes:
        return {}

    # Build networkx graph solely for layout calculation
    nx_g = nx.Graph()
    for n in all_nodes:
        nx_g.add_node(n)
    for u, v, w in graph.get_all_edges():
        nx_g.add_edge(u, v, weight=w)

    pos = nx.spring_layout(nx_g, seed=seed, k=1.5 / (len(all_nodes) ** 0.5) if len(all_nodes) > 1 else 1.0)
    return {node: (float(pos[node][0]), float(pos[node][1])) for node in all_nodes}


def draw_network_graph(
    graph: Graph,
    pos: Dict[str, Tuple[float, float]],
    highlight_path: Optional[List[str]] = None,
    bridges: Optional[List[Tuple[str, str]]] = None,
    articulation_points: Optional[List[str]] = None,
    current_step_node: Optional[str] = None,
    current_step_edge: Optional[Tuple[str, str]] = None,
    component_colors: Optional[Dict[str, str]] = None,
    title: str = "Network Topology Overview"
) -> go.Figure:
    """
    Creates an interactive Plotly figure representing the network graph.
    """
    fig = go.Figure()

    if not pos:
        fig.add_annotation(
            text="Empty Network Graph (No Routers)",
            xref="paper", yref="paper",
            x=0.5, y=0.5, showarrow=False,
            font=dict(size=18, color="gray")
        )
        fig.update_layout(xaxis=dict(visible=False), yaxis=dict(visible=False))
        return fig

    # Sets for fast lookup
    failed_nodes = graph.get_failed_nodes()
    failed_edges = graph.get_failed_edges()
    
    path_edges = set()
    if highlight_path and len(highlight_path) >= 2:
        for i in range(len(highlight_path) - 1):
            u, v = highlight_path[i], highlight_path[i + 1]
            path_edges.add(graph._normalize_edge(u, v))

    bridge_edges = set()
    if bridges:
        for u, v in bridges:
            bridge_edges.add(graph._normalize_edge(u, v))

    ap_nodes = set(articulation_points) if articulation_points else set()

    # Normalize step edge
    step_edge_norm = None
    if current_step_edge and len(current_step_edge) == 2:
        step_edge_norm = graph._normalize_edge(current_step_edge[0], current_step_edge[1])

    # 1. Render Edges
    all_edges = graph.get_all_edges()
    
    for u, v, w in all_edges:
        if u not in pos or v not in pos:
            continue
        
        x0, y0 = pos[u]
        x1, y1 = pos[v]
        norm_e = graph._normalize_edge(u, v)

        # Default Edge Styles
        is_failed = norm_e in failed_edges or u in failed_nodes or v in failed_nodes
        is_path = norm_e in path_edges
        is_bridge = norm_e in bridge_edges
        is_step_edge = norm_e == step_edge_norm

        if is_failed:
            line_color = "#e74c3c"  # Red
            line_dash = "dash"
            line_width = 1.5
            opacity = 0.5
        elif is_step_edge:
            line_color = "#3498db"  # Bright Blue
            line_dash = "solid"
            line_width = 4.5
            opacity = 1.0
        elif is_path:
            line_color = "#2ecc71"  # Emerald Green
            line_dash = "solid"
            line_width = 4.0
            opacity = 1.0
        elif is_bridge:
            line_color = "#f39c12"  # Amber Orange
            line_dash = "solid"
            line_width = 3.5
            opacity = 0.9
        else:
            line_color = "#7f8c8d"  # Medium Slate Gray
            line_dash = "solid"
            line_width = 1.8
            opacity = 0.7

        fig.add_trace(go.Scatter(
            x=[x0, x1, None],
            y=[y0, y1, None],
            mode="lines",
            line=dict(width=line_width, color=line_color, dash=line_dash),
            hoverinfo="none",
            showlegend=False,
            opacity=opacity
        ))

        # Render Edge Weight Label at Midpoint
        mid_x = (x0 + x1) / 2.0
        mid_y = (y0 + y1) / 2.0
        weight_str = f"{w:.1f}" if isinstance(w, float) and not w.is_integer() else f"{int(w)}"
        
        fig.add_trace(go.Scatter(
            x=[mid_x],
            y=[mid_y],
            mode="text",
            text=[weight_str],
            textfont=dict(size=10, color="#2c3e50" if not is_failed else "#c0392b"),
            hoverinfo="text",
            hovertext=[f"Link: {u} -- {v} | Cost: {w}" + (" (FAILED)" if is_failed else "")],
            showlegend=False
        ))

    # 2. Render Nodes
    node_x = []
    node_y = []
    node_text = []
    node_colors = []
    node_sizes = []
    node_symbols = []
    node_hovers = []

    for node in graph.get_all_nodes():
        if node not in pos:
            continue
        
        x, y = pos[node]
        node_x.append(x)
        node_y.append(y)
        node_text.append(node)

        is_failed = node in failed_nodes
        is_step = node == current_step_node
        is_path = highlight_path and node in highlight_path
        is_ap = node in ap_nodes
        comp_color = component_colors.get(node) if component_colors else None

        if is_failed:
            color = "#e74c3c"  # Red
            size = 28
            symbol = "circle"
            status = "FAILED"
        elif is_step:
            color = "#f1c40f"  # Yellow glowing step focus
            size = 36
            symbol = "diamond"
            status = "STEP ACTIVE"
        elif is_path:
            color = "#2ecc71"  # Emerald Green path node
            size = 32
            symbol = "circle"
            status = "ON SHORTEST PATH"
        elif is_ap:
            color = "#9b59b6"  # Purple Articulation Point
            size = 32
            symbol = "hexagram"
            status = "CRITICAL ROUTER (Articulation Point)"
        elif comp_color:
            color = comp_color
            size = 26
            symbol = "circle"
            status = "ACTIVE"
        else:
            color = "#34495e"  # Dark Slate Blue normal active node
            size = 26
            symbol = "circle"
            status = "ACTIVE"

        node_colors.append(color)
        node_sizes.append(size)
        node_symbols.append(symbol)
        node_hovers.append(f"Router: <b>{node}</b><br>Status: {status}")

    fig.add_trace(go.Scatter(
        x=node_x,
        y=node_y,
        mode="markers+text",
        text=node_text,
        textposition="middle center",
        textfont=dict(color="white", size=11, family="Arial Black"),
        marker=dict(
            size=node_sizes,
            color=node_colors,
            symbol=node_symbols,
            line=dict(width=2, color="#ffffff")
        ),
        hoverinfo="text",
        hovertext=node_hovers,
        showlegend=False
    ))

    # Add Custom Color Legend Traces
    legend_items = [
        ("Active Router", "#34495e", "circle"),
        ("Failed Router/Link", "#e74c3c", "circle"),
        ("Selected Path", "#2ecc71", "circle"),
        ("Critical Router (AP)", "#9b59b6", "hexagram"),
        ("Critical Link (Bridge)", "#f39c12", "line"),
    ]
    for label, color, sym in legend_items:
        if sym == "line":
            fig.add_trace(go.Scatter(
                x=[None], y=[None], mode="lines",
                line=dict(color=color, width=3), name=label
            ))
        else:
            fig.add_trace(go.Scatter(
                x=[None], y=[None], mode="markers",
                marker=dict(color=color, size=12, symbol=sym), name=label
            ))

    fig.update_layout(
        title=dict(text=title, font=dict(size=16, color="#2c3e50")),
        showlegend=True,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
        yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
        margin=dict(l=20, r=20, t=50, b=20),
        plot_bgcolor="rgba(245, 247, 250, 1)",
        paper_bgcolor="rgba(0,0,0,0)",
        height=550
    )

    return fig
