<template>
  <button
    class="poincare-toggle"
    :class="{ 'is-open': isOpen }"
    @click="$emit('toggle')"
    :title="isOpen ? 'Close Poincare Plot' : 'Open Poincare Plot'"
  >
    <v-icon size="14">{{ isOpen ? 'mdi-minus' : 'mdi-plus' }}</v-icon>
    <span class="toggle-text">Poincare Plot</span>
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
  gap: 6px;
  padding: 6px 12px;
  background: var(--color-surface);
  color: var(--color-text-secondary);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-sm);
  cursor: pointer;
  font-size: 0.75rem;
  font-weight: 500;
  transition: all 0.2s ease;
}

.poincare-toggle:hover {
  background: #f5f5f5;
  color: var(--color-text-primary);
}

.poincare-toggle.is-open {
  background: var(--color-accent);
  color: white;
  border-color: var(--color-accent);
}

.poincare-toggle.is-open:hover {
  background: var(--color-accent-hover);
}

.toggle-text {
  white-space: nowrap;
}
</style>
