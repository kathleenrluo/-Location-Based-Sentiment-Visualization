<template>
  <div class="timeline-slider">
    <div class="timeline-header">
      <h6 class="timeline-title">Timeline</h6>
      <div class="current-time-info">
        <div class="current-time">{{ formatTime(currentTime) }}</div>
        <div v-if="currentSentiment !== null" class="current-sentiment">
          Stress: {{ formatSentiment(currentSentiment) }}
        </div>
      </div>
    </div>
    <div class="slider-container">
      <input
        type="range"
        :min="0"
        :max="maxIndex"
        :value="currentIndex"
        @input="handleSliderChange"
        class="slider"
        :style="{ background: sliderBackground }"
      />
      <!-- Removed duplicate marker - using slider thumb instead -->
    </div>
    <div class="time-labels">
      <span class="time-label">{{ formatTime(startTime) }}</span>
      <span class="time-label">{{ formatTime(endTime) }}</span>
    </div>
  </div>
</template>

<script>
import { computed } from 'vue'

export default {
  name: 'TimelineSlider',
  props: {
    currentTime: {
      type: Date,
      required: true
    },
    startTime: {
      type: Date,
      required: true
    },
    endTime: {
      type: Date,
      required: true
    },
    currentIndex: {
      type: Number,
      required: true
    },
    maxIndex: {
      type: Number,
      required: true
    },
    currentSentiment: {
      type: Number,
      default: null
    },
    timeIncrements: {
      type: Array,
      default: () => []
    }
  },
  emits: ['update:currentTime', 'update:currentIndex'],
  setup(props, { emit }) {
    const formatTime = (time) => {
      if (!time) return ''
      if (time instanceof Date) {
        return time.toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit' })
      }
      return new Date(time).toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit' })
    }

    const handleSliderChange = (event) => {
      // Snap to nearest 5-minute increment
      let newIndex = parseInt(event.target.value)
      
      // Always snap to the exact index (since we're using 5-minute increments)
      // The slider should already be constrained to valid indices
      newIndex = Math.max(0, Math.min(newIndex, props.maxIndex))
      
      emit('update:currentIndex', newIndex)
    }
    
    const formatSentiment = (sentiment) => {
      if (sentiment === null || sentiment === undefined) return 'N/A'
      // Return the numeric value with 2 decimal places
      return sentiment.toFixed(2)
    }

    const sliderBackground = computed(() => {
      // Create gradient background showing progress
      const percentage = (props.currentIndex / props.maxIndex) * 100
      return `linear-gradient(to right, #007bff 0%, #007bff ${percentage}%, #ddd ${percentage}%, #ddd 100%)`
    })

    return {
      formatTime,
      handleSliderChange,
      sliderBackground,
      formatSentiment
    }
  }
}
</script>

<style scoped>
.timeline-slider {
  background: white;
  padding: 16px;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.15);
  margin-bottom: 16px;
}

.timeline-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.timeline-title {
  margin: 0;
  font-size: 14px;
  font-weight: bold;
  color: #333;
}

.current-time-info {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
}

.current-time {
  font-size: 16px;
  font-weight: bold;
  color: #007bff;
}

.current-sentiment {
  font-size: 12px;
  color: #666;
  margin-top: 2px;
}

.slider-container {
  position: relative;
  margin: 20px 0;
}

.slider {
  width: 100%;
  height: 6px;
  border-radius: 3px;
  outline: none;
  -webkit-appearance: none;
  appearance: none;
  cursor: pointer;
}

.slider::-webkit-slider-thumb {
  -webkit-appearance: none;
  appearance: none;
  width: 20px;
  height: 20px;
  border-radius: 50%;
  background: #007bff;
  border: 3px solid white;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
  cursor: pointer;
  position: relative;
  z-index: 2;
}

.slider::-moz-range-thumb {
  width: 20px;
  height: 20px;
  border-radius: 50%;
  background: #007bff;
  border: 3px solid white;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
  cursor: pointer;
  position: relative;
  z-index: 2;
}

/* Removed duplicate marker styles - using slider thumb instead */

.time-labels {
  display: flex;
  justify-content: space-between;
  font-size: 11px;
  color: #666;
  margin-top: 4px;
}

.time-label {
  font-weight: 500;
}
</style>

