"""
cad_engine/layer_manager.py
Enforces professional CAD layer standards, utilizing config.py defaults.
"""
from core.config import CAD_LAYERS

class LayerManager:
    @staticmethod
    def setup_layers(doc):
        """Injects professional standard layers into the ezdxf document."""
        for name, properties in CAD_LAYERS.items():
            color, lineweight = properties
            if name not in doc.layers:
                doc.layers.add(name, color=color, lineweight=lineweight)

    @staticmethod
    def infer_layer(group_name):
        """Infers the appropriate CAD layer based on the group name."""
        name_lower = str(group_name).lower()
        if any(kw in name_lower for kw in ['boundary', 'main', 'outer', 'edge']):
            return 'BOUNDARY'
        elif any(kw in name_lower for kw in ['plot', 'lot', 'subdivision']):
            return 'PLOT'
        elif any(kw in name_lower for kw in ['road', 'street', 'path']):
            return 'ROAD'
        return 'DEFAULT'
