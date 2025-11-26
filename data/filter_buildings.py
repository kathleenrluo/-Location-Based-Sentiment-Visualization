"""
Filter buildings to a smaller radius around USC for better performance
"""
import json
import os

def filter_buildings_by_radius(input_file, output_file, center_lat, center_lon, radius_km=1.0):
    """
    Filter buildings to only include those within radius_km of center point
    
    Args:
        input_file: Path to input GeoJSON file
        output_file: Path to output GeoJSON file
        center_lat: Center latitude
        center_lon: Center longitude
        radius_km: Radius in kilometers (default 1km)
    """
    print(f"Loading buildings from {input_file}...")
    with open(input_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # Convert radius from km to degrees (approximate)
    # At USC latitude (~34°), 1 degree ≈ 111 km
    radius_deg = radius_km / 111.0
    
    print(f"Filtering buildings within {radius_km}km of ({center_lat}, {center_lon})...")
    
    filtered_features = []
    for feature in data['features']:
        if feature['geometry']['type'] == 'Polygon':
            # Get building center (average of first few coordinates)
            coords = feature['geometry']['coordinates'][0]
            if len(coords) > 0:
                # Sample first few points for center calculation
                sample_size = min(10, len(coords))
                sum_lon = sum(c[0] for c in coords[:sample_size])
                sum_lat = sum(c[1] for c in coords[:sample_size])
                building_lon = sum_lon / sample_size
                building_lat = sum_lat / sample_size
                
                # Simple distance check (Euclidean in lat/lon space)
                d_lat = building_lat - center_lat
                d_lon = building_lon - center_lon
                distance_sq = d_lat * d_lat + d_lon * d_lon
                
                if distance_sq <= radius_deg * radius_deg:
                    filtered_features.append(feature)
    
    output_data = {
        "type": "FeatureCollection",
        "features": filtered_features
    }
    
    print(f"Writing {len(filtered_features)} buildings to {output_file}...")
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(output_data, f, indent=2)
    
    print(f"Filtered from {len(data['features'])} to {len(filtered_features)} buildings")
    print(f"Reduction: {((1 - len(filtered_features) / len(data['features'])) * 100):.1f}%")

if __name__ == "__main__":
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    # USC coordinates
    usc_lat = 34.0224
    usc_lon = -118.2851
    
    # Filter to 1.3km radius (expanded from 1km)
    input_file = os.path.join(script_dir, 'buildings_usc.geojson')
    output_file = os.path.join(script_dir, 'buildings_usc_filtered.geojson')
    
    filter_buildings_by_radius(input_file, output_file, usc_lat, usc_lon, radius_km=1.3)
    
    print(f"\nFiltered building file saved to: {output_file}")
    print("Copy this file to public/buildings_usc.geojson to use it in the app")

