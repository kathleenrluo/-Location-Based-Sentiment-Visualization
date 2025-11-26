<template>
  <div class="map-container">
    <div v-if="loading" class="loading-overlay">
      <div class="spinner-border text-primary" role="status">
        <span class="visually-hidden">Loading...</span>
      </div>
      <p class="mt-2">Loading data...</p>
    </div>
    <div ref="mapContainer" class="map-wrapper"></div>
    
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
import { 
  loadIntervals, 
  loadBuildings, 
  getSentimentColor,
  aggregateIntervalsByLocation,
  aggregateByTimeBuckets,
  getBuildingSentiment,
  createTravelPaths
} from '../utils/dataLoader'

export default {
  name: 'MapVisualization',
  setup() {
    const mapContainer = ref(null)
    const viewMode = ref('daily')
    const intervals = ref([])
    const buildings = ref(null)
    const loading = ref(true)
    let deck = null
    let map = null

    // Process intervals based on current mode
    const processedData = computed(() => {
      if (intervals.value.length === 0) return { locations: [], paths: [] }
      
      if (viewMode.value === 'daily') {
        // Daily mode: aggregate all intervals by location
        const locations = aggregateIntervalsByLocation(intervals.value)
        const paths = createTravelPaths(intervals.value)
        return { locations, paths }
      } else {
        // Lifetime mode: aggregate by time buckets
        const locations = aggregateByTimeBuckets(intervals.value, 3)
        const paths = createTravelPaths(intervals.value)
        return { locations, paths }
      }
    })

    // Create layers for deck.gl
    const layers = computed(() => {
      const layersList = []

      // Building footprints layer with sentiment coloring
      if (buildings.value && intervals.value.length > 0) {
        const buildingsWithSentiment = buildings.value.features.map(building => {
          const sentiment = getBuildingSentiment(building, intervals.value, 0.0002) // ~22 meters
          return {
            ...building,
            sentiment: sentiment
          }
        })
        
        layersList.push(
          new PolygonLayer({
            id: 'buildings',
            data: buildingsWithSentiment,
            getPolygon: d => d.geometry.coordinates[0],
            getFillColor: d => {
              if (d.sentiment !== null) {
                return getSentimentColor(d.sentiment)
              }
              return [200, 200, 200, 100] // Gray for buildings without sentiment data
            },
            getLineColor: [150, 150, 150, 200],
            lineWidthMinPixels: 1,
            pickable: true,
            opacity: 0.6
          })
        )
      } else if (buildings.value) {
        // Fallback: show buildings in gray if no intervals loaded
        layersList.push(
          new PolygonLayer({
            id: 'buildings',
            data: buildings.value.features,
            getPolygon: d => d.geometry.coordinates[0],
            getFillColor: [200, 200, 200, 100],
            getLineColor: [150, 150, 150, 200],
            lineWidthMinPixels: 1,
            pickable: false
          })
        )
      }

      // Travel paths layer
      if (processedData.value.paths.length > 0) {
        layersList.push(
          new PathLayer({
            id: 'paths',
            data: processedData.value.paths,
            getPath: d => [d.source, d.target],
            getColor: [100, 100, 100, 150],
            getWidth: 2,
            widthMinPixels: 1,
            widthMaxPixels: 3,
            pickable: false
          })
        )
      }

      // Sentiment dots layer (fixed size)
      if (processedData.value.locations.length > 0) {
        const dotData = processedData.value.locations.map(loc => ({
          position: [loc.location.longitude, loc.location.latitude],
          sentiment: loc.avgSentiment,
          location: loc.location,
          intervals: loc.intervals
        }))
        
        layersList.push(
          new ScatterplotLayer({
            id: 'sentiment-dots',
            data: dotData,
            getPosition: d => d.position,
            getRadius: 8, // Fixed size
            getFillColor: d => getSentimentColor(d.sentiment),
            getLineColor: [0, 0, 0, 255],
            lineWidthMinPixels: 1,
            pickable: true,
            radiusMinPixels: 8,
            radiusMaxPixels: 8
          })
        )
      }

      return layersList
    })

    // Update deck.gl layers when data changes
    watch([layers, viewMode], () => {
      if (deck) {
        deck.setProps({ layers: layers.value })
      }
    }, { deep: true })

    onMounted(async () => {
      // Load data
      try {
        loading.value = true
        intervals.value = await loadIntervals()
        buildings.value = await loadBuildings()
        loading.value = false
      } catch (error) {
        console.error('Error loading data:', error)
        loading.value = false
      }

      // Initialize Mapbox map
      mapboxgl.accessToken = 'pk.eyJ1IjoibWFwYm94IiwiYSI6ImNpejY4NXVycTA2emYycXBndHRqcmZ3N3gifQ.rJcFIG214AriISLbB6B5aw'
      
      map = new mapboxgl.Map({
        container: mapContainer.value,
        style: 'mapbox://styles/mapbox/light-v11',
        center: [-118.2851, 34.0224],
        zoom: 15
      })

      map.on('load', () => {
        // Initialize deck.gl
        deck = new Deck({
          canvas: map.getCanvas(),
          width: '100%',
          height: '100%',
          initialViewState: {
            longitude: -118.2851,
            latitude: 34.0224,
            zoom: 15,
            pitch: 0,
            bearing: 0
          },
          controller: true,
          layers: layers.value,
          onHover: (info) => {
            if (info.object) {
              map.getCanvas().style.cursor = 'pointer'
            } else {
              map.getCanvas().style.cursor = 'default'
            }
          }
        })

        // Sync deck.gl with mapbox
        map.on('move', () => {
          if (deck) {
            const { lng, lat } = map.getCenter()
            deck.setProps({
              viewState: {
                longitude: lng,
                latitude: lat,
                zoom: map.getZoom(),
                pitch: map.getPitch(),
                bearing: map.getBearing()
              }
            })
          }
        })
      })
    })

    return {
      mapContainer,
      viewMode,
      loading
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

