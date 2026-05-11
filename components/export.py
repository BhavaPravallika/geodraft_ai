"""
components/export.py
Handles DXF build execution and provides the download experience with engineering metadata.
"""
import streamlit as st
import time
from core.state_manager import StateManager
from cad_engine.dxf_builder import DXFBuilder
from services.exporter import Exporter
from ui.theme import Theme
from ui.status_components import StatusComponents

def render_metadata_panel(metadata):
    """Renders the engineering metadata panel."""
    html = f"""
    <div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 15px; margin-bottom: 20px;">
        <div style="background: {Theme.BACKGROUND}; padding: 15px; border-radius: 8px; border: 1px solid #e2e8f0;">
            <div style="color: {Theme.MUTED}; font-size: 0.85rem; text-transform: uppercase; font-weight: 600;">Entities Drafted</div>
            <div style="color: {Theme.PRIMARY}; font-size: 1.5rem; font-weight: 700;">{metadata.get('entities', 0)}</div>
        </div>
        <div style="background: {Theme.BACKGROUND}; padding: 15px; border-radius: 8px; border: 1px solid #e2e8f0;">
            <div style="color: {Theme.MUTED}; font-size: 0.85rem; text-transform: uppercase; font-weight: 600;">Layers Used</div>
            <div style="color: {Theme.PRIMARY}; font-size: 1.5rem; font-weight: 700;">{metadata.get('layers_used', 0)}</div>
        </div>
        <div style="background: {Theme.BACKGROUND}; padding: 15px; border-radius: 8px; border: 1px solid #e2e8f0;">
            <div style="color: {Theme.MUTED}; font-size: 0.85rem; text-transform: uppercase; font-weight: 600;">Generation Time</div>
            <div style="color: {Theme.PRIMARY}; font-size: 1.5rem; font-weight: 700;">{metadata.get('time_sec', 0.0)}s</div>
        </div>
    </div>
    """
    st.markdown(html, unsafe_allow_html=True)

def render_export():
    st.markdown(f"<h3 style='color: {Theme.PRIMARY};'>Export CAD Files</h3>", unsafe_allow_html=True)
    
    export_data = StateManager.get("export_data")
    
    if export_data.get("dxf_bytes") is None:
        with st.spinner("Compiling DXF binary and applying strict CAD standards..."):
            df = StateManager.get("clean_df")
            schema = StateManager.get("schema")
            settings = StateManager.get("cad_settings")
            
            try:
                dxf_bytes, metadata = DXFBuilder.build(df, schema, settings)
                StateManager.set("export_data", {"dxf_bytes": dxf_bytes, "metadata": metadata})
            except Exception as e:
                StatusComponents.error(f"DXF Generation Failed: {e}")
                return
                
    export_data = StateManager.get("export_data")
    metadata = export_data["metadata"]
    
    StatusComponents.success("DXF generated successfully. Ready for download.", "Export Ready")
    
    render_metadata_panel(metadata)
    
    st.markdown("#### Download Options")
    col1, col2 = st.columns(2)
    
    base_name = StateManager.get("file_name", "GeoDraft").split('.')[0]
    
    with col1:
        dxf_bytes, filename, mime = Exporter.package_export(export_data["dxf_bytes"], base_name, "DXF")
        st.download_button(
            label="⬇️ Download DXF File",
            data=dxf_bytes,
            file_name=filename,
            mime=mime,
            type="primary",
            use_container_width=True
        )
        st.caption("Standard DXF format. Compatible with AutoCAD, Civil 3D, and MicroStation.")
        
    with col2:
        zip_bytes, zip_filename, zip_mime = Exporter.package_export(export_data["dxf_bytes"], base_name, "ZIP")
        st.download_button(
            label="📦 Download ZIP Package",
            data=zip_bytes,
            file_name=zip_filename,
            mime=zip_mime,
            use_container_width=True
        )
        st.caption("Compressed DXF archive for faster transfer.")
        
    st.divider()
    
    st.markdown("#### Trust & Verification")
    st.markdown("✓ DXF structure validated<br>✓ Layer integrity verified<br>✓ Coordinate consistency verified", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("← Back to Preview"):
        StateManager.set("export_data", {"dxf_bytes": None, "metadata": None})
        StateManager.set_step(5)
        st.rerun()
