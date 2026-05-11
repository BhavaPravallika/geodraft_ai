"""
cad_engine/geometry_builder.py
Core geometry logic for forming closed polygons, calculating areas, and generating normals.
"""
import numpy as np
import pandas as pd

class GeometryBuilder:
    @staticmethod
    def sort_points_angularly(df, x_col, y_col, group_col):
        """Centroid-Based Polar Sort to form valid closed polygons per group."""
        sorted_dfs = []
        if group_col and group_col in df.columns:
            for grp, gdf in df.groupby(group_col):
                if len(gdf) >= 3:
                    cx, cy = gdf[x_col].mean(), gdf[y_col].mean()
                    angles = np.arctan2(gdf[y_col] - cy, gdf[x_col] - cx)
                    gdf_sorted = gdf.assign(angle=angles).sort_values(by="angle").drop(columns=["angle"])
                    sorted_dfs.append(gdf_sorted)
                else:
                    sorted_dfs.append(gdf)
            return pd.concat(sorted_dfs, ignore_index=True) if sorted_dfs else df
        else:
            if len(df) >= 3:
                cx, cy = df[x_col].mean(), df[y_col].mean()
                angles = np.arctan2(df[y_col] - cy, df[x_col] - cx)
                return df.assign(angle=angles).sort_values(by="angle").drop(columns=["angle"])
            return df

    @staticmethod
    def calculate_shoelace_area(pts):
        """Calculates area of a polygon defined by an array of [x, y] coordinates."""
        x_vals, y_vals = pts[:, 0], pts[:, 1]
        area = 0.5 * np.abs(np.dot(x_vals, np.roll(y_vals, 1)) - np.dot(y_vals, np.roll(x_vals, 1)))
        return area
