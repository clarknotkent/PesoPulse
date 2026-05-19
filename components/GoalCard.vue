<template>
  <div class="goal-row py-5 border-b border-[var(--border)] flex items-center gap-4">
    <!-- Ring -->
    <div class="relative w-16 h-16 shrink-0">
      <svg viewBox="0 0 36 36" class="w-full h-full -rotate-90">
        <circle cx="18" cy="18" r="15.915" fill="none" stroke="var(--border)" stroke-width="3" />
        <circle
          cx="18" cy="18" r="15.915"
          fill="none"
          stroke="#10b981"
          stroke-width="3"
          stroke-linecap="round"
          :stroke-dasharray="`${Math.min(100, goal.pctComplete)} 100`"
          class="transition-all duration-500"
        />
      </svg>
      <div class="absolute inset-0 flex items-center justify-center">
        <p class="text-[var(--text)] text-[11px] font-semibold tabular-nums">{{ Math.round(goal.pctComplete) }}%</p>
      </div>
    </div>

    <!-- Middle: name + meta -->
    <div class="min-w-0 flex-1">
      <p class="text-[var(--text)] text-sm font-medium truncate">{{ goal.name }}</p>
      <p class="text-[var(--text-subtle)] text-xs mt-0.5 tabular-nums">{{ goal.category }} · {{ goal.daysLeft }}d left</p>
      <p class="text-[var(--text-muted)] text-sm tabular-nums mt-1">
        {{ formatPHP(goal.progress) }}
        <span class="text-[var(--text-subtle)]">/ {{ formatPHP(goal.target) }}</span>
      </p>
    </div>

    <!-- Right: delete -->
    <button
      @click="$emit('delete', goal.id)"
      class="press text-[var(--text-subtle)] hover:text-[var(--c-expense)] w-8 h-8 flex items-center justify-center shrink-0"
      aria-label="Delete goal"
    >
      <Icon name="x" :size="14" />
    </button>
  </div>
</template>

<script setup lang="ts">
interface Goal {
  id: string
  name: string
  target: number
  deadline: string
  category: string
  startDate: string
  progress: number
  pctComplete: number
  daysLeft: number
}

defineProps<{ goal: Goal }>()
defineEmits<{ delete: [id: string] }>()
</script>
