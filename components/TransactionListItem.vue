<template>
  <button
    @click="$emit('select', tx)"
    class="press tx-row w-full bg-[var(--bg-surface)] rounded-xl px-4 py-3 flex items-center justify-between text-left"
  >
    <div class="min-w-0 mr-3">
      <p class="text-[var(--text)] text-sm font-medium truncate">{{ tx.category }}</p>
      <p class="text-[var(--text-subtle)] text-xs truncate">
        <span v-if="showDate" class="tabular-nums">{{ humanizeDate(tx.date) }}</span>
        <span v-if="showDate && tx.notes"> · </span>
        <span v-if="tx.notes">{{ tx.notes }}</span>
        <span v-if="!showDate && !tx.notes" class="opacity-60">—</span>
      </p>
    </div>
    <p
      class="font-medium text-sm shrink-0 tabular-nums"
      :class="tx.type === 'income' ? 'text-[var(--c-income)]' : 'text-[var(--c-expense)]'"
    >{{ tx.type === 'income' ? '+' : '-' }}{{ formatPHP(tx.amount) }}</p>
  </button>
</template>

<script setup lang="ts">
import { humanizeDate } from '~/utils/dateLabel'

export interface Transaction {
  id: string
  userId: string
  amount: number
  type: 'income' | 'expense'
  date: string
  category: string
  notes?: string | null
}

withDefaults(
  defineProps<{ tx: Transaction; showDate?: boolean }>(),
  { showDate: true },
)

defineEmits<{ select: [tx: Transaction] }>()
</script>

<style scoped>
.tx-row {
  transition:
    background-color 200ms var(--ease-out),
    transform 160ms var(--ease-out);
  will-change: transform;
}
@media (hover: hover) and (pointer: fine) {
  .tx-row:hover {
    background-color: var(--bg-input);
  }
}
</style>
