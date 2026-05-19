<template>
  <div class="page">
    <header class="page-header flex items-center gap-3">
      <NuxtLink
        to="/settings"
        class="press text-[var(--text-subtle)] hover:text-[var(--text)] w-8 h-8 flex items-center justify-center -ml-2"
        aria-label="Back"
      >
        <Icon
          name="chevron-left"
          :size="18"
        />
      </NuxtLink>
      <h1 class="text-[var(--text)] font-medium">
        Recurring
      </h1>
    </header>

    <div class="page-body">
      <Transition
        name="swap"
        mode="out-in"
      >
        <RecurringSkeleton
          v-if="initialLoading"
          key="skeleton"
        />

        <div
          v-else-if="rules.length === 0"
          key="empty"
          class="flex flex-col items-center text-center py-10 gap-3"
        >
          <span class="w-12 h-12 rounded-2xl border border-[var(--border)] flex items-center justify-center text-[var(--text-muted)]">
            <Icon
              name="recurring"
              :size="22"
            />
          </span>
          <div class="space-y-1">
            <p class="text-[var(--text)] text-sm font-medium">
              No recurring rules yet
            </p>
            <p class="text-[var(--text-subtle)] text-xs">
              Add one below to auto-post bills and income.
            </p>
          </div>
        </div>

        <section
          v-else
          key="list"
          class="page-section border-t border-[var(--border)]"
        >
          <div
            v-for="r in rules"
            :key="r.id"
            class="py-4 border-b border-[var(--border)]"
          >
            <div class="flex items-start justify-between gap-3">
              <div class="min-w-0 flex-1">
                <p class="text-[var(--text)] text-sm font-medium">
                  {{ r.category }} <span class="text-[var(--text-subtle)] font-normal">· {{ r.frequency }}</span>
                </p>
                <p class="text-[var(--text-muted)] text-xs tabular-nums mt-0.5">
                  <span :class="r.type === 'income' ? 'text-[var(--c-income)]' : 'text-[var(--c-expense)]'">{{ r.type === 'income' ? '+' : '-' }}{{ formatPHP(r.amount) }}</span>
                  <span class="text-[var(--text-subtle)]"> · from {{ r.startDate }}{{ r.endDate ? ' to ' + r.endDate : '' }}</span>
                </p>
                <p
                  v-if="r.notes"
                  class="text-[var(--text-subtle)] text-xs truncate mt-0.5"
                >
                  {{ r.notes }}
                </p>
              </div>
              <div class="flex items-center gap-1 shrink-0">
                <button
                  class="press text-[11px] px-2 py-1 rounded font-medium"
                  :class="r.active ? 'bg-emerald-500/10 text-[var(--c-income)]' : 'bg-[var(--bg-input)] text-[var(--text-subtle)]'"
                  @click="togglePause(r)"
                >
                  {{ r.active ? 'Active' : 'Paused' }}
                </button>
                <button
                  class="press text-[var(--text-subtle)] hover:text-[var(--c-expense)] w-7 h-7 flex items-center justify-center"
                  aria-label="Delete rule"
                  @click="remove(r.id)"
                >
                  <Icon
                    name="x"
                    :size="14"
                  />
                </button>
              </div>
            </div>
          </div>
        </section>
      </Transition>

      <!-- Add form (earned card) -->
      <section class="page-section">
        <div class="bg-[var(--bg-surface)] border border-[var(--border)] rounded-2xl p-4 space-y-4">
          <p class="label">
            Add rule
          </p>

          <div class="space-y-3">
            <div class="flex gap-2">
              <button
                v-for="t in (['expense', 'income'] as const)"
                :key="t"
                :class="[
                  'press flex-1 py-2 rounded-lg text-sm font-medium transition capitalize',
                  form.type === t
                    ? t === 'income' ? 'bg-emerald-500 text-white' : 'bg-red-500 text-white'
                    : 'bg-[var(--bg-input)] text-[var(--text-muted)]',
                ]"
                @click="form.type = t"
              >
                {{ t }}
              </button>
            </div>

            <input
              v-model="form.amount"
              type="number"
              min="0.01"
              step="0.01"
              placeholder="Amount (₱)"
              class="focus-ring w-full bg-[var(--bg-input)] text-[var(--text)] rounded-lg px-4 py-3 text-sm"
            />

            <CategoryPicker
              v-model="form.category"
              :categories="categories"
              :type="form.type"
            />

            <select
              v-model="form.frequency"
              class="focus-ring w-full bg-[var(--bg-input)] text-[var(--text)] rounded-lg px-4 py-3 text-sm"
            >
              <option value="daily">
                Daily
              </option>
              <option value="weekly">
                Weekly
              </option>
              <option value="monthly">
                Monthly
              </option>
              <option value="yearly">
                Yearly
              </option>
            </select>

            <div class="grid grid-cols-2 gap-2">
              <div class="space-y-1">
                <p class="label-quiet">
                  Start
                </p>
                <input
                  v-model="form.startDate"
                  type="date"
                  class="focus-ring w-full bg-[var(--bg-input)] text-[var(--text)] rounded-lg px-3 py-2 text-sm"
                />
              </div>
              <div class="space-y-1">
                <p class="label-quiet">
                  End (optional)
                </p>
                <input
                  v-model="form.endDate"
                  type="date"
                  class="focus-ring w-full bg-[var(--bg-input)] text-[var(--text)] rounded-lg px-3 py-2 text-sm"
                />
              </div>
            </div>

            <input
              v-model="form.notes"
              type="text"
              placeholder="Notes (optional)"
              class="focus-ring w-full bg-[var(--bg-input)] text-[var(--text)] rounded-lg px-4 py-3 text-sm"
            />
          </div>

          <p
            v-if="formError"
            class="text-[var(--c-expense)] text-xs"
          >
            {{ formError }}
          </p>

          <button
            :disabled="saving"
            class="press w-full bg-[var(--text)] text-[var(--bg)] font-medium py-3 rounded-lg text-sm disabled:opacity-50 disabled:active:scale-100"
            @click="save"
          >
            {{ saving ? 'Saving…' : 'Add recurring rule' }}
          </button>
        </div>
      </section>
    </div>
  </div>
</template>

<script setup lang="ts">
definePageMeta({ middleware: 'auth' })

interface Rule {
  id: string
  userId: string
  amount: number
  type: 'income' | 'expense'
  category: string
  notes?: string | null
  frequency: 'daily' | 'weekly' | 'monthly' | 'yearly'
  startDate: string
  endDate?: string | null
  active: boolean
  lastPostedDate?: string | null
}

interface Category { id: string, name: string, icon: string, type: 'income' | 'expense', isSystem: boolean }

const { user } = useAuth()
const api = useApi()

const rules = ref<Rule[]>([])
const categories = ref<Category[]>([])
const loading = ref(false)
const initialLoaded = ref(false)
const initialLoading = computed(() => loading.value && !initialLoaded.value)
const saving = ref(false)
const formError = ref('')

const todayIso = new Date().toISOString().slice(0, 10)

const form = reactive({
  type: 'expense' as 'income' | 'expense',
  amount: '',
  category: '',
  notes: '',
  frequency: 'monthly' as Rule['frequency'],
  startDate: todayIso,
  endDate: '',
})

const filteredCategories = computed(() => categories.value.filter((c) => c.type === form.type))

async function load() {
  const uid = user.value?.uid
  if (!uid) return
  loading.value = true
  const start = Date.now()
  try {
    const [r, c] = await Promise.all([
      api.get<Rule[]>(`/api/recurring/${uid}`),
      api.get<Category[]>(`/api/categories/${uid}`),
    ])
    rules.value = r
    categories.value = c
    initialLoaded.value = true
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

async function save() {
  formError.value = ''
  if (!form.amount || !form.category || !form.startDate) {
    formError.value = 'Amount, category, and start date required'
    return
  }
  const uid = user.value!.uid
  saving.value = true
  try {
    const rule = await api.post<Rule>(`/api/recurring/${uid}`, {
      amount: parseFloat(form.amount),
      type: form.type,
      category: form.category,
      notes: form.notes || null,
      frequency: form.frequency,
      startDate: form.startDate,
      endDate: form.endDate || null,
      active: true,
    })
    rules.value.unshift(rule)
    form.amount = ''
    form.category = ''
    form.notes = ''
    form.endDate = ''
  }
  catch (e: unknown) {
    formError.value = (e as { data?: { detail?: string } })?.data?.detail ?? 'Failed to save'
  }
  finally {
    saving.value = false
  }
}

async function togglePause(r: Rule) {
  const uid = user.value!.uid
  try {
    const updated = await api.put<Rule>(`/api/recurring/${uid}/${r.id}`, { active: !r.active })
    const idx = rules.value.findIndex((x) => x.id === r.id)
    if (idx !== -1) rules.value[idx] = updated
  }
  catch {}
}

async function remove(id: string) {
  const uid = user.value!.uid
  try {
    await api.del(`/api/recurring/${uid}/${id}`)
    rules.value = rules.value.filter((r) => r.id !== id)
  }
  catch {}
}

onMounted(load)
</script>
