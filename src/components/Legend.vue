<template>
  <div class="legend">
    <div class="card">
      <div class="card-body">
        <h6 class="card-title">Legend</h6>
        
        <!-- Sentiment Colors -->
        <div class="legend-section">
          <div class="legend-title">Sentiment Levels</div>
          <div class="legend-item">
            <div class="legend-color" style="background-color: rgb(255, 0, 0);"></div>
            <span class="legend-label">Negative (High Stress)</span>
            <span class="legend-range">&lt; 0</span>
          </div>
          <div class="legend-item">
            <div class="legend-color" style="background-color: rgb(255, 255, 0);"></div>
            <span class="legend-label">Neutral</span>
            <span class="legend-range">= 0</span>
          </div>
          <div class="legend-item">
            <div class="legend-color" style="background-color: rgb(0, 200, 0);"></div>
            <span class="legend-label">Positive (Low Stress)</span>
            <span class="legend-range">&gt; 0</span>
          </div>
        </div>

        <!-- Map Elements -->
        <div class="legend-section">
          <div class="legend-title">Map Elements</div>
          <div class="legend-item">
            <div class="legend-dot"></div>
            <span class="legend-label">Location Dots</span>
            <span class="legend-desc">Hover for details, click to expand</span>
          </div>
          <div class="legend-item">
            <div class="legend-line"></div>
            <span class="legend-label">Travel Paths</span>
            <span class="legend-desc">Color-coded by travel-time stress</span>
          </div>
          <div class="legend-item">
            <div class="legend-building"></div>
            <span class="legend-label">Buildings</span>
            <span class="legend-desc">Colored by nearby sentiment</span>
          </div>
        </div>

        <!-- View Modes -->
        <div class="legend-section">
          <div class="legend-title">View Modes</div>
          <div class="legend-item">
            <strong>Daily View:</strong> Single day with timeline slider
          </div>
          <div class="legend-item">
            <strong>Lifetime View:</strong> Multi-day aggregation by time-of-day
          </div>
        </div>
        
        <!-- Additional Info -->
        <div class="legend-section">
          <div class="legend-title">Interactions</div>
          <div class="legend-item" style="font-size: 10px;">
            • Hover dots for sentiment details<br>
            • Click dots to expand clusters<br>
            • Click sidebar events to jump timeline
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'Legend'
}
</script>

<style scoped>
.legend {
  position: absolute;
  bottom: 20px;
  right: 20px;
  z-index: 1000;
  max-width: 280px;
}

.card {
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.15);
}

.card-title {
  margin-bottom: 12px;
  font-size: 14px;
  font-weight: bold;
  color: #333;
}

.legend-section {
  margin-bottom: 16px;
}

.legend-section:last-child {
  margin-bottom: 0;
}

.legend-title {
  font-weight: 600;
  font-size: 12px;
  color: #555;
  margin-bottom: 8px;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.legend-item {
  display: flex;
  align-items: center;
  margin-bottom: 6px;
  font-size: 11px;
}

.legend-item:last-child {
  margin-bottom: 0;
}

.legend-color {
  width: 16px;
  height: 16px;
  border-radius: 3px;
  margin-right: 8px;
  border: 1px solid rgba(0, 0, 0, 0.2);
  flex-shrink: 0;
}

.legend-dot {
  width: 12px;
  height: 12px;
  border-radius: 50%;
  background-color: #007bff;
  margin-right: 8px;
  border: 1px solid #000;
  flex-shrink: 0;
}

.legend-line {
  width: 24px;
  height: 3px;
  background: linear-gradient(to right, #dc3545, #ffc107, #28a745);
  margin-right: 8px;
  border-radius: 2px;
  flex-shrink: 0;
}

.legend-building {
  width: 16px;
  height: 12px;
  background-color: #999;
  margin-right: 8px;
  border: 1px solid #666;
  flex-shrink: 0;
}

.legend-label {
  flex: 1;
  color: #333;
  font-weight: 500;
}

.legend-range {
  color: #666;
  font-size: 10px;
  margin-left: auto;
}

.legend-desc {
  color: #666;
  font-size: 10px;
  margin-left: auto;
  font-style: italic;
}
</style>

