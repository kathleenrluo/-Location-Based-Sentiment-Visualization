# Data Directory

This directory contains all data files and processing scripts for the sentiment visualization project.

## Data Files

### Processed Data (for web application)
- **intervals.json**: Time-stamped location visits with sentiment scores (2 weeks of synthetic data)
- **locations.json**: Key location coordinates (home, library, gym, etc.)
- **buildings_usc.geojson**: Building footprint polygons for USC area (~76k buildings)

### Source Data
- **buildings_usc.json**: Raw OpenStreetMap building data (OSM format)
- **buildings_usc_expanded.json**: Expanded OSM data (4km radius)

## Processing Scripts

- **generate_intervals_with_routes.py**: Main script to generate interval data with real Mapbox routes
- **filter_buildings.py**: Filter buildings to smaller radius for better performance

## Usage

### Generate/Regenerate Data

```bash
cd data
python generate_intervals_with_routes.py
```

This will:
1. Generate synthetic 2-week interval data with real Mapbox route paths
2. Save `intervals.json` to the `data/` directory
3. Copy to `public/` for the web application

### Filter Buildings (Performance)

To reduce building count for faster loading:
```bash
cd data
python filter_buildings.py
# This creates buildings_usc_filtered.geojson (1km radius, ~1,093 buildings)
```

### Copy to Web App

After processing, copy the following files to `public/` for the web application:
- `intervals.json`
- `locations.json`
- `buildings_usc.geojson` (or `buildings_usc_filtered.geojson` for better performance)

Or use:
```bash
# From project root
cp data/intervals.json data/locations.json data/buildings_usc.geojson public/

# Or use filtered version for better performance:
cp data/buildings_usc_filtered.geojson public/buildings_usc.geojson
```

## Data Format

### intervals.json
Array of time interval objects:
```json
{
  "start_time": "2024-11-18T07:00:00",
  "end_time": "2024-11-18T08:30:00",
  "location_name": "Home",
  "location_type": "home",
  "latitude": 34.025,
  "longitude": -118.29,
  "sentiment_score": 0.08,
  "activity": "morning_routine",
  "duration_minutes": 90
}
```

### locations.json
Array of location objects:
```json
{
  "name": "Doheny Library",
  "type": "library",
  "latitude": 34.0205,
  "longitude": -118.2839,
  "address": "3550 Trousdale Parkway, Los Angeles, CA 90089",
  "has_polygon": true
}
```

### buildings_usc.geojson
Standard GeoJSON FeatureCollection with building polygons.

