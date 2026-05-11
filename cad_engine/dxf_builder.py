"""
cad_engine/dxf_builder.py
High-performance DXF generation engine utilizing ezdxf.
Handles scaled geometry, polyline drafting, annotations, and dimensional rendering.
"""
import ezdxf
from ezdxf.enums import TextEntityAlignment
import numpy as np
import tempfile
import os
import time
import pandas as pd

from .layer_manager import LayerManager
from .geometry_builder import GeometryBuilder
from core.state_manager import StateManager
from services.logger import logger

class DXFBuilder:
    @staticmethod
    def build(df, schema, settings):
        """
        Builds the DXF document from the dataframe.
        Returns the DXF binary data and metadata.
        """
        start_time = time.time()
        
        doc = ezdxf.new('R2010')
        doc.header['$INSUNITS'] = 6  # meters
        
        if "SIMPLEX" not in doc.styles:
            doc.styles.add("SIMPLEX", font="simplex.shx")

        msp = doc.modelspace()
        LayerManager.setup_layers(doc)

        x_col = schema.get("x")
        y_col = schema.get("y")
        grp_col = schema.get("layer")
        label_col = schema.get("label")
        
        text_scale = settings.get("text_scale", 1.0)
        show_boundary = settings.get("show_boundary", True)
        
        if len(df) == 0:
            return doc.encode('utf-8'), {"entities": 0, "time_sec": 0}

        min_x, max_x = df[x_col].min(), df[x_col].max()
        min_y, max_y = df[y_col].min(), df[y_col].max()
        width = max_x - min_x
        height = max_y - min_y
        if width == 0: width = 10
        if height == 0: height = 10
        
        text_h = max(height * 0.02, 0.5) * text_scale
        entity_count = 0

        # Define block
        if "SURVEY_POINT" not in doc.blocks:
            point_block = doc.blocks.new(name="SURVEY_POINT")
            s = text_h * 0.3
            point_block.add_line((-s, 0), (s, 0), dxfattribs={'layer': 'POINTS'})
            point_block.add_line((0, -s), (0, s), dxfattribs={'layer': 'POINTS'})
            point_block.add_circle((0, 0), radius=s*0.5, dxfattribs={'layer': 'POINTS'})

        # 1. Plot Points & Labels
        for _, row in df.iterrows():
            x, y = row[x_col], row[y_col]
            msp.add_blockref("SURVEY_POINT", (x, y), dxfattribs={'layer': 'POINTS'})
            entity_count += 1
            
            if label_col and label_col in df.columns and pd.notna(row[label_col]):
                label_text = str(row[label_col])
                msp.add_text(
                    label_text,
                    height=text_h * 0.8,
                    dxfattribs={'layer': 'TEXT', 'style': 'SIMPLEX'}
                ).set_placement((x + text_h*0.5, y + text_h*0.5))
                entity_count += 1

        # 2. Geometry Construction
        if show_boundary and grp_col and grp_col in df.columns:
            for grp, gdf in df.groupby(grp_col):
                if len(gdf) >= 3:
                    pts = gdf[[x_col, y_col]].values
                    grp_layer = LayerManager.infer_layer(grp)
                    
                    msp.add_lwpolyline(pts.tolist(), close=True, dxfattribs={'layer': grp_layer})
                    entity_count += 1

                    # Area calculation
                    cx, cy = pts[:, 0].mean(), pts[:, 1].mean()
                    area = GeometryBuilder.calculate_shoelace_area(pts)

                    msp.add_text(
                        f"{grp}\\P AREA: {area:.2f} SQM",
                        height=text_h,
                        dxfattribs={'layer': 'TEXT', 'style': 'SIMPLEX'}
                    ).set_placement((cx, cy), align=TextEntityAlignment.MIDDLE_CENTER)
                    entity_count += 1

                    # Dimensions
                    for i in range(len(pts)):
                        p1 = pts[i]
                        p2 = pts[(i + 1) % len(pts)]
                        
                        dx, dy = p2[0] - p1[0], p2[1] - p1[1]
                        dist = np.hypot(dx, dy)
                        if dist < 0.001: continue
                        
                        nx, ny = -dy / dist, dx / dist
                        mid_x, mid_y = (p1[0] + p2[0]) / 2, (p1[1] + p2[1]) / 2
                        if (nx * (mid_x - cx) + ny * (mid_y - cy)) < 0:
                            nx, ny = -nx, -ny
                            
                        try:
                            msp.add_aligned_dim(
                                p1=(p1[0], p1[1]),
                                p2=(p2[0], p2[1]),
                                distance=text_h * 1.5,
                                dxfattribs={'layer': 'DIMENSIONS'},
                                override={"dimtxsty": "SIMPLEX", "dimtxt": text_h * 0.8}
                            ).render()
                            entity_count += 1
                        except Exception as e:
                            logger.warning(f"Failed to render dimension: {e}")

        # Finalize Viewport
        doc.set_modelspace_vport(
            height=height * 2.0,
            center=(min_x + width / 2, min_y + height / 2)
        )

        fd, temp_path = tempfile.mkstemp(suffix=".dxf")
        os.close(fd)
        try:
            doc.saveas(temp_path)
            with open(temp_path, "rb") as f:
                dxf_bytes = f.read()
        finally:
            if os.path.exists(temp_path):
                os.remove(temp_path)
                
        elapsed = time.time() - start_time
        logger.info(f"DXF generated successfully. {entity_count} entities in {elapsed:.2f}s.")
        
        metadata = {
            "entities": entity_count,
            "time_sec": round(elapsed, 2),
            "layers_used": len(doc.layers)
        }
                
        return dxf_bytes, metadata
