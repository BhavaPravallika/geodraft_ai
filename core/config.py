"""
core/config.py
Centralized configuration system for GeoDraft AI.
Stores default settings, coordinate aliases, rendering limits, and CAD defaults.
"""

# Supported file formats
SUPPORTED_FORMATS = [".csv", ".xlsx", ".txt"]

# AI Schema Detection: Aliases for finding columns
COLUMN_ALIASES = {
    "x": ["easting", "east", "x", "x_coord", "lon", "longitude"],
    "y": ["northing", "north", "y", "y_coord", "lat", "latitude"],
    "z": ["elevation", "elev", "z", "height", "z_coord", "alt", "altitude"],
    "point_id": ["id", "point_id", "point", "pnt", "pid"],
    "layer": ["layer", "group", "code", "desc", "description", "feature", "type"],
    "label": ["label", "text", "name", "annotation"]
}

# CAD Layer Defaults (Professional CAD settings)
# Tuple: (Color Index, Lineweight)
# AutoCAD colors: 1=Red, 2=Yellow, 3=Green, 4=Cyan, 5=Blue, 6=Magenta, 7=White
CAD_LAYERS = {
    "POINTS": (2, 30),        # Yellow
    "BOUNDARY": (7, 50),      # White (thick)
    "ROAD": (3, 25),          # Green
    "PLOT": (6, 25),          # Magenta
    "TEXT": (4, 13),          # Cyan (thin)
    "DIMENSIONS": (5, 13),    # Blue (thin)
    "DEFAULT": (7, 25)        # White
}

# Rendering Settings
MAX_PREVIEW_ENTITIES = 5000  # Avoid freezing browser for massive datasets
PREVIEW_THEME = "plotly_dark"  # Engineering-style dark mode for Plotly
DEFAULT_TEXT_SCALE = 1.0

# Workflow Steps
WORKFLOW_STEPS = {
    1: "Upload Dataset",
    2: "Detect Schema",
    3: "Validate Data",
    4: "Configure CAD",
    5: "Preview CAD",
    6: "Export Files"
}
