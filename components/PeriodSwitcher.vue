<template>
  <div class="space-y-3">
    <div class="flex gap-1 bg-[var(--bg-surface)] rounded-xl p-1 border border-[var(--border)]">
      <button
        v-for="p in (['week', 'month', 'year'] as const)"
        :key="p"
        :class="[
          'press tab flex-1 py-2 rounded-lg text-sm font-medium capitalize',
          period === p
            ? 'bg-[var(--text)] text-[var(--bg)] shadow-sm'
            : 'text-[var(--text-muted)]',
        ]"
        @click="setPeriod(p)"
      >
        {{ p }}
      </button>
    </div>

    <div class="flex items-center justify-between">
      <button
        class="press w-10 h-10 rounded-lg bg-[var(--bg-surface)] border border-[var(--border)] text-[var(--text-muted)] flex items-center justify-center arrow"
        aria-label="Previous period"
        @click="prev"
      >
        ‹
      </button>
      <button
        class="press text-sm font-medium text-[var(--text)] px-3 py-1 rounded-lg"
        :title="`Jump to current ${period}`"
        @click="today"
      >
        {{ label }}
      </button>
      <button
        class="press w-10 h-10 rounded-lg bg-[var(--bg-surface)] border border-[var(--border)] text-[var(--text-muted)] flex items-center justify-center arrow"
        aria-label="Next period"
        @click="next"
      >
        ›
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
const { period, label, setPeriod, prev, next, today } = usePeriod()
</script>

<style scoped>
.tab {
  transition:
    background-color 220ms var(--ease-out),
    color 180ms var(--ease-out),
    transform 160ms var(--ease-out),
    box-shadow 220ms var(--ease-out);
}
.arrow {
  transition:
    color 180ms var(--ease-out),
    background-color 180ms var(--ease-out),
    transform 160ms var(--ease-out);
}
@media (hover: hover) and (pointer: fine) {
  .tab:hover { color: var(--text); }
  .arrow:hover { color: var(--text); background-color: var(--bg-input); }
}
</style>
