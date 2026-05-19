<template>
  <div class="page">
    <!-- Header -->
    <header class="page-header flex items-center justify-between">
      <div class="flex flex-col gap-0.5 min-w-0">
        <Logo />
        <p class="text-[var(--text-subtle)] text-[11px] truncate max-w-[240px] ml-9">
          {{ initialized ? user?.email : '' }}
        </p>
      </div>
      <NuxtLink to="/settings" class="press w-10 h-10 rounded-xl border border-[var(--border)] text-[var(--text-muted)] hover:text-[var(--text)] flex items-center justify-center shrink-0" aria-label="Settings">
        <Icon name="settings" :size="18" />
      </NuxtLink>
    </header>

    <div class="page-body">
      <!-- Notification banner (gated to actually-not-granted, supported state) -->
      <NotifPermissionBanner v-if="showNotifBanner" class="mb-10" />

      <!-- Hero card: balance + period chips + bounded strip -->
      <section class="page-section">
        <Transition name="swap" mode="out-in">
          <DashboardSkeleton v-if="initialLoading" key="skeleton" />
          <div
            v-else
            key="hero"
            class="hero-card bg-[var(--bg-surface)] border border-[var(--border)] rounded-3xl p-6"
          >
            <div class="flex items-baseline justify-between gap-3">
              <p class="label">Net balance</p>
              <p v-if="stale" class="text-[var(--text-subtle)] text-[10px] tracking-wider syncing">syncing…</p>
            </div>

            <p
              class="text-5xl font-semibold tabular-nums tracking-tightest mt-2"
              :class="netBalance >= 0 ? 'text-[var(--text)]' : 'text-[var(--c-expense)]'"
            >{{ formatPHP(netBalance) }}</p>
            <p class="text-[var(--text-muted)] text-sm tabular-nums mt-2">{{ periodLabel }}</p>

            <!-- Period chips -->
            <div class="flex gap-2 mt-5">
              <button
                v-for="p in (['day', 'week', 'month'] as const)"
                :key="p"
                @click="setHeroPeriod(p)"
                :class="[
                  'press rounded-full px-3 py-1 text-xs font-medium border transition-colors',
                  heroPeriod === p
                    ? 'bg-emerald-500 text-white border-transparent'
                    : 'bg-transparent text-[var(--text-muted)] border-[var(--border)]',
                ]"
              >{{ chipLabel(p) }}</button>
            </div>

            <!-- Period-bounded strip -->
            <div
              class="mt-5 grid grid-cols-3 divide-x divide-[var(--border)] border-t border-[var(--border)] strip"
              :class="{ flicker: chipFlicker }"
            >
              <div class="py-3 pr-3">
                <p class="text-[var(--text-subtle)] text-[10px]">Income</p>
                <p class="text-[var(--c-income)] font-semibold text-sm tabular-nums mt-1">{{ formatPHP(periodIncome) }}</p>
              </div>
              <div class="py-3 px-3">
                <p class="text-[var(--text-subtle)] text-[10px]">Expenses</p>
                <p class="text-[var(--c-expense)] font-semibold text-sm tabular-nums mt-1">{{ formatPHP(periodExpense) }}</p>
              </div>
              <div class="py-3 pl-3">
                <p class="text-[var(--text-subtle)] text-[10px]">Txns</p>
                <p class="text-[var(--text)] font-semibold text-sm tabular-nums mt-1">{{ periodTxnCount }}</p>
              </div>
            </div>
          </div>
        </Transition>
      </section>

      <!-- Upcoming -->
      <section v-if="upcoming.length > 0" class="page-section">
        <p class="label-quiet mb-3">Upcoming</p>
        <div class="flex gap-2 overflow-x-auto -mx-5 px-5 pb-1">
          <div
            v-for="(u, idx) in upcoming"
            :key="idx"
            class="border border-[var(--border)] rounded-lg px-3 py-2 min-w-[140px] shrink-0"
          >
            <p class="text-[var(--text-subtle)] text-[10px] uppercase tracking-wider">{{ formatDueDate(u.dueDate) }}</p>
            <p class="text-[var(--text)] text-xs font-medium truncate mt-0.5">{{ u.category }}</p>
            <p
              class="text-xs tabular-nums mt-0.5"
              :class="u.type === 'income' ? 'text-[var(--c-income)]' : 'text-[var(--c-expense)]'"
            >{{ u.type === 'income' ? '+' : '-' }}{{ formatPHP(u.amount) }}</p>
          </div>
        </div>
      </section>

      <!-- Search + Filter -->
      <section class="page-section">
        <SearchBar
          :modelValue="filters.search"
          :activeCount="activeFilterCount"
          @update:modelValue="onSearch"
          @open-filters="filterOpen = true"
        />
      </section>

    <FilterDrawer
      :open="filterOpen"
      :filters="filters"
      :categories="categories"
      @close="filterOpen = false"
      @apply="onApplyFilters"
      @reset="onResetFilters"
    />

    <EditTransactionModal
      :open="editingTx !== null"
      :tx="editingTx"
      :categories="categories"
      @close="editingTx = null"
      @save="onEditSave"
      @delete="onEditDelete"
    />

    <AddTransactionModal
      :open="addOpen"
      :categories="categories"
      @close="hideAdd"
      @save="onAddSave"
    />

      <!-- Recent Transactions -->
      <section class="page-section pb-12">
        <NuxtLink
          to="/history"
          class="press flex items-center justify-between w-full mb-4 group"
        >
          <h2 class="label">Recent transactions</h2>
          <span class="text-[var(--text-muted)] text-xs flex items-center gap-1 group-hover:text-[var(--text)] transition-colors">View all <Icon name="chevron-right" :size="14" /></span>
        </NuxtLink>

        <p v-if="deleteError" class="text-[var(--c-expense)] text-xs mb-2">{{ deleteError }}</p>

        <Transition name="swap" mode="out-in">
          <div v-if="initialLoading" key="skeleton" class="space-y-2">
            <TransactionRowSkeleton v-for="n in 4" :key="n" />
          </div>

          <div v-else-if="transactions.length === 0" key="empty" class="text-[var(--text-subtle)] text-sm text-center py-12">
            No transactions yet. Tap + to add.
          </div>

          <TransitionGroup v-else key="list" tag="div" name="tx" class="space-y-2 relative">
            <TransactionListItem
              v-for="tx in recentTransactions"
              :key="tx.id"
              :tx="tx"
              @select="editingTx = $event"
            />
          </TransitionGroup>
        </Transition>

        <NuxtLink
          v-if="transactions.length > recentTransactions.length"
          to="/history"
          class="press inline-flex items-center gap-1 text-[var(--text-muted)] hover:text-[var(--text)] text-xs mt-4 py-2 mx-auto justify-center w-full"
        >See all {{ transactions.length }} <Icon name="arrow-right" :size="12" /></NuxtLink>
      </section>
    </div>
  </div>
</template>

<script setup lang="ts">
definePageMeta({ middleware: 'auth' })

interface Transaction {
  id: string
  userId: string
  amount: number
  type: 'income' | 'expense'
  date: string
  category: string
  notes?: string | null
}

interface Category {
  id: string
  name: string
  icon: string
  type: 'income' | 'expense'
  isSystem: boolean
}

interface UpcomingItem {
  ruleId: string
  amount: number
  type: 'income' | 'expense'
  category: string
  notes?: string | null
  dueDate: string
}

interface AddPayload {
  type: 'income' | 'expense'
  amount: number
  category: string
  notes: string | null
  date: string
}

interface EditPayload extends AddPayload {
  id: string
}

type HeroPeriod = 'day' | 'week' | 'month'

const { user, initialized } = useAuth()
const api = useApi()
const toast = useToast()
const budgetCheck = useBudgetCheck()
const { open: addOpen, hide: hideAdd } = useAddTransaction()

const editingTx = ref<Transaction | null>(null)
const filterOpen = ref(false)
const deleteError = ref('')
const { filters, reset: resetFilters, buildQuery, hasActive } = useTxnFilters()
const activeFilterCount = computed(() => (hasActive.value ? 1 : 0))

const uidKey = computed(() => user.value?.uid ?? 'anon')

const txCache = useCache<Transaction[]>(
  computed(() => `dash:txns:${uidKey.value}:${buildQuery()}`),
  () => api.get<Transaction[]>(`/api/transactions/${user.value!.uid}${buildQuery()}`),
)
const catCache = useCache<Category[]>(
  computed(() => `dash:cats:${uidKey.value}`),
  () => api.get<Category[]>(`/api/categories/${user.value!.uid}`),
)
const upCache = useCache<UpcomingItem[]>(
  computed(() => `dash:upcoming:${uidKey.value}`),
  () => api.get<UpcomingItem[]>(`/api/recurring/${user.value!.uid}/upcoming?days=7`).catch(() => [] as UpcomingItem[]),
)

const transactions = computed<Transaction[]>(() => txCache.data.value ?? [])
const categories = computed<Category[]>(() => catCache.data.value ?? [])
const upcoming = computed<UpcomingItem[]>(() => upCache.data.value ?? [])

const initialLoading = computed(() => txCache.isLoading.value && !txCache.data.value)
const stale = computed(() => txCache.isStale.value || catCache.isStale.value)

const netBalance = computed(() =>
  transactions.value.reduce(
    (sum, tx) => (tx.type === 'income' ? sum + tx.amount : sum - tx.amount),
    0,
  ),
)

const recentTransactions = computed(() => transactions.value.slice(0, 5))

// Hero period chips
const heroPeriod = ref<HeroPeriod>('week')
const chipFlicker = ref(false)

function chipLabel(p: HeroPeriod): string {
  return p === 'day' ? 'Day' : p === 'week' ? 'Week' : 'Month'
}

function periodBounds(p: HeroPeriod, now: Date = new Date()): { from: string; to: string } {
  const pad = (n: number) => String(n).padStart(2, '0')
  const iso = (d: Date) => `${d.getFullYear()}-${pad(d.getMonth() + 1)}-${pad(d.getDate())}`
  if (p === 'day') {
    return { from: iso(now), to: iso(now) }
  }
  if (p === 'week') {
    const day = now.getDay()
    const offset = day === 0 ? -6 : 1 - day
    const monday = new Date(now)
    monday.setDate(now.getDate() + offset)
    const sunday = new Date(monday)
    sunday.setDate(monday.getDate() + 6)
    return { from: iso(monday), to: iso(sunday) }
  }
  const start = new Date(now.getFullYear(), now.getMonth(), 1)
  const end = new Date(now.getFullYear(), now.getMonth() + 1, 0)
  return { from: `${start.getFullYear()}-${pad(start.getMonth() + 1)}-01`, to: iso(end) }
}

const periodFilteredTxns = computed(() => {
  const { from, to } = periodBounds(heroPeriod.value)
  return transactions.value.filter((tx) => tx.date >= from && tx.date <= to)
})
const periodIncome = computed(() =>
  periodFilteredTxns.value.filter((tx) => tx.type === 'income').reduce((s, tx) => s + tx.amount, 0),
)
const periodExpense = computed(() =>
  periodFilteredTxns.value.filter((tx) => tx.type === 'expense').reduce((s, tx) => s + tx.amount, 0),
)
const periodTxnCount = computed(() => periodFilteredTxns.value.length)

function setHeroPeriod(p: HeroPeriod) {
  if (p === heroPeriod.value) return
  chipFlicker.value = true
  heroPeriod.value = p
  setTimeout(() => { chipFlicker.value = false }, 140)
}

const periodLabel = computed(() => {
  const now = new Date()
  const { from, to } = periodBounds(heroPeriod.value, now)
  if (heroPeriod.value === 'day') {
    return new Date(from).toLocaleDateString('en-PH', { weekday: 'long', month: 'short', day: 'numeric' })
  }
  if (heroPeriod.value === 'week') {
    const fromS = new Date(from).toLocaleDateString('en-PH', { month: 'short', day: 'numeric' })
    const toS = new Date(to).toLocaleDateString('en-PH', { month: 'short', day: 'numeric' })
    return `Week of ${fromS} – ${toS}`
  }
  return now.toLocaleDateString('en-PH', { month: 'long', year: 'numeric' })
})

const fcm = useFcm()
const showNotifBanner = computed(() => fcm.status.value === 'default')

function formatDueDate(iso: string): string {
  const d = new Date(iso)
  const today = new Date()
  today.setHours(0, 0, 0, 0)
  const diff = Math.round((d.getTime() - today.getTime()) / 86400000)
  if (diff === 0) return 'Today'
  if (diff === 1) return 'Tomorrow'
  if (diff < 7) return `In ${diff}d`
  return d.toLocaleDateString('en-PH', { month: 'short', day: 'numeric' })
}

function onSearch(val: string) {
  filters.value.search = val
}

function onApplyFilters(f: typeof filters.value) {
  filters.value = f
}

function onResetFilters() {
  resetFilters()
}

function breachPeriodAdj(period: 'week' | 'month'): string {
  return period === 'week' ? 'weekly' : 'monthly'
}

async function onAddSave(payload: AddPayload) {
  try {
    const uid = user.value!.uid

    if (payload.type === 'expense') {
      const check = await budgetCheck.check(payload.amount, payload.category)
      if (check?.wouldOverspend) {
        for (const b of check.breaches) {
          const cap = b.limit + b.rollover
          if (b.scope === 'category') {
            toast.warning(
              `Over ${b.category} (${breachPeriodAdj(b.period)})`,
              `${formatPHP(b.spent)} / ${formatPHP(cap)}`,
            )
          } else {
            toast.warning(
              `Over total ${breachPeriodAdj(b.period)} budget`,
              `${formatPHP(b.spent)} / ${formatPHP(cap)}`,
            )
          }
        }
      }
    }

    await api.post<Transaction>(`/api/transactions/${uid}`, payload)
    await txCache.refresh()
    hideAdd()
  } catch (e: unknown) {
    const detail = (e as { data?: { detail?: string } })?.data?.detail ?? 'Failed to save'
    toast.error('Save failed', detail)
  }
}

async function deleteTransaction(id: string) {
  deleteError.value = ''
  try {
    const uid = user.value!.uid
    await api.del(`/api/transactions/${uid}/${id}`)
    await txCache.refresh()
  } catch {
    deleteError.value = 'Failed to delete transaction'
  }
}

async function onEditSave(payload: EditPayload) {
  try {
    const uid = user.value!.uid
    const { id, ...body } = payload
    await api.put<Transaction>(`/api/transactions/${uid}/${id}`, body)
    await txCache.refresh()
    editingTx.value = null
  } catch (e: unknown) {
    deleteError.value = (e as { data?: { detail?: string } })?.data?.detail ?? 'Failed to update'
  }
}

async function onEditDelete(id: string) {
  await deleteTransaction(id)
  editingTx.value = null
}
</script>

<style scoped>
.strip {
  transition: opacity 140ms var(--ease-out);
}
.strip.flicker {
  opacity: 0.55;
}
.syncing {
  animation: syncing-pulse 1.2s var(--ease-in-out) infinite;
}
@keyframes syncing-pulse {
  0%, 100% { opacity: 0.5; }
  50% { opacity: 1; }
}

.tx-row {
  transition:
    background-color 200ms var(--ease-out),
    transform 160ms var(--ease-out);
  will-change: transform;
}
@media (hover: hover) and (pointer: fine) {
  .tx-row:hover {
    background-color: rgb(39 39 42 / 0.7);
  }
}

.tx-enter-active {
  transition:
    opacity 260ms var(--ease-out),
    transform 260ms var(--ease-out);
}
.tx-leave-active {
  transition:
    opacity 160ms var(--ease-out),
    transform 160ms var(--ease-out);
  position: absolute;
  left: 0;
  right: 0;
}
.tx-enter-from {
  opacity: 0;
  transform: translateY(-6px) scale(0.98);
}
.tx-leave-to {
  opacity: 0;
  transform: translateY(-4px) scale(0.98);
}
.tx-move {
  transition: transform 320ms var(--ease-out);
}
</style>
