<template>
  <div class="page">
    <header class="page-header flex items-center gap-3">
      <NuxtLink to="/budgets" class="press text-[var(--text-subtle)] hover:text-[var(--text)] w-8 h-8 flex items-center justify-center -ml-2" aria-label="Back">
        <Icon name="chevron-left" :size="18" />
      </NuxtLink>
      <h1 class="text-[var(--text)] font-medium">Savings goals</h1>
    </header>

    <div class="page-body">
      <Transition name="swap" mode="out-in">
        <GoalsSkeleton v-if="initialLoading" key="skeleton" />

        <div v-else-if="goals.length === 0" key="empty" class="flex flex-col items-center text-center py-10 gap-3">
          <span class="w-12 h-12 rounded-2xl border border-[var(--border)] flex items-center justify-center text-[var(--text-muted)]">
            <Icon name="piggy" :size="22" />
          </span>
          <div class="space-y-1">
            <p class="text-[var(--text)] text-sm font-medium">No savings goals yet</p>
            <p class="text-[var(--text-subtle)] text-xs">Add one below — track progress against an income category.</p>
          </div>
        </div>

        <section v-else key="list" class="page-section border-t border-[var(--border)]">
          <GoalCard
            v-for="g in goals"
            :key="g.id"
            :goal="g"
            @delete="remove"
          />
        </section>
      </Transition>

      <!-- Add form (earned card) -->
      <section class="page-section">
        <div class="bg-[var(--bg-surface)] border border-[var(--border)] rounded-2xl p-4 space-y-4">
          <p class="label">New goal</p>

          <div class="space-y-3">
            <input
              v-model="form.name"
              placeholder="Goal name (e.g. Emergency Fund)"
              class="focus-ring w-full bg-[var(--bg-input)] text-[var(--text)] rounded-lg px-4 py-3 text-sm"
            />

            <input
              v-model="form.target"
              type="number" min="0.01" step="0.01" placeholder="Target (₱)"
              class="focus-ring w-full bg-[var(--bg-input)] text-[var(--text)] rounded-lg px-4 py-3 text-sm"
            />

            <CategoryPicker
              v-model="form.category"
              :categories="incomeCategories"
              type="income"
              placeholder="Tracking category (income)"
            />

            <div class="space-y-1">
              <p class="label-quiet">Deadline</p>
              <input
                v-model="form.deadline"
                type="date"
                class="focus-ring w-full bg-[var(--bg-input)] text-[var(--text)] rounded-lg px-4 py-3 text-sm"
              />
            </div>
          </div>

          <p v-if="formError" class="text-[var(--c-expense)] text-xs">{{ formError }}</p>

          <button
            @click="save"
            :disabled="saving"
            class="press w-full bg-[var(--text)] text-[var(--bg)] font-medium py-3 rounded-lg text-sm disabled:opacity-50 disabled:active:scale-100"
          >{{ saving ? 'Saving…' : 'Add goal' }}</button>
        </div>
      </section>
    </div>
  </div>
</template>

<script setup lang="ts">
definePageMeta({ middleware: 'auth' })

interface Goal {
  id: string
  name: string
  target: number
  deadline: string
  category: string
  startDate: string
  progress: number
  pctComplete: number
  daysLeft: number
}

interface Category { id: string; name: string; icon: string; type: 'income' | 'expense'; isSystem: boolean }

const { user } = useAuth()
const api = useApi()

const goals = ref<Goal[]>([])
const categories = ref<Category[]>([])
const loading = ref(false)
const initialLoaded = ref(false)
const initialLoading = computed(() => loading.value && !initialLoaded.value)
const saving = ref(false)
const formError = ref('')

const form = reactive({
  name: '',
  target: '',
  category: '',
  deadline: '',
})

const incomeCategories = computed(() => categories.value.filter((c) => c.type === 'income'))

async function load() {
  const uid = user.value?.uid
  if (!uid) return
  loading.value = true
  const start = Date.now()
  try {
    const [g, c] = await Promise.all([
      api.get<Goal[]>(`/api/goals/${uid}`),
      api.get<Category[]>(`/api/categories/${uid}`),
    ])
    goals.value = g
    categories.value = c
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

async function save() {
  formError.value = ''
  if (!form.name || !form.target || !form.category || !form.deadline) {
    formError.value = 'All fields required'
    return
  }
  const uid = user.value!.uid
  saving.value = true
  try {
    const goal = await api.post<Goal>(`/api/goals/${uid}`, {
      name: form.name,
      target: parseFloat(form.target),
      category: form.category,
      deadline: form.deadline,
    })
    goals.value.push(goal)
    form.name = ''
    form.target = ''
    form.category = ''
    form.deadline = ''
  } catch (e: unknown) {
    formError.value = (e as { data?: { detail?: string } })?.data?.detail ?? 'Failed to save'
  } finally {
    saving.value = false
  }
}

async function remove(id: string) {
  const uid = user.value!.uid
  try {
    await api.del(`/api/goals/${uid}/${id}`)
    goals.value = goals.value.filter((g) => g.id !== id)
  } catch {}
}

onMounted(load)
</script>
