<template>
  <div>
    <div
      v-if="buckets.length === 0"
      class="text-[var(--text-subtle)] text-sm text-center py-8"
    >
      No data.
    </div>
    <div
      v-else
      class="h-56"
    >
      <Bar
        :data="chartData"
        :options="chartOptions"
      />
    </div>
  </div>
</template>

<script setup lang="ts">
import { Bar } from 'vue-chartjs'
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  BarElement,
  Tooltip,
  Legend,
  type ChartData,
  type ChartOptions,
} from 'chart.js'

const props = defineProps<{
  buckets: { bucket: string, income: number, expense: number }[]
  period: 'week' | 'month' | 'year'
}>()

ChartJS.register(CategoryScale, LinearScale, BarElement, Tooltip, Legend)

function formatLabel(bucket: string): string {
  if (props.period === 'year') {
    const [, m] = bucket.split('-')
    return ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'][parseInt(m, 10) - 1]
  }
  const d = new Date(bucket)
  if (props.period === 'week') {
    return d.toLocaleDateString('en-PH', { weekday: 'short' })
  }
  return String(d.getDate())
}

const chartData = computed<ChartData<'bar'>>(() => ({
  labels: props.buckets.map((b) => formatLabel(b.bucket)),
  datasets: [
    {
      label: 'Income',
      data: props.buckets.map((b) => b.income),
      backgroundColor: '#10b981',
      borderRadius: 4,
    },
    {
      label: 'Expense',
      data: props.buckets.map((b) => b.expense),
      backgroundColor: '#ef4444',
      borderRadius: 4,
    },
  ],
}))

const chartOptions: ChartOptions<'bar'> = {
  responsive: true,
  maintainAspectRatio: false,
  plugins: {
    legend: {
      position: 'bottom',
      labels: { color: '#a1a1aa', boxWidth: 10, boxHeight: 10, padding: 12 },
    },
    tooltip: {
      callbacks: { label: (ctx) => `${ctx.dataset.label}: ${formatPHP(ctx.parsed.y)}` },
    },
  },
  scales: {
    x: { ticks: { color: '#71717a' }, grid: { display: false } },
    y: {
      ticks: { color: '#71717a', callback: (v) => `₱${v}` },
      grid: { color: 'rgba(113,113,122,0.15)' },
    },
  },
}
</script>
