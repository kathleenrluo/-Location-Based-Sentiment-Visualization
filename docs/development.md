# Development Log

## Week's Worth of Data Generation

**Date**: Current session

**Problem**: User requested a week's worth of data so that the lifetime view can have more data than the daily view.

**Solution**:
1. Modified `data/generate_intervals_with_routes.py` to generate 7 days of data instead of 1 day
2. Added a loop that generates the same schedule for each day of the week
3. Added weekend variations (skip gym on weekends, shorter study time)
4. Added date filtering to the daily view so it only shows one day at a time
5. Added a date selector UI component in the control panel for daily mode
6. Updated all computed properties to use `filteredIntervals` instead of `intervals` for daily view

**Changes Made**:
- `data/generate_intervals_with_routes.py`: Added 7-day loop with weekend variations
- `src/utils/dataLoader.js`: Added `filterIntervalsByDate()` function
- `src/components/MapVisualization.vue`: 
  - Added `selectedDate` and `availableDates` refs
  - Added `filteredIntervals` computed property
  - Updated timeline and sentiment calculations to use filtered intervals
  - Added date selector dropdown in control panel
  - Updated building sentiment calculation to use all intervals (for lifetime aggregation)

**Result**: 
- Generated 6,540 intervals across 7 days (Nov 18-24, 2024)
- Daily view now filters to show only the selected day
- Lifetime view aggregates across all 7 days
- Date selector allows users to navigate between days in daily mode
- Weekend variations: gym segments replaced with home time, shorter study sessions

**Issue Found**: The generated data file needs to be copied to `public/intervals.json` for the web app to access it. The script generates it in `data/intervals.json`.

## Schedule Variations and Date Range Update

**Date**: Current session

**Problem**: User requested to remove Monday Nov 18th and add variation in daily schedules so each day isn't identical.

**Solution**:
1. Changed base date from Nov 18 (Monday) to Nov 19 (Tuesday)
2. Reduced generation from 7 days to 6 days (Tuesday through Sunday)
3. Added `get_schedule_for_day()` function that creates day-specific schedule variations:
   - **Tuesday**: Late gym (9am), skip class (replace with home time)
   - **Wednesday**: Early class (11:30am), longer study session (until 10:30pm)
   - **Thursday**: No gym (replace with home time), longer class (until 3pm)
   - **Friday**: Early finish (study ends at 8pm instead of 10pm)
   - **Weekends**: No gym (replace with home time), shorter study (ends at 9pm)

**Changes Made**:
- `data/generate_intervals_with_routes.py`: 
  - Changed `base_date` to Nov 19, 2024
  - Changed loop from `range(7)` to `range(6)`
  - Renamed `schedule` to `base_schedule`
  - Added `get_schedule_for_day()` function with day-specific logic
  - Each day now gets a modified schedule based on day of week

**Result**: 
- Generated 6 days of data (Nov 19-24, 2024) with unique schedules per day
- Each weekday has different activities/times
- Weekends have relaxed schedules (no gym, shorter study)

## Timezone Fix for Date Filtering

**Date**: Current session

**Problem**: Days were appearing to run from 7pm to 7pm instead of midnight to midnight due to timezone conversion issues.

**Solution**:
1. Updated `filterIntervalsByDate()` to use local date components instead of ISO string conversion
2. Updated `availableDates` computed property to create dates at local midnight instead of UTC midnight
3. Updated date selector change handler to create dates using local time components

**Changes Made**:
- `src/utils/dataLoader.js`: Changed date filtering to use `getFullYear()`, `getMonth()`, `getDate()` instead of `toISOString()`
- `src/components/MapVisualization.vue`: 
  - Updated `availableDates` to create dates at local midnight: `new Date(year, month - 1, day, 0, 0, 0, 0)`
  - Updated date selector to parse dates in local timezone

**Result**: 
- Days now correctly show from midnight to midnight in local time
- No more timezone conversion issues causing 7pm offset

## Lifetime View: Buildings Only with Crosshatch Patterns

**Date**: Current session

**Problem**: User requested that lifetime view should only show colored buildings (no dots or lines), with crosshatch patterns for buildings with multiple time-of-day sentiments, and hover tooltips showing time-of-day breakdown.

**Solution**:
1. Updated `processedData` to return empty locations and paths arrays for lifetime view
2. Updated `getBuildingSentiment()` to support time bucket calculation (3-hour buckets) when `groupByTimeBucket` is true
3. Updated building rendering to show crosshatch/striped pattern for buildings with multiple time buckets in lifetime mode
4. Added `handleBuildingHover()` and `handleBuildingClick()` functions for lifetime mode building interactions
5. Made paths and dots layers only render in daily mode
6. Buildings in lifetime mode are now pickable and show tooltips with time-of-day sentiment breakdown

**Changes Made**:
- `src/components/MapVisualization.vue`: 
  - Updated `processedData` to return `{ locations: [], paths: [] }` for lifetime view
  - Added building hover/click handlers for lifetime mode
  - Updated building rendering to show striped pattern for multiple time buckets in lifetime mode
  - Made paths and dots layers conditional on `viewMode.value === 'daily'`
  - Updated `calculateBuildingSentiment()` to pass `groupByTimeBucket` flag
- `src/utils/dataLoader.js`: 
  - Updated `getBuildingSentiment()` to calculate time buckets (3-hour windows) when `groupByTimeBucket` is true
  - Returns `timeBuckets` array with time ranges, average sentiment, count, and duration per bucket

**Result**: 
- Lifetime view now shows only colored buildings
- Buildings with multiple time-of-day sentiments show crosshatch/striped patterns
- Hovering buildings shows tooltip with breakdown by time of day (e.g., "00:00 - 03:00: sentiment 0.25, 45 min")
- Clicking buildings locks the tooltip for scrolling

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
- Uses Mapbox Directions API to get routes between locations
- Routes integrated directly into intervals.json format
- Travel intervals include route coordinates and travel_mode field
- **Status**: ✅ Complete - Routes embedded in intervals.json

### Step 4.8: Return to Intervals Format with Routes
**Date**: Latest update
**Action**: Switched back to intervals.json format with embedded Mapbox routes
- Created `generate_intervals_with_routes.py` to generate intervals with real route paths
- Travel segments include intermediate route points for curved paths
- Travel mode (walking/driving) included in data
- **Status**: ✅ Complete - Using intervals.json as primary data format

### Step 4.9: Timeline Slider Re-implementation
**Action**: Re-added timeline slider with 5-minute increment support
- Slider works with intervals using 5-minute time increments
- Shows current time and sentiment value
- Black "you are here" dot moves with timeline
- **Status**: ✅ Complete

### Step 4.10: Sidebar Activity Aggregation
**Action**: Updated sidebar to aggregate consecutive stays at same location
- Multiple intervals at same location shown as single event
- Average sentiment calculated for aggregated stays
- Travel segments grouped and show correct travel mode
- **Status**: ✅ Complete

### Step 4.11: Click-to-Jump Timeline Feature
**Action**: Added ability to click sidebar events to jump timeline
- Clicking any activity card jumps timeline to start of that event
- Timeline updates current position dot and sentiment display
- **Status**: ✅ Complete

### Step 4.12: Code Cleanup
**Action**: Removed unused files and code
- Deleted increments.json and related generation scripts
- Removed unused building data files
- Cleaned up imports and fallback code
- **Status**: ✅ Complete

## Recent Fixes

### Issue 12: Map Not Draggable
**Problem**: Map could only zoom, not drag/pan
**Solution**: 
- Updated mouse event handling to check for pickable objects before passing to Mapbox
- Only pass drag events when not over deck.gl pickable objects
- **Status**: ✅ Fixed

### Issue 13: Red Sentiment Not Showing
**Problem**: Negative sentiment values not showing as red on map
**Solution**: 
- Updated `getSentimentColor()` to show red for any negative value (not just < -0.3)
- Now properly displays red for all negative sentiment scores
- **Status**: ✅ Fixed

### Issue 14: Too Many Dots Along Paths
**Problem**: Dots appearing everywhere along travel paths
**Solution**: 
- Updated `aggregateIntervalsByLocation()` to filter out travel intervals
- Dots now only appear at stay locations, not along paths
- **Status**: ✅ Fixed

### Issue 15: Timeline Slider Disappeared
**Problem**: Timeline slider not showing when using intervals
**Solution**: 
- Updated timeline slider to work with intervals using 5-minute increments
- Added computed properties for time increments and current sentiment
- **Status**: ✅ Fixed

### Issue 16: Hover/Click Not Working
**Problem**: Hover tooltips and click expansion not working
**Solution**: 
- Fixed mouse event handling to properly detect pickable objects
- Updated hover handlers to correctly identify dot layers
- **Status**: ✅ Fixed

### Issue 17: Lifetime Mode Shows Timeline
**Problem**: Timeline slider appearing in Lifetime mode
**Solution**: 
- Updated timeline slider condition to only show in Daily mode
- **Status**: ✅ Fixed

### Issue 18: Hover Tooltips Not Working
**Problem**: Hover tooltips were not appearing when hovering over sentiment dots, despite state being set correctly
**Root Cause**: Multiple issues:
1. Building layers had `pickable: true`, intercepting hover events before they reached dot layers
2. Tooltip was rendered inside `map-container` which had CSS constraints (overflow, z-index) hiding it
3. Tooltip positioning didn't account for viewport boundaries, causing long tooltips to be cut off

**Solution**: 
1. Set building layers to `pickable: false` so they don't intercept hover events
2. Used Vue's `Teleport` component to render tooltip directly in `<body>`, bypassing map container CSS constraints
3. Added `!important` flags to tooltip CSS to ensure visibility properties aren't overridden
4. Implemented smart positioning that detects viewport boundaries and adjusts tooltip position:
   - If tooltip would go off right edge, positions it to the left of cursor
   - If tooltip would go off bottom edge, positions it above cursor
   - Ensures tooltip stays within viewport bounds
5. Made long tooltips scrollable with `max-height` and `overflow-y: auto` on both the tooltip container and detail sections
6. Added comprehensive debugging logs to track tooltip state changes and DOM rendering

**Date**: Latest update
**Status**: ✅ Fixed - Tooltips now appear correctly and stay within viewport

### Issue 19: Tooltips Not Scrollable on Hover
**Problem**: Long tooltips couldn't be scrolled because moving mouse into tooltip area would cause unhover, making tooltip disappear
**Solution**: 
1. Changed tooltips from hover-based to click-based interaction
2. Tooltips now open on click and stay open until:
   - Same dot is clicked again (toggle)
   - User clicks outside the tooltip (click-outside detection)
3. Enabled `pointer-events: auto` on tooltip so it can receive mouse events for scrolling
4. Updated hover handlers to only change cursor, not show tooltip
5. Updated click handlers to show/hide tooltip and handle cluster expansion
6. Added click-outside event listener to close tooltip when clicking on map

**Date**: Latest update
**Status**: ✅ Fixed - Tooltips are now click-based and fully scrollable

## Next Steps

1. ✅ All major features implemented
2. ✅ Code cleanup complete
3. ✅ Tooltip hover functionality working
4. Test and refine all interactions
5. Performance optimization if needed

