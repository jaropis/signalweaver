<template>
  <header class="app-header">
    <div class="header-brand">
      <h1>SignalWeaver</h1>
      <span class="header-divider"></span>
      <p>ECG Signal Analysis</p>
    </div>
  </header>
</template>

<script setup>
</script>

<style scoped>
.app-header {
  background: var(--color-surface);
  border-bottom: 1px solid var(--color-border);
  padding: 12px 24px;
  display: flex;
  align-items: center;
}

.header-brand {
  display: flex;
  align-items: center;
  gap: 12px;
}

.header-brand h1 {
  font-size: 1.1rem;
  font-weight: 600;
  color: var(--color-text-primary);
  letter-spacing: -0.01em;
}

.header-divider {
  width: 1px;
  height: 16px;
  background: var(--color-border);
}

.header-brand p {
  font-size: 0.8rem;
  color: var(--color-text-secondary);
  font-weight: 400;
}
</style>
