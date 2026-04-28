import pandas as pd
from app import create_dxf

def test_dxf():
    df = pd.read_csv('dummy_data.csv')
    df['Include'] = True
    
    # Ensure numeric
    df['Easting'] = pd.to_numeric(df['Easting'])
    df['Northing'] = pd.to_numeric(df['Northing'])
    df['Elevation'] = pd.to_numeric(df['Elevation'])
    
    try:
        data = create_dxf(df, 'Easting', 'Northing', 'Elevation', 'Category')
        print(f"DXF created successfully. Size: {len(data)} bytes")
        with open("test_output.dxf", "wb") as f:
            f.write(data)
        print("Wrote to test_output.dxf")
    except Exception as e:
        print(f"Error creating DXF: {e}")

if __name__ == "__main__":
    test_dxf()
