/**
 * Data loading and processing utilities
 */

/**
 * Load intervals data from JSON file
 */
export async function loadIntervals() {
  const response = await fetch('/intervals.json')
  const data = await response.json()
  return data.map(interval => ({
    ...interval,
    start_time: new Date(interval.start_time),
    end_time: new Date(interval.end_time)
  }))
}

/**
 * Load locations data from JSON file
 */
export async function loadLocations() {
  const response = await fetch('/locations.json')
  return await response.json()
}

/**
 * Load building footprints from GeoJSON file
 */
export async function loadBuildings() {
  const response = await fetch('/buildings_usc.geojson')
  return await response.json()
}

/**
 * Filter intervals by time window (for Daily mode)
 */
export function filterIntervalsByTime(intervals, startHour, endHour) {
  return intervals.filter(interval => {
    const hour = interval.start_time.getHours() + interval.start_time.getMinutes() / 60
    return hour >= startHour && hour < endHour
  })
}

/**
 * Get sentiment color (green = positive, red = negative, yellow = neutral)
 */
export function getSentimentColor(sentiment) {
  // Sentiment range: -1 (very negative) to +1 (very positive)
  if (sentiment >= 0.3) {
    // Positive - green shades
    const intensity = Math.min(sentiment, 1)
    return [0, Math.floor(200 + 55 * intensity), 0, 200]
  } else if (sentiment <= -0.3) {
    // Negative - red shades
    const intensity = Math.min(Math.abs(sentiment), 1)
    return [Math.floor(200 + 55 * intensity), 0, 0, 200]
  } else {
    // Neutral - yellow shades
    const intensity = Math.abs(sentiment) / 0.3
    return [Math.floor(200 + 55 * intensity), Math.floor(200 + 55 * intensity), 0, 200]
  }
}

/**
 * Group intervals by location for clustering
 */
export function groupIntervalsByLocation(intervals) {
  const groups = {}
  intervals.forEach(interval => {
    const key = `${interval.latitude.toFixed(6)},${interval.longitude.toFixed(6)}`
    if (!groups[key]) {
      groups[key] = {
        location: {
          latitude: interval.latitude,
          longitude: interval.longitude,
          name: interval.location_name,
          type: interval.location_type
        },
        intervals: []
      }
    }
    groups[key].intervals.push(interval)
  })
  return Object.values(groups)
}

/**
 * Aggregate intervals by location (for Daily mode - aggregate all intervals at same location)
 */
export function aggregateIntervalsByLocation(intervals) {
  const groups = {}
  
  intervals.forEach(interval => {
    const key = `${interval.latitude.toFixed(6)},${interval.longitude.toFixed(6)}`
    if (!groups[key]) {
      groups[key] = {
        location: {
          latitude: interval.latitude,
          longitude: interval.longitude,
          name: interval.location_name,
          type: interval.location_type
        },
        intervals: [],
        totalDuration: 0,
        avgSentiment: 0
      }
    }
    
    groups[key].intervals.push(interval)
    groups[key].totalDuration += interval.duration_minutes
  })
  
  // Calculate average sentiment for each location
  Object.values(groups).forEach(group => {
    const sum = group.intervals.reduce((acc, i) => acc + i.sentiment_score, 0)
    group.avgSentiment = sum / group.intervals.length
  })
  
  return Object.values(groups)
}

/**
 * Aggregate intervals by time-of-day buckets (for Lifetime mode)
 */
export function aggregateByTimeBuckets(intervals, bucketSize = 3) {
  const buckets = {}
  
  intervals.forEach(interval => {
    const hour = interval.start_time.getHours()
    const bucket = Math.floor(hour / bucketSize) * bucketSize
    
    const key = `${interval.latitude.toFixed(6)},${interval.longitude.toFixed(6)}_${bucket}`
    if (!buckets[key]) {
      buckets[key] = {
        location: {
          latitude: interval.latitude,
          longitude: interval.longitude,
          name: interval.location_name,
          type: interval.location_type
        },
        timeBucket: bucket,
        intervals: [],
        totalDuration: 0,
        avgSentiment: 0
      }
    }
    
    buckets[key].intervals.push(interval)
    buckets[key].totalDuration += interval.duration_minutes
  })
  
  // Calculate average sentiment for each bucket
  Object.values(buckets).forEach(bucket => {
    const sum = bucket.intervals.reduce((acc, i) => acc + i.sentiment_score, 0)
    bucket.avgSentiment = sum / bucket.intervals.length
  })
  
  return Object.values(buckets)
}

/**
 * Get sentiment for a building based on nearby intervals
 */
export function getBuildingSentiment(building, intervals, threshold = 0.0001) {
  // Find intervals that are within the building polygon or very close
  const buildingCenter = getPolygonCenter(building.geometry.coordinates[0])
  const nearbyIntervals = intervals.filter(interval => {
    const distance = haversineDistance(
      buildingCenter[1], buildingCenter[0],
      interval.latitude, interval.longitude
    )
    return distance < threshold // ~11 meters
  })
  
  if (nearbyIntervals.length === 0) return null
  
  const avgSentiment = nearbyIntervals.reduce((sum, i) => sum + i.sentiment_score, 0) / nearbyIntervals.length
  return avgSentiment
}

/**
 * Get center point of a polygon
 */
function getPolygonCenter(coordinates) {
  let sumLat = 0, sumLon = 0
  coordinates.forEach(coord => {
    sumLon += coord[0]
    sumLat += coord[1]
  })
  return [sumLon / coordinates.length, sumLat / coordinates.length]
}

/**
 * Calculate distance between two points using Haversine formula (in km)
 */
function haversineDistance(lat1, lon1, lat2, lon2) {
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

/**
 * Create path segments between consecutive intervals
 */
export function createTravelPaths(intervals) {
  const paths = []
  
  // Sort intervals by start time
  const sorted = [...intervals].sort((a, b) => a.start_time - b.start_time)
  
  for (let i = 0; i < sorted.length - 1; i++) {
    const current = sorted[i]
    const next = sorted[i + 1]
    
    // Only create path if locations are different
    if (current.latitude !== next.latitude || current.longitude !== next.longitude) {
      paths.push({
        source: [current.longitude, current.latitude],
        target: [next.longitude, next.latitude],
        startTime: current.end_time,
        endTime: next.start_time
      })
    }
  }
  
  return paths
}

