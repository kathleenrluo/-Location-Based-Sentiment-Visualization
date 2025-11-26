<template>
  <div class="map-container">
    <div v-if="loading" class="loading-overlay">
      <div class="spinner-border text-primary" role="status">
        <span class="visually-hidden">Loading...</span>
      </div>
      <p class="mt-2">Loading data...</p>
    </div>
    <div ref="mapContainer" class="map-wrapper"></div>
    
    <!-- Tooltip -->
    <Tooltip
      v-if="tooltip.visible"
      :visible="tooltip.visible"
      :x="tooltip.x"
      :y="tooltip.y"
      :title="tooltip.title"
      :details="tooltip.details"
    />
    
    <!-- Stays Sidebar -->
    <StaysSidebar 
      v-if="useIncrements ? increments.length > 0 : intervals.length > 0"
      :increments="useIncrements ? increments : []"
      :intervals="!useIncrements ? intervals : []"
      :current-time-index="currentTimeIndex"
      :time-increments="timeIncrements"
      @jump-to-time="handleJumpToTime"
    />
    
    <!-- Legend -->
    <Legend />
    
    <!-- Timeline Slider (for Daily mode with either increments or intervals) -->
    <TimelineSlider
      v-if="viewMode === 'daily' && ((useIncrements && increments.length > 0) || (!useIncrements && intervals.length > 0))"
      :current-time="currentTime"
      :start-time="startTime"
      :end-time="endTime"
      :current-index="currentTimeIndex"
      :max-index="maxTimeIndex"
      :current-sentiment="currentSentiment"
      :time-increments="timeIncrements"
      @update:current-index="currentTimeIndex = $event"
    />
    
    <!-- Control Panel -->
    <div class="control-panel">
      <div class="card">
        <div class="card-body">
          <h5 class="card-title">View Mode</h5>
          <div class="btn-group" role="group">
            <button 
              type="button" 
              class="btn"
              :class="viewMode === 'daily' ? 'btn-primary' : 'btn-outline-primary'"
              @click="viewMode = 'daily'"
            >
              Daily View
            </button>
            <button 
              type="button" 
              class="btn"
              :class="viewMode === 'lifetime' ? 'btn-primary' : 'btn-outline-primary'"
              @click="viewMode = 'lifetime'"
            >
              Lifetime View
            </button>
          </div>
          
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, onMounted, watch, computed } from 'vue'
import { Deck } from '@deck.gl/core'
import { ScatterplotLayer, PolygonLayer, PathLayer } from '@deck.gl/layers'
import mapboxgl from 'mapbox-gl'
import Tooltip from './Tooltip.vue'
import Legend from './Legend.vue'
import TimelineSlider from './TimelineSlider.vue'
import StaysSidebar from './StaysSidebar.vue'
import { 
  loadIntervals, 
  loadBuildings, 
  getSentimentColor,
  aggregateIntervalsByLocation,
  aggregateByTimeBuckets,
  getBuildingSentiment,
  createTravelPaths
} from '../utils/dataLoader'
import { createStripedDotData, createStripedPolygonData } from '../utils/stripedVisualization'

export default {
  name: 'MapVisualization',
  components: {
    Tooltip,
    Legend,
    TimelineSlider,
    StaysSidebar
  },
  setup() {
    const mapContainer = ref(null)
    const viewMode = ref('daily')
    const intervals = ref([]) // Legacy format
    const increments = ref([]) // New time-increment format
    const buildings = ref(null)
    const buildingsWithSentiment = ref(null) // Pre-calculated building sentiment
    const loading = ref(true)
    const hoveredObject = ref(null)
    const hoveredLocation = ref(null)
    const tooltip = ref({
      visible: false,
      x: 0,
      y: 0,
      title: '',
      details: {}
    })
    // Timeline slider state
    const currentTimeIndex = ref(0)
    const useIncrements = ref(false) // Use intervals by default (faster, with real routes)
    let deck = null
    let map = null

    // Generate 5-minute time increments for intervals
    const timeIncrements = computed(() => {
      if (intervals.value.length === 0) return []
      
      const increments = []
      const start = new Date(intervals.value[0].start_time)
      const end = new Date(intervals.value[intervals.value.length - 1].end_time)
      
      // Generate 5-minute increments
      let current = new Date(start)
      while (current <= end) {
        increments.push(new Date(current))
        current = new Date(current.getTime() + 5 * 60 * 1000) // Add 5 minutes
      }
      
      return increments
    })
    
    // Computed properties for timeline
    const currentTime = computed(() => {
      if (useIncrements.value && increments.value.length > 0) {
        const index = Math.min(currentTimeIndex.value, increments.value.length - 1)
        return increments.value[index]?.timestamp || new Date()
      } else if (intervals.value.length > 0 && timeIncrements.value.length > 0) {
        const index = Math.min(currentTimeIndex.value, timeIncrements.value.length - 1)
        return timeIncrements.value[index] || new Date()
      } else if (intervals.value.length > 0) {
        const index = Math.min(currentTimeIndex.value, intervals.value.length - 1)
        return intervals.value[index]?.start_time || new Date()
      }
      return new Date()
    })
    
    const startTime = computed(() => {
      if (useIncrements.value && increments.value.length > 0) {
        return increments.value[0]?.timestamp || new Date()
      } else if (intervals.value.length > 0) {
        return intervals.value[0]?.start_time || new Date()
      }
      return new Date()
    })
    
    const endTime = computed(() => {
      if (useIncrements.value && increments.value.length > 0) {
        return increments.value[increments.value.length - 1]?.timestamp || new Date()
      } else if (intervals.value.length > 0) {
        return intervals.value[intervals.value.length - 1]?.end_time || new Date()
      }
      return new Date()
    })
    
    const maxTimeIndex = computed(() => {
      if (useIncrements.value && increments.value.length > 0) {
        return Math.max(0, increments.value.length - 1)
      } else if (intervals.value.length > 0 && timeIncrements.value.length > 0) {
        // For intervals, use 5-minute increments
        return Math.max(0, timeIncrements.value.length - 1)
      } else if (intervals.value.length > 0) {
        return Math.max(0, intervals.value.length - 1)
      }
      return 0
    })
    
    // Get current sentiment based on current time index
    const currentSentiment = computed(() => {
      if (useIncrements.value && increments.value.length > 0) {
        const index = Math.min(currentTimeIndex.value, increments.value.length - 1)
        return increments.value[index]?.sentiment_score || null
      } else if (intervals.value.length > 0 && timeIncrements.value.length > 0) {
        // Find which interval the current time falls into
        const currentTime = timeIncrements.value[currentTimeIndex.value]
        if (!currentTime) return null
        
        // Find the interval that contains this time
        for (const interval of intervals.value) {
          const start = new Date(interval.start_time)
          const end = new Date(interval.end_time)
          if (currentTime >= start && currentTime <= end) {
            return interval.sentiment_score
          }
        }
        return null
      }
      return null
    })
    
    // Get visible increments up to current time
    const visibleIncrements = computed(() => {
      if (!useIncrements.value || increments.value.length === 0) return []
      return increments.value.slice(0, currentTimeIndex.value + 1)
    })
    
    // Process data based on current mode and data format
    const processedData = computed(() => {
      if (useIncrements.value && increments.value.length > 0) {
        // Use new increment format
        if (viewMode.value === 'daily') {
          // For dots: use all increments (not filtered by time), but filter for >= 2 consecutive
          // For paths: use visible increments up to current time
          const filtered = filterIncrementsForDots(increments.value, 1)  // Changed to 1 to show all stays
          const paths = createTravelPathsFromIncrements(visibleIncrements.value)
          console.log('Daily mode - filtered locations:', filtered.length, 'paths:', paths.length, 'total increments:', increments.value.length)
          return { locations: filtered, paths }
        } else {
          // Lifetime mode: aggregate all increments by time buckets
          // For now, use all increments
          const filtered = filterIncrementsForDots(increments.value, 2)
          const paths = createTravelPathsFromIncrements(increments.value)
          return { locations: filtered, paths }
        }
      } else if (intervals.value.length > 0) {
        // Use legacy interval format
        if (viewMode.value === 'daily') {
          const locations = aggregateIntervalsByLocation(intervals.value)
          const paths = createTravelPaths(intervals.value)
          return { locations, paths }
        } else {
          const locations = aggregateByTimeBuckets(intervals.value, 3)
          const paths = createTravelPaths(intervals.value)
          return { locations, paths }
        }
      }
      return { locations: [], paths: [] }
    })

    // Pre-calculate building sentiment (only once when data loads)
    const calculateBuildingSentiment = () => {
      if (!buildings.value || intervals.value.length === 0) {
        buildingsWithSentiment.value = null
        return
      }

      console.log('Calculating building sentiment for', buildings.value.features.length, 'buildings...')
      const startTime = performance.now()
      
      // Only process buildings that might have nearby intervals
      // Create a spatial index for faster lookup
      const intervalLocations = intervals.value.map(i => ({
        lat: i.latitude,
        lon: i.longitude,
        sentiment: i.sentiment_score
      }))

      // Process buildings in batches to avoid blocking
      const processedBuildings = []
      const batchSize = 1000
      
      for (let i = 0; i < buildings.value.features.length; i += batchSize) {
        const batch = buildings.value.features.slice(i, i + batchSize)
        batch.forEach(building => {
          const result = getBuildingSentiment(building, intervals.value, 0.0003) // ~33 meters
          if (result !== null) {
            // Only include buildings with sentiment data to reduce rendering load
            processedBuildings.push({
              ...building,
              sentiment: result.sentiment,
              intervals: result.intervals // Store intervals for striping
            })
          }
        })
      }

      console.log(`Found ${processedBuildings.length} buildings with sentiment data (${((performance.now() - startTime) / 1000).toFixed(2)}s)`)
      buildingsWithSentiment.value = processedBuildings
      
      // Trigger layer update after calculation
      if (deck) {
        setTimeout(() => {
          updateDeckLayers()
        }, 50)
      }
    }

    // Handle dot hover for tooltips
    const handleDotHover = (info) => {
      console.log('handleDotHover called', { hasObject: !!info.object, x: info.x, y: info.y, layer: info.layer?.id })
      if (info && info.object && info.x !== undefined && info.y !== undefined) {
        hoveredObject.value = info.object
        const obj = info.object
        
        // Get tooltip details
        const details = {
          location_name: obj.location?.name || 'Unknown',
          location_type: obj.location?.type || 'Unknown'
        }
        
        // Check if this is a striped dot with multiple intervals
        if (obj.intervals && Array.isArray(obj.intervals) && obj.intervals.length > 1) {
          // Multiple intervals - show breakdown
          details.intervals = obj.intervals.map(interval => ({
            start_time: interval.start_time,
            end_time: interval.end_time,
            sentiment_score: interval.sentiment_score,
            activity: interval.activity,
            duration_minutes: interval.duration_minutes
          }))
          details.avgSentiment = obj.avgSentiment || obj.sentiment
          details.totalDuration = obj.totalDuration || obj.intervals.reduce((sum, i) => sum + i.duration_minutes, 0)
        } else if (obj.interval) {
          // Single interval from expanded view
          details.sentiment_score = obj.interval.sentiment_score
          details.activity = obj.interval.activity
          details.duration_minutes = obj.interval.duration_minutes
          details.start_time = obj.interval.start_time
          details.end_time = obj.interval.end_time
        } else if (obj.intervals && obj.intervals.length === 1) {
          // Single interval in array
          const interval = obj.intervals[0]
          details.sentiment_score = interval.sentiment_score
          details.activity = interval.activity
          details.duration_minutes = interval.duration_minutes
          details.start_time = interval.start_time
          details.end_time = interval.end_time
        } else {
          // Fallback for aggregated data
          details.avgSentiment = obj.avgSentiment || obj.sentiment
          if (obj.intervals && obj.intervals.length > 0) {
            details.intervals = obj.intervals.map(interval => ({
              start_time: interval.start_time,
              end_time: interval.end_time,
              sentiment_score: interval.sentiment_score,
              activity: interval.activity,
              duration_minutes: interval.duration_minutes
            }))
          }
        }
        
        if (viewMode.value === 'lifetime' && obj.timeBucket !== undefined) {
          details.timeBucket = obj.timeBucket
        }
        
        // Get coordinates relative to viewport for tooltip
        const canvas = document.getElementById('deck-overlay-canvas')
        const rect = canvas ? canvas.getBoundingClientRect() : null
        const tooltipX = rect ? info.x + rect.left : info.x
        const tooltipY = rect ? info.y + rect.top : info.y
        
        tooltip.value = {
          visible: true,
          x: tooltipX,
          y: tooltipY,
          title: obj.location?.name || 'Location',
          details: details
        }
        
        console.log('Tooltip set:', { visible: true, x: tooltipX, y: tooltipY, title: tooltip.value.title })
      } else {
        hoveredObject.value = null
        tooltip.value.visible = false
      }
    }
    
    // Handle dot click to expand clusters
    const handleDotClick = (info) => {
      console.log('handleDotClick called', { object: info.object, layer: info.layer?.id })
      if (!info.object) return
      
      // Get the actual dot object (might be nested in dot property for expanded view)
      const dotObj = info.object.dot || info.object
      
      // Check if this dot has multiple intervals (is a cluster)
      if (dotObj.intervals && Array.isArray(dotObj.intervals) && dotObj.intervals.length > 1) {
        // Get position from the object
        const position = dotObj.position || (info.object.position ? 
          [info.object.position[0], info.object.position[1]] : 
          (info.coordinate ? [info.coordinate[0], info.coordinate[1]] : null))
        
        if (!position) {
          console.warn('No position found for dot', dotObj)
          return
        }
        
        // Toggle expansion - check if this location is already expanded
        if (hoveredLocation.value && 
            hoveredLocation.value.position && 
            Math.abs(hoveredLocation.value.position[0] - position[0]) < 0.00001 &&
            Math.abs(hoveredLocation.value.position[1] - position[1]) < 0.00001) {
          // Already expanded, collapse it
          hoveredLocation.value = null
          console.log('Collapsing cluster at', position)
        } else {
          // Expand it
          hoveredLocation.value = {
            ...dotObj,
            position: position
          }
          console.log('Expanding cluster at', position, 'with', dotObj.intervals.length, 'intervals')
        }
        // Force layer update to show expanded view
        updateDeckLayers()
      } else {
        console.log('Dot clicked but has only', dotObj.intervals?.length || 0, 'intervals')
      }
    }

    // Create layers for deck.gl
    const layers = computed(() => {
      const layersList = []

      // Building footprints layer - show striped buildings for multiple intervals
      if (buildingsWithSentiment.value && buildingsWithSentiment.value.length > 0) {
        buildingsWithSentiment.value.forEach((building, idx) => {
          // Use stored intervals from building calculation
          const buildingIntervals = building.intervals || []
          
          if (buildingIntervals.length > 1 && viewMode.value === 'daily') {
            // Create striped polygon for multiple intervals
            const stripedData = createStripedPolygonData(building, buildingIntervals)
            if (stripedData && stripedData.buckets.length > 1) {
              // Render each time bucket as a separate semi-transparent layer for striping effect
              stripedData.buckets.forEach((bucket, bucketIdx) => {
                const color = getSentimentColor(bucket.avgSentiment)
                layersList.push(
                  new PolygonLayer({
                    id: `building-striped-${idx}-${bucketIdx}`,
                    data: [building],
                    getPolygon: d => d.geometry.coordinates[0],
                    getFillColor: [color[0], color[1], color[2], Math.floor(color[3] * 0.4)],
                    getLineColor: [150, 150, 150, 100],
                    lineWidthMinPixels: 0.5,
                    pickable: true,
                    opacity: 0.4,
                    filled: true,
                    stroked: false,
                    updateTriggers: {
                      getFillColor: [viewMode.value, bucket.bucket]
                    }
                  })
                )
              })
            } else {
              // Single sentiment - render normally
              const color = getSentimentColor(building.sentiment)
              layersList.push(
                new PolygonLayer({
                  id: `building-sentiment-${idx}`,
                  data: [building],
                  getPolygon: d => d.geometry.coordinates[0],
                  getFillColor: [color[0], color[1], color[2], Math.floor(color[3] * 0.6)],
                  getLineColor: [150, 150, 150, 150],
                  lineWidthMinPixels: 1,
                  pickable: true,
                  opacity: 0.5,
                  updateTriggers: {
                    getFillColor: [viewMode.value]
                  }
                })
              )
            }
          } else {
            // Single sentiment building
            const color = getSentimentColor(building.sentiment)
            layersList.push(
              new PolygonLayer({
                id: `building-sentiment-${idx}`,
                data: [building],
                getPolygon: d => d.geometry.coordinates[0],
                getFillColor: [color[0], color[1], color[2], Math.floor(color[3] * 0.6)],
                getLineColor: [150, 150, 150, 150],
                lineWidthMinPixels: 1,
                pickable: true,
                opacity: 0.5,
                updateTriggers: {
                  getFillColor: [viewMode.value]
                }
              })
            )
          }
        })
      }
      
      // Always show all buildings as light gray outlines for context
      if (buildings.value && buildings.value.features && buildings.value.features.length > 0) {
        console.log(`Rendering ${buildings.value.features.length} buildings as gray outlines`)
        layersList.push(
          new PolygonLayer({
            id: 'buildings-outline',
            data: buildings.value.features,
            getPolygon: d => {
              if (!d || !d.geometry || !d.geometry.coordinates || !d.geometry.coordinates[0]) {
                console.warn('Invalid building geometry:', d)
                return []
              }
              return d.geometry.coordinates[0]
            },
            getFillColor: [200, 200, 200, 100], // Medium gray, semi-transparent so map shows through
            getLineColor: [150, 150, 150, 150], // Darker gray lines, semi-transparent
            lineWidthMinPixels: 1,
            pickable: false,
            opacity: 0.4, // Make buildings semi-transparent
            filled: true,
            stroked: true
          })
        )
      }

      // Travel paths layer - color coded by travel-time sentiment
      console.log('Creating paths layer, paths count:', processedData.value.paths.length)
      if (processedData.value.paths.length > 0) {
        // Convert paths to format expected by PathLayer
        const pathData = processedData.value.paths.map(path => {
          // If path has 'path' array, use it (route with multiple points)
          // Otherwise, use source/target (legacy format)
          if (path.path && Array.isArray(path.path)) {
            return {
              path: path.path,
              sentiment: path.sentiment
            }
          } else {
            // Legacy format: convert source/target to path array
            return {
              path: [path.source, path.target],
              sentiment: path.sentiment
            }
          }
        })
        
        layersList.push(
          new PathLayer({
            id: 'paths',
            data: pathData,
            getPath: d => d.path, // Use the path array directly
            getColor: d => {
              // Color code based on travel-time sentiment (not destination)
              const sentiment = d.sentiment || 0
              const color = getSentimentColor(sentiment)
              // Make paths slightly more transparent
              return [color[0], color[1], color[2], 180]
            },
            getWidth: 3,
            widthMinPixels: 2,
            widthMaxPixels: 4,
            pickable: false
          })
        )
      }
      
      // Current position indicator (black dot showing "you are here")
      // Show for both increments and intervals
      if (useIncrements.value && increments.value.length > 0) {
        const currentIndex = Math.min(currentTimeIndex.value, increments.value.length - 1)
        const currentIncrement = increments.value[currentIndex]
        if (currentIncrement) {
          // Show current position even if traveling (but maybe with different style)
          layersList.push(
            new ScatterplotLayer({
              id: 'current-position',
              data: [{
                position: [currentIncrement.longitude, currentIncrement.latitude],
                timestamp: currentIncrement.timestamp,
                is_traveling: currentIncrement.is_traveling
              }],
              getPosition: d => d.position,
              getRadius: d => d.is_traveling ? 10 : 12,
              getFillColor: d => d.is_traveling ? [100, 100, 100, 255] : [0, 0, 0, 255], // Gray if traveling, black if at location
              getLineColor: [255, 255, 255, 255], // White border
              lineWidthMinPixels: 2,
              pickable: false,
              radiusMinPixels: 10,
              radiusMaxPixels: 12,
              updateTriggers: {
                getPosition: [currentTimeIndex.value],
                getRadius: [currentTimeIndex.value],
                getFillColor: [currentTimeIndex.value]
              }
            })
          )
        }
      } else if (intervals.value.length > 0 && timeIncrements.value.length > 0) {
        // Show current position for intervals - find which interval contains the current time
        const currentTime = timeIncrements.value[currentTimeIndex.value]
        if (currentTime) {
          // Find the interval that contains this time
          let currentInterval = null
          for (const interval of intervals.value) {
            const start = new Date(interval.start_time)
            const end = new Date(interval.end_time)
            if (currentTime >= start && currentTime <= end) {
              currentInterval = interval
              break
            }
          }
          
          if (currentInterval) {
            const isTraveling = currentInterval.location_name === 'Traveling' || currentInterval.location_type === 'traveling'
            layersList.push(
              new ScatterplotLayer({
                id: 'current-position',
                data: [{
                  position: [currentInterval.longitude, currentInterval.latitude],
                  is_traveling: isTraveling
                }],
                getPosition: d => d.position,
                getRadius: d => d.is_traveling ? 10 : 12,
                getFillColor: d => d.is_traveling ? [100, 100, 100, 255] : [0, 0, 0, 255], // Gray if traveling, black if at location
                getLineColor: [255, 255, 255, 255], // White border
                lineWidthMinPixels: 2,
                pickable: false,
                radiusMinPixels: 10,
                radiusMaxPixels: 12,
                updateTriggers: {
                  getPosition: [currentTimeIndex.value],
                  getRadius: [currentTimeIndex.value],
                  getFillColor: [currentTimeIndex.value]
                }
              })
            )
          }
        }
      }

      // Sentiment dots layer (with striped support for multiple intervals)
      console.log('Creating dots layer, locations count:', processedData.value.locations.length)
      if (processedData.value.locations.length > 0) {
        const dotData = processedData.value.locations.map(loc => {
          const stripedData = createStripedDotData(loc.location, loc.intervals)
          return {
            ...stripedData,
            location: loc.location,
            totalDuration: loc.totalDuration || loc.intervals.reduce((sum, i) => sum + i.duration_minutes, 0),
            avgSentiment: loc.avgSentiment
          }
        })
        
        // For simple dots (single interval), use normal scatterplot
        const simpleDots = dotData.filter(d => d.type === 'simple')
        const stripedDots = dotData.filter(d => d.type === 'striped')
        
        // Simple dots layer
        if (simpleDots.length > 0) {
          layersList.push(
            new ScatterplotLayer({
              id: 'sentiment-dots-simple',
              data: simpleDots,
              getPosition: d => d.position,
              getRadius: 8,
              getFillColor: d => getSentimentColor(d.sentiment),
              getLineColor: [0, 0, 0, 255],
              lineWidthMinPixels: 1,
              pickable: true,
              radiusMinPixels: 8,
              radiusMaxPixels: 8,
              onHover: (info) => handleDotHover(info),
              onClick: (info) => handleDotClick(info)
            })
          )
        }
        
        // Striped dots - use single layer with all dots
        if (stripedDots.length > 0) {
          // Flatten all striped dots into single data array
          const stripedDotData = stripedDots.map((dot, idx) => {
            const isHovered = hoveredLocation.value && 
              hoveredLocation.value.position &&
              Math.abs(hoveredLocation.value.position[0] - dot.position[0]) < 0.00001 &&
              Math.abs(hoveredLocation.value.position[1] - dot.position[1]) < 0.00001
            
            if (isHovered && dot.intervals.length > 1) {
              // Expanded view: show each interval as separate dot
              const numIntervals = dot.intervals.length
              const angleStep = (2 * Math.PI) / numIntervals
              const radius = 0.00015 // ~15 meters in lat/lon
              
              return dot.intervals.map((interval, i) => {
                const angle = i * angleStep
                const offsetX = Math.cos(angle) * radius
                const offsetY = Math.sin(angle) * radius
                return {
                  position: [
                    dot.position[0] + offsetX,
                    dot.position[1] + offsetY
                  ],
                  sentiment: interval.sentiment_score,
                  interval: interval,
                  dot: dot,
                  location: dot.location
                }
              })
            } else {
              // Collapsed view: show as single dot with average sentiment
              return [{
                position: dot.position,
                sentiment: dot.avgSentiment,
                dot: dot,
                intervals: dot.intervals,
                location: dot.location,
                // Store position in a format that can be compared
                positionArray: [dot.position[0], dot.position[1]]
              }]
            }
          }).flat()
          
          layersList.push(
            new ScatterplotLayer({
              id: 'sentiment-dots-striped',
              data: stripedDotData,
              getPosition: d => d.position,
              getRadius: d => d.intervals && d.intervals.length > 1 ? 10 : 8,
              getFillColor: d => getSentimentColor(d.sentiment),
              getLineColor: [0, 0, 0, 255],
              lineWidthMinPixels: 1.5,
              pickable: true,
              radiusMinPixels: 8,
              radiusMaxPixels: 10,
              onHover: (info) => {
                if (info.object) {
                  handleDotHover(info)
                }
              },
              onClick: (info) => {
                if (info.object) {
                  handleDotClick(info)
                }
              }
            })
          )
        }
        
        // Old striped dot code removed - was creating too many layers
        if (false && stripedDots.length > 0) {
          stripedDots.forEach((dot, idx) => {
            const isHovered = hoveredLocation.value && 
              hoveredLocation.value.position[0] === dot.position[0] &&
              hoveredLocation.value.position[1] === dot.position[1]
            
            if (isHovered) {
              // Expanded view: show each interval as separate dot
              const numIntervals = dot.intervals.length
              const angleStep = (2 * Math.PI) / numIntervals
              const radius = 0.00015 // ~15 meters in lat/lon
              
              dot.intervals.forEach((interval, i) => {
                const angle = i * angleStep
                const offsetX = Math.cos(angle) * radius
                const offsetY = Math.sin(angle) * radius
                
                layersList.push(
                  new ScatterplotLayer({
                    id: `sentiment-dot-expanded-${idx}-${i}`,
                    data: [{
                      position: [
                        dot.position[0] + offsetX,
                        dot.position[1] + offsetY
                      ],
                      sentiment: interval.sentiment_score,
                      interval: interval,
                      dot: dot,
                      location: dot.location
                    }],
                    getPosition: d => d.position,
                    getRadius: 10,
                    getFillColor: d => getSentimentColor(d.sentiment),
                    getLineColor: [0, 0, 0, 255],
                    lineWidthMinPixels: 1.5,
                    pickable: true,
                    radiusMinPixels: 10,
                    radiusMaxPixels: 10,
                    onHover: (info) => {
                      if (info.object) {
                        handleDotHover({ ...info, object: { ...info.object.dot, interval: info.object.interval } })
                      }
                    }
                  })
                )
              })
            } else {
              // Collapsed view: show as single striped dot (multiple overlapping circles)
              // Create a pattern by rendering segments as small offset circles
              dot.segments.forEach((segment, segIdx) => {
                const centerAngle = segment.startAngle + (segment.endAngle - segment.startAngle) / 2
                const offset = 0.00003 // Very small offset for visual striping effect
                const offsetX = Math.cos(centerAngle) * offset
                const offsetY = Math.sin(centerAngle) * offset
                
                layersList.push(
                  new ScatterplotLayer({
                    id: `sentiment-dot-striped-${idx}-${segIdx}`,
                    data: [{
                      position: [
                        dot.position[0] + offsetX,
                        dot.position[1] + offsetY
                      ],
                      sentiment: segment.sentiment,
                      dot: dot
                    }],
                    getPosition: d => d.position,
                    getRadius: 8,
                    getFillColor: d => {
                      const color = getSentimentColor(d.sentiment)
                      // Make slightly transparent for overlapping effect
                      return [color[0], color[1], color[2], 200]
                    },
                    getLineColor: [0, 0, 0, 255],
                    lineWidthMinPixels: 1,
                    pickable: true,
                    radiusMinPixels: 8,
                    radiusMaxPixels: 8,
                    onHover: (info) => {
                      if (info.object) {
                        handleDotHover({ ...info, object: info.object.dot })
                      }
                    },
                    onClick: (info) => {
                      if (info.object) {
                        handleDotClick({ ...info, object: info.object.dot })
                      }
                    }
                  })
                )
              })
            }
          })
        }
      }

      return layersList
    })

    // Function to update deck.gl layers
    const updateDeckLayers = () => {
      if (deck && map) {
        console.log('Updating deck.gl layers, layer count:', layers.value.length)
        layers.value.forEach((layer, idx) => {
          console.log(`Layer ${idx}: ${layer.id}, data length:`, layer.props?.data?.length || 'N/A')
        })
        // Update layers with current map viewState
        const { lng, lat } = map.getCenter()
        deck.setProps({ 
          layers: layers.value,
          viewState: {
            longitude: lng,
            latitude: lat,
            zoom: map.getZoom(),
            pitch: map.getPitch() || 0,
            bearing: map.getBearing() || 0
          }
        })
      } else {
        console.warn('Deck.gl not initialized, cannot update layers')
      }
    }

    // Update deck.gl layers when view mode changes
    watch([viewMode], () => {
      updateDeckLayers()
    })
    
    // Watch for currentTimeIndex changes to update current position indicator
    watch([currentTimeIndex], () => {
      // Update layers when timeline changes (for both increments and intervals)
      updateDeckLayers()
    })
    
    // Watch for hoveredLocation changes to update expanded clusters
    watch([hoveredLocation], () => {
      // Update layers when cluster expansion state changes
      updateDeckLayers()
    })
    
    // Handle jump to time from sidebar
    const handleJumpToTime = (timeIndex) => {
      currentTimeIndex.value = timeIndex
      // updateDeckLayers will be called by the watch above
    }

    // Recalculate building sentiment when intervals change
    watch([intervals], () => {
      if (intervals.value.length > 0 && buildings.value) {
        // Use setTimeout to avoid blocking the UI
        setTimeout(() => {
          calculateBuildingSentiment()
          // Update layers after sentiment calculation
          updateDeckLayers()
        }, 100)
      }
    }, { deep: false })

    // Watch for building sentiment changes
    watch([buildingsWithSentiment], () => {
      if (buildingsWithSentiment.value !== null) {
        updateDeckLayers()
      }
    })

    onMounted(async () => {
      // Initialize Mapbox map with your token
      mapboxgl.accessToken = 'pk.eyJ1Ijoia3JsdW8iLCJhIjoiY21oaWwwdTNuMTR1aTJzb242ejQybm0zYiJ9.baefOu17StTORLdFeRHMEA'
      
      map = new mapboxgl.Map({
        container: mapContainer.value,
        style: 'mapbox://styles/mapbox/light-v11',
        center: [-118.2851, 34.0224],
        zoom: 15
      })

      map.on('load', () => {
        console.log('Map loaded, initializing deck.gl overlay...')
        
        // Create a separate canvas for deck.gl that overlays on top of Mapbox
        const deckCanvas = document.createElement('canvas')
        deckCanvas.id = 'deck-overlay-canvas'
        // Use pointer-events: auto for hover, but pass wheel events to map for zoom
        deckCanvas.style.cssText = 'position: absolute; top: 0; left: 0; width: 100%; height: 100%; pointer-events: auto; z-index: 1;'
        const containerRect = mapContainer.value.getBoundingClientRect()
        deckCanvas.width = containerRect.width
        deckCanvas.height = containerRect.height
        mapContainer.value.appendChild(deckCanvas)
        
        // Pass wheel events to mapbox for zooming
        deckCanvas.addEventListener('wheel', (e) => {
          // Don't prevent default - let it bubble to mapbox
          const mapCanvas = map.getCanvas()
          if (mapCanvas) {
            // Create a new wheel event and dispatch to map canvas
            const wheelEvent = new WheelEvent('wheel', {
              bubbles: true,
              cancelable: true,
              clientX: e.clientX,
              clientY: e.clientY,
              deltaX: e.deltaX,
              deltaY: e.deltaY,
              deltaZ: e.deltaZ,
              deltaMode: e.deltaMode,
              wheelDelta: e.wheelDelta
            })
            mapCanvas.dispatchEvent(wheelEvent)
          }
        }, { passive: true })
        
        // Pass mouse events to mapbox for dragging when not hovering over pickable objects
        let isDragging = false
        let lastMouseX = 0
        let lastMouseY = 0
        let isOverPickableObject = false
        
        // Track when we're over a pickable object
        deckCanvas.addEventListener('mousemove', (e) => {
          // Check if we're over a pickable object using deck.gl's pickObject
          if (deck) {
            const rect = deckCanvas.getBoundingClientRect()
            const x = e.clientX - rect.left
            const y = e.clientY - rect.top
            const pickInfo = deck.pickObject({ x, y })
            isOverPickableObject = !!(pickInfo && pickInfo.object)
          }
          
          if (isDragging && !isOverPickableObject) {
            const mapCanvas = map.getCanvas()
            if (mapCanvas) {
              const mouseEvent = new MouseEvent('mousemove', {
                bubbles: true,
                cancelable: true,
                clientX: e.clientX,
                clientY: e.clientY,
                button: e.button,
                buttons: e.buttons,
                movementX: e.clientX - lastMouseX,
                movementY: e.clientY - lastMouseY
              })
              mapCanvas.dispatchEvent(mouseEvent)
            }
            lastMouseX = e.clientX
            lastMouseY = e.clientY
          }
        })
        
        deckCanvas.addEventListener('mousedown', (e) => {
          // Only start dragging if NOT over a pickable object
          if (!isOverPickableObject) {
            isDragging = true
            lastMouseX = e.clientX
            lastMouseY = e.clientY
            const mapCanvas = map.getCanvas()
            if (mapCanvas) {
              const mouseEvent = new MouseEvent('mousedown', {
                bubbles: true,
                cancelable: true,
                clientX: e.clientX,
                clientY: e.clientY,
                button: e.button,
                buttons: e.buttons
              })
              mapCanvas.dispatchEvent(mouseEvent)
            }
          }
          // If over pickable object, let deck.gl handle it (don't prevent default)
        })
        
        deckCanvas.addEventListener('mouseup', (e) => {
          if (isDragging && !isOverPickableObject) {
            isDragging = false
            const mapCanvas = map.getCanvas()
            if (mapCanvas) {
              const mouseEvent = new MouseEvent('mouseup', {
                bubbles: true,
                cancelable: true,
                clientX: e.clientX,
                clientY: e.clientY,
                button: e.button,
                buttons: e.buttons
              })
              mapCanvas.dispatchEvent(mouseEvent)
            }
          }
          isDragging = false // Always reset on mouseup
        })
        
        // Also handle mouseleave to stop dragging if mouse leaves canvas
        deckCanvas.addEventListener('mouseleave', () => {
          if (isDragging) {
            isDragging = false
          }
          isOverPickableObject = false
        })
        
        console.log('Created deck.gl overlay canvas:', deckCanvas.width, 'x', deckCanvas.height)
        
        // Initialize deck.gl on the overlay canvas
        deck = new Deck({
          canvas: deckCanvas,
          width: '100%',
          height: '100%',
          initialViewState: {
            longitude: -118.2851,
            latitude: 34.0224,
            zoom: 15,
            pitch: 0,
            bearing: 0
          },
          controller: false, // Let mapbox handle controls
          layers: [],
          onHover: (info) => {
            // Handle hover at deck level - this is called for all layers
            if (info.object) {
              map.getCanvas().style.cursor = 'pointer'
              // Temporarily enable pointer events on deck canvas for hover
              const deckCanvas = document.getElementById('deck-overlay-canvas')
              if (deckCanvas) {
                deckCanvas.style.pointerEvents = 'auto'
              }
              // Call handleDotHover for any sentiment dot layer
              if (info.layer && info.layer.id && (
                info.layer.id.includes('sentiment-dot') || 
                info.layer.id.includes('sentiment-dot-simple') ||
                info.layer.id.includes('sentiment-dot-striped') ||
                info.layer.id.includes('sentiment-dot-expanded')
              )) {
                handleDotHover(info)
              }
            } else {
              map.getCanvas().style.cursor = 'default'
              // Hide tooltip when not hovering over any object
              hoveredObject.value = null
              tooltip.value.visible = false
            }
          },
          onClick: (info) => {
            // Handle clicks for expanding clusters
            if (info.object && info.layer && info.layer.id && (
              info.layer.id.includes('sentiment-dot') ||
              info.layer.id.includes('sentiment-dot-striped') ||
              info.layer.id.includes('sentiment-dot-expanded')
            )) {
              handleDotClick(info)
            }
          },
          onError: (error) => {
            console.error('Deck.gl error:', error)
          }
        })
        
        console.log('Deck.gl initialized as overlay canvas')

        // Sync deck.gl viewState with mapbox
        const syncDeckView = () => {
          if (deck && map) {
            try {
              const { lng, lat } = map.getCenter()
              deck.setProps({
                viewState: {
                  longitude: lng,
                  latitude: lat,
                  zoom: map.getZoom(),
                  pitch: map.getPitch() || 0,
                  bearing: map.getBearing() || 0
                },
                layers: layers.value // Always include current layers
              })
              console.log('Synced deck view, layer count:', layers.value.length)
            } catch (error) {
              console.warn('Error syncing deck view:', error)
            }
          }
        }
        
        // Sync on map movements
        map.on('move', syncDeckView)
        map.on('zoom', syncDeckView)
        map.on('rotate', syncDeckView)
        map.on('pitch', syncDeckView)
        
        // Also sync when map is idle
        map.on('idle', syncDeckView)
        
        // Handle window resize and map container resize
        const handleResize = () => {
          if (deckCanvas && mapContainer.value) {
            const containerRect = mapContainer.value.getBoundingClientRect()
            deckCanvas.width = containerRect.width
            deckCanvas.height = containerRect.height
            if (deck) {
              deck.setProps({
                width: containerRect.width,
                height: containerRect.height
              })
              // Also update layers to trigger re-render
              syncDeckView()
            }
          }
        }
        window.addEventListener('resize', handleResize)
        
        // Also listen to map resize
        map.on('resize', handleResize)

        // Load data after map is ready
        loadData()
      })
      
      // Handle map errors gracefully
      map.on('error', (e) => {
        console.warn('Mapbox error:', e.error?.message || e)
      })
    })

    // Separate function for loading data
    const loadData = async () => {
      try {
        loading.value = true
        console.log('Loading data...')
        
        // Load intervals (with real routes)
        try {
          console.log('Attempting to load intervals.json...')
          const intervalsData = await loadIntervals()
          if (intervalsData && intervalsData.length > 0) {
            intervals.value = intervalsData
            useIncrements.value = false
            console.log(`✓ Loaded ${intervals.value.length} intervals (with real routes)`)
            console.log('Sample interval:', intervals.value[0])
            // Set initial time index to end (show full day)
            currentTimeIndex.value = intervals.value.length - 1
          } else {
            console.warn('Intervals data is empty')
          }
        } catch (e) {
          console.error('Failed to load intervals.json:', e)
          throw e // Re-throw to show error in UI
        }
        
        const buildingsData = await loadBuildings()
        buildings.value = buildingsData
        
        console.log(`Loaded ${buildings.value.features.length} buildings`)
        console.log('Buildings data structure:', {
          type: buildings.value.type,
          featureCount: buildings.value.features?.length,
          firstFeature: buildings.value.features?.[0] ? 'exists' : 'missing'
        })
        
        // Pre-calculate building sentiment (this may take a moment)
        calculateBuildingSentiment()
        
        // Update layers after data loads
        if (deck) {
          setTimeout(() => {
            updateDeckLayers()
        console.log('Layers updated. Locations:', processedData.value.locations.length, 'Paths:', processedData.value.paths.length)
        console.log('Use increments:', useIncrements.value)
        console.log('Increments count:', increments.value.length)
        console.log('Intervals count:', intervals.value.length)
        if (intervals.value.length > 0) {
          console.log('First interval sample:', intervals.value[0])
          const travelIntervals = intervals.value.filter(i => i.location_name === 'Traveling' || i.location_type === 'traveling')
          console.log('Travel intervals count:', travelIntervals.length)
          if (travelIntervals.length > 0) {
            console.log('First travel interval:', travelIntervals[0])
          }
        }
          }, 100)
        }
        
        loading.value = false
        console.log('Data loading complete')
      } catch (error) {
        console.error('Error loading data:', error)
        loading.value = false
      }
    }

    return {
      mapContainer,
      viewMode,
      loading,
      tooltip,
      hoveredObject,
      hoveredLocation,
      useIncrements,
      increments,
      intervals,
      currentTimeIndex,
      currentTime,
      startTime,
      endTime,
      maxTimeIndex,
      timeIncrements,
      currentSentiment,
      handleJumpToTime
    }
  }
}
</script>

<style scoped>
.map-container {
  position: relative;
  width: 100vw;
  height: 100vh;
}

.map-wrapper {
  width: 100%;
  height: 100%;
  position: relative;
  overflow: hidden;
}

/* Ensure deck.gl overlay canvas is properly positioned */
.map-wrapper canvas:not(.mapboxgl-canvas) {
  position: absolute !important;
  top: 0 !important;
  left: 0 !important;
  width: 100% !important;
  height: 100% !important;
  pointer-events: auto !important;
  z-index: 1 !important;
}

.timeline-slider {
  position: absolute;
  top: 20px;
  left: 50%;
  transform: translateX(-50%);
  z-index: 1000;
  min-width: 400px;
  max-width: 600px;
}

.control-panel {
  position: absolute;
  top: 20px;
  right: 20px;
  z-index: 1000;
  min-width: 250px;
}

.card {
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.15);
}

.loading-overlay {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(255, 255, 255, 0.9);
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  z-index: 2000;
}
</style>

