"""
ui/theme.py
Configuration for the application's visual theme.
Provides utility functions to inject custom HTML/CSS and standardized colors.
"""
import streamlit as st
import textwrap

class Theme:
    # Colors
    PRIMARY = "#0f172a"
    SECONDARY = "#334155"
    ACCENT = "#3b82f6"
    SUCCESS = "#10b981"
    WARNING = "#f59e0b"
    ERROR = "#ef4444"
    BACKGROUND = "#f8fafc"
    SURFACE = "#ffffff"
    TEXT = "#1e293b"
    MUTED = "#64748b"

    @staticmethod
    def load_css():
        """Loads the global custom CSS file."""
        import os
        css_path = os.path.join(os.path.dirname(__file__), "styles.css")
        try:
            with open(css_path, "r") as f:
                css_content = f.read()
                st.markdown(f"<style>{css_content}</style>", unsafe_allow_html=True)
        except Exception as e:
            st.error(f"Failed to load CSS: {e}")

    @staticmethod
    def card(title, content, icon="📄", color=None):
        """Helper to render a standardized card."""
        border_color = color if color else "#e2e8f0"
        html = f"""
        <div class="saas-card" style="border-left: 4px solid {border_color};">
            <div style="display: flex; align-items: center; gap: 8px; margin-bottom: 12px;">
                <span style="font-size: 1.2rem;">{icon}</span>
                <h4 style="margin: 0; color: {Theme.PRIMARY};">{title}</h4>
            </div>
            <div style="color: {Theme.TEXT}; font-size: 0.95rem;">
                {content}
            </div>
        </div>
        """
        st.markdown(textwrap.dedent(html), unsafe_allow_html=True)
