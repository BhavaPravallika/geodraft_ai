"""
services/data_loader.py
Handles robust file ingestion, supporting CSV, XLSX, and TXT files.
Extracts dataset metadata like row count and size.
"""
import pandas as pd
from core.config import SUPPORTED_FORMATS

class DataLoader:
    @staticmethod
    def load(file_buffer):
        """Loads uploaded file into a Pandas DataFrame."""
        try:
            name = file_buffer.name.lower()
            if name.endswith(".csv") or name.endswith(".txt"):
                df = pd.read_csv(file_buffer)
            elif name.endswith(".xlsx"):
                df = pd.read_excel(file_buffer)
            else:
                raise ValueError(f"Unsupported file format. Supported: {SUPPORTED_FORMATS}")
            
            # Extract metadata
            metadata = {
                "filename": file_buffer.name,
                "size_kb": file_buffer.size / 1024,
                "rows": len(df),
                "columns": len(df.columns)
            }
            return df, metadata
        except Exception as e:
            raise RuntimeError(f"Data loading failed: {e}")
