<template>
  <div class="bg-[var(--bg-surface)] border border-[var(--border)] rounded-2xl p-5">
    <div class="flex items-center justify-between mb-3">
      <p class="label">Categories</p>
      <div class="flex gap-1 bg-[var(--bg-input)] rounded-lg p-0.5">
        <button
          v-for="t in (['expense', 'income'] as const)"
          :key="t"
          @click="$emit('update:type', t)"
          :class="[
            'press px-3 py-1 rounded-md text-xs font-medium transition capitalize',
            type === t ? 'bg-[var(--text)] text-[var(--bg)]' : 'text-[var(--text-muted)]',
          ]"
        >{{ t }}</button>
      </div>
    </div>

    <p v-if="rows.length === 0" class="text-[var(--text-subtle)] text-sm text-center py-8">
      No {{ type }} data in this period.
    </p>

    <div v-else class="flex flex-col items-center">
      <div class="relative w-48 h-48">
        <Doughnut :data="chartData" :options="chartOptions" />
        <div class="absolute inset-0 flex items-center justify-center pointer-events-none">
          <div class="text-center">
            <p class="text-[var(--text-subtle)] text-[10px] uppercase">Total</p>
            <p class="text-[var(--text)] font-bold text-sm tabular-nums">{{ formatPHP(total) }}</p>
          </div>
        </div>
      </div>

      <ul class="w-full mt-4 space-y-1.5">
        <li
          v-for="(row, idx) in rows"
          :key="row.category"
          class="flex items-center justify-between text-xs"
        >
          <span class="flex items-center gap-2">
            <span class="w-2.5 h-2.5 rounded-full" :style="{ background: colors[idx % colors.length] }"></span>
            <span class="text-[var(--text)]">{{ row.category }}</span>
          </span>
          <span class="text-[var(--text-muted)] tabular-nums">
            {{ formatPHP(row.total) }} · {{ row.pct.toFixed(0) }}%
          </span>
        </li>
      </ul>
    </div>
  </div>
</template>

<script setup lang="ts">
import { Doughnut } from 'vue-chartjs'
import {
  Chart as ChartJS,
  ArcElement,
  Tooltip,
  Legend,
  type ChartData,
  type ChartOptions,
} from 'chart.js'
ChartJS.register(ArcElement, Tooltip, Legend)

const props = defineProps<{
  rows: { category: string; total: number; pct: number }[]
  type: 'income' | 'expense'
}>()

defineEmits<{ 'update:type': [value: 'income' | 'expense'] }>()

const expensePalette = [
  '#ef4444', '#f97316', '#f59e0b', '#eab308', '#ec4899',
  '#f43f5e', '#d97706', '#dc2626', '#c2410c', '#a855f7',
]
const incomePalette = [
  '#10b981', '#14b8a6', '#06b6d4', '#0ea5e9', '#3b82f6',
  '#6366f1', '#22c55e', '#8b5cf6', '#0284c7', '#059669',
]
const colors = computed(() => (props.type === 'income' ? incomePalette : expensePalette))

const total = computed(() => props.rows.reduce((s, r) => s + r.total, 0))

const chartData = computed<ChartData<'doughnut'>>(() => ({
  labels: props.rows.map((r) => r.category),
  datasets: [
    {
      data: props.rows.map((r) => r.total),
      backgroundColor: props.rows.map((_, i) => colors.value[i % colors.value.length]),
      borderWidth: 0,
    },
  ],
}))

const chartOptions: ChartOptions<'doughnut'> = {
  responsive: true,
  maintainAspectRatio: true,
  cutout: '70%',
  plugins: {
    legend: { display: false },
    tooltip: {
      callbacks: {
        label: (ctx) => `${ctx.label}: ${formatPHP(ctx.parsed)}`,
      },
    },
  },
}
</script>
