"""
components/upload.py
Drag-and-drop upload zone with metadata extraction.
"""
import streamlit as st
import time
from core.state_manager import StateManager
from services.data_loader import DataLoader
from services.logger import logger
from ui.theme import Theme
from ui.status_components import StatusComponents

def render_upload():
    st.markdown(f"<h3 style='color: {Theme.PRIMARY};'>Upload Survey Data</h3>", unsafe_allow_html=True)
    st.markdown("Upload your raw survey coordinate dataset. Supported formats: **CSV, XLSX, TXT**.")
    
    uploaded_file = st.file_uploader("", type=["csv", "xlsx", "txt"], label_visibility="collapsed")
    
    if uploaded_file:
        # Check if already processed to avoid re-running loader unnecessarily
        if StateManager.get("raw_df") is None or StateManager.get("file_name") != uploaded_file.name:
            with st.spinner("Processing file..."):
                time.sleep(0.5) # UX feel
                try:
                    df, metadata = DataLoader.load(uploaded_file)
                    StateManager.set("raw_df", df)
                    StateManager.set("file_name", uploaded_file.name)
                    StateManager.set("file_metadata", metadata)
                    logger.info(f"Loaded {uploaded_file.name}: {metadata['rows']} rows.")
                    StateManager.add_log(f"Loaded {uploaded_file.name}")
                except Exception as e:
                    StatusComponents.error(str(e))
                    logger.error("Failed to load file", e)
                    return

        # Display metadata card
        meta = StateManager.get("file_metadata", {})
        StatusComponents.file_upload_success(
            filename=meta.get('filename'),
            size_kb=meta.get('size_kb', 0),
            rows=meta.get('rows', 0),
            columns=meta.get('columns', 0)
        )
        
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("Continue to AI Detection →", type="primary"):
            StateManager.next_step()
            st.rerun()
    else:
        StatusComponents.empty_state("No File Uploaded", "Drag and drop your survey file above to begin.", "📂")
