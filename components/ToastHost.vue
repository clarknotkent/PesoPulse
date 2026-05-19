<template>
  <div class="fixed top-4 left-0 right-0 z-[var(--z-toast)] flex flex-col items-center gap-2 px-4 pointer-events-none">
    <TransitionGroup name="toast">
      <div
        v-for="(t, i) in toasts"
        :key="t.id"
        :style="{ '--i': Math.min(i, 5) }"
        :class="[
          'toast-item press pointer-events-auto w-full max-w-sm rounded-xl px-4 py-3 shadow-lg backdrop-blur cursor-pointer select-none',
          toneClass(t.tone),
        ]"
        @click="dismiss(t.id)"
      >
        <p class="font-medium text-sm">
          {{ t.title }}
        </p>
        <p
          v-if="t.message"
          class="text-xs opacity-90 mt-0.5"
        >
          {{ t.message }}
        </p>
      </div>
    </TransitionGroup>
  </div>
</template>

<script setup lang="ts">
import type { ToastTone } from '~/composables/useToast'

const { toasts, dismiss } = useToast()

function toneClass(tone: ToastTone) {
  switch (tone) {
    case 'success':
      return 'bg-emerald-600/90 text-white'
    case 'error':
      return 'bg-red-600/90 text-white'
    case 'warning':
      return 'bg-amber-600/90 text-white'
    default:
      return 'bg-zinc-800/90 text-white'
  }
}
</script>

<style scoped>
.toast-enter-active {
  transition:
    transform 280ms var(--ease-out),
    opacity 240ms var(--ease-out);
  transition-delay: calc(var(--i, 0) * 60ms);
}
.toast-leave-active {
  transition:
    transform 180ms var(--ease-out),
    opacity 160ms var(--ease-out);
  position: absolute;
}
.toast-enter-from {
  opacity: 0;
  transform: translateY(-16px) scale(0.96);
}
.toast-leave-to {
  opacity: 0;
  transform: translateY(-8px) scale(0.97);
}
.toast-move {
  transition: transform 280ms var(--ease-out);
}
</style>
