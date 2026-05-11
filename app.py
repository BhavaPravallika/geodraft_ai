"""
app.py
Main orchestrator for the GeoDraft AI platform.
Loads global styles, state, and routes to the appropriate workflow step.
"""
import streamlit as st

# Must be the first Streamlit command
st.set_page_config(
    page_title="GeoDraft AI | Engineering Automation",
    page_icon="📐",
    layout="wide",
    initial_sidebar_state="expanded"
)

from core.state_manager import StateManager
from ui.theme import Theme

# Import UI Components
from components.sidebar import render_sidebar
from components.hero import render_hero
from components.upload import render_upload
from components.schema_mapper import render_schema_mapper
from components.data_preview import render_data_preview
from components.cad_config import render_cad_config
from components.cad_preview import render_cad_preview
from components.export import render_export

def main():
    # Initialize state and styles
    StateManager.init_state()
    Theme.load_css()
    
    # Render global layout
    render_sidebar()
    
    # Main content area
    current_step = StateManager.get("step")
    
    if current_step == 1:
        render_hero()
        

    
    # Route to the appropriate workflow step component
    if current_step == 1:
        render_upload()
    elif current_step == 2:
        render_schema_mapper()
    elif current_step == 3:
        render_data_preview()
    elif current_step == 4:
        render_cad_config()
    elif current_step == 5:
        render_cad_preview()
    elif current_step == 6:
        render_export()

if __name__ == "__main__":
    main()