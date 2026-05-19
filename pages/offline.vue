<template>
  <div class="min-h-[100dvh] bg-[var(--bg)] text-[var(--text)] flex items-center justify-center px-4 relative overflow-hidden">
    <div class="absolute -top-32 -left-20 w-96 h-96 rounded-full bg-emerald-500/10 blur-3xl pointer-events-none" />
    <div class="absolute -bottom-32 -right-20 w-96 h-96 rounded-full bg-emerald-500/5 blur-3xl pointer-events-none" />

    <div class="w-full max-w-sm relative text-center space-y-5">
      <div class="flex justify-center">
        <Logo />
      </div>

      <div class="space-y-2">
        <h1 class="text-[var(--text)] text-2xl font-semibold tracking-tightest">
          You're offline
        </h1>
        <p class="text-[var(--text-muted)] text-sm leading-relaxed">
          PesoPulse needs a connection to sync your transactions. Reconnect and retry.
        </p>
      </div>

      <button
        class="press inline-flex items-center justify-center gap-2 bg-emerald-500 text-white font-medium py-3 px-6 rounded-lg text-sm"
        @click="retry"
      >
        <Icon
          name="recurring"
          :size="14"
        />
        Retry
      </button>

      <p class="text-[var(--text-subtle)] text-[10px] tabular-nums">
        Last attempt: {{ stamp }}
      </p>
    </div>
  </div>
</template>

<script setup lang="ts">
definePageMeta({ layout: false })

const stamp = ref('')

function refreshStamp() {
  stamp.value = new Date().toLocaleTimeString('en-PH', { hour: '2-digit', minute: '2-digit' })
}

function retry() {
  if (import.meta.client) {
    if (navigator.onLine) {
      window.location.assign('/dashboard')
    }
    else {
      refreshStamp()
    }
  }
}

onMounted(() => {
  refreshStamp()
  window.addEventListener('online', () => {
    window.location.assign('/dashboard')
  })
})
</script>
