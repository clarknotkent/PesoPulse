<template>
  <div class="page">
    <header class="page-header space-y-5">
      <h1 class="text-[var(--text)] font-medium">
        Budgets
      </h1>

      <!-- Top tab: Budgets | Goals -->
      <div class="flex gap-1 bg-[var(--bg-input)] rounded-xl p-1">
        <button
          v-for="t in (['budgets', 'goals'] as const)"
          :key="t"
          :class="[
            'press flex-1 py-2 rounded-lg text-sm font-medium transition capitalize',
            subTab === t ? 'bg-[var(--bg-surface)] text-[var(--text)] shadow-sm' : 'text-[var(--text-muted)]',
          ]"
          @click="subTab = t"
        >
          {{ t }}
        </button>
      </div>

      <div
        v-if="subTab === 'budgets'"
        class="space-y-3"
      >
        <!-- Period toggle -->
        <div class="flex gap-1 bg-[var(--bg-input)] rounded-xl p-1">
          <button
            v-for="p in (['day', 'week', 'month'] as const)"
            :key="p"
            :class="[
              'press flex-1 py-2 rounded-lg text-sm font-medium transition capitalize',
              period === p ? 'bg-emerald-500 text-white' : 'text-[var(--text-muted)]',
            ]"
            @click="setPeriod(p)"
          >
            {{ periodLabelFor(p) }}
          </button>
        </div>

        <!-- Anchor shifter -->
        <div class="flex items-center justify-between gap-2">
          <button
            class="press w-10 h-10 rounded-lg border border-[var(--border)] text-[var(--text-muted)] hover:text-[var(--text)] flex items-center justify-center"
            aria-label="Previous"
            @click="shiftAnchor(-1)"
          >
            <Icon
              name="chevron-left"
              :size="18"
            />
          </button>
          <p class="text-[var(--text)] text-sm font-medium tabular-nums">
            {{ anchorLabel }}
          </p>
          <button
            class="press w-10 h-10 rounded-lg border border-[var(--border)] text-[var(--text-muted)] hover:text-[var(--text)] flex items-center justify-center"
            aria-label="Next"
            @click="shiftAnchor(1)"
          >
            <Icon
              name="chevron-right"
              :size="18"
            />
          </button>
        </div>
      </div>
    </header>

    <div
      v-if="subTab === 'budgets'"
      class="page-body"
    >
      <Transition
        name="swap"
        mode="out-in"
      >
        <BudgetsSkeleton
          v-if="initialLoading"
          key="skeleton"
        />

        <div
          v-else
          key="content"
        >
          <!-- Burn-down (earned card surface) -->
          <section class="page-section">
            <PeriodBurndown
              :key="period + anchor"
              :period="period"
              :anchor="anchor"
            />
          </section>

          <!-- Total — no card, hairline framing -->
          <section class="page-section">
            <div class="flex items-center justify-between mb-3">
              <p class="label">
                {{ totalLabel }}
              </p>
              <button
                v-if="!editingTotal"
                class="press text-[var(--text-subtle)] hover:text-[var(--text)] w-7 h-7 flex items-center justify-center -mr-1"
                aria-label="Edit total cap"
                @click="editingTotal = true"
              >
                <Icon
                  name="edit"
                  :size="14"
                />
              </button>
            </div>

            <div
              v-if="editingTotal"
              class="flex gap-2"
            >
              <input
                v-model="totalDraft"
                type="number"
                min="0"
                step="0.01"
                class="focus-ring flex-1 bg-[var(--bg-input)] text-[var(--text)] rounded-lg px-4 py-2 text-sm outline-none"
                placeholder="Total cap (₱)"
              />
              <button
                class="press bg-[var(--text)] text-[var(--bg)] font-medium px-4 rounded-lg text-sm"
                @click="saveTotal"
              >
                Save
              </button>
              <button
                class="press bg-[var(--bg-input)] text-[var(--text-muted)] w-10 rounded-lg text-sm flex items-center justify-center"
                aria-label="Cancel"
                @click="editingTotal = false"
              >
                <Icon
                  name="x"
                  :size="14"
                />
              </button>
            </div>

            <div v-else>
              <div class="flex items-baseline justify-between border-t border-[var(--border)] pt-4">
                <p class="text-3xl font-semibold text-[var(--text)] tabular-nums tracking-tightest">
                  {{ formatPHP(totalSpent) }}
                </p>
                <p class="text-xs text-[var(--text-subtle)] tabular-nums">
                  of {{ formatPHP(totalLimit + totalRollover) }}
                </p>
              </div>
              <div class="h-1.5 bg-[var(--bg-input)] rounded-full overflow-hidden mt-3">
                <div
                  class="h-full rounded-full transition-[width] duration-500"
                  :class="totalBarColor"
                  :style="{ width: `${Math.min(100, totalPct)}%` }"
                />
              </div>
              <p
                v-if="totalRollover > 0"
                class="text-[var(--c-income)] text-xs mt-2 tabular-nums"
              >
                +{{ formatPHP(totalRollover) }} rollover from prior {{ rolloverNoun }}
              </p>
              <p
                v-if="data?.total.overspent"
                class="text-[var(--c-expense)] text-xs mt-2 tabular-nums"
              >
                Over total budget by {{ formatPHP(totalSpent - (totalLimit + totalRollover)) }}
              </p>
            </div>
          </section>

          <!-- Per-category — hairline list -->
          <section class="page-section">
            <p class="label mb-2">
              Per category
            </p>

            <div
              v-if="(data?.categories?.length ?? 0) > 0"
              class="border-t border-[var(--border)]"
            >
              <BudgetRow
                v-for="row in data?.categories ?? []"
                :key="row.category ?? '?'"
                :label="row.category ?? '?'"
                :limit="row.limit"
                :spent="row.spent"
                :rollover="row.rollover"
                :overspent="row.overspent"
                editable
                @edit="startEditCategory(row.category)"
              />
            </div>
            <p
              v-else
              class="text-[var(--text-subtle)] text-sm py-6"
            >
              No category budgets yet.
            </p>
          </section>

          <!-- Add/edit category budget — keep card (form, earned elevation) -->
          <section class="page-section">
            <div class="bg-[var(--bg-surface)] border border-[var(--border)] rounded-2xl p-4 space-y-4">
              <p class="label">
                Set category budget
              </p>

              <div class="space-y-3">
                <CategoryPicker
                  v-model="catDraft.category"
                  :categories="expenseCategories"
                  type="expense"
                />
                <input
                  v-model="catDraft.amount"
                  type="number"
                  min="0"
                  step="0.01"
                  placeholder="Limit (₱) — 0 to remove"
                  class="focus-ring w-full bg-[var(--bg-input)] text-[var(--text)] rounded-lg px-4 py-3 text-sm"
                />
              </div>

              <button
                :disabled="catSaving"
                class="press w-full bg-[var(--text)] text-[var(--bg)] font-medium py-3 rounded-lg text-sm disabled:opacity-50 disabled:active:scale-100"
                @click="saveCategory"
              >
                {{ catSaving ? 'Saving…' : 'Save' }}
              </button>
            </div>
          </section>

          <p
            v-if="error"
            class="text-[var(--c-expense)] text-xs text-center py-2"
          >
            {{ error }}
          </p>
        </div>
      </Transition>
    </div>

    <!-- Goals sub-tab — single CTA card (earned, it's an action) -->
    <div
      v-else
      class="page-body"
    >
      <NuxtLink
        to="/goals"
        class="press block bg-[var(--bg-surface)] border border-[var(--border)] rounded-2xl p-5 flex items-center justify-between"
      >
        <div>
          <p class="text-[var(--text)] text-sm font-medium">Savings goals</p>
          <p class="text-[var(--text-subtle)] text-xs mt-0.5">Track progress against income categories.</p>
        </div>
        <Icon
          name="chevron-right"
          :size="16"
          class="text-[var(--text-subtle)]"
        />
      </NuxtLink>
    </div>
  </div>
</template>

<script setup lang="ts">
definePageMeta({ middleware: 'auth' })

type BudgetPeriod = 'day' | 'week' | 'month'

function periodLabelFor(p: BudgetPeriod): string {
  if (p === 'day') return 'Daily'
  if (p === 'week') return 'Weekly'
  return 'Monthly'
}

interface BudgetView {
  period: BudgetPeriod
  anchor: string
  range: { from: string, to: string }
  total: { category: string | null, limit: number, spent: number, rollover: number, remaining: number, overspent: boolean }
  categories: { category: string | null, limit: number, spent: number, rollover: number, remaining: number, overspent: boolean }[]
}

interface Category {
  id: string
  name: string
  icon: string
  type: 'income' | 'expense'
  isSystem: boolean
}

const { user } = useAuth()
const api = useApi()

const subTab = ref<'budgets' | 'goals'>('budgets')
const period = ref<BudgetPeriod>('week')
const anchor = ref<string>(canonicalAnchor('week', new Date()))

const data = ref<BudgetView | null>(null)
const loading = ref(false)
const initialLoaded = ref(false)
const initialLoading = computed(() => loading.value && !initialLoaded.value)
const error = ref('')

const editingTotal = ref(false)
const totalDraft = ref('')

const catDraft = reactive({ category: '', amount: '' })
const catSaving = ref(false)
const expenseCategories = ref<Category[]>([])

function pad(n: number): string {
  return String(n).padStart(2, '0')
}

function isoFromDate(d: Date): string {
  return `${d.getFullYear()}-${pad(d.getMonth() + 1)}-${pad(d.getDate())}`
}

function canonicalAnchor(p: BudgetPeriod, d: Date): string {
  if (p === 'day') return isoFromDate(d)
  if (p === 'week') {
    const day = d.getDay()
    const diff = day === 0 ? -6 : 1 - day
    const monday = new Date(d)
    monday.setDate(d.getDate() + diff)
    return isoFromDate(monday)
  }
  return `${d.getFullYear()}-${pad(d.getMonth() + 1)}-01`
}

function setPeriod(p: BudgetPeriod) {
  period.value = p
  anchor.value = canonicalAnchor(p, new Date())
}

function shiftAnchor(delta: number) {
  const [y, m, d] = anchor.value.split('-').map(Number)
  const date = new Date(y, m - 1, d)
  if (period.value === 'day') {
    date.setDate(date.getDate() + delta)
  }
  else if (period.value === 'week') {
    date.setDate(date.getDate() + 7 * delta)
  }
  else {
    date.setMonth(date.getMonth() + delta, 1)
  }
  anchor.value = canonicalAnchor(period.value, date)
}

const anchorLabel = computed(() => {
  const [y, m, d] = anchor.value.split('-').map(Number)
  const start = new Date(y, m - 1, d)
  if (period.value === 'day') {
    return start.toLocaleDateString('en-PH', { weekday: 'long', month: 'short', day: 'numeric', year: 'numeric' })
  }
  if (period.value === 'week') {
    const end = new Date(start)
    end.setDate(start.getDate() + 6)
    const startS = start.toLocaleDateString('en-PH', { month: 'short', day: 'numeric' })
    const endS = end.toLocaleDateString('en-PH', { month: 'short', day: 'numeric' })
    return `Week of ${startS}–${endS}`
  }
  return start.toLocaleDateString('en-PH', { month: 'long', year: 'numeric' })
})

const totalLabel = computed(() => {
  if (period.value === 'day') return 'Total Daily'
  if (period.value === 'week') return 'Total Weekly'
  return 'Total Monthly'
})

const rolloverNoun = computed(() => {
  if (period.value === 'day') return 'days'
  if (period.value === 'week') return 'weeks'
  return 'months'
})

const totalLimit = computed(() => data.value?.total.limit ?? 0)
const totalRollover = computed(() => data.value?.total.rollover ?? 0)
const totalSpent = computed(() => data.value?.total.spent ?? 0)
const totalPct = computed(() => {
  const cap = totalLimit.value + totalRollover.value
  return cap <= 0 ? 0 : (totalSpent.value / cap) * 100
})
const totalBarColor = computed(() => {
  if (data.value?.total.overspent) return 'bg-red-500'
  if (totalPct.value >= 80) return 'bg-amber-400'
  return 'bg-emerald-500'
})

function queryString(): string {
  return `period=${period.value}&anchor=${anchor.value}`
}

async function load() {
  const uid = user.value?.uid
  if (!uid) return
  loading.value = true
  error.value = ''
  const start = Date.now()
  try {
    data.value = await api.get<BudgetView>(`/api/budgets/${uid}?${queryString()}`)
    totalDraft.value = String(data.value.total.limit || '')
    initialLoaded.value = true
  }
  catch (e: unknown) {
    error.value = (e as { data?: { detail?: string } })?.data?.detail ?? 'Failed to load'
  }
  finally {
    const elapsed = Date.now() - start
    const remain = 150 - elapsed
    if (remain > 0 && !initialLoaded.value) {
      await new Promise((r) => setTimeout(r, remain))
    }
    loading.value = false
  }
}

async function loadCategories() {
  const uid = user.value?.uid
  if (!uid) return
  try {
    const all = await api.get<Category[]>(`/api/categories/${uid}`)
    expenseCategories.value = all.filter((c) => c.type === 'expense')
  }
  catch (e) {
    void e
  }
}

async function saveTotal() {
  const uid = user.value?.uid
  if (!uid) return
  const val = parseFloat(totalDraft.value || '0')
  try {
    data.value = await api.put<BudgetView>(`/api/budgets/${uid}?${queryString()}`, { total: val })
    editingTotal.value = false
  }
  catch (e: unknown) {
    error.value = (e as { data?: { detail?: string } })?.data?.detail ?? 'Failed to save'
  }
}

function startEditCategory(category: string | null) {
  if (!category) return
  catDraft.category = category
  const row = data.value?.categories.find((c) => c.category === category)
  catDraft.amount = String(row?.limit ?? '')
}

async function saveCategory() {
  const uid = user.value?.uid
  if (!uid || !catDraft.category) return
  catSaving.value = true
  try {
    const val = parseFloat(catDraft.amount || '0')
    data.value = await api.put<BudgetView>(`/api/budgets/${uid}?${queryString()}`, {
      categories: { [catDraft.category]: val },
    })
    catDraft.amount = ''
  }
  catch (e: unknown) {
    error.value = (e as { data?: { detail?: string } })?.data?.detail ?? 'Failed to save'
  }
  finally {
    catSaving.value = false
  }
}

onMounted(() => {
  load()
  loadCategories()
})
watch([period, anchor], load)
</script>
