/**
 * Data loading and processing utilities
 */

/**
 * Load intervals data from JSON file (legacy format)
 */
export async function loadIntervals() {
  const response = await fetch('/intervals.json')
  if (!response.ok) {
    throw new Error(`Failed to load intervals.json: ${response.status} ${response.statusText}`)
  }
  const data = await response.json()
  if (!Array.isArray(data)) {
    throw new Error('intervals.json is not an array')
  }
  console.log(`Loaded ${data.length} intervals from JSON`)
  return data.map(interval => ({
    ...interval,
    start_time: new Date(interval.start_time),
    end_time: new Date(interval.end_time)
  }))
}

// loadIncrements removed - using intervals.json instead

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
 * Filter intervals by date (for Daily mode - show only one day)
 */
export function filterIntervalsByDate(intervals, targetDate) {
  if (!targetDate) return intervals
  // Get date string in local timezone to avoid UTC conversion issues
  const year = targetDate.getFullYear()
  const month = String(targetDate.getMonth() + 1).padStart(2, '0')
  const day = String(targetDate.getDate()).padStart(2, '0')
  const targetDateStr = `${year}-${month}-${day}` // YYYY-MM-DD in local time
  
  return intervals.filter(interval => {
    const intervalDate = new Date(interval.start_time)
    // Compare dates in local timezone
    const intervalYear = intervalDate.getFullYear()
    const intervalMonth = String(intervalDate.getMonth() + 1).padStart(2, '0')
    const intervalDay = String(intervalDate.getDate()).padStart(2, '0')
    const intervalDateStr = `${intervalYear}-${intervalMonth}-${intervalDay}`
    return intervalDateStr === targetDateStr
  })
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
  if (sentiment > 0) {
    // Positive - green shades (any positive value)
    const intensity = Math.min(sentiment, 1)
    return [0, Math.floor(200 + 55 * intensity), 0, 200]
  } else if (sentiment < 0) {
    // Negative - red shades (any negative value)
    const intensity = Math.min(Math.abs(sentiment), 1)
    return [Math.floor(200 + 55 * intensity), 0, 0, 200]
  } else {
    // Exactly zero - yellow/neutral
    return [255, 255, 0, 200]
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
  
  // Filter out travel intervals - only show dots at stay locations
  const stayIntervals = intervals.filter(interval => {
    return interval.location_name !== 'Traveling' && interval.location_type !== 'traveling'
  })
  
  stayIntervals.forEach(interval => {
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
 * Optimized: uses simple distance calculation instead of expensive haversine
 */
export function getBuildingSentiment(building, intervals, threshold = 0.0003, groupByTimeBucket = false) {
  // Get building center (simplified - just average of coordinates)
  const coords = building.geometry.coordinates[0]
  let sumLat = 0, sumLon = 0
  const coordCount = Math.min(coords.length, 10) // Sample first 10 points for speed
  for (let i = 0; i < coordCount; i++) {
    sumLon += coords[i][0]
    sumLat += coords[i][1]
  }
  const buildingCenter = [sumLon / coordCount, sumLat / coordCount]
  
  // Use simple Euclidean distance (much faster than haversine for small distances)
  // At USC latitude, 0.0001 degrees ≈ 11 meters
  const thresholdSq = threshold * threshold
  const nearbyIntervals = []
  
  for (const interval of intervals) {
    const dLat = interval.latitude - buildingCenter[1]
    const dLon = interval.longitude - buildingCenter[0]
    const distSq = dLat * dLat + dLon * dLon
    
    if (distSq < thresholdSq) {
      nearbyIntervals.push(interval)
    }
  }
  
  if (nearbyIntervals.length === 0) return null
  
  if (groupByTimeBucket) {
    // Group intervals by time-of-day buckets (3-hour windows)
    const timeBuckets = {}
    nearbyIntervals.forEach(interval => {
      const date = interval.start_time instanceof Date ? interval.start_time : new Date(interval.start_time)
      const hour = date.getHours()
      const bucket = Math.floor(hour / 3) * 3 // 0-2, 3-5, 6-8, etc.
      
      if (!timeBuckets[bucket]) {
        timeBuckets[bucket] = {
          bucket,
          intervals: [],
          sumSentiment: 0,
          count: 0
        }
      }
      timeBuckets[bucket].intervals.push(interval)
      timeBuckets[bucket].sumSentiment += interval.sentiment_score
      timeBuckets[bucket].count++
    })
    
    // Calculate average sentiment per bucket
    const buckets = Object.values(timeBuckets).map(bucket => ({
      ...bucket,
      avgSentiment: bucket.sumSentiment / bucket.count,
      timeRange: `${bucket.bucket}:00 - ${bucket.bucket + 3}:00`
    }))
    
    // Sort by time bucket
    buckets.sort((a, b) => a.bucket - b.bucket)
    
    // Calculate overall average
    const totalSum = buckets.reduce((sum, b) => sum + b.sumSentiment, 0)
    const totalCount = buckets.reduce((sum, b) => sum + b.count, 0)
    const overallSentiment = totalCount > 0 ? totalSum / totalCount : 0
    
    return {
      sentiment: overallSentiment,
      intervals: nearbyIntervals,
      timeBuckets: buckets,
      hasMultipleBuckets: buckets.length > 1
    }
  } else {
    // Simple aggregation (for daily view)
    let sumSentiment = 0
    for (const interval of nearbyIntervals) {
      sumSentiment += interval.sentiment_score
    }
    
    return {
      sentiment: sumSentiment / nearbyIntervals.length,
      intervals: nearbyIntervals
    }
  }
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
 * Handles both travel intervals (with multiple route points) and simple location changes
 */
export function createTravelPaths(intervals) {
  const paths = []
  
  // Sort intervals by start time
  const sorted = [...intervals].sort((a, b) => {
    const aTime = a.start_time instanceof Date ? a.start_time : new Date(a.start_time)
    const bTime = b.start_time instanceof Date ? b.start_time : new Date(b.start_time)
    return aTime - bTime
  })
  
  // Group consecutive travel intervals together to form complete routes
  let i = 0
  while (i < sorted.length) {
    const current = sorted[i]
    const isTravel = current.location_name === 'Traveling' || current.location_type === 'traveling'
    
    if (isTravel) {
      // Collect all consecutive travel intervals (these form a route)
      const travelPoints = []
      let travelStart = i
      let sentimentSum = 0
      let sentimentCount = 0
      
      while (i < sorted.length && (sorted[i].location_name === 'Traveling' || sorted[i].location_type === 'traveling')) {
        travelPoints.push([sorted[i].longitude, sorted[i].latitude])
        sentimentSum += sorted[i].sentiment_score
        sentimentCount++
        i++
      }
      
      // Create a single path with all route points (for curved route visualization)
      if (travelPoints.length > 1) {
        // Calculate average sentiment for the entire route
        const avgSentiment = sentimentCount > 0 ? sentimentSum / sentimentCount : 0
        
        paths.push({
          path: travelPoints, // All route points in order
          startTime: sorted[travelStart].start_time,
          endTime: sorted[travelStart + travelPoints.length - 1].end_time,
          sentiment: avgSentiment
        })
      }
    } else {
      // Regular location - check if next is different location (shouldn't happen with proper data)
      if (i < sorted.length - 1) {
        const next = sorted[i + 1]
        const nextIsTravel = next.location_name === 'Traveling' || next.location_type === 'traveling'
        
        if (!nextIsTravel && (current.latitude !== next.latitude || current.longitude !== next.longitude)) {
          // Direct location change (shouldn't happen often, but handle it)
          paths.push({
            source: [current.longitude, current.latitude],
            target: [next.longitude, next.latitude],
            startTime: current.end_time,
            endTime: next.start_time,
            sentiment: next.sentiment_score
          })
        }
      }
      i++
    }
  }
  
  return paths
}

/**
 * Create path segments from time increments
 * Colors paths based on travel-time sentiment, not destination
 */
export function createTravelPathsFromIncrements(increments) {
  const paths = []
  
  for (let i = 0; i < increments.length - 1; i++) {
    const current = increments[i]
    const next = increments[i + 1]
    
    // Only create path if locations are different
    if (current.latitude !== next.latitude || current.longitude !== next.longitude) {
      // Use the sentiment during travel (current increment if traveling, or average)
      const travelSentiment = current.is_traveling ? current.sentiment_score : 
                             (current.sentiment_score + next.sentiment_score) / 2
      
      paths.push({
        source: [current.longitude, current.latitude],
        target: [next.longitude, next.latitude],
        timestamp: current.timestamp,
        nextTimestamp: next.timestamp,
        sentiment: travelSentiment, // Travel-time sentiment
        is_traveling: current.is_traveling || next.is_traveling
      })
    }
  }
  
  return paths
}

/**
 * Filter increments to only show dots where person stayed >= minConsecutive increments
 */
export function filterIncrementsForDots(increments, minConsecutive = 2) {
  const locationGroups = []
  let currentGroup = null
  
  for (let i = 0; i < increments.length; i++) {
    const increment = increments[i]
    
    // Skip traveling increments for dots
    if (increment.is_traveling) {
      if (currentGroup) {
        locationGroups.push(currentGroup)
        currentGroup = null
      }
      continue
    }
    
    const locationKey = `${increment.latitude.toFixed(6)},${increment.longitude.toFixed(6)}`
    
    if (!currentGroup || currentGroup.locationKey !== locationKey) {
      // Start new group
      if (currentGroup) {
        locationGroups.push(currentGroup)
      }
      currentGroup = {
        locationKey,
        location: {
          latitude: increment.latitude,
          longitude: increment.longitude,
          name: increment.location_name,
          type: increment.location_type
        },
        intervals: [increment],
        startTime: increment.timestamp
      }
    } else {
      // Add to current group
      currentGroup.intervals.push(increment)
    }
  }
  
  // Add last group
  if (currentGroup) {
    locationGroups.push(currentGroup)
  }
  
  // Filter groups that have >= minConsecutive increments
  return locationGroups
    .filter(group => group.intervals.length >= minConsecutive)
    .map(group => {
      // Calculate average sentiment for the stay
      const avgSentiment = group.intervals.reduce((sum, inc) => sum + inc.sentiment_score, 0) / group.intervals.length
      const totalDuration = group.intervals.length * 5 // 5 minutes per increment
      
      return {
        location: group.location,
        intervals: group.intervals,
        avgSentiment,
        totalDuration,
        startTime: group.startTime,
        endTime: group.intervals[group.intervals.length - 1].timestamp
      }
    })
}

