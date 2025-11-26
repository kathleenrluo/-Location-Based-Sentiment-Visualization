/**
 * Utilities for creating striped visualizations (dots and polygons)
 */

/**
 * Create striped dot data for multiple intervals at same location
 * Returns data for rendering multiple concentric circles or pie segments
 */
export function createStripedDotData(location, intervals) {
  if (intervals.length === 1) {
    return {
      type: 'simple',
      position: [location.longitude, location.latitude],
      sentiment: intervals[0].sentiment_score,
      interval: intervals[0]
    }
  }
  
  // Multiple intervals - create striped representation
  // Sort intervals by start time
  const sorted = [...intervals].sort((a, b) => a.start_time - b.start_time)
  const totalDuration = sorted.reduce((sum, i) => sum + i.duration_minutes, 0)
  
  // Create pie segments based on duration
  const segments = sorted.map((interval, index) => {
    const startAngle = sorted.slice(0, index).reduce((sum, i) => 
      sum + (i.duration_minutes / totalDuration) * 2 * Math.PI, 0
    )
    const angleSpan = (interval.duration_minutes / totalDuration) * 2 * Math.PI
    
    return {
      interval,
      startAngle,
      endAngle: startAngle + angleSpan,
      sentiment: interval.sentiment_score
    }
  })
  
  return {
    type: 'striped',
    position: [location.longitude, location.latitude],
    segments,
    intervals: sorted,
    totalDuration
  }
}

/**
 * Create striped polygon data for buildings with multiple time intervals
 */
export function createStripedPolygonData(building, intervals) {
  if (intervals.length === 0) {
    return null
  }
  
  // Group intervals by time-of-day for striping
  const timeBuckets = {}
  intervals.forEach(interval => {
    const hour = interval.start_time.getHours()
    const bucket = Math.floor(hour / 3) * 3 // 3-hour buckets
    
    if (!timeBuckets[bucket]) {
      timeBuckets[bucket] = {
        bucket,
        intervals: [],
        avgSentiment: 0,
        totalDuration: 0
      }
    }
    timeBuckets[bucket].intervals.push(interval)
    timeBuckets[bucket].totalDuration += interval.duration_minutes
  })
  
  // Calculate average sentiment per bucket
  Object.values(timeBuckets).forEach(bucket => {
    const sum = bucket.intervals.reduce((acc, i) => acc + i.sentiment_score, 0)
    bucket.avgSentiment = sum / bucket.intervals.length
  })
  
  // Sort buckets by time
  const sortedBuckets = Object.values(timeBuckets).sort((a, b) => a.bucket - b.bucket)
  const totalDuration = sortedBuckets.reduce((sum, b) => sum + b.totalDuration, 0)
  
  return {
    building,
    buckets: sortedBuckets,
    totalDuration
  }
}

