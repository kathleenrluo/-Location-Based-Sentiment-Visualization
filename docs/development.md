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
**Status**: ⏳ Pending - Currently showing as larger dots with average sentiment

### Step 3.3: Hover Interactions
**Status**: ⏳ Pending - Basic hover cursor change implemented, tooltips needed

### Step 3.4: Building Color Coding
**Status**: ✅ Complete - Buildings now colored by sentiment of nearby intervals

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

---

## Next Steps

1. Implement striped dot visualization for overlapping intervals
2. Add hover tooltips with detailed interval information
3. Implement striped polygon fills for buildings/rooms
4. Add expand-on-hover cluster behavior
5. Improve timeline interaction (range selection)
6. Add day selector for Daily mode
7. Performance optimization for large building dataset

