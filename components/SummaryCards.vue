<template>
  <div class="grid grid-cols-1 sm:grid-cols-[1.4fr_1fr] gap-6 items-stretch">
    <!-- Net (prominent, no card) -->
    <div class="py-1">
      <p class="label">
        Net
      </p>
      <p
        class="text-4xl font-semibold tabular-nums tracking-tightest mt-2"
        :class="net >= 0 ? 'text-[var(--text)]' : 'text-[var(--c-expense)]'"
      >
        {{ formatPHP(net) }}
      </p>
      <p
        v-if="deltaNet !== undefined"
        class="text-xs mt-2 tabular-nums"
        :class="deltaNet >= 0 ? 'text-[var(--c-income)]' : 'text-[var(--c-expense)]'"
      >
        {{ deltaNet >= 0 ? '↑' : '↓' }} {{ formatPHP(Math.abs(deltaNet)) }} vs prev period
      </p>
    </div>

    <!-- Mini stats stack — divided rows, no boxes -->
    <div class="divide-y divide-[var(--border)] border-y border-[var(--border)]">
      <div class="flex items-baseline justify-between py-3">
        <span class="text-[var(--text-muted)] text-sm">Income</span>
        <div class="text-right">
          <p class="text-[var(--c-income)] font-semibold tabular-nums">
            {{ formatPHP(income) }}
          </p>
          <p
            v-if="deltaIncome !== undefined"
            class="text-[10px] tabular-nums"
            :class="deltaIncome >= 0 ? 'text-[var(--c-income)]' : 'text-[var(--c-expense)]'"
          >
            {{ deltaIncome >= 0 ? '↑' : '↓' }} {{ formatPHP(Math.abs(deltaIncome)) }}
          </p>
        </div>
      </div>
      <div class="flex items-baseline justify-between py-3">
        <span class="text-[var(--text-muted)] text-sm">Expense</span>
        <div class="text-right">
          <p class="text-[var(--c-expense)] font-semibold tabular-nums">
            {{ formatPHP(expense) }}
          </p>
          <p
            v-if="deltaExpense !== undefined"
            class="text-[10px] tabular-nums"
            :class="deltaExpense <= 0 ? 'text-[var(--c-income)]' : 'text-[var(--c-expense)]'"
          >
            {{ deltaExpense >= 0 ? '↑' : '↓' }} {{ formatPHP(Math.abs(deltaExpense)) }}
          </p>
        </div>
      </div>
      <div class="flex items-baseline justify-between py-3">
        <span class="text-[var(--text-muted)] text-sm">Savings rate</span>
        <p class="text-[var(--text)] font-semibold tabular-nums">
          {{ savingsRate.toFixed(1) }}%
        </p>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
defineProps<{
  income: number
  expense: number
  net: number
  savingsRate: number
  deltaIncome?: number
  deltaExpense?: number
  deltaNet?: number
}>()
</script>
