"""
components/cad_preview.py
Live CAD Preview System using Plotly to simulate a real engineering CAD viewer.
"""
import streamlit as st
import plotly.graph_objects as go
from core.state_manager import StateManager
from core.config import PREVIEW_THEME, MAX_PREVIEW_ENTITIES
from cad_engine.geometry_builder import GeometryBuilder
from ui.theme import Theme
from ui.status_components import StatusComponents

def generate_plotly_figure(df, schema, settings):
    fig = go.Figure()

    x_col = schema.get("x")
    y_col = schema.get("y")
    grp_col = schema.get("layer")
    label_col = schema.get("label")
    
    show_boundary = settings.get("show_boundary", True)
    show_labels = settings.get("show_labels", True)
    auto_close = settings.get("auto_close", True)

    # Process Points
    plot_df = df.copy()
    if len(plot_df) > MAX_PREVIEW_ENTITIES:
        st.warning(f"Preview limited to {MAX_PREVIEW_ENTITIES} points for performance.")
        plot_df = plot_df.head(MAX_PREVIEW_ENTITIES)

    # Base Scatter Points
    text_labels = None
    mode = "markers"
    if show_labels and label_col and label_col in plot_df.columns:
        text_labels = plot_df[label_col].astype(str).tolist()
        mode = "markers+text"

    fig.add_trace(go.Scatter(
        x=plot_df[x_col],
        y=plot_df[y_col],
        mode=mode,
        text=text_labels,
        textposition="top right",
        marker=dict(size=6, color='#fbbf24', symbol='circle-cross'),
        name="Survey Points",
        hoverinfo="text+x+y" if text_labels else "x+y"
    ))

    # Add Boundaries
    if show_boundary and grp_col and grp_col in plot_df.columns:
        if auto_close:
            plot_df = GeometryBuilder.sort_points_angularly(plot_df, x_col, y_col, grp_col)
            
        for grp, gdf in plot_df.groupby(grp_col):
            if len(gdf) >= 3:
                x_pts = gdf[x_col].tolist()
                y_pts = gdf[y_col].tolist()
                x_pts.append(x_pts[0])  # Close loop
                y_pts.append(y_pts[0])
                
                grp_lower = str(grp).lower()
                if 'road' in grp_lower:
                    line_color = '#34d399' # Green
                elif 'plot' in grp_lower:
                    line_color = '#d946ef' # Magenta
                elif any(kw in grp_lower for kw in ['boundary', 'main', 'outer']):
                    line_color = '#f8fafc' # White
                else:
                    line_color = '#94a3b8' # Gray
                    
                fig.add_trace(go.Scatter(
                    x=x_pts,
                    y=y_pts,
                    mode="lines",
                    line=dict(color=line_color, width=2),
                    name=f"Layer: {grp}",
                    hoverinfo="name"
                ))

    # CAD-like Layout
    fig.update_layout(
        title="",
        xaxis=dict(
            title="Easting (X)",
            showgrid=True,
            gridcolor='#334155',
            zeroline=False,
            scaleanchor="y",
            scaleratio=1
        ),
        yaxis=dict(
            title="Northing (Y)",
            showgrid=True,
            gridcolor='#334155',
            zeroline=False
        ),
        plot_bgcolor='#0f172a',
        paper_bgcolor='#0f172a',
        font=dict(color='#f8fafc'),
        margin=dict(l=10, r=10, t=10, b=10),
        showlegend=True,
        legend=dict(
            yanchor="top",
            y=0.99,
            xanchor="left",
            x=0.01,
            bgcolor="rgba(15, 23, 42, 0.8)",
            bordercolor="#334155",
            borderwidth=1
        ),
        dragmode='pan'
    )
    
    return fig

def render_cad_preview():
    st.markdown(f"<h3 style='color: {Theme.PRIMARY};'>Live CAD Preview</h3>", unsafe_allow_html=True)
    st.markdown("Interact with the drafted geometry below. Use your mouse to pan and zoom.")
    
    df = StateManager.get("clean_df")
    schema = StateManager.get("schema")
    settings = StateManager.get("cad_settings")
    
    if df is None:
        StatusComponents.error("No valid geometry data found.")
        return
        
    fig = generate_plotly_figure(df, schema, settings)
    
    # Custom CSS to make the chart container look like a CAD window
    st.markdown("""
        <style>
        .cad-container {
            border: 2px solid #334155;
            border-radius: 8px;
            overflow: hidden;
            box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.5);
            margin-bottom: 20px;
        }
        </style>
    """, unsafe_allow_html=True)
    
    st.markdown('<div class="cad-container">', unsafe_allow_html=True)
    st.plotly_chart(fig, use_container_width=True, config={
        'scrollZoom': True,
        'displayModeBar': True,
        'modeBarButtonsToRemove': ['lasso2d', 'select2d'],
        'displaylogo': False
    })
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    c1, c2 = st.columns([1, 4])
    with c1:
        if st.button("← Back"):
            StateManager.set_step(4)
            st.rerun()
    with c2:
        if st.button("Approve & Export CAD →", type="primary", use_container_width=True):
            StateManager.next_step()
            st.rerun()
