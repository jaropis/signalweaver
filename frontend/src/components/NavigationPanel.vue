<template>
  <div class="panel">
    <h3>🧭 Navigation</h3>
    <div class="form-group">
      <label>Navigate through the signal</label>
      <div class="button-group">
        <button
          @click="moveLeft"
          :disabled="store.loading"
        >
          ← Move Left
        </button>
        <button
          @click="moveRight"
          :disabled="store.loading"
        >
          Move Right →
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { useECGStore } from '../stores/ecg'

const store = useECGStore()

async function moveLeft() {
  await store.navigate('left')
}

async function moveRight() {
  await store.navigate('right')
}
</script>
