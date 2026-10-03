"""
ui/step_player.py
Interactive Step-by-Step animation player for algorithm state visualization.
Includes Play/Pause controls, slider, manual step navigation, and state breakdown cards.
"""

import time
import streamlit as st
import pandas as pd
from typing import List, Dict, Any, Optional


def render_step_player_controls(
    steps: List[Dict[str, Any]],
    key_prefix: str = "anim"
) -> int:
    """
    Renders step player playback controls (Play/Pause, Prev, Next, Reset, Slider, Speed).
    Returns current active step index (0-indexed).
    """
    if not steps:
        st.info("No step log available for this algorithm.")
        return 0

    total_steps = len(steps)
    max_idx = total_steps - 1

    # Session State keys for player
    idx_key = f"{key_prefix}_step_idx"
    play_key = f"{key_prefix}_is_playing"
    speed_key = f"{key_prefix}_speed"

    if idx_key not in st.session_state:
        st.session_state[idx_key] = 0
    if play_key not in st.session_state:
        st.session_state[play_key] = False
    if speed_key not in st.session_state:
        st.session_state[speed_key] = 0.5

    # Bounds check
    if st.session_state[idx_key] < 0:
        st.session_state[idx_key] = 0
    elif st.session_state[idx_key] > max_idx:
        st.session_state[idx_key] = max_idx

    # Playback Control Buttons Row
    col_play, col_prev, col_next, col_reset, col_speed = st.columns([1.2, 1, 1, 1, 1.5])

    with col_play:
        play_label = "⏸️ Pause" if st.session_state[play_key] else "▶️ Play"
        if st.button(play_label, key=f"{key_prefix}_btn_play", use_container_width=True):
            st.session_state[play_key] = not st.session_state[play_key]
            st.rerun()

    with col_prev:
        if st.button("⏮️ Prev", key=f"{key_prefix}_btn_prev", use_container_width=True):
            st.session_state[play_key] = False
            st.session_state[idx_key] = max(0, st.session_state[idx_key] - 1)
            st.rerun()

    with col_next:
        if st.button("⏭️ Next", key=f"{key_prefix}_btn_next", use_container_width=True):
            st.session_state[play_key] = False
            st.session_state[idx_key] = min(max_idx, st.session_state[idx_key] + 1)
            st.rerun()

    with col_reset:
        if st.button("🔄 Reset", key=f"{key_prefix}_btn_reset", use_container_width=True):
            st.session_state[play_key] = False
            st.session_state[idx_key] = 0
            st.rerun()

    with col_speed:
        st.session_state[speed_key] = st.select_slider(
            "Playback Delay (s)",
            options=[0.1, 0.3, 0.5, 1.0, 1.5, 2.0],
            value=st.session_state[speed_key],
            key=f"{key_prefix}_slider_speed",
            label_visibility="collapsed"
        )

    # Step Slider
    new_idx = st.slider(
        f"Step Navigation (1 to {total_steps})",
        min_value=0,
        max_value=max_idx,
        value=st.session_state[idx_key],
        format="Step %d",
        key=f"{key_prefix}_slider_step"
    )

    if new_idx != st.session_state[idx_key]:
        st.session_state[play_key] = False
        st.session_state[idx_key] = new_idx

    # Handle Play Auto-Looping
    if st.session_state[play_key]:
        if st.session_state[idx_key] < max_idx:
            time.sleep(st.session_state[speed_key])
            st.session_state[idx_key] += 1
            st.rerun()
        else:
            st.session_state[play_key] = False

    return st.session_state[idx_key]


def render_step_details(step: Dict[str, Any], algo_type: str = "BFS") -> None:
    """Renders formatted state breakdown card for the current execution step."""
    step_num = step.get("step_num", 1)
    curr_node = step.get("current_node", "N/A")
    explanation = step.get("explanation", "")

    st.markdown(f"### 📍 Step {step_num}: Current Node `{curr_node}`")
    st.info(f"**Explanation**: {explanation}")

    col1, col2 = st.columns(2)

    with col1:
        if "queue" in step:
            st.markdown(f"**Queue State**: `{step['queue']}`")
        if "stack" in step:
            st.markdown(f"**Stack State**: `{step['stack']}`")
        if "visited" in step:
            st.markdown(f"**Visited Set**: `{step['visited']}`")
        if "heap" in step:
            st.markdown(f"**Min-Heap State**: `{step['heap']}`")

    with col2:
        # Distance Table for Dijkstra
        if "distances" in step and step["distances"]:
            dist_data = [
                {"Router": node, "Distance": "inf" if d == float("inf") else round(d, 2)}
                for node, d in step["distances"].items()
            ]
            st.markdown("**Tentative Distance Table**")
            st.dataframe(pd.DataFrame(dist_data), height=150, use_container_width=True)

        # Discovery & Low Values for Tarjan
        if "disc" in step and step["disc"]:
            disc_data = [
                {
                    "Router": node,
                    "Discovery Time (disc)": step["disc"].get(node, "-"),
                    "Low Value (low)": step["low"].get(node, "-")
                }
                for node in sorted(step["disc"].keys())
            ]
            st.markdown("**Tarjan Node Metadata**")
            st.dataframe(pd.DataFrame(disc_data), height=150, use_container_width=True)
