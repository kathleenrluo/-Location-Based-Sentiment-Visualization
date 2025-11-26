# Development Log

This document tracks the development process, decisions, and problem-solving for the sentiment visualization project.

## Project Overview
Building a Vue.js web application to visualize location-based sentiment data with:
- Daily Mode: 24-hour timeline with per-interval sentiment dots
- Lifetime Mode: Multi-day aggregation with time-of-day bucketing
- Striped dots/polygons for overlapping intervals
- Interactive hover expansions and tooltips

---

## Phase 1: Data Preparation

### Step 1.1: Building Footprint Extraction
**Date**: Initial setup
**Action**: Extracted building footprints from OpenStreetMap using Overpass API
- Initial extraction: 2000m radius around USC (34.0224, -118.2851)
- Result: 15,555 buildings covering ~4km x 4km area
- Expanded extraction: 4000m radius for more complete map coverage
- **Status**: ✅ Complete

### Step 1.2: Location Coordinates
**Action**: Collected GPS coordinates for key locations
- Doheny Library: 34.0205, -118.2839
- Lyon Center (gym): 34.0219, -118.2871
- Ralphs (grocery): 34.0256, -118.2845
- Home & Friend's house: West side residential area
- Classrooms, restaurants: USC campus locations
- **Status**: ✅ Complete

### Step 1.3: Synthetic Data Generation
**Action**: Generated 2 weeks of realistic student activity data
- 107 time intervals from Nov 18 - Dec 1, 2024
- Includes: sleep, classes, studying, gym, social, eating, grocery shopping
- Realistic sentiment ranges per activity type
- **Status**: ✅ Complete

---

## Directory Organization

### Reorganization (Latest)
**Date**: Project organization
**Action**: Organized project structure for better maintainability
- Created `data/` folder for all data files and processing scripts
- Created `docs/` folder for documentation files
- Moved source data files to `data/`
- Moved documentation to `docs/`
- Updated Python scripts to use relative paths from `data/` directory
- Updated README to reflect new structure
- **Status**: ✅ Complete

**New Structure**:
- `data/`: Source data files and processing scripts
- `docs/`: All project documentation
- `public/`: Data files served to web application
- `src/`: Application source code

---

## Phase 2: Project Setup

### Step 2.1: Vue.js Project Initialization
**Date**: Initial setup
**Action**: Created Vue.js project structure manually
- Created `package.json` with dependencies: Vue 3, deck.gl, Mapbox GL, Bootstrap
- Set up Vite as build tool
- Created basic project structure: `src/`, `public/`, `components/`, `utils/`
- **Status**: ✅ Complete

### Step 2.2: Core Application Files
**Action**: Created base application files
- `index.html`: Main HTML template with Bootstrap and Mapbox CSS
- `src/main.js`: Vue app initialization
- `src/App.vue`: Root component
- `vite.config.js`: Vite configuration
- **Status**: ✅ Complete

### Step 2.3: Data Utilities
**Action**: Created data loading and processing utilities
- `src/utils/dataLoader.js`: Functions for loading intervals, locations, buildings
- Functions for filtering, grouping, and aggregating data
- Sentiment color mapping utilities
- **Status**: ✅ Complete

### Step 2.4: Map Component - Basic Setup
**Action**: Created MapVisualization component with basic map
- Integrated Mapbox GL JS for base map
- Integrated deck.gl for data visualization layers
- Added view mode toggle (Daily/Lifetime)
- Added 24-hour timeline slider for Daily mode
- **Status**: ✅ Complete

### Step 2.5: Data Loading and Display
**Action**: Implemented data loading and basic visualization
- Load intervals, locations, and building data on mount
- Created computed layers for deck.gl
- Implemented ScatterplotLayer for sentiment dots
- Implemented PolygonLayer for building footprints
- Added filtering by time window in Daily mode
- Added aggregation by time buckets in Lifetime mode
- **Status**: ✅ Complete

### Step 2.6: Data Files Setup
**Action**: Copied data files to public directory
- Moved `intervals.json`, `locations.json`, `buildings_usc.geojson` to `public/`
- Expanded building data: 76,396 buildings covering larger USC area
- **Status**: ✅ Complete

### Step 2.7: README Documentation
**Action**: Created comprehensive README
- Installation instructions
- Usage guide for both view modes
- Troubleshooting section
- Project structure documentation
- **Status**: ✅ Complete

### Step 2.8: Project Configuration
**Action**: Final setup tasks
- Created `.gitignore` file
- Installed all npm dependencies
- Verified data files in `public/` directory
- **Status**: ✅ Complete

### Step 2.9: Directory Organization
**Action**: Organized project structure
- Created `data/` folder for source data and processing scripts
- Created `docs/` folder for all documentation
- Moved data files to `data/` directory
- Moved documentation to `docs/` directory
- Updated Python scripts to use relative paths
- Created README files in `data/` and `docs/` directories
- Updated main README with new structure
- **Status**: ✅ Complete

---

## Phase 3: Feature Implementation (In Progress)

### Step 3.1: Basic Sentiment Dots
**Status**: ✅ Complete - Basic dots showing with sentiment colors

### Step 3.2: Striped Dots for Clusters
**Status**: ✅ Complete - Implemented striped dot visualization
- Created `stripedVisualization.js` utility for striped dot data
- Multiple intervals at same location show as overlapping colored circles
- Click to expand clusters - shows individual interval dots in circular pattern
- Collapsed view shows striped pattern with slight offsets

### Step 3.3: Hover Interactions & Tooltips
**Status**: ✅ Complete - Full hover and tooltip system implemented
- Created `Tooltip.vue` component for displaying detailed information
- Hover over dots shows location name, sentiment, duration, activity
- Tooltip positioned dynamically based on mouse coordinates
- Supports both single interval and aggregated interval displays
- Click on striped dots to expand/collapse cluster view

### Step 3.4: Building Color Coding & Striped Buildings
**Status**: ✅ Complete - Buildings colored by sentiment with striped support
- Buildings colored by average sentiment of nearby intervals
- Updated `getBuildingSentiment()` to return both sentiment and intervals
- Striped buildings for multiple time intervals (Daily mode)
- Multiple time buckets render as overlapping semi-transparent layers
- Single-sentiment buildings render as solid colored polygons

### Step 3.5: Travel Path Visualization
**Status**: ✅ Complete - PathLayer shows lines between consecutive location visits

### Step 3.6: Fixed-Size Dots
**Status**: ✅ Complete - All sentiment dots use fixed 8px radius

### Step 3.7: Removed Timeline Slider
**Status**: ✅ Complete - Removed from Daily mode per user feedback

---

## Known Issues & Solutions

### Issue 1: Building Data File Size
**Problem**: `buildings_usc.geojson` is very large (~76k buildings)
**Solution**: File loads successfully, but may need optimization for slower connections
**Status**: Monitoring performance

### Issue 2: Mapbox Token
**Current**: Using public demo token
**Note**: For production, should use own Mapbox token
**Status**: Works for development

### Issue 3: Timeline Slider Not Useful
**Problem**: User feedback - Timeline slider doesn't make sense since dots are aggregated daily
**Solution**: Removed timeline slider from Daily mode
**Date**: User feedback session
**Status**: ✅ Fixed - Removed timeline slider UI and related filtering logic

### Issue 4: Dot Sizes Too Large
**Problem**: User feedback - Dots based on duration are too large and confusing
**Solution**: Changed to fixed-size dots (8 pixels) showing aggregate sentiment value
**Date**: User feedback session
**Status**: ✅ Fixed - All dots now use fixed radius of 8 pixels

### Issue 5: Building Colors Not Visible
**Problem**: User feedback - Buildings not color-coded by sentiment
**Solution**: Implemented building sentiment calculation based on nearby intervals
- Added `getBuildingSentiment()` function to find intervals within ~22 meters of building center
- Buildings now colored by average sentiment of nearby intervals
- Buildings without sentiment data remain gray
**Date**: User feedback session
**Status**: ✅ Fixed - Buildings now show sentiment colors

### Issue 6: Travel Lines Not Visible
**Problem**: User feedback - Lines between locations not showing
**Solution**: Implemented PathLayer to visualize travel between consecutive intervals
- Added `createTravelPaths()` function to generate path segments
- Paths connect consecutive intervals at different locations
- Gray lines with 2px width
**Date**: User feedback session
**Status**: ✅ Fixed - Travel paths now visible between locations

### Issue 7: Performance - Very Slow Rendering
**Problem**: User feedback - White screen after loading, buildings flash briefly, extremely slow rendering
**Root Cause**: 
- Calculating sentiment for all 76,396 buildings on every render
- Expensive haversine distance calculations for every building-interval pair
- Recreating layer objects on every computed property evaluation
**Solution**: 
- Pre-calculate building sentiment once when data loads (not on every render)
- Optimized distance calculation (simple Euclidean instead of haversine for small distances)
- Only render buildings that have sentiment data (much fewer buildings)
- Show all buildings as light gray outlines for context
- Use deck.gl's `updateTriggers` to prevent unnecessary recalculations
- Process buildings in batches to avoid blocking UI
**Date**: Performance optimization
**Status**: ✅ Fixed - Significant performance improvement

### Issue 8: Still Too Many Buildings - Load Time
**Problem**: User feedback - Still taking too long to load even with optimizations
**Solution**: 
- Created `filter_buildings.py` script to filter buildings by radius
- Reduced from 76,396 buildings to 1,093 buildings (1km radius instead of 4km)
- 98.6% reduction in building count
- Much faster loading and rendering
**Date**: Further performance optimization
**Status**: ✅ Fixed - Reduced to 1km radius around USC

### Issue 9: Mapbox 403 Errors - Invalid Token
**Problem**: User feedback - 403 errors on map tiles, everything disappears on zoom
**Root Cause**: Using hardcoded demo Mapbox token that's invalid/expired
**Solution**: 
- User provided valid Mapbox token
- Restored Mapbox integration with user's token
- Fixed layer persistence on zoom by always including layers in viewState updates
- Throttled render event updates for better performance
**Date**: Token issue resolution
**Status**: ✅ Fixed - Using user's Mapbox token, layers persist on zoom

### Issue 10: Mapbox Hidden Behind Layers
**Problem**: User feedback - Mapbox completely hidden, can't see base map
**Solution**: 
- Made building layers semi-transparent (opacity 0.4-0.5)
- Reduced fill color alpha values
- Mapbox base map now visible through transparent layers
**Date**: Visibility fix
**Status**: ✅ Fixed - Mapbox visible through semi-transparent layers

### Issue 11: Expand Building Radius
**Problem**: User request - Expand building coverage area
**Solution**: 
- Increased radius from 1.0km to 1.3km (1.3x expansion)
- Now includes 2,690 buildings (up from 1,093)
- Better coverage of USC area and surroundings
**Date**: Radius expansion
**Status**: ✅ Fixed - Expanded to 1.3km radius

---

## Phase 4: Time-Increment Data & Timeline Features

### Step 4.1: Time-Increment Data Format
**Date**: Latest update
**Action**: Refactored data structure from intervals to 5-minute time increments
- Created `generate_increments.py` to generate time-increment data
- Each increment includes: timestamp, location, sentiment, activity, is_traveling flag
- Enables more granular tracking of location and sentiment changes
- **Status**: ✅ Complete

### Step 4.2: Timeline Slider Implementation
**Action**: Added interactive timeline slider for navigating through the day
- Created `TimelineSlider.vue` component
- Shows current time and "you are here" indicator
- Allows scrubbing through the day to see path unfold
- **Status**: ✅ Complete

### Step 4.3: Travel Path Coloring by Travel-Time Sentiment
**Action**: Updated path coloring to use travel-time sentiment instead of destination sentiment
- Paths now colored based on sentiment during travel, not at destination
- More accurately represents stress/emotion during movement
- **Status**: ✅ Complete

### Step 4.4: Dot Filtering (Minimum Stay Duration)
**Action**: Implemented filtering to only show dots where person stayed >= 2 consecutive increments
- Prevents showing dots for brief pass-throughs
- Only locations with 10+ minute stays (2 x 5-minute increments) are shown
- **Status**: ✅ Complete

### Step 4.5: Current Position Indicator
**Action**: Added black dot showing current position on timeline
- "You are here" indicator updates as timeline slider moves
- Only shows when not traveling (at a location)
- **Status**: ✅ Complete

### Step 4.6: Stays Sidebar
**Action**: Created collapsible sidebar showing daily activity breakdown
- Shows stays with time ranges and locations
- Shows travel segments with inferred travel modes (walk, bike, drive) based on speed
- Calculates travel speed from distance and duration
- Displays sentiment for each activity
- **Status**: ✅ Complete

### Step 4.7: Mapbox Directions API Integration
**Action**: Integrated routing API for realistic travel paths
- Uses Mapbox Directions API to get walking routes between locations
- Caches routes to avoid repeated API calls
- **Status**: ⏳ Partial - API integration added but route points not yet interpolated into increments

## Next Steps

1. ✅ Implement striped dot visualization for overlapping intervals
2. ✅ Add hover tooltips with detailed interval information
3. ✅ Implement striped polygon fills for buildings/rooms
4. ✅ Add expand-on-click cluster behavior
5. ✅ Add legend for sentiment color coding
6. ✅ Implement time-increment data format
7. ✅ Add timeline slider with current position indicator
8. ✅ Create stays sidebar with travel mode inference
9. Complete route interpolation into increment data
10. Test and refine all interactions

