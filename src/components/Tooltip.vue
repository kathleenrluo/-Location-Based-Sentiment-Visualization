<template>
  <div v-if="visible" class="tooltip" :style="tooltipStyle">
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
              <span class="tooltip-label">{{ formatLabel(detailKey) }}:</span>
              <span class="tooltip-value" :style="detailKey === 'sentiment_score' || detailKey === 'avgSentiment' ? { color: getStressColor(value) } : {}">
                {{ formatValue(detailKey, value) }}
              </span>
            </div>
          </template>
        </template>
      </div>
    </div>
  </div>
</template>

<script>
import { computed } from 'vue'

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
    const tooltipStyle = computed(() => {
      // Position relative to viewport
      return {
        left: `${props.x + 10}px`,
        top: `${props.y + 10}px`,
        position: 'fixed' // Use fixed positioning for viewport-relative coordinates
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
      if (key === 'sentiment_score' || key === 'avgSentiment') {
        return value.toFixed(2)
      }
      if (key === 'duration_minutes' || key === 'totalDuration') {
        const hours = Math.floor(value / 60)
        const minutes = value % 60
        if (hours > 0) {
          return `${hours}h ${minutes}m`
        }
        return `${minutes}m`
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
      tooltipStyle,
      formatLabel,
      formatValue,
      formatTime,
      formatSentiment,
      formatActivity,
      getStressColor
    }
  }
}
</script>

<style scoped>
.tooltip {
  position: fixed;
  background: white;
  border: 1px solid #ccc;
  border-radius: 4px;
  padding: 8px 12px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.15);
  z-index: 2000;
  pointer-events: none;
  max-width: 300px;
  font-size: 12px;
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

