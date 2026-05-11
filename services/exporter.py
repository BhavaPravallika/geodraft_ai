"""
services/exporter.py
Handles the final export logic, packaging files and generating export metadata.
"""
import io
import zipfile
import datetime

class Exporter:
    @staticmethod
    def package_export(dxf_bytes, base_name="GeoDraft_Export", format_type="DXF"):
        """
        Packages the DXF bytes into the requested format (DXF or ZIP).
        Currently supports pure DXF. DWG requires external converters so we provide DXF optimized for DWG import.
        """
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{base_name}_{timestamp}.dxf"
        
        if format_type == "ZIP":
            zip_buffer = io.BytesIO()
            with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zip_file:
                zip_file.writestr(filename, dxf_bytes)
            return zip_buffer.getvalue(), f"{base_name}_{timestamp}.zip", "application/zip"
            
        return dxf_bytes, filename, "application/dxf"
