<template>
  <div id="app" class="container-fluid p-0">
    <div class="row g-0">
      <!-- Main Map Area -->
      <div class="col-12">
        <MapVisualization />
      </div>
    </div>
  </div>
</template>

<script>
import MapVisualization from './components/MapVisualization.vue'

export default {
  name: 'App',
  components: {
    MapVisualization
  }
}
</script>

<style>
#app {
  width: 100vw;
  height: 100vh;
  margin: 0;
  padding: 0;
}

body {
  margin: 0;
  padding: 0;
  overflow: hidden;
}
</style>

