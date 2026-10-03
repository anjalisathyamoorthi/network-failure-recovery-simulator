"""
app.py
Network Failure Recovery Simulator (DAA Project - Problem 55)
Main Streamlit application entry point.
"""

import streamlit as st
import plotly.express as px
import pandas as pd

from core.graph import Graph
from core.presets import (
    get_campus_network_preset,
    get_ring_topology_preset,
    get_star_topology_preset,
    get_core_router_failure_preset,
    generate_random_graph,
)
from core.bfs import bfs
from core.dfs import dfs
from core.dijkstra import dijkstra
from core.components import find_components, compare_components
from core.critical import find_critical_connections
from core.recovery import analyze_failure_recovery
from core.benchmark import run_algorithm_benchmarks
from ui.drawing import compute_node_positions, draw_network_graph
from ui.step_player import render_step_player_controls, render_step_details


# Page Configuration
st.set_page_config(
    page_title="Network Failure Recovery Simulator",
    page_icon="🌐",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS Styling (Theme-aware for Light & Dark Mode)
st.markdown("""
    <style>
    .main .block-container { padding-top: 1.5rem; padding-bottom: 2rem; }
    div[data-testid="stMetric"] {
        background-color: var(--secondary-background-color, rgba(128, 128, 128, 0.08));
        padding: 12px 16px;
        border-radius: 10px;
        border: 1px solid rgba(128, 128, 128, 0.2);
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }
    div[data-testid="stMetric"] label {
        color: var(--text-color, inherit);
    }
    .stAlert { border-radius: 8px; }
    </style>
""", unsafe_allow_html=True)


# Session State Initialization
if "graph" not in st.session_state:
    st.session_state.graph = get_campus_network_preset()
    st.session_state.pos = compute_node_positions(st.session_state.graph)

if "source_node" not in st.session_state:
    nodes = st.session_state.graph.get_all_nodes()
    st.session_state.source_node = nodes[0] if nodes else ""

if "target_node" not in st.session_state:
    nodes = st.session_state.graph.get_all_nodes()
    st.session_state.target_node = nodes[-1] if len(nodes) > 1 else (nodes[0] if nodes else "")

g: Graph = st.session_state.graph


# ------------------------------------------------------------------
# SIDEBAR CONTROLS
# ------------------------------------------------------------------
st.sidebar.title("🌐 Network Simulator")
st.sidebar.markdown("---")

# 1. Preset Topologies Selector
st.sidebar.subheader("1. Preset Topologies")
preset_choice = st.sidebar.selectbox(
    "Choose Preset Network",
    options=["Campus Enterprise Network", "Ring Topology", "Star Topology", "Core Router Failure Bottleneck", "Random Graph Generator"]
)

if preset_choice == "Random Graph Generator":
    rand_nodes = st.sidebar.slider("Number of Routers (V)", min_value=5, max_value=100, value=15, step=5)
    rand_density = st.sidebar.slider("Link Density", min_value=0.05, max_value=0.4, value=0.15, step=0.05)
    if st.sidebar.button("⚙️ Generate Random Network", use_container_width=True):
        st.session_state.graph = generate_random_graph(num_nodes=rand_nodes, edge_density=rand_density)
        st.session_state.pos = compute_node_positions(st.session_state.graph)
        nodes = st.session_state.graph.get_all_nodes()
        st.session_state.source_node = nodes[0] if nodes else ""
        st.session_state.target_node = nodes[-1] if len(nodes) > 1 else ""
        st.rerun()

else:
    if st.sidebar.button("📌 Load Selected Preset", use_container_width=True):
        if preset_choice == "Campus Enterprise Network":
            st.session_state.graph = get_campus_network_preset()
        elif preset_choice == "Ring Topology":
            st.session_state.graph = get_ring_topology_preset(num_nodes=8)
        elif preset_choice == "Star Topology":
            st.session_state.graph = get_star_topology_preset(num_spokes=7)
        elif preset_choice == "Core Router Failure Bottleneck":
            st.session_state.graph = get_core_router_failure_preset()

        st.session_state.pos = compute_node_positions(st.session_state.graph)
        nodes = st.session_state.graph.get_all_nodes()
        st.session_state.source_node = nodes[0] if nodes else ""
        st.session_state.target_node = nodes[-1] if len(nodes) > 1 else ""
        st.rerun()

st.sidebar.markdown("---")


# 2. Graph Editor
st.sidebar.subheader("2. Custom Graph Editor")
editor_action = st.sidebar.selectbox("Action", options=["Add Router", "Add Link", "Delete Router", "Delete Link", "Upload CSV/JSON"])

if editor_action == "Add Router":
    new_router = st.sidebar.text_input("New Router ID (e.g. R99)")
    if st.sidebar.button("➕ Add Router", use_container_width=True):
        if new_router:
            try:
                g.add_node(new_router)
                st.session_state.pos = compute_node_positions(g)
                st.sidebar.success(f"Router '{new_router}' added.")
                st.rerun()
            except Exception as e:
                st.sidebar.error(str(e))

elif editor_action == "Add Link":
    all_n = g.get_all_nodes()
    if len(all_n) >= 2:
        u_link = st.sidebar.selectbox("Source Router", options=all_n, key="add_u")
        v_link = st.sidebar.selectbox("Target Router", options=all_n, key="add_v")
        weight_link = st.sidebar.number_input("Cost / Latency Weight", min_value=0.0, value=5.0, step=1.0)
        if st.sidebar.button("➕ Add Link", use_container_width=True):
            try:
                g.add_edge(u_link, v_link, weight_link)
                st.session_state.pos = compute_node_positions(g)
                st.sidebar.success(f"Link '{u_link}' -- '{v_link}' added.")
                st.rerun()
            except Exception as e:
                st.sidebar.error(str(e))
    else:
        st.sidebar.info("Add at least 2 routers first.")

elif editor_action == "Delete Router":
    all_n = g.get_all_nodes()
    if all_n:
        del_r = st.sidebar.selectbox("Select Router to Delete", options=all_n)
        if st.sidebar.button("🗑️ Delete Router", use_container_width=True):
            try:
                g.remove_node(del_r)
                st.session_state.pos = compute_node_positions(g)
                st.sidebar.success(f"Router '{del_r}' removed.")
                st.rerun()
            except Exception as e:
                st.sidebar.error(str(e))

elif editor_action == "Delete Link":
    all_edges = g.get_all_edges()
    if all_edges:
        edge_opts = [f"{u} -- {v} (weight {w})" for u, v, w in all_edges]
        selected_e = st.sidebar.selectbox("Select Link to Delete", options=edge_opts)
        if st.sidebar.button("🗑️ Delete Link", use_container_width=True):
            idx = edge_opts.index(selected_e)
            u, v, _ = all_edges[idx]
            g.remove_edge(u, v)
            st.session_state.pos = compute_node_positions(g)
            st.sidebar.success(f"Link '{u}' -- '{v}' removed.")
            st.rerun()

elif editor_action == "Upload CSV/JSON":
    uploaded_file = st.sidebar.file_uploader("Upload Edge List (CSV)", type=["csv", "json"])
    if uploaded_file is not None:
        try:
            content = uploaded_file.getvalue().decode("utf-8")
            if uploaded_file.name.endswith(".json"):
                data = json.loads(content)
                new_g = Graph.from_dict(data)
            else:
                new_g = Graph.from_csv_string(content)
            st.session_state.graph = new_g
            st.session_state.pos = compute_node_positions(new_g)
            st.sidebar.success("Graph loaded successfully!")
            st.rerun()
        except Exception as e:
            st.sidebar.error(f"Failed to parse file: {e}")

st.sidebar.markdown("---")


# 3. Failure Simulation Controls
st.sidebar.subheader("3. Failure Controls")
all_nodes_list = g.get_all_nodes()
currently_failed_nodes = list(g.get_failed_nodes())

selected_failed_nodes = st.sidebar.multiselect(
    "Fail Routers (Nodes)",
    options=all_nodes_list,
    default=currently_failed_nodes,
    key="failed_nodes_select"
)

# Apply router failures
for n in all_nodes_list:
    if n in selected_failed_nodes and n not in currently_failed_nodes:
        g.fail_node(n)
    elif n not in selected_failed_nodes and n in currently_failed_nodes:
        g.restore_node(n)

# Link failures
all_edges_tuples = [(u, v) for u, v, _ in g.get_all_edges()]
edge_labels = [f"{u} -- {v}" for u, v in all_edges_tuples]
currently_failed_edges = g.get_failed_edges()
default_failed_edge_labels = [f"{u} -- {v}" for u, v in all_edges_tuples if (u, v) in currently_failed_edges or (v, u) in currently_failed_edges]

selected_failed_edge_labels = st.sidebar.multiselect(
    "Fail Links (Edges)",
    options=edge_labels,
    default=default_failed_edge_labels,
    key="failed_edges_select"
)

# Apply link failures
for idx, label in enumerate(edge_labels):
    u, v = all_edges_tuples[idx]
    norm_e = g._normalize_edge(u, v)
    if label in selected_failed_edge_labels and norm_e not in currently_failed_edges:
        g.fail_edge(u, v)
    elif label not in selected_failed_edge_labels and norm_e in currently_failed_edges:
        g.restore_edge(u, v)

if st.sidebar.button("🔄 Restore All (Clear Failures)", use_container_width=True):
    g.clear_failures()
    st.rerun()


# ------------------------------------------------------------------
# MAIN APPLICATION HEADER
# ------------------------------------------------------------------
st.title("🌐 Network Failure Recovery Simulator")
st.caption("Design and Analysis of Algorithms (DAA Project - Problem 55)")

# Global Source / Target Router Selector
col_src, col_tgt, col_metrics1, col_metrics2, col_metrics3 = st.columns([1.5, 1.5, 1, 1, 1])

all_active_nodes = g.get_all_nodes()
if not all_active_nodes:
    st.warning("The graph is currently empty. Please add routers or load a preset.")
    st.stop()

with col_src:
    src_idx = all_active_nodes.index(st.session_state.source_node) if st.session_state.source_node in all_active_nodes else 0
    source_node = st.selectbox("Source Router (A)", options=all_active_nodes, index=src_idx, key="global_source")
    st.session_state.source_node = source_node

with col_tgt:
    tgt_default = st.session_state.target_node if st.session_state.target_node in all_active_nodes else all_active_nodes[-1]
    tgt_idx = all_active_nodes.index(tgt_default) if tgt_default in all_active_nodes else len(all_active_nodes) - 1
    target_node = st.selectbox("Target Router (B)", options=all_active_nodes, index=tgt_idx, key="global_target")
    st.session_state.target_node = target_node

active_routers_cnt = len(g.get_active_nodes())
total_routers_cnt = len(g.get_all_nodes())
failed_nodes_cnt = len(g.get_failed_nodes())

active_links_cnt = len(g.get_active_edges())
total_links_cnt = len(g.get_all_edges())
failed_edges_cnt = len(g.get_failed_edges())

comp_summary = find_components(g, method="BFS")
comp_count = comp_summary["component_count"]

with col_metrics1:
    st.metric(
        "Active Routers",
        f"{active_routers_cnt} / {total_routers_cnt}",
        delta=f"-{failed_nodes_cnt} failed" if failed_nodes_cnt > 0 else "All Healthy",
        delta_color="inverse" if failed_nodes_cnt > 0 else "normal"
    )
with col_metrics2:
    st.metric(
        "Active Links",
        f"{active_links_cnt} / {total_links_cnt}",
        delta=f"-{failed_edges_cnt} failed" if failed_edges_cnt > 0 else "All Healthy",
        delta_color="inverse" if failed_edges_cnt > 0 else "normal"
    )
with col_metrics3:
    st.metric(
        "Network Components",
        comp_count,
        delta="Fully Connected" if comp_count == 1 else f"Split ({comp_count} parts)",
        delta_color="normal" if comp_count == 1 else "inverse"
    )

st.markdown("---")


# ------------------------------------------------------------------
# 9 MAIN TABS
# ------------------------------------------------------------------
tabs = st.tabs([
    "🌐 Network",
    "🧩 Components",
    "⚡ Shortest Path (Dijkstra)",
    "🎯 Minimum Hops (BFS)",
    "🔄 Alternate Route",
    "⚠️ Critical Connections",
    "🔍 Reachability",
    "🎬 Step-by-Step",
    "📊 Comparison & Benchmarks"
])


# ==================================================================
# TAB 1: NETWORK VIEW
# ==================================================================
with tabs[0]:
    st.subheader("🌐 Active Network Topology View")
    
    if g.get_failed_nodes() or g.get_failed_edges():
        st.warning(f"Network running under failure state! Failed Routers: {list(g.get_failed_nodes())} | Failed Links: {[f'{u}-{v}' for u,v in g.get_failed_edges()]}")
    else:
        st.success("Network operating normally (0 failures).")

    fig = draw_network_graph(g, st.session_state.pos, title="Interactive Network Graph")
    st.plotly_chart(fig, use_container_width=True)


# ==================================================================
# TAB 2: CONNECTED COMPONENTS
# ==================================================================
with tabs[1]:
    st.subheader("🧩 Connected Component Analysis")
    
    method = st.radio("Traversal Algorithm for Component Discovery", options=["BFS", "DFS"], horizontal=True)
    comp_res = find_components(g, method=method)

    n_parts = comp_res["component_count"]
    if n_parts == 1:
        st.success("✅ Network is FULLY CONNECTED (1 Component). All active routers can communicate.")
    else:
        st.error(f"⚠️ NETWORK SPLIT INTO {n_parts} DISCONNECTED PARTS! Communication between sub-networks is severed.")

    # Assign distinct colors to components
    colors_palette = px.colors.qualitative.Set1 + px.colors.qualitative.Bold
    comp_color_map = {}
    for idx, comp in enumerate(comp_res["components"]):
        color = colors_palette[idx % len(colors_palette)]
        for node in comp:
            comp_color_map[node] = color

    fig_comp = draw_network_graph(g, st.session_state.pos, component_colors=comp_color_map, title=f"Connected Components ({n_parts} Partitioned Subgraphs)")
    st.plotly_chart(fig_comp, use_container_width=True)

    col1, col2 = st.columns(2)
    with col1:
        st.markdown("### Component Breakdown")
        comp_df = pd.DataFrame([
            {"Component ID": idx + 1, "Router Count": len(c), "Routers": ", ".join(c)}
            for idx, c in enumerate(comp_res["components"])
        ])
        st.dataframe(comp_df, use_container_width=True)

    with col2:
        st.markdown("### Isolated Routers")
        if comp_res["isolated_nodes"]:
            st.warning(f"Isolated Routers (completely disconnected): `{comp_res['isolated_nodes']}`")
        else:
            st.info("No completely isolated single-node routers.")


# ==================================================================
# TAB 3: SHORTEST PATH (DIJKSTRA)
# ==================================================================
with tabs[2]:
    st.subheader("⚡ Shortest Path Analysis (Dijkstra's Algorithm)")
    
    dijk_res = dijkstra(g, start_node=source_node, target_node=target_node)

    if dijk_res["reachable"]:
        st.success(f"✅ Shortest Route Found from `{source_node}` to `{target_node}`! Total Cost / Latency: **{dijk_res['total_cost']:.2f}**")
        st.markdown(f"**Path**: `{' ➔ '.join(dijk_res['path'])}`")
        
        fig_dijk = draw_network_graph(g, st.session_state.pos, highlight_path=dijk_res["path"], title=f"Dijkstra Shortest Path ({source_node} ➔ {target_node})")
        st.plotly_chart(fig_dijk, use_container_width=True)
    else:
        st.error(f"❌ NO ROUTE EXISTS! Router `{target_node}` is unreachable from `{source_node}`.")
        fig_dijk = draw_network_graph(g, st.session_state.pos, title="Unreachable Path View")
        st.plotly_chart(fig_dijk, use_container_width=True)

    st.markdown("### Distance Table to All Active Routers")
    dist_df = pd.DataFrame([
        {"Router": node, "Shortest Cost": round(d, 2) if d < float("inf") else "Unreachable (∞)"}
        for node, d in sorted(dijk_res["distances"].items())
    ])
    st.dataframe(dist_df, use_container_width=True)


# ==================================================================
# TAB 4: MINIMUM HOPS (BFS)
# ==================================================================
with tabs[3]:
    st.subheader("🎯 Minimum Hop Path Analysis (BFS)")

    bfs_res = bfs(g, start_node=source_node, target_node=target_node)

    if bfs_res["reachable"]:
        st.success(f"✅ Minimum Hop Route Found from `{source_node}` to `{target_node}`! Total Hop Count: **{bfs_res['hop_count']}**")
        st.markdown(f"**Path**: `{' ➔ '.join(bfs_res['path'])}`")

        fig_bfs = draw_network_graph(g, st.session_state.pos, highlight_path=bfs_res["path"], title=f"BFS Minimum Hop Path ({source_node} ➔ {target_node})")
        st.plotly_chart(fig_bfs, use_container_width=True)
    else:
        st.error(f"❌ Target Router `{target_node}` is unreachable from `{source_node}`.")

    st.markdown("### BFS Distance Level Table (Hops from Source)")
    level_df = pd.DataFrame([
        {"Router": node, "Hop Distance Level": lvl}
        for node, lvl in sorted(bfs_res["levels"].items(), key=lambda item: item[1])
    ])
    st.dataframe(level_df, use_container_width=True)


# ==================================================================
# TAB 5: ALTERNATE ROUTE & FAILURE RECOVERY
# ==================================================================
with tabs[4]:
    st.subheader("🔄 Failure Recovery & Alternate Route Analysis")

    rec_res = analyze_failure_recovery(g, source_node=source_node, target_node=target_node)

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("### 🟢 Healthy Network Primary Route")
        if rec_res["primary_reachable"]:
            st.info(f"**Primary Route**: `{' ➔ '.join(rec_res['primary_route'])}`\n\n**Primary Cost**: `{rec_res['primary_cost']:.2f}`")
        else:
            st.warning("No primary route exists even on healthy network.")

    with col2:
        st.markdown("### 🔴 Active Network Alternate Route")
        if rec_res["alternate_reachable"]:
            st.success(f"**Alternate Route**: `{' ➔ '.join(rec_res['alternate_route'])}`\n\n**Alternate Cost**: `{rec_res['alternate_cost']:.2f}`")
        else:
            st.error("❌ NO ALTERNATE ROUTE EXISTS!")

    st.markdown("---")
    st.markdown(f"### Status: `{rec_res['status']}`")
    st.info(rec_res["message"])

    if rec_res["cost_increase"] is not None:
        st.metric("Routing Cost Increase", f"+{rec_res['cost_increase']:.2f}", delta=f"+{rec_res['cost_increase_pct']}% Latency", delta_color="inverse")

    col_a, col_b = st.columns(2)
    with col_a:
        st.markdown(f"**Component Partition Count**: Healthy `{rec_res['healthy_component_count']}` ➔ Active `{rec_res['active_component_count']}`")
    with col_b:
        if rec_res["lost_reachable_nodes"]:
            st.warning(f"**Routers that lost reachability from `{source_node}`**: `{rec_res['lost_reachable_nodes']}`")
        else:
            st.success(f"All originally reachable routers remain accessible from `{source_node}`.")


# ==================================================================
# TAB 6: CRITICAL CONNECTIONS (TARJAN)
# ==================================================================
with tabs[5]:
    st.subheader("⚠️ Critical Network Connections (Single Points of Failure)")

    # Analyze critical connections on HEALTHY network before failures
    healthy_g = g.clone()
    healthy_g.clear_failures()
    crit_res = find_critical_connections(healthy_g)

    b_count = len(crit_res["bridges"])
    ap_count = len(crit_res["articulation_points"])

    if b_count > 0 or ap_count > 0:
        st.warning(f"⚠️ CRITICAL VULNERABILITIES DETECTED! Found **{b_count} Bridge Links** and **{ap_count} Articulation Point Routers** on the base topology.")
    else:
        st.success("✅ HIGH RESILIENCE TOPOLOGY! No single points of failure detected (0 bridges, 0 articulation points).")

    fig_crit = draw_network_graph(
        healthy_g,
        st.session_state.pos,
        bridges=crit_res["bridges"],
        articulation_points=crit_res["articulation_points"],
        title="Critical Vulnerabilities (Healthy Network Structure)"
    )
    st.plotly_chart(fig_crit, use_container_width=True)

    col1, col2 = st.columns(2)
    with col1:
        st.markdown("### 🌉 Critical Links (Bridges)")
        st.caption("Failure of any bridge link disconnects the network into separate components.")
        if crit_res["bridges"]:
            b_df = pd.DataFrame([{"Link": f"{u} -- {v}"} for u, v in crit_res["bridges"]])
            st.dataframe(b_df, use_container_width=True)
        else:
            st.info("No bridge links present.")

    with col2:
        st.markdown("### 📍 Critical Routers (Articulation Points)")
        st.caption("Failure of any articulation point router disconnects the network into separate components.")
        if crit_res["articulation_points"]:
            ap_df = pd.DataFrame([{"Router ID": r} for r in crit_res["articulation_points"]])
            st.dataframe(ap_df, use_container_width=True)
        else:
            st.info("No articulation point routers present.")


# ==================================================================
# TAB 7: REACHABILITY
# ==================================================================
with tabs[6]:
    st.subheader("🔍 Network Reachability Analysis")
    st.markdown(f"Evaluating whether Router **`{source_node}`** can currently reach Router **`{target_node}`**...")

    bfs_reach = bfs(g, start_node=source_node, target_node=target_node)
    dfs_reach = dfs(g, start_node=source_node, target_node=target_node)

    if bfs_reach["reachable"]:
        st.success(f"✅ YES! Router `{source_node}` CAN reach `{target_node}`.")
    else:
        st.error(f"❌ NO! Router `{source_node}` CANNOT reach `{target_node}` under current failure conditions.")

    col1, col2 = st.columns(2)
    with col1:
        st.markdown("### BFS Traversal Order")
        st.write(f"**Visited Order**: `{bfs_reach['visit_order']}`")
        st.write(f"**Path**: `{bfs_reach['path']}`")

    with col2:
        st.markdown("### DFS Traversal Order")
        st.write(f"**Visited Order**: `{dfs_reach['visit_order']}`")
        st.write(f"**Path**: `{dfs_reach['path']}`")


# ==================================================================
# TAB 8: STEP-BY-STEP INTERACTIVE VISUALIZER
# ==================================================================
with tabs[7]:
    st.subheader("🎬 Step-by-Step Algorithm Execution Animator")

    algo_anim = st.selectbox("Select Algorithm to Animate", options=["Dijkstra Shortest Path", "Breadth-First Search (BFS)", "Depth-First Search (DFS)", "Tarjan Critical Connections"])

    if algo_anim == "Dijkstra Shortest Path":
        anim_data = dijkstra(g, start_node=source_node, target_node=target_node)
    elif algo_anim == "Breadth-First Search (BFS)":
        anim_data = bfs(g, start_node=source_node, target_node=target_node)
    elif algo_anim == "Depth-First Search (DFS)":
        anim_data = dfs(g, start_node=source_node, target_node=target_node)
    else:
        anim_data = find_critical_connections(g)

    steps_log = anim_data["steps"]

    # Interactive Step Player Controller
    active_step_idx = render_step_player_controls(steps_log, key_prefix="main_step")
    curr_step = steps_log[active_step_idx]

    # Graph Highlight for Active Step
    step_node = curr_step.get("current_node")
    step_edge = curr_step.get("highlight_edge")
    step_bridges = curr_step.get("bridges")
    step_ap = curr_step.get("articulation_points")

    fig_step = draw_network_graph(
        g,
        st.session_state.pos,
        current_step_node=step_node,
        current_step_edge=step_edge,
        bridges=step_bridges,
        articulation_points=step_ap,
        title=f"Step {active_step_idx + 1} / {len(steps_log)}: {algo_anim}"
    )
    st.plotly_chart(fig_step, use_container_width=True)

    # Detailed Step State Card
    render_step_details(curr_step, algo_type=algo_anim)


# ==================================================================
# TAB 9: COMPARISON & BENCHMARKS
# ==================================================================
with tabs[8]:
    st.subheader("📊 Algorithm Comparison & Benchmarks")

    # Section A: BFS vs Dijkstra Comparison
    st.markdown("### A. BFS vs Dijkstra (Same Source & Target)")
    bfs_comp_res = bfs(g, start_node=source_node, target_node=target_node)
    dijk_comp_res = dijkstra(g, start_node=source_node, target_node=target_node)

    comp_path_df = pd.DataFrame([
        {
            "Algorithm": "BFS (Minimum Hops)",
            "Path": " -> ".join(bfs_comp_res["path"]) if bfs_comp_res["path"] else "Unreachable",
            "Hop Count": bfs_comp_res["hop_count"] if bfs_comp_res["hop_count"] is not None else "-",
            "Total Cost": sum([g.get_edge_weight(bfs_comp_res["path"][i], bfs_comp_res["path"][i+1]) or 0 for i in range(len(bfs_comp_res["path"])-1)]) if bfs_comp_res["path"] else "-"
        },
        {
            "Algorithm": "Dijkstra (Least Cost)",
            "Path": " -> ".join(dijk_comp_res["path"]) if dijk_comp_res["path"] else "Unreachable",
            "Hop Count": len(dijk_comp_res["path"]) - 1 if dijk_comp_res["path"] else "-",
            "Total Cost": round(dijk_comp_res["total_cost"], 2) if dijk_comp_res["total_cost"] is not None else "-"
        }
    ])
    st.dataframe(comp_path_df, use_container_width=True)

    st.info(
        "💡 **Why do BFS and Dijkstra results differ?**\n\n"
        "BFS minimizes the **number of hops** regardless of link weights (treating every link as cost 1). "
        "Dijkstra minimizes the **cumulative link cost/latency** using edge weights. "
        "A path with fewer hops may have higher overall latency than a multi-hop path with lighter edge weights."
    )

    st.markdown("---")

    # Section B: BFS vs DFS Component Discovery Comparison
    st.markdown("### B. BFS vs DFS Component Discovery Comparison")
    comp_eval = compare_components(g)
    
    col_c1, col_c2, col_c3 = st.columns(3)
    with col_c1:
        st.metric("BFS Execution Time", f"{comp_eval['bfs_time_ms']:.3f} ms")
    with col_c2:
        st.metric("DFS Execution Time", f"{comp_eval['dfs_time_ms']:.3f} ms")
    with col_c3:
        st.metric("Component Equivalence", "Identical ✅" if comp_eval["identical_components"] else "Different ❌")

    st.caption(comp_eval["explanation"])

    st.markdown("---")

    # Section C: Algorithmic Complexity Table
    st.markdown("### C. Theoretical Time & Space Complexity")
    complexity_df = pd.DataFrame([
        {"Algorithm": "Breadth-First Search (BFS)", "Time Complexity": "O(V + E)", "Space Complexity": "O(V)", "Primary Data Structure": "Queue (collections.deque)"},
        {"Algorithm": "Depth-First Search (DFS)", "Time Complexity": "O(V + E)", "Space Complexity": "O(V)", "Primary Data Structure": "Explicit Stack"},
        {"Algorithm": "Dijkstra's Algorithm", "Time Complexity": "O((V + E) log V)", "Space Complexity": "O(V)", "Primary Data Structure": "Binary Min-Heap (heapq)"},
        {"Algorithm": "Connected Components", "Time Complexity": "O(V + E)", "Space Complexity": "O(V)", "Primary Data Structure": "Visited Set + Queue/Stack"},
        {"Algorithm": "Tarjan Critical Connections", "Time Complexity": "O(V + E)", "Space Complexity": "O(V)", "Primary Data Structure": "Iterative State Stack + Arrays"}
    ])
    st.dataframe(complexity_df, use_container_width=True)

    st.markdown("---")

    # Section D: Benchmark Chart
    st.markdown("### D. Runtime Performance Benchmarks")
    st.write("Run empirical benchmarking across random graph sizes (V = 50, 100, 200, 400, 800):")

    if st.button("🚀 Run Empirical Benchmark Suite", use_container_width=True):
        with st.spinner("Executing performance benchmark runs..."):
            df_bench = run_algorithm_benchmarks(sizes=[50, 100, 200, 400, 800])
            st.session_state["benchmark_df"] = df_bench

    if "benchmark_df" in st.session_state:
        df_bench = st.session_state["benchmark_df"]
        st.dataframe(df_bench, use_container_width=True)

        # Plotly Line Chart
        fig_bench = px.line(
            df_bench,
            x="Graph Size (V)",
            y=["BFS (ms)", "DFS (ms)", "Dijkstra (ms)", "Components (ms)", "Tarjan (ms)"],
            markers=True,
            title="Algorithm Execution Time (ms) vs. Graph Size (Nodes)",
            labels={"value": "Runtime (ms)", "variable": "Algorithm"}
        )
        fig_bench.update_layout(height=450, hovermode="x unified")
        st.plotly_chart(fig_bench, use_container_width=True)
