import json
import os

script_dir = os.path.dirname(os.path.abspath(__file__))
with open(os.path.join(script_dir, 'buildings_usc_expanded.json'), 'r', encoding='utf-8') as f:
    osm_data = json.load(f)

print(f"Total elements in expanded file: {len(osm_data.get('elements', []))}")

features = []
for element in osm_data.get('elements', []):
    if element.get('type') == 'way' and 'geometry' in element:
        coords = [[point['lon'], point['lat']] for point in element['geometry']]
        if coords[0] != coords[-1]:
            coords.append(coords[0])
        
        feature = {
            "type": "Feature",
            "geometry": {
                "type": "Polygon",
                "coordinates": [coords]
            },
            "properties": {
                "id": element.get('id'),
                "tags": element.get('tags', {})
            }
        }
        features.append(feature)

geojson = {
    "type": "FeatureCollection",
    "features": features
}

output_file = os.path.join(script_dir, 'buildings_usc.geojson')
with open(output_file, 'w', encoding='utf-8') as f:
    json.dump(geojson, f, indent=2)

print(f"Converted {len(features)} buildings to GeoJSON")

