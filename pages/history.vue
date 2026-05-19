<template>
  <div class="page">
    <header class="page-header flex items-center justify-between">
      <div class="flex items-center gap-3">
        <NuxtLink to="/dashboard" class="press text-[var(--text-subtle)] hover:text-[var(--text)] w-8 h-8 flex items-center justify-center -ml-2" aria-label="Back">
          <Icon name="chevron-left" :size="18" />
        </NuxtLink>
        <h1 class="text-[var(--text)] font-medium">History</h1>
      </div>

      <!-- View toggle -->
      <div class="flex gap-1 bg-[var(--bg-input)] rounded-lg p-1">
        <button
          v-for="v in (['calendar', 'list'] as const)"
          :key="v"
          @click="view = v"
          :class="[
            'press tab px-3 py-1 rounded-md text-xs font-medium capitalize',
            view === v ? 'bg-[var(--bg-surface)] text-[var(--text)] shadow-sm' : 'text-[var(--text-muted)]',
          ]"
        >{{ v }}</button>
      </div>
    </header>

    <!-- Calendar view -->
    <div v-if="view === 'calendar'" class="page-body">
      <Transition name="swap" mode="out-in">
        <HistorySkeleton v-if="initialLoading" view="calendar" key="skeleton" />

        <div v-else key="content" class="space-y-4">
          <MonthCalendar
            :anchor="anchor"
            :dayData="dayData"
            :selectedDate="selectedDate"
            @update:anchor="onAnchorChange"
            @select-date="selectedDate = $event"
          />

      <!-- Day detail -->
      <Transition name="day">
        <div v-if="selectedDate" :key="selectedDate" class="bg-[var(--bg-surface)] border border-[var(--border)] rounded-2xl p-4 space-y-3">
          <div class="flex items-center justify-between">
            <p class="text-[var(--text)] text-sm font-medium">{{ selectedLabel }}</p>
            <div class="text-[10px] tabular-nums text-[var(--text-subtle)] flex gap-2">
              <span v-if="dayTotals.income > 0" class="text-[var(--c-income)]">+{{ formatPHP(dayTotals.income) }}</span>
              <span v-if="dayTotals.expense > 0" class="text-[var(--c-expense)]">-{{ formatPHP(dayTotals.expense) }}</span>
            </div>
          </div>

          <div v-if="dayTxns.length === 0" class="text-[var(--text-subtle)] text-xs text-center py-4">
            No transactions this day.
          </div>
          <div v-else class="space-y-2">
            <TransactionListItem
              v-for="tx in dayTxns"
              :key="tx.id"
              :tx="tx"
              :showDate="false"
              @select="editingTx = $event"
            />
          </div>
        </div>
      </Transition>
        </div>
      </Transition>
    </div>

    <!-- List view -->
    <div v-else class="page-body">
      <Transition name="swap" mode="out-in">
        <HistorySkeleton v-if="initialLoading" view="list" key="skeleton" />

        <div v-else-if="txns.length === 0" key="empty" class="text-[var(--text-subtle)] text-sm text-center py-12">
          No transactions yet.
        </div>

        <TransitionGroup v-else key="list" tag="div" name="tx" class="space-y-8">
          <div v-for="group in groupedByDay" :key="group.date" class="space-y-2">
            <div class="flex items-center justify-between px-1">
              <p class="text-[var(--text-subtle)] text-[10px] uppercase tracking-widest">{{ group.label }}</p>
              <p class="text-[10px] tabular-nums text-[var(--text-subtle)]">
                <span v-if="group.income > 0" class="text-[var(--c-income)]">+{{ formatPHP(group.income) }}</span>
                <span v-if="group.income > 0 && group.expense > 0"> · </span>
                <span v-if="group.expense > 0" class="text-[var(--c-expense)]">-{{ formatPHP(group.expense) }}</span>
              </p>
            </div>
            <TransactionListItem
              v-for="tx in group.txns"
              :key="tx.id"
              :tx="tx"
              :showDate="false"
              @select="editingTx = $event"
            />
          </div>
        </TransitionGroup>
      </Transition>
    </div>

    <EditTransactionModal
      :open="editingTx !== null"
      :tx="editingTx"
      :categories="categories"
      @close="editingTx = null"
      @save="onEditSave"
      @delete="onEditDelete"
    />
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

interface DayData {
  date: string
  income: number
  expense: number
  net: number
  txnCount: number
}

const { user } = useAuth()
const api = useApi()

const view = ref<'calendar' | 'list'>('calendar')

function pad(n: number): string { return String(n).padStart(2, '0') }
function isoFromDate(d: Date): string { return `${d.getFullYear()}-${pad(d.getMonth() + 1)}-${pad(d.getDate())}` }

const today = new Date()
const anchor = ref<string>(`${today.getFullYear()}-${pad(today.getMonth() + 1)}-01`)
const selectedDate = ref<string | null>(isoFromDate(today))
const editingTx = ref<Transaction | null>(null)

const txns = ref<Transaction[]>([])
const categories = ref<Category[]>([])
const loading = ref(false)
const initialLoaded = ref(false)
const initialLoading = computed(() => loading.value && !initialLoaded.value)

function monthRange(monthAnchor: string): { from: string; to: string } {
  const [y, m] = monthAnchor.split('-').map(Number)
  const start = new Date(y, m - 1, 1)
  const end = new Date(y, m, 0)
  return { from: isoFromDate(start), to: isoFromDate(end) }
}

async function loadCategories() {
  const uid = user.value?.uid
  if (!uid) return
  try {
    categories.value = await api.get<Category[]>(`/api/categories/${uid}`)
  } catch {}
}

async function loadMonth() {
  const uid = user.value?.uid
  if (!uid) return
  loading.value = true
  const start = Date.now()
  try {
    const { from, to } = monthRange(anchor.value)
    txns.value = await api.get<Transaction[]>(`/api/transactions/${uid}?from=${from}&to=${to}`)
    initialLoaded.value = true
  } finally {
    const elapsed = Date.now() - start
    const remain = 150 - elapsed
    if (remain > 0 && !initialLoaded.value) {
      await new Promise((r) => setTimeout(r, remain))
    }
    loading.value = false
  }
}

function onAnchorChange(iso: string) {
  anchor.value = iso
  selectedDate.value = null
}

const dayData = computed<DayData[]>(() => {
  const map = new Map<string, DayData>()
  for (const t of txns.value) {
    const key = t.date
    const cur = map.get(key) ?? { date: key, income: 0, expense: 0, net: 0, txnCount: 0 }
    if (t.type === 'income') cur.income += t.amount
    else cur.expense += t.amount
    cur.net = cur.income - cur.expense
    cur.txnCount += 1
    map.set(key, cur)
  }
  return [...map.values()]
})

const dayTxns = computed(() => {
  if (!selectedDate.value) return []
  return txns.value.filter((t) => t.date === selectedDate.value)
})

const dayTotals = computed(() => {
  let income = 0, expense = 0
  for (const t of dayTxns.value) {
    if (t.type === 'income') income += t.amount
    else expense += t.amount
  }
  return { income, expense }
})

const selectedLabel = computed(() => {
  if (!selectedDate.value) return ''
  const d = new Date(selectedDate.value)
  return d.toLocaleDateString('en-PH', { weekday: 'long', month: 'short', day: 'numeric' })
})

function dayLabel(iso: string): string {
  const todayIso = isoFromDate(new Date())
  const yesterdayDate = new Date()
  yesterdayDate.setDate(yesterdayDate.getDate() - 1)
  const yesterdayIso = isoFromDate(yesterdayDate)
  if (iso === todayIso) return 'TODAY'
  if (iso === yesterdayIso) return 'YESTERDAY'
  return new Date(iso).toLocaleDateString('en-PH', { weekday: 'short', month: 'short', day: 'numeric' })
}

const groupedByDay = computed(() => {
  const map = new Map<string, { date: string; label: string; income: number; expense: number; txns: Transaction[] }>()
  const sorted = [...txns.value].sort((a, b) => (a.date < b.date ? 1 : -1))
  for (const t of sorted) {
    const cur = map.get(t.date) ?? { date: t.date, label: dayLabel(t.date), income: 0, expense: 0, txns: [] }
    if (t.type === 'income') cur.income += t.amount
    else cur.expense += t.amount
    cur.txns.push(t)
    map.set(t.date, cur)
  }
  return [...map.values()]
})

async function onEditSave(payload: {
  id: string
  amount: number
  type: 'income' | 'expense'
  category: string
  notes: string | null
  date: string
}) {
  const uid = user.value!.uid
  const { id, ...body } = payload
  try {
    const updated = await api.put<Transaction>(`/api/transactions/${uid}/${id}`, body)
    const idx = txns.value.findIndex((t) => t.id === id)
    if (idx !== -1) txns.value[idx] = updated
    editingTx.value = null
  } catch {}
}

async function onEditDelete(id: string) {
  const uid = user.value!.uid
  try {
    await api.del(`/api/transactions/${uid}/${id}`)
    txns.value = txns.value.filter((t) => t.id !== id)
    editingTx.value = null
  } catch {}
}

onMounted(() => {
  loadCategories()
  loadMonth()
})
watch(anchor, loadMonth)
</script>

<style scoped>
.day-enter-active, .day-leave-active {
  transition: opacity 220ms var(--ease-out), transform 220ms var(--ease-out);
}
.day-enter-from {
  opacity: 0;
  transform: translateY(8px);
}
.day-leave-to {
  opacity: 0;
  transform: translateY(-4px);
}

.tx-enter-active {
  transition: opacity 360ms var(--ease-out), transform 360ms var(--ease-out);
}
.tx-enter-from {
  opacity: 0;
  transform: translateY(8px);
}
.tx-leave-active {
  transition: opacity 180ms var(--ease-out);
  position: absolute;
}
.tx-leave-to {
  opacity: 0;
}
.tx-move {
  transition: transform 320ms var(--ease-out);
}
.tab {
  transition: background-color 180ms var(--ease-out), color 180ms var(--ease-out), transform 160ms var(--ease-out);
}
</style>
