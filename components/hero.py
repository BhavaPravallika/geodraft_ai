"""
components/hero.py
Premium landing section with branding and value proposition.
"""
import streamlit as st
from ui.theme import Theme

def render_hero():
    """Renders the premium hero section."""
    html = f"""
    <div style="background: linear-gradient(135deg, {Theme.PRIMARY} 0%, {Theme.SECONDARY} 100%); padding: 60px 40px; border-radius: 16px; margin-bottom: 30px; color: white; text-align: center; box-shadow: 0 10px 25px rgba(15, 23, 42, 0.2);">
        <h1 style="font-size: 3rem; font-weight: 700; margin-bottom: 10px; letter-spacing: -1px;">GeoDraft AI</h1>
        <p style="font-size: 1.25rem; font-weight: 300; opacity: 0.9; margin-bottom: 30px;">
            Production-Grade Survey-to-CAD Automation Platform
        </p>
        <div style="display: flex; justify-content: center; gap: 15px; flex-wrap: wrap; margin-bottom: 30px;">
            <span style="background: rgba(255,255,255,0.1); padding: 8px 16px; border-radius: 20px; font-size: 0.9rem;">1. Upload Dataset</span>
            <span style="color: rgba(255,255,255,0.5);">→</span>
            <span style="background: rgba(255,255,255,0.1); padding: 8px 16px; border-radius: 20px; font-size: 0.9rem;">2. AI Detection</span>
            <span style="color: rgba(255,255,255,0.5);">→</span>
            <span style="background: rgba(255,255,255,0.1); padding: 8px 16px; border-radius: 20px; font-size: 0.9rem;">3. Validation</span>
            <span style="color: rgba(255,255,255,0.5);">→</span>
            <span style="background: rgba(255,255,255,0.1); padding: 8px 16px; border-radius: 20px; font-size: 0.9rem;">4. CAD Generation</span>
        </div>
    </div>
    """
    st.markdown(html, unsafe_allow_html=True)

def render_step_indicator(current_step):
    """Renders a custom HTML step progress indicator."""
    steps = ["Upload", "Detect", "Validate", "Configure", "Preview", "Export"]
    
    cols_html = ""
    for i, step_name in enumerate(steps):
        step_num = i + 1
        is_active = step_num == current_step
        is_completed = step_num < current_step
        
        circle_class = "step-circle active" if is_active else ("step-circle completed" if is_completed else "step-circle")
        label_class = "step-label active" if is_active else "step-label"
        icon = "✓" if is_completed else str(step_num)
        
        cols_html += f"""
        <div class="step-item">
            <div class="{circle_class}">{icon}</div>
            <div class="{label_class}">{step_name}</div>
        </div>
        """
        
    progress_width = (current_step - 1) / (len(steps) - 1) * 100
        
    html = f"""
    <div class="saas-card" style="padding: 30px 20px 10px 20px;">
        <div class="step-indicator">
            <div class="step-line">
                <div class="step-line-progress" style="width: {progress_width}%;"></div>
            </div>
            {cols_html}
        </div>
    </div>
    """
    st.markdown(html, unsafe_allow_html=True)
