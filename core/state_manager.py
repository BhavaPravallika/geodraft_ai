"""
core/state_manager.py
Centralized state management system for GeoDraft AI workflow.
Encapsulates Streamlit's session_state to prevent key errors and ensure consistency.
"""
import streamlit as st

class StateManager:
    @staticmethod
    def init_state():
        """Initialize all required session state variables."""
        defaults = {
            "step": 1,
            "raw_df": None,
            "clean_df": None,
            "schema": {
                "x": None,
                "y": None,
                "z": None,
                "point_id": None,
                "layer": None,
                "label": None
            },
            "validation_summary": None,
            "validation_errors": [],
            "cad_settings": {
                "text_scale": 1.0,
                "show_boundary": True,
                "show_labels": True,
                "auto_close": True
            },
            "export_data": {
                "dxf_bytes": None,
                "metadata": None
            },
            "logs": []
        }
        
        for key, value in defaults.items():
            if key not in st.session_state:
                st.session_state[key] = value

    @staticmethod
    def get(key, default=None):
        return st.session_state.get(key, default)

    @staticmethod
    def set(key, value):
        st.session_state[key] = value

    @staticmethod
    def update_schema(key, value):
        """Update a specific schema mapping."""
        if "schema" not in st.session_state:
            StateManager.init_state()
        st.session_state.schema[key] = value

    @staticmethod
    def get_schema(key):
        return st.session_state.get("schema", {}).get(key)

    @staticmethod
    def update_cad_setting(key, value):
        if "cad_settings" not in st.session_state:
            StateManager.init_state()
        st.session_state.cad_settings[key] = value

    @staticmethod
    def set_step(step_num):
        st.session_state.step = step_num
        
    @staticmethod
    def next_step():
        st.session_state.step += 1
        
    @staticmethod
    def reset_workflow():
        st.session_state.step = 1
        st.session_state.raw_df = None
        st.session_state.clean_df = None
        st.session_state.export_data = {"dxf_bytes": None, "metadata": None}
        st.session_state.validation_summary = None
        st.session_state.validation_errors = []

    @staticmethod
    def add_log(msg):
        if "logs" not in st.session_state:
            st.session_state.logs = []
        st.session_state.logs.append(msg)
