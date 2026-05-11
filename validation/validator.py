"""
validation/validator.py
Advanced engineering-grade data validation.
Validates coordinates, duplicates, missing values, and outliers.
Returns professional warning summaries and action recommendations.
"""
import pandas as pd
import numpy as np

class Validator:
    @staticmethod
    def validate(df, schema):
        """
        Validates the dataset based on the mapped schema.
        Returns a cleaned DataFrame and a dictionary of validation results.
        """
        initial_len = len(df)
        errors = []
        warnings = []
        
        x_col = schema.get("x")
        y_col = schema.get("y")
        
        if not x_col or not y_col:
            errors.append("Critical: X and Y coordinate columns must be mapped.")
            return None, {"errors": errors, "warnings": warnings, "valid_count": 0, "invalid_count": initial_len}

        # 1. Coerce to numeric
        df_clean = df.copy()
        df_clean[x_col] = pd.to_numeric(df_clean[x_col], errors='coerce')
        df_clean[y_col] = pd.to_numeric(df_clean[y_col], errors='coerce')
        
        z_col = schema.get("z")
        if z_col and z_col != "None":
            df_clean[z_col] = pd.to_numeric(df_clean[z_col], errors='coerce')
            
        # 2. Missing values
        missing_xy = df_clean[df_clean[x_col].isna() | df_clean[y_col].isna()]
        if not missing_xy.empty:
            warnings.append(f"Dropped {len(missing_xy)} rows with missing or non-numeric X/Y coordinates.")
            df_clean = df_clean.dropna(subset=[x_col, y_col])
            
        # 3. Duplicate coordinates (Topology integrity)
        duplicates = df_clean.duplicated(subset=[x_col, y_col])
        if duplicates.sum() > 0:
            warnings.append(f"Dropped {duplicates.sum()} overlapping points (exact X,Y duplicates).")
            df_clean = df_clean.drop_duplicates(subset=[x_col, y_col])
            
        # 4. Outlier detection (Z-score heuristic)
        if len(df_clean) > 5:
            zx = np.abs((df_clean[x_col] - df_clean[x_col].mean()) / df_clean[x_col].std())
            zy = np.abs((df_clean[y_col] - df_clean[y_col].mean()) / df_clean[y_col].std())
            outliers = (zx > 3) | (zy > 3)
            if outliers.sum() > 0:
                warnings.append(f"Detected {outliers.sum()} spatial outliers (>3 std dev). Please review preview carefully.")
        
        final_len = len(df_clean)
        invalid_count = initial_len - final_len
        
        summary = {
            "errors": errors,
            "warnings": warnings,
            "valid_count": final_len,
            "invalid_count": invalid_count,
            "x_range": [float(df_clean[x_col].min()), float(df_clean[x_col].max())] if final_len > 0 else [0,0],
            "y_range": [float(df_clean[y_col].min()), float(df_clean[y_col].max())] if final_len > 0 else [0,0]
        }
        
        return df_clean, summary
