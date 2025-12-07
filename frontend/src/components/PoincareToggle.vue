<template>
  <button
    class="poincare-toggle"
    :class="{ 'is-open': isOpen }"
    @click="$emit('toggle')"
    :title="isOpen ? 'Close Poincaré Plot' : 'Open Poincaré Plot'"
  >
    <span class="toggle-icon">{{ isOpen ? '−' : '+' }}</span>
    <span class="toggle-text">Poincaré</span>
  </button>
</template>

<script setup>
defineProps({
  isOpen: {
    type: Boolean,
    default: false
  }
})

defineEmits(['toggle'])
</script>

<style scoped>
.poincare-toggle {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  padding: 4px 8px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 11px;
  font-weight: 500;
  transition: all 0.2s ease;
  box-shadow: 0 1px 4px rgba(102, 126, 234, 0.3);
}

.poincare-toggle:hover {
  box-shadow: 0 2px 6px rgba(102, 126, 234, 0.4);
}

.poincare-toggle.is-open {
  background: linear-gradient(135deg, #764ba2 0%, #667eea 100%);
}

.toggle-icon {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 14px;
  height: 14px;
  background: rgba(255, 255, 255, 0.2);
  border-radius: 2px;
  font-size: 12px;
  font-weight: bold;
}

.toggle-text {
  white-space: nowrap;
}
</style>
