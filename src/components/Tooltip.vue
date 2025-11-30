<template>
  <Teleport to="body">
    <div 
      v-if="visible" 
      class="tooltip" 
      :style="tooltipStyle" 
      ref="tooltipElement"
      @mouseenter.stop
      @mouseleave.stop
      @click.stop
    >
      <div class="tooltip-content">
        <h6 class="tooltip-title">{{ title }}</h6>
        <div v-if="details" class="tooltip-details">
        <!-- Show interval breakdown if intervals array exists -->
        <div v-if="details.intervals && Array.isArray(details.intervals) && details.intervals.length > 0" class="intervals-breakdown">
          <div class="breakdown-header">Stress Breakdown:</div>
          <div v-for="(interval, intervalIdx) in details.intervals" :key="`interval-${intervalIdx}`" class="interval-item">
            <div class="interval-time">
              <span class="time-label">Time:</span>
              <span class="time-value">{{ formatTime(interval.start_time) }} - {{ formatTime(interval.end_time) }}</span>
            </div>
            <div class="interval-stress">
              <span class="stress-label">Stress:</span>
              <span class="stress-value" :style="{ color: getStressColor(interval.sentiment_score) }">
                {{ formatSentiment(interval.sentiment_score) }}
              </span>
            </div>
            <div class="interval-activity" v-if="interval.activity">
              <span class="activity-label">Activity:</span>
              <span class="activity-value">{{ formatActivity(interval.activity) }}</span>
            </div>
          </div>
        </div>
        <!-- Show single interval or summary info -->
        <template v-else>
          <template v-for="(value, detailKey) in details" :key="`detail-${detailKey}`">
            <div v-if="detailKey !== 'intervals'" class="tooltip-row">
              <span class="tooltip-label">{{ detailKey }}:</span>
              <span class="tooltip-value" :style="(detailKey === 'sentiment_score' || detailKey === 'avgSentiment' || (typeof value === 'object' && value.sentiment !== undefined)) ? { color: getStressColor(typeof value === 'object' ? value.sentiment : value) } : {}">
                {{ formatValue(detailKey, value) }}
              </span>
            </div>
          </template>
        </template>
        </div>
      </div>
    </div>
  </Teleport>
</template>

<script>
import { computed, ref, watch, nextTick } from 'vue'

export default {
  name: 'Tooltip',
  props: {
    visible: {
      type: Boolean,
      default: false
    },
    x: {
      type: Number,
      default: 0
    },
    y: {
      type: Number,
      default: 0
    },
    title: {
      type: String,
      default: ''
    },
    details: {
      type: Object,
      default: () => ({})
    }
  },
  setup(props) {
    const tooltipElement = ref(null)
    
    const tooltipStyle = computed(() => {
      // Position relative to viewport with smart positioning to avoid going off-screen
      const offset = 10
      const tooltipMaxWidth = 300
      const tooltipMaxHeight = 400
      
      // Get viewport dimensions
      const viewportWidth = window.innerWidth
      const viewportHeight = window.innerHeight
      
      // Calculate initial position (below and to the right of cursor)
      let left = props.x + offset
      let top = props.y + offset
      
      // Adjust horizontal position if tooltip would go off right edge
      if (left + tooltipMaxWidth > viewportWidth) {
        // Try positioning to the left of cursor
        left = props.x - tooltipMaxWidth - offset
        // If that's also off-screen, position at right edge with margin
        if (left < 0) {
          left = viewportWidth - tooltipMaxWidth - offset
        }
      }
      
      // Adjust vertical position if tooltip would go off bottom edge
      if (top + tooltipMaxHeight > viewportHeight) {
        // Try positioning above cursor
        top = props.y - tooltipMaxHeight - offset
        // If that's also off-screen, position at bottom edge with margin
        if (top < 0) {
          top = viewportHeight - tooltipMaxHeight - offset
        }
      }
      
      // Ensure tooltip doesn't go off left or top edges
      if (left < offset) {
        left = offset
      }
      if (top < offset) {
        top = offset
      }
      
      const style = {
        left: `${left}px`,
        top: `${top}px`,
        position: 'fixed',
        display: 'block',
        visibility: 'visible',
        opacity: '1',
        zIndex: '10000'
      }
      return style
    })
    
    watch(() => props.visible, (newVal) => {
      console.log('Tooltip visible prop changed:', newVal)
      if (newVal) {
        // Use nextTick to ensure element is in DOM
        nextTick(() => {
          if (tooltipElement.value) {
            const computed = window.getComputedStyle(tooltipElement.value)
            const rect = tooltipElement.value.getBoundingClientRect()
            console.log('Tooltip element exists in DOM:', tooltipElement.value)
            console.log('Tooltip computed styles:', {
              display: computed.display,
              visibility: computed.visibility,
              opacity: computed.opacity,
              zIndex: computed.zIndex,
              position: computed.position,
              left: computed.left,
              top: computed.top,
              width: computed.width,
              height: computed.height
            })
            console.log('Tooltip bounding rect:', {
              x: rect.x,
              y: rect.y,
              width: rect.width,
              height: rect.height,
              top: rect.top,
              left: rect.left
            })
          } else {
            console.warn('Tooltip element not found in DOM!')
          }
        })
      }
    })

    const formatLabel = (key) => {
      const labels = {
        location_name: 'Location',
        location_type: 'Type',
        sentiment_score: 'Sentiment',
        activity: 'Activity',
        duration_minutes: 'Duration',
        start_time: 'Start Time',
        end_time: 'End Time',
        avgSentiment: 'Avg Sentiment',
        totalDuration: 'Total Duration',
        intervals: 'Visits',
        timeBucket: 'Time Window'
      }
      return labels[key] || key.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())
    }

    const formatValue = (key, value) => {
      // Handle time range keys (e.g., "00:00 - 03:00") with object values
      if (typeof value === 'object' && value !== null && !Array.isArray(value)) {
        // This is a time bucket object with sentiment, count, duration
        const sentiment = value.sentiment !== undefined ? value.sentiment.toFixed(2) : 'N/A'
        const duration = value.duration !== undefined ? formatDuration(value.duration) : ''
        const count = value.count !== undefined ? `${value.count} visits` : ''
        // Format: "sentiment (count) duration"
        const parts = [sentiment]
        if (count) parts.push(`(${count})`)
        if (duration) parts.push(duration)
        return parts.join(' ')
      }
      
      if (key === 'sentiment_score' || key === 'avgSentiment') {
        return value.toFixed(2)
      }
      if (key === 'duration_minutes' || key === 'totalDuration') {
        return formatDuration(value)
      }
      if (key === 'start_time' || key === 'end_time') {
        return formatTime(value)
      }
      if (key === 'timeBucket') {
        return `${value}:00 - ${value + 3}:00`
      }
      if (key === 'intervals' && Array.isArray(value)) {
        return value.length
      }
      return value
    }
    
    const formatDuration = (minutes) => {
      if (!minutes || minutes === 0) return ''
      const hours = Math.floor(minutes / 60)
      const mins = Math.round(minutes % 60)
      if (hours > 0) {
        return mins > 0 ? `${hours}h ${mins}m` : `${hours}h`
      }
      return `${mins}m`
    }

    const formatTime = (time) => {
      if (!time) return 'N/A'
      if (time instanceof Date) {
        return time.toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit' })
      }
      return new Date(time).toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit' })
    }

    const formatSentiment = (sentiment) => {
      if (sentiment === undefined || sentiment === null) return 'N/A'
      return sentiment.toFixed(2)
    }

    const formatActivity = (activity) => {
      return activity.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())
    }

    const getStressColor = (sentiment) => {
      if (sentiment === undefined || sentiment === null) return '#666'
      if (sentiment < -0.1) return '#dc3545' // Red for negative
      if (sentiment > 0.1) return '#28a745' // Green for positive
      return '#ffc107' // Yellow for neutral
    }

    return {
      tooltipElement,
      tooltipStyle,
      formatLabel,
      formatValue,
      formatTime,
      formatSentiment,
      formatActivity,
      getStressColor,
      formatDuration
    }
  }
}
</script>

<style scoped>
.tooltip {
  position: fixed !important;
  background: white !important;
  border: 1px solid #ccc !important;
  border-radius: 4px !important;
  padding: 8px 12px !important;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.15) !important;
  z-index: 10000 !important;
  pointer-events: auto !important;
  max-width: 300px !important;
  max-height: 400px !important;
  font-size: 12px !important;
  display: block !important;
  visibility: visible !important;
  opacity: 1 !important;
  min-width: 150px;
  overflow-y: auto !important;
  overflow-x: hidden !important;
  /* Ensure tooltip can receive all mouse events */
  touch-action: auto !important;
  -webkit-overflow-scrolling: touch;
}

.tooltip-title {
  margin: 0 0 8px 0;
  font-weight: bold;
  font-size: 14px;
  color: #333;
}

.tooltip-details {
  display: flex;
  flex-direction: column;
  gap: 4px;
  max-height: 350px;
  overflow-y: auto;
  overflow-x: hidden;
  /* Ensure scrolling works */
  pointer-events: auto;
  -webkit-overflow-scrolling: touch;
}

.tooltip-row {
  display: flex;
  justify-content: space-between;
  gap: 12px;
}

.tooltip-label {
  font-weight: 500;
  color: #666;
}

.tooltip-value {
  color: #333;
  text-align: right;
}

.intervals-breakdown {
  margin-top: 8px;
  max-height: 300px;
  overflow-y: auto;
  overflow-x: hidden;
}

.breakdown-header {
  font-weight: bold;
  margin-bottom: 8px;
  color: #333;
  border-bottom: 1px solid #eee;
  padding-bottom: 4px;
}

.interval-item {
  margin-bottom: 8px;
  padding: 6px;
  background: #f8f9fa;
  border-radius: 3px;
  border-left: 3px solid #007bff;
}

.interval-item:last-child {
  margin-bottom: 0;
}

.interval-time,
.interval-stress,
.interval-activity {
  display: flex;
  justify-content: space-between;
  margin-bottom: 4px;
  font-size: 11px;
}

.interval-time:last-child,
.interval-stress:last-child,
.interval-activity:last-child {
  margin-bottom: 0;
}

.time-label,
.stress-label,
.activity-label {
  font-weight: 500;
  color: #666;
}

.time-value,
.stress-value,
.activity-value {
  color: #333;
  font-weight: 500;
}
</style>

