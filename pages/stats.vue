<template>
  <div class="page">
    <header class="page-header">
      <h1 class="text-[var(--text)] font-medium">Statistics</h1>
    </header>

    <div class="page-body">
      <Transition name="swap" mode="out-in">
        <StatsSkeleton v-if="showSkeleton" key="skeleton" />

        <div v-else key="content">
          <!-- All-time inline strip (no card) -->
          <section class="page-section">
            <div class="flex items-baseline justify-between gap-4 border-b border-[var(--border)] pb-4">
              <div>
                <p class="label">All-time net</p>
                <p
                  class="text-3xl font-semibold tabular-nums tracking-tightest mt-1"
                  :class="(allTime?.net ?? 0) >= 0 ? 'text-[var(--text)]' : 'text-[var(--c-expense)]'"
                >{{ formatPHP(allTime?.net ?? 0) }}</p>
              </div>
              <div class="text-right tabular-nums text-xs space-y-1">
                <p class="text-[var(--c-income)]">+{{ formatPHP(allTime?.income ?? 0) }}</p>
                <p class="text-[var(--c-expense)]">-{{ formatPHP(allTime?.expense ?? 0) }}</p>
              </div>
            </div>
          </section>

          <!-- Period switcher -->
          <section class="page-section">
            <PeriodSwitcher />
          </section>

          <!-- Summary (asymmetric 1+2) -->
          <section class="page-section">
            <SummaryCards
              :income="summary?.income ?? 0"
              :expense="summary?.expense ?? 0"
              :net="summary?.net ?? 0"
              :savingsRate="summary?.savingsRate ?? 0"
              :deltaIncome="summary?.deltaVsPrev?.income"
              :deltaExpense="summary?.deltaVsPrev?.expense"
              :deltaNet="summary?.deltaVsPrev?.net"
            />
          </section>

          <!-- Donut (earned card surface) -->
          <section class="page-section">
            <CategoryDonut
              :rows="categoryRows ?? []"
              :type="catType"
              @update:type="catType = $event"
            />
          </section>

          <!-- Trend bars (no shell) -->
          <section class="page-section">
            <p class="label mb-3">Trend</p>
            <TrendBars :buckets="trendBuckets ?? []" :period="period" />
          </section>

          <p v-if="anyError" class="text-[var(--c-expense)] text-xs text-center py-4">{{ anyError }}</p>
        </div>
      </Transition>
    </div>
  </div>
</template>

<script setup lang="ts">
definePageMeta({ middleware: 'auth' })

interface Summary {
  income: number
  expense: number
  net: number
  savingsRate: number
  deltaVsPrev: { income: number; expense: number; net: number }
  range: { from: string; to: string }
}

interface CategoryRow { category: string; total: number; pct: number }
interface TrendBucket { bucket: string; income: number; expense: number }
interface AllTime { income: number; expense: number; net: number }

const { user } = useAuth()
const api = useApi()
const { period, anchor } = usePeriod()

const catType = ref<'income' | 'expense'>('expense')
const uid = computed(() => user.value?.uid ?? 'anon')

const summaryKey = computed(() => `stats:summary:${uid.value}:${period.value}:${anchor.value}`)
const trendKey = computed(() => `stats:trend:${uid.value}:${period.value}:${anchor.value}`)
const catKey = computed(() => `stats:cat:${uid.value}:${period.value}:${anchor.value}:${catType.value}`)
const allTimeKey = computed(() => `stats:all-time:${uid.value}`)

const summaryCache = useCache<Summary>(summaryKey, () =>
  api.get<Summary>(`/api/stats/${user.value!.uid}/summary?period=${period.value}&anchor=${anchor.value}`),
)
const trendCache = useCache<TrendBucket[]>(trendKey, () =>
  api.get<TrendBucket[]>(`/api/stats/${user.value!.uid}/trend?period=${period.value}&anchor=${anchor.value}`),
)
const catCache = useCache<CategoryRow[]>(catKey, () =>
  api.get<CategoryRow[]>(`/api/stats/${user.value!.uid}/categories?period=${period.value}&anchor=${anchor.value}&type=${catType.value}`),
)
const allTimeCache = useCache<AllTime>(allTimeKey, () =>
  api.get<AllTime>(`/api/stats/${user.value!.uid}/all-time`),
)

const summary = computed(() => summaryCache.data.value)
const trendBuckets = computed(() => trendCache.data.value)
const categoryRows = computed(() => catCache.data.value)
const allTime = computed(() => allTimeCache.data.value)

const hasLoadedOnce = ref(false)
watch(summary, (val) => {
  if (val) hasLoadedOnce.value = true
}, { immediate: true })

const showSkeleton = computed(() => !hasLoadedOnce.value && !summary.value)

const anyError = computed(() => {
  const e = summaryCache.error.value || trendCache.error.value || catCache.error.value
  if (!e) return ''
  return (e as { data?: { detail?: string } })?.data?.detail ?? 'Failed to load stats'
})
</script>
