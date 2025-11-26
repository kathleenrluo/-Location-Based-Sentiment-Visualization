import json
import os

# Load the buildings
script_dir = os.path.dirname(os.path.abspath(__file__))
with open(os.path.join(script_dir, 'buildings_usc.geojson'), 'r', encoding='utf-8') as f:
    data = json.load(f)

print(f"Total buildings extracted: {len(data['features'])}")

# Get bounding box
all_lons = []
all_lats = []

for feature in data['features']:
    if feature['geometry']['type'] == 'Polygon':
        coords = feature['geometry']['coordinates'][0]
        for coord in coords:
            all_lons.append(coord[0])
            all_lats.append(coord[1])

if all_lons and all_lats:
    print(f"\nCoverage area:")
    print(f"  Latitude: {min(all_lats):.6f} to {max(all_lats):.6f}")
    print(f"  Longitude: {min(all_lons):.6f} to {max(all_lons):.6f}")
    print(f"\n  Center: ({sum(all_lats)/len(all_lats):.6f}, {sum(all_lons)/len(all_lons):.6f})")
    print(f"  Span: ~{(max(all_lats) - min(all_lats)) * 111:.2f} km N-S")
    print(f"  Span: ~{(max(all_lons) - min(all_lons)) * 111 * 0.8:.2f} km E-W (at this latitude)")

