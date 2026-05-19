<template>
  <div class="bg-[var(--bg-surface)] rounded-2xl p-5">
    <!-- Empty state -->
    <div v-if="!hasCap && !loading">
      <p class="text-[var(--text-muted)] text-xs uppercase tracking-widest mb-1">
        {{ periodTitle }}
      </p>
      <p class="text-[var(--text)] font-medium mb-3">
        No {{ periodAdj }} budget yet
      </p>
      <p class="text-[var(--text-subtle)] text-xs">
        Set a total cap below to track your pace.
      </p>
    </div>

    <!-- Loading -->
    <div
      v-else-if="loading && !data"
      class="text-[var(--text-subtle)] text-sm py-2"
    >
      Loading…
    </div>

    <!-- Widget -->
    <div v-else-if="data">
      <div class="flex items-baseline justify-between mb-1">
        <p class="text-[var(--text-muted)] text-xs uppercase tracking-widest">
          {{ periodLabel }}
        </p>
        <span
          :class="[
            'text-[10px] font-medium px-2 py-0.5 rounded-full',
            paceClasses,
          ]"
        >{{ paceLabel }}</span>
      </div>

      <p
        class="text-3xl font-bold tabular-nums"
        :class="remaining < 0 ? 'text-[var(--c-expense)]' : 'text-[var(--text)]'"
      >
        {{ formatPHP(remaining) }}
      </p>
      <p class="text-[var(--text-subtle)] text-xs mt-0.5">
        {{ formatPHP(spent) }} / {{ formatPHP(cap) }} · {{ timeLeftLabel }}
        <span
          v-if="rollover > 0"
          class="text-[var(--c-income)]"
        >· +{{ formatPHP(rollover) }} rollover</span>
      </p>

      <!-- Time elapsed bar -->
      <div class="mt-3">
        <div class="flex items-center justify-between text-[10px] text-[var(--text-subtle)] mb-1">
          <span>Time</span>
          <span class="tabular-nums">{{ Math.round(pctTime) }}%</span>
        </div>
        <div class="h-1.5 bg-[var(--bg-input)] rounded-full overflow-hidden">
          <div
            class="bar bar-time h-full bg-[var(--text-subtle)] rounded-full"
            :class="{ ready: animateReady }"
            :style="{ width: `${pctTime}%` }"
          />
        </div>
      </div>

      <!-- Budget used bar -->
      <div class="mt-2">
        <div class="flex items-center justify-between text-[10px] text-[var(--text-subtle)] mb-1">
          <span>Spent</span>
          <span class="tabular-nums">{{ Math.round(pctBudget) }}%</span>
        </div>
        <div class="h-1.5 bg-[var(--bg-input)] rounded-full overflow-hidden">
          <div
            class="bar h-full rounded-full"
            :class="[barColor, { ready: animateReady }]"
            :style="{ width: `${Math.min(100, pctBudget)}%` }"
          />
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
type Period = 'day' | 'week' | 'month'

interface BudgetView {
  period: Period
  anchor: string
  range: { from: string, to: string }
  total: { limit: number, spent: number, rollover: number, remaining: number, overspent: boolean }
  categories: { category: string | null, limit: number, spent: number, rollover: number, remaining: number, overspent: boolean }[]
}

const props = defineProps<{
  period: Period
  anchor: string
}>()

const { user } = useAuth()
const api = useApi()

const data = ref<BudgetView | null>(null)
const loading = ref(false)

async function load() {
  const uid = user.value?.uid
  if (!uid) return
  loading.value = true
  try {
    data.value = await api.get<BudgetView>(
      `/api/budgets/${uid}?period=${props.period}&anchor=${props.anchor}`,
    )
  }
  catch (e) {
    void e
  }
  finally {
    loading.value = false
  }
}

const periodTitle = computed(() => {
  if (props.period === 'day') return 'Today'
  if (props.period === 'week') return 'This Week'
  return 'This Month'
})

const periodAdj = computed(() => {
  if (props.period === 'day') return 'daily'
  if (props.period === 'week') return 'weekly'
  return 'monthly'
})

const cap = computed(() => (data.value ? data.value.total.limit + data.value.total.rollover : 0))
const rollover = computed(() => data.value?.total.rollover ?? 0)
const spent = computed(() => data.value?.total.spent ?? 0)
const remaining = computed(() => cap.value - spent.value)
const hasCap = computed(() => cap.value > 0)

const periodLabel = computed(() => {
  if (!data.value) return periodTitle.value
  const from = new Date(data.value.range.from)
  const to = new Date(data.value.range.to)
  const fromS = from.toLocaleDateString('en-PH', { month: 'short', day: 'numeric' })
  if (props.period === 'day') {
    return `${fromS}, ${from.getFullYear()}`
  }
  const toS = to.toLocaleDateString('en-PH', { month: 'short', day: 'numeric' })
  if (props.period === 'week') return `Week of ${fromS}–${toS}`
  return from.toLocaleDateString('en-PH', { month: 'long', year: 'numeric' })
})

const timeLeftLabel = computed(() => {
  if (!data.value) return ''
  const today = new Date()
  today.setHours(0, 0, 0, 0)
  const to = new Date(data.value.range.to)
  const diff = Math.ceil((to.getTime() - today.getTime()) / 86400000) + 1
  if (props.period === 'day') {
    if (diff === 1) return 'Today'
    if (diff <= 0) return 'Day ended'
    return `${diff} days ahead`
  }
  if (diff <= 0) return props.period === 'week' ? 'Week ended' : 'Month ended'
  if (diff === 1) return 'Last day'
  return `${diff} days left`
})

const pctBudget = computed(() => (cap.value <= 0 ? 0 : (spent.value / cap.value) * 100))
const pctTime = computed(() => {
  if (!data.value) return 0
  const from = new Date(data.value.range.from).getTime()
  const to = new Date(data.value.range.to).getTime() + 86400000
  const now = Date.now()
  if (now < from) return 0
  if (now > to) return 100
  return ((now - from) / (to - from)) * 100
})

const paceLabel = computed(() => {
  if (pctBudget.value > 100) return 'Over'
  const delta = pctBudget.value - pctTime.value
  if (delta > 15) return 'Spending fast'
  if (delta < -15) return 'Coasting'
  return 'On track'
})

const paceClasses = computed(() => {
  const label = paceLabel.value
  if (label === 'Over') return 'bg-red-900/60 text-[var(--c-expense)]'
  if (label === 'Spending fast') return 'bg-amber-900/60 text-[var(--c-warn)]'
  if (label === 'Coasting') return 'bg-sky-900/60 text-[var(--c-info)]'
  return 'bg-emerald-900/60 text-[var(--c-income)]'
})

const barColor = computed(() => {
  if (pctBudget.value > 100) return 'bg-red-500'
  if (pctBudget.value > 80) return 'bg-amber-400'
  return 'bg-emerald-500'
})

const animateReady = ref(false)

defineExpose({ refresh: load })

watch(() => [props.period, props.anchor], load, { immediate: true })

watch(data, (val) => {
  if (val && !animateReady.value) {
    requestAnimationFrame(() => requestAnimationFrame(() => {
      animateReady.value = true
    }))
  }
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
.bar-time.ready {
  transition: width 700ms var(--ease-in-out);
}
</style>
