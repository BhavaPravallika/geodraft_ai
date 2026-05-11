"""
components/sidebar.py
Professional sidebar for navigation and global settings.
"""
import streamlit as st
from core.state_manager import StateManager
from core.config import WORKFLOW_STEPS

def render_sidebar():
    with st.sidebar:
        st.markdown(f"### ⚙️ GeoDraft AI")
        st.caption("v2.0.0 Production Build")
        
        st.divider()
        st.markdown("#### 🔄 Workflow Status")
        current_step = StateManager.get("step")
        
        for num, name in WORKFLOW_STEPS.items():
            if num == current_step:
                st.markdown(f"**▶ {num}. {name}**")
            elif num < current_step:
                st.markdown(f"✓ *{num}. {name}*")
            else:
                st.markdown(f"<span style='color: gray'>  {num}. {name}</span>", unsafe_allow_html=True)
                
        st.divider()
        st.markdown("#### 🛠️ Global CAD Settings")
        
        scale = st.slider("Annotation Scale", 0.1, 3.0, StateManager.get("cad_settings").get("text_scale", 1.0), 0.1)
        if scale != StateManager.get("cad_settings").get("text_scale"):
            StateManager.update_cad_setting("text_scale", scale)
            
        show_bnd = st.toggle("Show Boundaries", value=StateManager.get("cad_settings").get("show_boundary", True))
        if show_bnd != StateManager.get("cad_settings").get("show_boundary"):
            StateManager.update_cad_setting("show_boundary", show_bnd)
            
        st.divider()
        st.markdown("#### 📋 Session Logs")
        with st.expander("View Logs"):
            logs = StateManager.get("logs", [])
            if not logs:
                st.caption("No logs yet.")
            else:
                for log in logs[-5:]:  # Show last 5
                    st.caption(f"- {log}")
                    
        st.divider()
        if st.button("Reset Workflow", use_container_width=True):
            StateManager.reset_workflow()
            st.rerun()
