<template>
  <div class="sidebar" :class="{ 'sidebar-open': isOpen }">
    <button class="sidebar-toggle" @click="toggleSidebar" :title="isOpen ? 'Hide sidebar' : 'Show sidebar'">
      <span v-if="!isOpen">▶</span>
      <span v-else>◀</span>
    </button>
    
    <div class="sidebar-content" v-if="isOpen">
      <h5 class="sidebar-title">Daily Activity</h5>
      
      <div v-if="loading" class="loading-text">Loading...</div>
      
      <div v-else-if="activities.length === 0" class="no-data">
        No activity data available
      </div>
      
      <div v-else class="activities-list">
        <div 
          v-for="(activity, idx) in activities" 
          :key="idx" 
          class="activity-item"
          :class="{ 'activity-travel': activity.type === 'travel', 'activity-clickable': true }"
          @click="handleActivityClick(activity)"
        >
          <div class="activity-time">
            {{ formatTimeRange(activity.startTime, activity.endTime) }}
          </div>
          <div class="activity-details">
            <div class="activity-icon">
              <span v-if="activity.type === 'stay'">📍</span>
              <span v-else-if="activity.mode === 'walk'">🚶</span>
              <span v-else-if="activity.mode === 'drive'">🚗</span>
              <span v-else-if="activity.mode === 'bike'">🚲</span>
              <span v-else>➡️</span>
            </div>
            <div class="activity-info">
              <div class="activity-description">
                <span v-if="activity.type === 'stay'">
                  At <strong>{{ activity.location }}</strong>
                </span>
                <span v-else>
                  {{ activity.description }}
                </span>
              </div>
              <div v-if="activity.sentiment !== undefined" class="activity-sentiment">
                <span class="sentiment-label">Sentiment:</span>
                <span 
                  class="sentiment-value" 
                  :style="{ color: getSentimentColor(activity.sentiment) }"
                >
                  {{ formatSentiment(activity.sentiment) }}
                </span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed, ref } from 'vue'

const props = defineProps({
  increments: {
    type: Array,
    default: () => []
  },
  intervals: {
    type: Array,
    default: () => []
  },
  currentTimeIndex: {
    type: Number,
    default: 0
  },
  timeIncrements: {
    type: Array,
    default: () => []
  }
})

const emit = defineEmits(['jump-to-time'])

const isOpen = ref(true)
const loading = computed(() => props.increments.length === 0 && props.intervals.length === 0)

// Convert intervals to increments format if needed
const displayIncrements = computed(() => {
  if (props.increments.length > 0) {
    return props.increments
  }
  // Convert intervals to a simple increment-like format for display
  return props.intervals.flatMap(interval => {
    const increments = []
    const start = new Date(interval.start_time)
    const end = new Date(interval.end_time)
    const duration = (end - start) / (1000 * 60) // minutes
    const numIncrements = Math.ceil(duration / 5) // 5-minute increments
    
    for (let i = 0; i < numIncrements; i++) {
      const timestamp = new Date(start.getTime() + i * 5 * 60 * 1000)
      if (timestamp <= end) {
        increments.push({
          timestamp,
          latitude: interval.latitude,
          longitude: interval.longitude,
          location_name: interval.location_name,
          location_type: interval.location_type,
          sentiment_score: interval.sentiment_score,
          activity: interval.activity,
          is_traveling: false
        })
      }
    }
    return increments
  })
})

const toggleSidebar = () => {
  isOpen.value = !isOpen.value
}

const formatTimeRange = (start, end) => {
  if (!start || !end) return ''
  const startTime = start instanceof Date ? start : new Date(start)
  const endTime = end instanceof Date ? end : new Date(end)
  
  const formatTime = (date) => {
    return date.toLocaleTimeString('en-US', { 
      hour: 'numeric', 
      minute: '2-digit',
      hour12: true 
    })
  }
  
  return `${formatTime(startTime)} - ${formatTime(endTime)}`
}

const formatSentiment = (sentiment) => {
  if (sentiment === undefined || sentiment === null) return 'N/A'
  return sentiment.toFixed(2)
}

const getSentimentColor = (sentiment) => {
  if (sentiment === undefined || sentiment === null) return '#666'
  if (sentiment < -0.1) return '#dc3545' // Red
  if (sentiment > 0.1) return '#28a745' // Green
  return '#ffc107' // Yellow
}

// Calculate distance between two points (Haversine formula)
const calculateDistance = (lat1, lon1, lat2, lon2) => {
  const R = 6371 // Earth's radius in km
  const dLat = (lat2 - lat1) * Math.PI / 180
  const dLon = (lon2 - lon1) * Math.PI / 180
  const a = 
    Math.sin(dLat/2) * Math.sin(dLat/2) +
    Math.cos(lat1 * Math.PI / 180) * Math.cos(lat2 * Math.PI / 180) *
    Math.sin(dLon/2) * Math.sin(dLon/2)
  const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1-a))
  return R * c
}

// Infer travel mode based on speed
const inferTravelMode = (distanceKm, durationMinutes) => {
  if (durationMinutes === 0) return 'unknown'
  const speedKmh = (distanceKm / durationMinutes) * 60
  
  // For very short durations (like 5 minutes), check if it's a drive
  // Driving typically covers more distance in short time
  if (durationMinutes <= 5 && distanceKm > 0.5) {
    return 'drive' // Short duration with significant distance = driving
  }
  
  if (speedKmh < 6) return 'walk' // Walking: ~5 km/h
  if (speedKmh < 20) return 'bike' // Biking: ~15 km/h
  if (speedKmh >= 20) return 'drive' // Driving: ~30-50 km/h
  return 'drive' // Default to drive for faster speeds
}

// Process intervals into stays and travel segments
const processIntervals = (intervals) => {
  if (!intervals || intervals.length === 0) return []
  
  const activitiesList = []
  let i = 0
  
  while (i < intervals.length) {
    const interval = intervals[i]
    const isTravel = interval.location_name === 'Traveling' || interval.location_type === 'traveling'
    
    if (isTravel) {
      // Group consecutive travel intervals together
      const travelStart = i
      let travelEnd = i
      let travelMode = interval.travel_mode || 'walk'
      let sentimentSum = interval.sentiment_score
      let sentimentCount = 1
      
      // Find end of travel segment
      while (travelEnd < intervals.length - 1) {
        const next = intervals[travelEnd + 1]
        if (next.location_name === 'Traveling' || next.location_type === 'traveling') {
          travelEnd++
          // Use travel_mode from any interval in the segment (they should all be the same)
          if (next.travel_mode) {
            travelMode = next.travel_mode
          }
          sentimentSum += next.sentiment_score
          sentimentCount++
        } else {
          break
        }
      }
      
      // Debug: log travel mode
      console.log('Travel segment:', { travelMode, from: intervals[travelStart > 0 ? travelStart - 1 : 0]?.location_name, to: intervals[travelEnd + 1]?.location_name })
      
      // Get start and end locations
      const prevInterval = travelStart > 0 ? intervals[travelStart - 1] : null
      const nextInterval = travelEnd < intervals.length - 1 ? intervals[travelEnd + 1] : null
      
      const from = prevInterval ? (prevInterval.location_name || prevInterval.location_type) : 'Unknown'
      const to = nextInterval ? (nextInterval.location_name || nextInterval.location_type) : 'Unknown'
      
      const startTime = intervals[travelStart].start_time
      const endTime = intervals[travelEnd].end_time
      const duration = (new Date(endTime) - new Date(startTime)) / (1000 * 60) // minutes
      const avgSentiment = sentimentSum / sentimentCount
      
      // Convert travel_mode to display format
      // travel_mode from data is "driving" or "walking", convert to "drive" or "walk"
      let mode = 'walk' // default
      if (travelMode === 'driving' || travelMode === 'drive') {
        mode = 'drive'
      } else if (travelMode === 'walking' || travelMode === 'walk') {
        mode = 'walk'
      } else if (travelMode) {
        mode = travelMode
      }
      
      console.log('Travel mode conversion:', { travelMode, mode, from, to })
      
      activitiesList.push({
        type: 'travel',
        startTime: startTime,
        endTime: endTime,
        from: from,
        to: to,
        mode: mode,
        description: `${formatDuration(duration)} ${mode} to ${to}`,
        sentiment: avgSentiment
      })
      
      i = travelEnd + 1
    } else {
      // Stay segment - group consecutive stays at the same location
      const stayStart = i
      let stayEnd = i
      let sentimentSum = interval.sentiment_score
      let sentimentCount = 1
      const locationName = interval.location_name || interval.location_type
      const locationKey = `${interval.latitude.toFixed(6)},${interval.longitude.toFixed(6)}`
      
      // Find end of stay segment (consecutive intervals at same location)
      while (stayEnd < intervals.length - 1) {
        const next = intervals[stayEnd + 1]
        const nextIsTravel = next.location_name === 'Traveling' || next.location_type === 'traveling'
        if (nextIsTravel) {
          break
        }
        // Check if same location (by coordinates)
        const nextKey = `${next.latitude.toFixed(6)},${next.longitude.toFixed(6)}`
        if (nextKey === locationKey) {
          stayEnd++
          sentimentSum += next.sentiment_score
          sentimentCount++
        } else {
          break
        }
      }
      
      // Aggregate all consecutive stays at same location
      const startTime = intervals[stayStart].start_time
      const endTime = intervals[stayEnd].end_time
      const avgSentiment = sentimentSum / sentimentCount
      
      activitiesList.push({
        type: 'stay',
        startTime: startTime,
        endTime: endTime,
        location: locationName,
        sentiment: avgSentiment
      })
      
      i = stayEnd + 1
    }
  }
  
  return activitiesList
}

// Process intervals or increments into stays and travel segments
const activities = computed(() => {
  // If using intervals, process them differently
  if (props.intervals && props.intervals.length > 0) {
    return processIntervals(props.intervals)
  }
  
  if (displayIncrements.value.length === 0) return []
  
  // Always show full day, regardless of timeline position
  const visibleIncrements = displayIncrements.value
      if (visibleIncrements.length === 0) return []
      
      const activitiesList = []
      let currentStay = null
      let currentTravel = null
      
      for (let i = 0; i < visibleIncrements.length; i++) {
        const increment = visibleIncrements[i]
        const nextIncrement = visibleIncrements[i + 1]
        const prevIncrement = visibleIncrements[i - 1]
        
        if (increment.is_traveling) {
          // This is travel
          if (currentStay) {
            // End current stay before travel starts
            activitiesList.push({
              type: 'stay',
              startTime: currentStay.startTime,
              endTime: prevIncrement ? prevIncrement.timestamp : increment.timestamp,
              location: currentStay.location,
              sentiment: currentStay.avgSentiment
            })
            currentStay = null
          }
          
          // Start or continue travel
          if (!currentTravel) {
            // Get the location before travel started (from previous increment or current if it's the first)
            const startLoc = prevIncrement && !prevIncrement.is_traveling ? {
              lat: prevIncrement.latitude,
              lon: prevIncrement.longitude,
              name: prevIncrement.location_name || prevIncrement.location_type
            } : {
              lat: increment.latitude,
              lon: increment.longitude,
              name: increment.location_name || increment.location_type
            }
            
            currentTravel = {
              type: 'travel',
              startTime: prevIncrement && !prevIncrement.is_traveling ? prevIncrement.timestamp : increment.timestamp,
              startLocation: startLoc,
              increments: [increment]
            }
          } else {
            currentTravel.increments.push(increment)
          }
          
          // Check if travel ends (next increment is NOT traveling)
          if (nextIncrement && !nextIncrement.is_traveling) {
            // Travel ended, calculate mode
            const start = currentTravel.startLocation
            const end = {
              lat: nextIncrement.latitude,
              lon: nextIncrement.longitude,
              name: nextIncrement.location_name || nextIncrement.location_type
            }
            const distance = calculateDistance(start.lat, start.lon, end.lat, end.lon)
            const duration = (new Date(nextIncrement.timestamp) - new Date(currentTravel.startTime)) / (1000 * 60) // minutes
            const mode = inferTravelMode(distance, duration)
            
            activitiesList.push({
              type: 'travel',
              startTime: currentTravel.startTime,
              endTime: nextIncrement.timestamp,
              from: start.name,
              to: end.name,
              mode: mode,
              description: `${formatDuration(duration)} ${mode} to ${end.name}`,
              sentiment: currentTravel.increments.reduce((sum, inc) => sum + inc.sentiment_score, 0) / currentTravel.increments.length
            })
            currentTravel = null
          } else if (!nextIncrement && currentTravel) {
            // Travel at end of day - use last increment's location as destination
            const start = currentTravel.startLocation
            const end = {
              lat: increment.latitude,
              lon: increment.longitude,
              name: increment.location_name || increment.location_type
            }
            const distance = calculateDistance(start.lat, start.lon, end.lat, end.lon)
            const duration = (new Date(increment.timestamp) - new Date(currentTravel.startTime)) / (1000 * 60)
            const mode = inferTravelMode(distance, duration)
            
            activitiesList.push({
              type: 'travel',
              startTime: currentTravel.startTime,
              endTime: increment.timestamp,
              from: start.name,
              to: end.name,
              mode: mode,
              description: `${formatDuration(duration)} ${mode} to ${end.name}`,
              sentiment: currentTravel.increments.reduce((sum, inc) => sum + inc.sentiment_score, 0) / currentTravel.increments.length
            })
            currentTravel = null
          }
        } else {
          // This is a stay (not traveling)
          if (currentTravel) {
            // End current travel - we've arrived
            const start = currentTravel.startLocation
            const end = {
              lat: increment.latitude,
              lon: increment.longitude,
              name: increment.location_name || increment.location_type
            }
            const distance = calculateDistance(start.lat, start.lon, end.lat, end.lon)
            const duration = (new Date(increment.timestamp) - new Date(currentTravel.startTime)) / (1000 * 60)
            const mode = inferTravelMode(distance, duration)
            
            activitiesList.push({
              type: 'travel',
              startTime: currentTravel.startTime,
              endTime: increment.timestamp,
              from: start.name,
              to: end.name,
              mode: mode,
              description: `${formatDuration(duration)} ${mode} to ${end.name}`,
              sentiment: currentTravel.increments.reduce((sum, inc) => sum + inc.sentiment_score, 0) / currentTravel.increments.length
            })
            currentTravel = null
          }
          
          // Start or continue stay
          if (!currentStay) {
            currentStay = {
              startTime: increment.timestamp,
              location: increment.location_name || increment.location_type,
              increments: [increment],
              sentimentSum: increment.sentiment_score
            }
          } else {
            // Check if location changed (shouldn't happen during stay, but handle it)
            const currentLocKey = `${increment.latitude.toFixed(6)},${increment.longitude.toFixed(6)}`
            const stayLocKey = `${currentStay.increments[0].latitude.toFixed(6)},${currentStay.increments[0].longitude.toFixed(6)}`
            
            if (currentLocKey !== stayLocKey) {
              // Location changed, end current stay and start new one
              activitiesList.push({
                type: 'stay',
                startTime: currentStay.startTime,
                endTime: prevIncrement ? prevIncrement.timestamp : increment.timestamp,
                location: currentStay.location,
                sentiment: currentStay.avgSentiment
              })
              currentStay = {
                startTime: increment.timestamp,
                location: increment.location_name || increment.location_type,
                increments: [increment],
                sentimentSum: increment.sentiment_score
              }
            } else {
              currentStay.increments.push(increment)
              currentStay.sentimentSum += increment.sentiment_score
            }
          }
          currentStay.avgSentiment = currentStay.sentimentSum / currentStay.increments.length
        }
      }
      
      // Add final stay if exists
      if (currentStay && visibleIncrements.length > 0) {
        const lastIncrement = visibleIncrements[visibleIncrements.length - 1]
        activitiesList.push({
          type: 'stay',
          startTime: currentStay.startTime,
          endTime: lastIncrement.timestamp,
          location: currentStay.location,
          sentiment: currentStay.avgSentiment
        })
      }
      
      // Add final travel if exists (shouldn't happen, but handle it)
      if (currentTravel && visibleIncrements.length > 0) {
        const lastIncrement = visibleIncrements[visibleIncrements.length - 1]
        const start = currentTravel.startLocation
        const end = {
          lat: lastIncrement.latitude,
          lon: lastIncrement.longitude,
          name: lastIncrement.location_name || lastIncrement.location_type
        }
        const distance = calculateDistance(start.lat, start.lon, end.lat, end.lon)
        const duration = (new Date(lastIncrement.timestamp) - new Date(currentTravel.startTime)) / (1000 * 60)
        const mode = inferTravelMode(distance, duration)
        
        activitiesList.push({
          type: 'travel',
          startTime: currentTravel.startTime,
          endTime: lastIncrement.timestamp,
          from: start.name,
          to: end.name,
          mode: mode,
          description: `${formatDuration(duration)} ${mode} to ${end.name}`,
          sentiment: currentTravel.increments.reduce((sum, inc) => sum + inc.sentiment_score, 0) / currentTravel.increments.length
        })
      }
      
  return activitiesList
})

const formatDuration = (minutes) => {
  if (minutes < 1) return `${Math.round(minutes * 60)}s`
  if (minutes < 60) return `${Math.round(minutes)}min`
  const hours = Math.floor(minutes / 60)
  const mins = Math.round(minutes % 60)
  return mins > 0 ? `${hours}h ${mins}min` : `${hours}h`
}

// Handle activity click - jump timeline to start of event
const handleActivityClick = (activity) => {
  const startTime = new Date(activity.startTime)
  
  // If we have time increments, find the closest one
  if (props.timeIncrements && props.timeIncrements.length > 0) {
    let closestIndex = 0
    let minDiff = Infinity
    
    props.timeIncrements.forEach((time, idx) => {
      const timeDate = new Date(time)
      const diff = Math.abs(timeDate - startTime)
      if (diff < minDiff) {
        minDiff = diff
        closestIndex = idx
      }
    })
    
    emit('jump-to-time', closestIndex)
  } else if (props.intervals && props.intervals.length > 0) {
    // Find the interval that contains or is closest to the start time
    let closestIndex = 0
    let minDiff = Infinity
    
    props.intervals.forEach((interval, idx) => {
      const intervalStart = new Date(interval.start_time)
      const diff = Math.abs(intervalStart - startTime)
      if (diff < minDiff) {
        minDiff = diff
        closestIndex = idx
      }
    })
    
    emit('jump-to-time', closestIndex)
  } else if (props.increments && props.increments.length > 0) {
    // Find the increment closest to the start time
    let closestIndex = 0
    let minDiff = Infinity
    
    props.increments.forEach((increment, idx) => {
      const incrementTime = new Date(increment.timestamp)
      const diff = Math.abs(incrementTime - startTime)
      if (diff < minDiff) {
        minDiff = diff
        closestIndex = idx
      }
    })
    
    emit('jump-to-time', closestIndex)
  }
}
</script>

<style scoped>
.sidebar {
  position: fixed;
  left: 0;
  top: 0;
  height: 100vh;
  width: 320px;
  background: white;
  box-shadow: 2px 0 8px rgba(0, 0, 0, 0.15);
  z-index: 1500;
  transform: translateX(-100%);
  transition: transform 0.3s ease;
  overflow-y: auto;
}

.sidebar-open {
  transform: translateX(0);
}

.sidebar-toggle {
  position: fixed;
  left: 0;
  top: 50%;
  transform: translateY(-50%);
  width: 40px;
  height: 80px;
  background: white;
  border: 1px solid #ddd;
  border-left: none;
  border-radius: 0 4px 4px 0;
  cursor: pointer;
  font-size: 18px;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 2px 0 4px rgba(0, 0, 0, 0.1);
  z-index: 1502;
  transition: left 0.3s ease;
}

.sidebar-open .sidebar-toggle {
  left: 320px;
}

.sidebar-toggle:hover {
  background: #f8f9fa;
  box-shadow: 2px 0 6px rgba(0, 0, 0, 0.15);
}

.sidebar-toggle:hover {
  background: #f8f9fa;
}

.sidebar-content {
  padding: 20px;
  height: 100%;
}

.sidebar-title {
  margin: 0 0 16px 0;
  font-size: 18px;
  font-weight: bold;
  color: #333;
  border-bottom: 2px solid #007bff;
  padding-bottom: 8px;
}

.loading-text,
.no-data {
  text-align: center;
  color: #666;
  padding: 20px;
}

.activities-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.activity-item {
  padding: 12px;
  border: 1px solid #e0e0e0;
  border-radius: 6px;
  background: #f8f9fa;
  transition: all 0.2s;
  cursor: pointer;
}

.activity-item:hover {
  background: #e9ecef;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.activity-item.activity-travel {
  background: #e3f2fd;
  border-color: #90caf9;
}

.activity-time {
  font-size: 12px;
  font-weight: 600;
  color: #666;
  margin-bottom: 8px;
}

.activity-details {
  display: flex;
  gap: 12px;
  align-items: flex-start;
}

.activity-icon {
  font-size: 24px;
  flex-shrink: 0;
}

.activity-info {
  flex: 1;
}

.activity-description {
  font-size: 14px;
  color: #333;
  margin-bottom: 4px;
  line-height: 1.4;
}

.activity-sentiment {
  font-size: 12px;
  display: flex;
  gap: 6px;
  align-items: center;
}

.sentiment-label {
  color: #666;
  font-weight: 500;
}

.sentiment-value {
  font-weight: bold;
}
</style>

