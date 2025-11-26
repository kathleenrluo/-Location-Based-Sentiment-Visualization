# Data Requirements Checklist

## What You Need to Provide

### 1. **Building Footprint Data (Polygons)**
   - **Format**: GeoJSON or Shapefile
   - **Coverage**: USC campus and surrounding area (approximately 1-2 mile radius)
   - **Sources**:
     - OpenStreetMap (OSM) - can extract via Overpass API
     - Los Angeles Open Data Portal
     - USC GIS data (if available)
   - **What we need**: Building polygons with coordinates (lat/lon pairs forming closed polygons)
   - **Priority**: High - needed for the striped room/building visualizations

### 2. **Location Coordinates (GPS Points)**
   - **Format**: JSON or CSV with columns: `location_name`, `latitude`, `longitude`, `location_type`
   - **Locations needed**:
     - Home/apartment (off-campus or on-campus)
     - Library (Doheny, Leavey, etc.)
     - Gym (USC gym or nearby)
     - Classrooms (2-3 different buildings)
     - Grocery store (Ralph's, Trader Joe's, etc.)
     - Restaurants (2-3 different places)
     - Friend's house
     - Coffee shops (optional)
   - **How to get**: 
     - Google Maps (right-click → coordinates)
     - OpenStreetMap
     - GPS coordinates from your phone
   - **Priority**: High - needed for all location-based features

### 3. **Location Type Metadata** (Optional but helpful)
   - For each location, specify:
     - `location_name`: e.g., "Doheny Library"
     - `location_type`: e.g., "library", "home", "gym", "classroom", "restaurant", "grocery", "friend_house"
     - `has_building_polygon`: boolean (whether we have building footprint data)
   - **Priority**: Medium - helps with better visualization

---

## What I Can Generate (Synthetic Data)

Once you provide the above, I can generate:

### 1. **Time Interval Data (2 weeks)**
   - **Format**: JSON array of intervals
   - **Fields per interval**:
     ```json
     {
       "start_time": "2024-01-15T08:00:00Z",
       "end_time": "2024-01-15T10:30:00Z",
       "location_name": "Doheny Library",
       "latitude": 34.0206,
       "longitude": -118.2854,
       "sentiment_score": 0.65,  // -1 (very negative) to +1 (very positive)
       "activity": "studying",
       "duration_minutes": 150
     }
     ```
   - **Realistic patterns**:
     - Sleep at home (11pm-7am) - calm/neutral sentiment
     - Morning routine - varies
     - Classes - mixed (stressed during exams, neutral otherwise)
     - Library study sessions - stressed during finals, calm otherwise
     - Gym - stressed during workout, positive after
     - Social time - generally positive
     - Grocery shopping - neutral
     - Eating out - positive

### 2. **Sentiment Score Distribution**
   - Realistic sentiment ranges per activity:
     - Sleep: 0.3 to 0.7 (calm)
     - Studying: -0.2 to 0.4 (varies by stress level)
     - Gym: -0.3 to 0.8 (stressed during, positive after)
     - Social: 0.4 to 0.9 (positive)
     - Eating: 0.2 to 0.7 (positive)
     - Classes: -0.1 to 0.3 (neutral to slightly stressed)

---

## Minimum to Get Started

**You can start with just:**
1. ✅ **GPS coordinates for 8-10 key locations** (can get from Google Maps in 10 minutes)
2. ✅ **Basic building footprint data** (can extract from OpenStreetMap)

**I can then:**
- Generate all synthetic time interval data
- Create realistic 2-week patterns
- Build the visualization system

---

## Recommended Data Sources

### For Building Footprints:
1. **OpenStreetMap Overpass API** (Free, easiest)
   - Query: `[out:json][timeout:25];(way["building"](around:2000,34.0224,-118.2851););out geom;`
   - Area: USC campus coordinates (34.0224°N, 118.2851°W)

2. **Los Angeles GeoHub** (Free)
   - https://geohub.lacity.org/
   - Search for "building footprints"

3. **USC GIS Resources** (If you have access)
   - Check USC library GIS resources

### For GPS Coordinates:
1. **Google Maps** (Easiest)
   - Right-click on location → "What's here?" → shows coordinates
   - Or use Google Maps URL: `https://www.google.com/maps/@34.0224,-118.2851,17z`

2. **OpenStreetMap Nominatim API** (Free)
   - Search for "USC Doheny Library" → get coordinates

---

## Data Format I'll Expect

Once you have the data, provide it as:

### `locations.json`:
```json
[
  {
    "name": "Doheny Library",
    "type": "library",
    "latitude": 34.0206,
    "longitude": -118.2854,
    "has_polygon": true
  },
  {
    "name": "Home",
    "type": "home",
    "latitude": 34.0250,
    "longitude": -118.2800,
    "has_polygon": false
  }
]
```

### `buildings.geojson`:
```json
{
  "type": "FeatureCollection",
  "features": [
    {
      "type": "Feature",
      "geometry": {
        "type": "Polygon",
        "coordinates": [[[-118.2854, 34.0206], ...]]
      },
      "properties": {
        "name": "Doheny Library"
      }
    }
  ]
}
```

---

## Quick Start Option

**If you want to get started immediately:**
1. Give me 8-10 location names and I can look up approximate coordinates
2. I can generate synthetic building polygons (simple rectangles) for demo purposes
3. We can refine with real data later

**Would you like me to:**
- A) Wait for you to gather real data (more accurate, better demo)
- B) Start with synthetic/approximate data now (faster start, can refine later)

