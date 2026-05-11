"""
services/schema_detector.py
Intelligent schema detection using heuristics and aliases to automatically map columns.
"""
from core.config import COLUMN_ALIASES

class SchemaDetector:
    @staticmethod
    def detect(columns):
        """
        Attempts to automatically detect X, Y, Z, Point ID, Layer, and Label columns.
        Returns a mapping and a confidence score.
        """
        mapping = {
            "x": None,
            "y": None,
            "z": None,
            "point_id": None,
            "layer": None,
            "label": None
        }
        
        confidence = 0
        total_expected = 4 # X, Y are mandatory, ID and Layer are good to have
        
        cols_lower = [str(c).lower().strip() for c in columns]
        
        for key, aliases in COLUMN_ALIASES.items():
            for i, col in enumerate(cols_lower):
                if col in aliases or any(alias in col for alias in aliases):
                    mapping[key] = columns[i]
                    confidence += 1
                    break
                    
        # Score calculation
        score_percentage = min(100, int((confidence / total_expected) * 100))
        
        # Smart suggestions: If X and Y are missing but there are exactly 2 numeric columns,
        # we can suggest them, but for now we rely on aliases.
        
        return mapping, score_percentage
