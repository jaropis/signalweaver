<template>
  <Teleport to="body">
    <div
      v-if="visible"
      class="floating-window"
      :style="windowStyle"
      @mousedown="bringToFront"
    >
      <!-- Title Bar -->
      <div
        class="floating-window-header"
        @mousedown.prevent="startDrag"
      >
        <span class="floating-window-title">{{ title }}</span>
        <button
          class="floating-window-close"
          @click="$emit('close')"
          @mousedown.stop
        >
          ✕
        </button>
      </div>

      <!-- Content -->
      <div class="floating-window-content">
        <slot></slot>
      </div>

      <!-- Resize Handle -->
      <div
        class="floating-window-resize"
        @mousedown.prevent="startResize"
      ></div>
    </div>
  </Teleport>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'

const props = defineProps({
  title: {
    type: String,
    default: 'Window'
  },
  visible: {
    type: Boolean,
    default: false
  },
  initialWidth: {
    type: Number,
    default: 750
  },
  initialHeight: {
    type: Number,
    default: 800
  },
  minWidth: {
    type: Number,
    default: 400
  },
  minHeight: {
    type: Number,
    default: 400
  }
})

const emit = defineEmits(['close'])

// Window position and size
const x = ref(100)
const y = ref(100)
const width = ref(props.initialWidth)
const height = ref(props.initialHeight)
const zIndex = ref(1000)

// Drag state
const isDragging = ref(false)
const dragStartX = ref(0)
const dragStartY = ref(0)
const dragOffsetX = ref(0)
const dragOffsetY = ref(0)

// Resize state
const isResizing = ref(false)
const resizeStartX = ref(0)
const resizeStartY = ref(0)
const resizeStartWidth = ref(0)
const resizeStartHeight = ref(0)

const windowStyle = computed(() => ({
  left: `${x.value}px`,
  top: `${y.value}px`,
  width: `${width.value}px`,
  height: `${height.value}px`,
  zIndex: zIndex.value
}))

function bringToFront() {
  zIndex.value = 1001
}

function startDrag(event) {
  isDragging.value = true
  dragStartX.value = event.clientX
  dragStartY.value = event.clientY
  dragOffsetX.value = x.value
  dragOffsetY.value = y.value
  bringToFront()
}

function onDrag(event) {
  if (!isDragging.value) return

  const deltaX = event.clientX - dragStartX.value
  const deltaY = event.clientY - dragStartY.value

  x.value = Math.max(0, dragOffsetX.value + deltaX)
  y.value = Math.max(0, dragOffsetY.value + deltaY)
}

function stopDrag() {
  isDragging.value = false
}

function startResize(event) {
  isResizing.value = true
  resizeStartX.value = event.clientX
  resizeStartY.value = event.clientY
  resizeStartWidth.value = width.value
  resizeStartHeight.value = height.value
  bringToFront()
}

function onResize(event) {
  if (!isResizing.value) return

  const deltaX = event.clientX - resizeStartX.value
  const deltaY = event.clientY - resizeStartY.value

  width.value = Math.max(props.minWidth, resizeStartWidth.value + deltaX)
  height.value = Math.max(props.minHeight, resizeStartHeight.value + deltaY)
}

function stopResize() {
  isResizing.value = false
}

function onMouseMove(event) {
  onDrag(event)
  onResize(event)
}

function onMouseUp() {
  stopDrag()
  stopResize()
}

// Center the window on mount
onMounted(() => {
  x.value = Math.max(50, (window.innerWidth - width.value) / 2)
  y.value = Math.max(50, (window.innerHeight - height.value) / 3)

  document.addEventListener('mousemove', onMouseMove)
  document.addEventListener('mouseup', onMouseUp)
})

onUnmounted(() => {
  document.removeEventListener('mousemove', onMouseMove)
  document.removeEventListener('mouseup', onMouseUp)
})
</script>

<style scoped>
.floating-window {
  position: fixed;
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
  box-shadow: var(--shadow-lg);
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.floating-window-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 10px 16px;
  background: #fafafa;
  border-bottom: 1px solid var(--color-border);
  cursor: move;
  user-select: none;
}

.floating-window-title {
  font-weight: 600;
  font-size: 0.85rem;
  color: var(--color-text-primary);
}

.floating-window-close {
  background: transparent;
  border: none;
  color: var(--color-text-secondary);
  width: 28px;
  height: 28px;
  border-radius: var(--radius-sm);
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 14px;
  padding: 0;
  transition: all 0.2s;
}

.floating-window-close:hover {
  background: rgba(0, 0, 0, 0.05);
  color: var(--color-text-primary);
}

.floating-window-content {
  flex: 1;
  overflow: auto;
  padding: 16px;
}

.floating-window-resize {
  position: absolute;
  bottom: 0;
  right: 0;
  width: 16px;
  height: 16px;
  cursor: nwse-resize;
}

.floating-window-resize::after {
  content: '';
  position: absolute;
  bottom: 4px;
  right: 4px;
  width: 6px;
  height: 6px;
  border-right: 2px solid var(--color-border);
  border-bottom: 2px solid var(--color-border);
}
</style>
