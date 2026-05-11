"""
components/schema_mapper.py
UI for the intelligent schema detection.
"""
import streamlit as st
import time
from core.state_manager import StateManager
from services.schema_detector import SchemaDetector
from ui.theme import Theme
from ui.status_components import StatusComponents
from services.logger import logger

def render_schema_mapper():
    st.markdown(f"<h3 style='color: {Theme.PRIMARY};'>AI Schema Detection</h3>", unsafe_allow_html=True)
    st.markdown("The system has automatically analyzed your dataset to identify standard survey columns. Please verify the mappings.")

    raw_df = StateManager.get("raw_df")
    if raw_df is None:
        st.warning("No data loaded.")
        return

    cols = raw_df.columns.tolist()
    
    # Auto-detect if not already done in this session
    if StateManager.get_schema("x") is None:
        with st.spinner("Analyzing dataset schema..."):
            time.sleep(0.8) # UX feel
            mapping, confidence = SchemaDetector.detect(cols)
            for k, v in mapping.items():
                StateManager.update_schema(k, v)
            StateManager.set("schema_confidence", confidence)
            logger.info(f"Schema detection complete. Confidence: {confidence}%")
            StateManager.add_log(f"Schema auto-detected with {confidence}% confidence.")

    conf = StateManager.get("schema_confidence", 0)
    if conf > 80:
        StatusComponents.success(f"High confidence ({conf}%) in automatic schema detection. Please review below.", title="AI Detection Complete")
    elif conf > 40:
        StatusComponents.warning(f"Moderate confidence ({conf}%) in automatic schema detection. Manual verification recommended.", title="Review Required")
    else:
        StatusComponents.error("Low confidence in schema detection. Please map columns manually.", title="Manual Mapping Required")

    st.markdown("<br>", unsafe_allow_html=True)
    
    # Render mapping UI
    c1, c2, c3 = st.columns(3)
    
    def get_index(col_name):
        return cols.index(col_name) if col_name in cols else 0
        
    options = ["None"] + cols
    def get_opt_index(col_name):
        return options.index(col_name) if col_name in options else 0

    with c1:
        Theme.card("Easting (X)", "Required coordinate", "📍")
        x_val = st.selectbox("Select X Column", cols, index=get_index(StateManager.get_schema("x")), key="x_sel")
        StateManager.update_schema("x", x_val)

    with c2:
        Theme.card("Northing (Y)", "Required coordinate", "📍")
        y_val = st.selectbox("Select Y Column", cols, index=get_index(StateManager.get_schema("y")), key="y_sel")
        StateManager.update_schema("y", y_val)

    with c3:
        Theme.card("Elevation (Z)", "Optional coordinate", "🏔️")
        z_val = st.selectbox("Select Z Column", options, index=get_opt_index(StateManager.get_schema("z")), key="z_sel")
        StateManager.update_schema("z", None if z_val == "None" else z_val)

    c4, c5, c6 = st.columns(3)
    with c4:
        Theme.card("Point ID", "Optional identifier", "🔢")
        pid_val = st.selectbox("Select ID Column", options, index=get_opt_index(StateManager.get_schema("point_id")), key="pid_sel")
        StateManager.update_schema("point_id", None if pid_val == "None" else pid_val)

    with c5:
        Theme.card("CAD Layer", "Used for boundaries", "📁")
        lyr_val = st.selectbox("Select Layer Column", options, index=get_opt_index(StateManager.get_schema("layer")), key="lyr_sel")
        StateManager.update_schema("layer", None if lyr_val == "None" else lyr_val)
        
    with c6:
        Theme.card("Label", "Text annotation", "📝")
        lbl_val = st.selectbox("Select Label Column", options, index=get_opt_index(StateManager.get_schema("label")), key="lbl_sel")
        StateManager.update_schema("label", None if lbl_val == "None" else lbl_val)

    st.markdown("<br>", unsafe_allow_html=True)
    col1, col2 = st.columns([1, 4])
    with col1:
        if st.button("← Back", use_container_width=True):
            StateManager.set_step(1)
            st.rerun()
    with col2:
        if st.button("Confirm Schema & Validate Data →", type="primary", use_container_width=True):
            StateManager.next_step()
            st.rerun()
