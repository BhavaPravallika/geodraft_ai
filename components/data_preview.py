"""
components/data_preview.py
Handles data validation logic execution and renders the professional data preview table.
"""
import streamlit as st
import time
from core.state_manager import StateManager
from validation.validator import Validator
from ui.theme import Theme
from ui.status_components import StatusComponents
from services.logger import logger

def render_data_preview():
    st.markdown(f"<h3 style='color: {Theme.PRIMARY};'>Engineering Data Validation</h3>", unsafe_allow_html=True)
    
    # Run Validation if not already run for this schema
    if StateManager.get("clean_df") is None:
        with st.spinner("Validating geometry and running integrity checks..."):
            time.sleep(1.0) # UX feel
            raw_df = StateManager.get("raw_df")
            schema = StateManager.get("schema")
            
            clean_df, summary = Validator.validate(raw_df, schema)
            
            StateManager.set("clean_df", clean_df)
            StateManager.set("validation_summary", summary)
            
            if summary.get("errors"):
                for err in summary["errors"]:
                    logger.error(f"Validation Error: {err}")
                    StateManager.add_log(f"Validation Error: {err}")
            else:
                logger.info("Data validation completed successfully.")
                StateManager.add_log("Data validation passed.")
                
    summary = StateManager.get("validation_summary", {})
    clean_df = StateManager.get("clean_df")
    
    if summary.get("errors"):
        for err in summary["errors"]:
            StatusComponents.error(err)
        st.warning("Please go back and correct the schema mapping.")
        if st.button("← Back to Schema Mapper"):
            StateManager.set_step(2)
            StateManager.set("clean_df", None)
            st.rerun()
        return

    # Display Validation Summary
    StatusComponents.validation_summary(
        summary.get("valid_count", 0),
        summary.get("invalid_count", 0)
    )
    
    if summary.get("warnings"):
        for w in summary["warnings"]:
            StatusComponents.warning(w)

    st.markdown("#### Validated Dataset Preview")
    st.markdown("Review the cleaned dataset below. Invalid and duplicated rows have been automatically dropped.")
    
    # Display the dataframe with Streamlit's new dataframe features
    st.dataframe(
        clean_df,
        use_container_width=True,
        hide_index=True,
        height=300
    )
    
    st.markdown("<br>", unsafe_allow_html=True)
    col1, col2 = st.columns([1, 4])
    with col1:
        if st.button("← Back"):
            StateManager.set_step(2)
            StateManager.set("clean_df", None)
            st.rerun()
    with col2:
        if st.button("Proceed to CAD Configuration →", type="primary", use_container_width=True):
            StateManager.next_step()
            st.rerun()
