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

- **process_data.py**: Main script to generate synthetic interval data and convert OSM to GeoJSON
- **convert_expanded.py**: Convert expanded OSM building data to GeoJSON
- **check_buildings.py**: Utility to check building data coverage

## Usage

### Generate/Regenerate Data

```bash
cd data
python process_data.py
```

This will:
1. Convert OSM building data to GeoJSON format
2. Generate synthetic 2-week interval data
3. Save files to the `data/` directory

### Copy to Web App

After processing, copy the following files to `public/` for the web application:
- `intervals.json`
- `locations.json`
- `buildings_usc.geojson`

Or use:
```bash
# From project root
cp data/intervals.json data/locations.json data/buildings_usc.geojson public/
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

