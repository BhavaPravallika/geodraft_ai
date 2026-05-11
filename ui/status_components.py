"""
ui/status_components.py
Provides reusable status cards (Success, Warning, Error, Info) to maintain visual consistency.
"""
import streamlit as st
import textwrap
from .theme import Theme

class StatusComponents:
    @staticmethod
    def success(message, title="Success"):
        Theme.card(title, message, icon="✅", color=Theme.SUCCESS)
        
    @staticmethod
    def warning(message, title="Warning"):
        Theme.card(title, message, icon="⚠️", color=Theme.WARNING)
        
    @staticmethod
    def error(message, title="Error"):
        Theme.card(title, message, icon="❌", color=Theme.ERROR)
        
    @staticmethod
    def info(message, title="Information"):
        Theme.card(title, message, icon="ℹ️", color=Theme.ACCENT)
        
    @staticmethod
    def file_upload_success(filename, size_kb, rows, columns):
        html = f"""
        <style>
        @keyframes fadeIn {{ from {{ opacity: 0; transform: translateY(10px); }} to {{ opacity: 1; transform: translateY(0); }} }}
        .premium-card:hover {{ transform: translateY(-2px); box-shadow: 0 10px 15px -3px rgba(0,0,0,0.1); }}
        </style>
        <div class="premium-card" style="background: white; border-radius: 12px; padding: 20px; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.05); border: 1px solid #e2e8f0; animation: fadeIn 0.5s ease; transition: transform 0.2s, box-shadow 0.2s; margin-bottom: 20px;">
            <div style="display: flex; align-items: center; gap: 16px; margin-bottom: 20px;">
                <div style="font-size: 2.2rem; background: #f8fafc; padding: 12px; border-radius: 12px; border: 1px solid #e2e8f0;">📄</div>
                <div>
                    <div style="color: {Theme.MUTED}; font-size: 0.8rem; font-weight: 600; text-transform: uppercase; letter-spacing: 0.5px;">File Uploaded Successfully</div>
                    <div style="color: {Theme.PRIMARY}; font-size: 1.15rem; font-weight: 700; margin-top: 4px;">{filename}</div>
                </div>
            </div>
            <div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 10px; border-top: 1px solid #f1f5f9; padding-top: 16px;">
                <div>
                    <div style="color: {Theme.MUTED}; font-size: 0.8rem; margin-bottom: 4px;">Size</div>
                    <div style="color: {Theme.PRIMARY}; font-weight: 600; font-size: 1.05rem;">{size_kb:.1f} KB</div>
                </div>
                <div>
                    <div style="color: {Theme.MUTED}; font-size: 0.8rem; margin-bottom: 4px;">Rows</div>
                    <div style="color: {Theme.PRIMARY}; font-weight: 600; font-size: 1.05rem;">{rows}</div>
                </div>
                <div>
                    <div style="color: {Theme.MUTED}; font-size: 0.8rem; margin-bottom: 4px;">Columns</div>
                    <div style="color: {Theme.PRIMARY}; font-weight: 600; font-size: 1.05rem;">{columns}</div>
                </div>
            </div>
        </div>
        """
        st.markdown(textwrap.dedent(html), unsafe_allow_html=True)

    @staticmethod
    def validation_summary(valid_count, invalid_count, fixes_applied=None):
        total = valid_count + invalid_count
        valid_pct = (valid_count / total * 100) if total > 0 else 0
        invalid_pct = (invalid_count / total * 100) if total > 0 else 0
        html = f"""
        <style>
        @keyframes fadeIn {{ from {{ opacity: 0; transform: translateY(10px); }} to {{ opacity: 1; transform: translateY(0); }} }}
        </style>
        <div style="background: white; border-radius: 12px; padding: 24px; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.05); border: 1px solid #e2e8f0; border-left: 4px solid {Theme.ACCENT}; animation: fadeIn 0.5s ease; margin-bottom: 20px;">
            <h4 style="margin: 0 0 4px 0; color: {Theme.PRIMARY}; font-size: 1.1rem; font-weight: 600;">Validation Summary</h4>
            <p style="margin: 0 0 24px 0; color: {Theme.MUTED}; font-size: 0.9rem;">Dataset Integrity Check Completed</p>
            <div style="height: 8px; width: 100%; background: #f1f5f9; border-radius: 4px; margin-bottom: 24px; overflow: hidden; display: flex;">
                <div style="height: 100%; background: {Theme.SUCCESS}; width: {valid_pct}%; transition: width 1s ease-in-out;"></div>
                <div style="height: 100%; background: {Theme.ERROR}; width: {invalid_pct}%; transition: width 1s ease-in-out;"></div>
            </div>
            <div style="display: flex; justify-content: space-between; padding: 14px 0; border-bottom: 1px solid #f1f5f9;">
                <span style="color: {Theme.SECONDARY}; font-weight: 500; display: flex; align-items: center; gap: 10px;">
                    <span style="color: {Theme.SUCCESS}; font-size: 1.2rem;">●</span> Valid Entities
                </span>
                <span style="color: {Theme.PRIMARY}; font-weight: 600; font-size: 1.1rem;">{valid_count}</span>
            </div>
            <div style="display: flex; justify-content: space-between; padding: 14px 0; border-bottom: 1px solid #f1f5f9;">
                <span style="color: {Theme.SECONDARY}; font-weight: 500; display: flex; align-items: center; gap: 10px;">
                    <span style="color: {Theme.ERROR}; font-size: 1.2rem;">●</span> Invalid Entities Dropped
                </span>
                <span style="color: {Theme.PRIMARY}; font-weight: 600; font-size: 1.1rem;">{invalid_count}</span>
            </div>
            <div style="margin-top: 20px; color: {Theme.MUTED}; font-size: 0.95rem;">
                Validation Accuracy: <strong style="color: {Theme.PRIMARY};">{valid_pct:.1f}%</strong>
            </div>
        </div>
        """
        st.markdown(textwrap.dedent(html), unsafe_allow_html=True)

    @staticmethod
    def empty_state(title, description, icon="📦"):
        html = f"""
        <div style="text-align: center; padding: 40px 20px; background: {Theme.BACKGROUND}; border-radius: 12px; border: 2px dashed #cbd5e1; color: {Theme.MUTED};">
            <div style="font-size: 3rem; margin-bottom: 16px;">{icon}</div>
            <h3 style="color: {Theme.PRIMARY}; margin-bottom: 8px;">{title}</h3>
            <p>{description}</p>
        </div>
        """
        st.markdown(textwrap.dedent(html), unsafe_allow_html=True)
