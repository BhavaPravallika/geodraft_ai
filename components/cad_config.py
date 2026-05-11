"""
components/cad_config.py
Step 4: Configure CAD output parameters.
"""
import streamlit as st
from core.state_manager import StateManager
from ui.theme import Theme

def render_cad_config():
    st.markdown(f"<h3 style='color: {Theme.PRIMARY};'>CAD Configuration</h3>", unsafe_allow_html=True)
    st.markdown("Configure how the AI will draft your geometry. These settings apply to the final DXF export.")
    
    settings = StateManager.get("cad_settings")
    
    col1, col2 = st.columns(2)
    
    with col1:
        Theme.card("Annotation Scale", "Controls the size of text and dimensions.", "📏")
        scale = st.slider("Scale Factor", 0.1, 5.0, settings.get("text_scale", 1.0), 0.1, key="cfg_scale")
        StateManager.update_cad_setting("text_scale", scale)
        
        Theme.card("Draw Boundaries", "Automatically draft closed polylines for groups.", "📐")
        show_bnd = st.toggle("Enable Polylines", value=settings.get("show_boundary", True), key="cfg_bnd")
        StateManager.update_cad_setting("show_boundary", show_bnd)
        
    with col2:
        Theme.card("Point Labels", "Draw text annotations for Point IDs/Labels.", "📝")
        show_lbl = st.toggle("Enable Labels", value=settings.get("show_labels", True), key="cfg_lbl")
        StateManager.update_cad_setting("show_labels", show_lbl)
        
        Theme.card("Auto-Close Polygons", "Uses Polar Sorting to prevent intersecting lines.", "🔄")
        auto_close = st.toggle("Enable Auto-Sorting", value=settings.get("auto_close", True), key="cfg_sort")
        StateManager.update_cad_setting("auto_close", auto_close)

    st.markdown("<br>", unsafe_allow_html=True)
    c1, c2 = st.columns([1, 4])
    with c1:
        if st.button("← Back"):
            StateManager.set_step(3)
            st.rerun()
    with c2:
        if st.button("Generate CAD Preview →", type="primary", use_container_width=True):
            StateManager.next_step()
            st.rerun()
