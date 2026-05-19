<template>
  <div class="budget-row py-4 border-b border-[var(--border)]">
    <div class="flex items-baseline justify-between gap-3 mb-2">
      <div class="min-w-0 flex-1">
        <p class="text-[var(--text)] text-sm font-medium truncate">
          {{ label }}
        </p>
        <p
          v-if="rollover > 0"
          class="text-[var(--c-income)] text-[10px] tabular-nums mt-0.5"
        >
          +{{ formatPHP(rollover) }} rollover
        </p>
      </div>
      <div class="flex items-center gap-3 shrink-0">
        <span class="text-[var(--text-muted)] text-xs tabular-nums">
          {{ formatPHP(spent) }} / {{ formatPHP(limit + rollover) }}
        </span>
        <button
          v-if="editable"
          class="press text-[var(--text-subtle)] hover:text-[var(--text)] w-7 h-7 flex items-center justify-center -mr-1"
          aria-label="Edit budget"
          @click="$emit('edit')"
        >
          <Icon
            name="edit"
            :size="14"
          />
        </button>
      </div>
    </div>

    <div class="h-1.5 bg-[var(--bg-input)] rounded-full overflow-hidden">
      <div
        class="bar h-full rounded-full"
        :class="[barColor, { ready: animateReady }]"
        :style="{ width: `${Math.min(100, pct)}%` }"
      />
    </div>

    <p
      v-if="overspent"
      class="text-[var(--c-expense)] text-[10px] mt-1.5 tabular-nums"
    >
      Over by {{ formatPHP(spent - (limit + rollover)) }}
    </p>
  </div>
</template>

<script setup lang="ts">
const props = defineProps<{
  label: string
  limit: number
  spent: number
  rollover: number
  overspent: boolean
  editable?: boolean
}>()

defineEmits<{ edit: [] }>()

const effective = computed(() => props.limit + props.rollover)
const pct = computed(() => (effective.value <= 0 ? 0 : (props.spent / effective.value) * 100))
const barColor = computed(() => {
  if (props.overspent) return 'bg-red-500'
  if (pct.value >= 80) return 'bg-amber-400'
  return 'bg-emerald-500'
})

const animateReady = ref(false)
onMounted(() => {
  requestAnimationFrame(() => requestAnimationFrame(() => {
    animateReady.value = true
  }))
})
</script>

<style scoped>
.bar {
  transition: none;
  will-change: width;
}
.bar.ready {
  transition:
    width 500ms var(--ease-in-out),
    background-color 300ms var(--ease-out);
}
</style>
