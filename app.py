import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from scipy.spatial import ConvexHull, Delaunay
import ezdxf
from ezdxf.enums import TextEntityAlignment
import io
import datetime
import numpy as np

st.set_page_config(page_title="GeoDraft AI", layout="wide")

# ---------------- DXF GENERATION ---------------- #
@st.cache_data(show_spinner=False)
def create_dxf(df, x_col, y_col, z_col, group_col, label_col=None, text_scale=1.0, format_type="DXF", lw_boundary=50, lw_plot=25, lw_text=13, lw_dim=13):
    doc = ezdxf.new('R2010')
    doc.header['$INSUNITS'] = 6  # meters
    
    if "SIMPLEX" not in doc.styles:
        doc.styles.add("SIMPLEX", font="simplex.shx")

    msp = doc.modelspace()

    # Data Cleanliness: Deduplicate data to prevent overlapping entities
    df = df.drop_duplicates(subset=[x_col, y_col])

    # Professional Layers - Standard CAD colors and lineweights
    for name, color, lineweight in [
        ("POINTS", 2, 30),
        ("BOUNDARY", 7, lw_boundary), 
        ("ROAD", 3, lw_boundary),
        ("PLOT", 6, lw_plot),
        ("TEXT", 4, lw_text), 
        ("SURFACE", 8, 13),
        ("BORDER", 7, 50),
        ("DIMENSIONS", 5, lw_dim), 
    ]:
        if name not in doc.layers:
            doc.layers.add(name, color=color, lineweight=lineweight)

    min_x, max_x = df[x_col].min(), df[x_col].max()
    min_y, max_y = df[y_col].min(), df[y_col].max()
    width = max_x - min_x
    height = max_y - min_y
    if width == 0: width = 10
    if height == 0: height = 10
    
    text_h = max(height * 0.02, 0.5) * text_scale

    # Object Types: Define SURVEY_POINT block for repeated elements
    if "SURVEY_POINT" not in doc.blocks:
        point_block = doc.blocks.new(name="SURVEY_POINT")
        s = text_h * 0.3
        point_block.add_line((-s, 0), (s, 0), dxfattribs={'layer': 'POINTS'})
        point_block.add_line((0, -s), (0, s), dxfattribs={'layer': 'POINTS'})
        point_block.add_circle((0, 0), radius=s*0.5, dxfattribs={'layer': 'POINTS'})

    # Border Frame and Title Block (Only for DWG export to keep DXF clean)
    if format_type == "DWG":
        offset_x = max(10, width * 0.15)
        offset_y = max(10, height * 0.15)

        border_min_x = min_x - offset_x
        border_max_x = max_x + offset_x
        border_min_y = min_y - offset_y
        border_max_y = max_y + offset_y

        # Border Frame (Polyline)
        border_pts = [
            (border_min_x, border_min_y),
            (border_max_x, border_min_y),
            (border_max_x, border_max_y),
            (border_min_x, border_max_y),
        ]
        msp.add_lwpolyline(border_pts, close=True, dxfattribs={'layer': 'BORDER'})

        # Architectural Title Block
        date_str = datetime.datetime.now().strftime("%Y-%m-%d")
        
        tb_w = max(width * 0.3, text_h * 20)
        tb_h = max(height * 0.15, text_h * 8)
        tb_x = border_max_x - tb_w
        tb_y = border_min_y + tb_h
        
        # Title Block Lines
        msp.add_lwpolyline([(tb_x, border_min_y), (tb_x, tb_y), (border_max_x, tb_y)], dxfattribs={'layer': 'BORDER'})
        msp.add_lwpolyline([(tb_x, tb_y - tb_h/3), (border_max_x, tb_y - tb_h/3)], dxfattribs={'layer': 'BORDER'})
        msp.add_lwpolyline([(tb_x, tb_y - tb_h*2/3), (border_max_x, tb_y - tb_h*2/3)], dxfattribs={'layer': 'BORDER'})

        msp.add_text("GEODRAFT AI", height=text_h * 1.5, dxfattribs={'layer': 'TEXT', 'style': 'SIMPLEX'}).set_placement(
            (tb_x + text_h, tb_y - text_h * 2)
        )
        msp.add_text(f"FORMAT: {format_type} (CAD Compatible)", height=text_h, dxfattribs={'layer': 'TEXT', 'style': 'SIMPLEX'}).set_placement(
            (tb_x + text_h, tb_y - tb_h/3 - text_h * 1.5)
        )
        msp.add_text(f"DATE: {date_str}   UNITS: METERS", height=text_h, dxfattribs={'layer': 'TEXT', 'style': 'SIMPLEX'}).set_placement(
            (tb_x + text_h, tb_y - tb_h*2/3 - text_h * 1.5)
        )

    # Points + Labels (Instancing Blocks)
    for _, row in df.iterrows():
        x, y = row[x_col], row[y_col]
        
        msp.add_blockref("SURVEY_POINT", (x, y), dxfattribs={'layer': 'POINTS'})
        
        if label_col:
            msp.add_text(
                str(row[label_col]),
                height=text_h * 0.8,
                dxfattribs={'layer': 'TEXT', 'style': 'SIMPLEX'}
            ).set_placement((x + text_h*0.5, y + text_h*0.5))

    # Boundaries and Dimensions (Only drawn for DWG export as requested)
    if format_type == "DWG" and group_col:
        for grp, gdf in df.groupby(group_col):
            if len(gdf) >= 3:
                # 1. Geometry Accuracy: Ordered valid boundary
                pts = gdf[[x_col, y_col]].values
                
                grp_lower = str(grp).lower()
                if 'road' in grp_lower:
                    grp_layer = 'ROAD'
                elif 'plot' in grp_lower:
                    grp_layer = 'PLOT'
                else:
                    grp_layer = 'BOUNDARY'
                
                # Closed polyline
                msp.add_lwpolyline(pts.tolist(), close=True, dxfattribs={'layer': grp_layer})

                # Calculate center for label
                cx, cy = pts[:, 0].mean(), pts[:, 1].mean()
                
                x_vals = pts[:, 0]
                y_vals = pts[:, 1]
                area = 0.5 * np.abs(np.dot(x_vals, np.roll(y_vals, 1)) - np.dot(y_vals, np.roll(x_vals, 1)))

                msp.add_text(
                    f"{grp}\\P AREA: {area:.2f} SQM",
                    height=text_h,
                    dxfattribs={'layer': 'TEXT', 'style': 'SIMPLEX'}
                ).set_placement((cx, cy), align=TextEntityAlignment.MIDDLE_CENTER)

                # 6. Dimensions: Accurate Segment Dimensions
                for i in range(len(pts)):
                    p1 = pts[i]
                    p2 = pts[(i + 1) % len(pts)]
                    
                    dx = p2[0] - p1[0]
                    dy = p2[1] - p1[1]
                    dist = np.hypot(dx, dy)
                    if dist < 0.001: continue
                    
                    # Determine offset direction (outward)
                    nx, ny = -dy / dist, dx / dist
                    mid_x, mid_y = (p1[0] + p2[0]) / 2, (p1[1] + p2[1]) / 2
                    if (nx * (mid_x - cx) + ny * (mid_y - cy)) < 0:
                        nx, ny = -nx, -ny
                        
                    offset_dist = text_h * 1.5
                    # ezdxf add_aligned_dim requires distance property instead of base in some configurations.
                    # By passing 'distance', it offsets the line by that amount.
                    try:
                        msp.add_aligned_dim(
                            p1=(p1[0], p1[1]),
                            p2=(p2[0], p2[1]),
                            distance=offset_dist,
                            dxfattribs={'layer': 'DIMENSIONS'},
                            override={"dimtxsty": "SIMPLEX", "dimtxt": text_h * 0.8}
                        ).render()
                    except Exception:
                        pass

    # 3D Surface (Only drawn for DWG export)
    if format_type == "DWG" and z_col and len(df) >= 3:
        pts2d = df[[x_col, y_col]].values
        tri = Delaunay(pts2d)

        mesh = msp.add_mesh(dxfattribs={'layer': 'SURFACE'})
        with mesh.edit_data() as md:
            md.vertices = df[[x_col, y_col, z_col]].values.tolist()
            md.faces = tri.simplices.tolist()

    # Center the viewport so the user sees the drawing immediately when opening
    doc.set_modelspace_vport(
        height=height * 2.0,
        center=(min_x + width / 2, min_y + height / 2)
    )

    # ✅ FIXED: Use ezdxf's native saveas with a safe temporary file
    import tempfile
    import os
    
    fd, temp_path = tempfile.mkstemp(suffix=".dxf")
    os.close(fd)  # Close the file descriptor so ezdxf can write to it on Windows
    
    try:
        doc.saveas(temp_path)
        with open(temp_path, "rb") as f:
            dxf_bytes = f.read()
    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)
            
    return dxf_bytes

# ---------------- UI ---------------- #

st.title("GeoDraft AI")

uploaded_file = st.file_uploader("Upload CSV", type=["csv"])

if uploaded_file:
    df = pd.read_csv(uploaded_file)

    st.subheader("Select Columns")
    cols = df.columns.tolist()

    x_col = st.selectbox("X", cols)
    y_col = st.selectbox("Y", cols)
    z_col = st.selectbox("Z (optional)", ["None"] + cols)
    grp_col = st.selectbox("Group (optional)", ["None"] + cols)
    label_col = st.selectbox("Label (optional)", ["None"] + cols)

    z_col = None if z_col == "None" else z_col
    grp_col = None if grp_col == "None" else grp_col
    label_col = None if label_col == "None" else label_col

    # Ensure coordinates are numeric (handles string-based CSV issues)
    df[x_col] = pd.to_numeric(df[x_col], errors='coerce').fillna(0)
    df[y_col] = pd.to_numeric(df[y_col], errors='coerce').fillna(0)
    if z_col:
        df[z_col] = pd.to_numeric(df[z_col], errors='coerce').fillna(0)

    if "Include" not in df.columns:
        df["Include"] = True
        
    if "Sort_Order" not in df.columns:
        df["Sort_Order"] = range(1, len(df) + 1)

    st.subheader("Edit Data")
    st.markdown("Toggle `Include` to remove points, or edit `Sort_Order` to change how the boundary lines connect them.")
    df_edit = st.data_editor(df, num_rows="dynamic")

    df_valid = df_edit[df_edit["Include"] == True].sort_values(by="Sort_Order")

    if len(df_valid) > 0:
        st.subheader("Preview")

        fig = go.Figure()

        fig.add_trace(go.Scatter(
            x=df_valid[x_col],
            y=df_valid[y_col],
            mode="markers+text",
            text=[f"({x:.1f},{y:.1f})" for x, y in zip(df_valid[x_col], df_valid[y_col])],
            textposition="top center"
        ))

        st.plotly_chart(fig, use_container_width=True)

        st.subheader("Generate File")

        with st.expander("Advanced CAD Settings (Optional)"):
            st.markdown("Customize layer lineweights and scales for the DXF export.")
            text_scale = st.slider("Text & Marker Scale", 0.1, 3.0, 1.0, 0.1)
            lw_boundary = st.selectbox("Boundary/Road Lineweight", [13, 25, 30, 50, 70], index=3, format_func=lambda x: f"{x/100}mm")
            lw_plot = st.selectbox("Internal Plot Lineweight", [13, 25, 30, 50], index=1, format_func=lambda x: f"{x/100}mm")
            lw_text = st.selectbox("Text Lineweight", [13, 25, 30, 50], index=0, format_func=lambda x: f"{x/100}mm")
            lw_dim = st.selectbox("Dimensions Lineweight", [13, 25, 30, 50], index=0, format_func=lambda x: f"{x/100}mm")

        output_format = st.radio("Select Output Format:", ["DXF", "DWG"], horizontal=True)

        dxf_data = create_dxf(df_valid, x_col, y_col, z_col, grp_col, label_col, text_scale, output_format, lw_boundary, lw_plot, lw_text, lw_dim)

        # Note: We must always output a .dxf extension because Python's ezdxf library
        # generates DXF bytes. If we rename it to .dwg, AutoCAD will reject the file format.
        file_extension = ".dxf"
        file_name = f"geodraft_export{file_extension}"

        # Create a ZIP file in memory to bypass strict browser download filters
        import zipfile
        import io
        
        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zip_file:
            zip_file.writestr(file_name, dxf_data)
        zip_bytes = zip_buffer.getvalue()

        button_label = "Download DXF" if output_format == "DXF" else "Download DWG (AutoCAD Compatible DXF)"

        col1, col2 = st.columns(2)
        with col1:
            st.download_button(
                button_label,
                data=dxf_data,
                file_name=file_name,
                mime="application/octet-stream"
            )
        with col2:
            st.download_button(
                f"Download {output_format} as ZIP",
                data=zip_bytes,
                file_name=f"geodraft_export_{output_format.lower()}.zip",
                mime="application/zip"
            )