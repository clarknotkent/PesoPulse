<template>
  <div class="min-h-screen bg-[#0a0a0a] text-white">
    <!-- Header -->
    <header class="px-4 pt-10 pb-4">
      <div class="flex items-center justify-between mb-6">
        <div>
          <p class="text-zinc-400 text-xs uppercase tracking-widest">PesoPulse</p>
          <p class="text-white text-sm font-medium truncate max-w-[200px]">{{ initialized ? user?.email : '' }}</p>
        </div>
        <div class="flex items-center gap-4">
          <NuxtLink to="/settings" class="text-zinc-500 hover:text-white text-sm transition">⚙</NuxtLink>
          <button @click="signOut" class="text-zinc-500 hover:text-white text-sm transition">
            Sign out
          </button>
        </div>
      </div>

      <!-- Balance Card -->
      <div class="bg-zinc-900 rounded-2xl p-5">
        <p class="text-zinc-400 text-xs mb-1">Net Balance</p>
        <p
          class="text-3xl font-bold"
          :class="balance >= 0 ? 'text-white' : 'text-red-400'"
        >{{ formatPHP(balance) }}</p>
        <div class="flex gap-6 mt-4">
          <div>
            <p class="text-zinc-500 text-xs">Income</p>
            <p class="text-emerald-400 font-medium text-sm">{{ formatPHP(totalIncome) }}</p>
          </div>
          <div>
            <p class="text-zinc-500 text-xs">Expenses</p>
            <p class="text-red-400 font-medium text-sm">{{ formatPHP(totalExpense) }}</p>
          </div>
        </div>
      </div>
    </header>

    <!-- Add Transaction Toggle -->
    <div class="px-4 mb-4">
      <button
        @click="showForm = !showForm"
        class="w-full bg-white text-black font-medium py-3 rounded-xl text-sm hover:bg-zinc-200 transition"
      >{{ showForm ? 'Cancel' : '+ Add Transaction' }}</button>
    </div>

    <!-- Add Transaction Form -->
    <Transition name="slide">
      <div v-if="showForm" class="px-4 mb-4">
        <div class="bg-zinc-900 rounded-2xl p-5 space-y-3">
          <ReceiptScanner @parsed="onReceiptParsed" />

          <!-- Income / Expense toggle -->
          <div class="flex gap-2">
            <button
              v-for="t in (['expense', 'income'] as const)"
              :key="t"
              @click="form.type = t"
              :class="[
                'flex-1 py-2 rounded-lg text-sm font-medium transition',
                form.type === t
                  ? t === 'income' ? 'bg-emerald-500 text-white' : 'bg-red-500 text-white'
                  : 'bg-zinc-800 text-zinc-400',
              ]"
            >{{ t === 'income' ? 'Income' : 'Expense' }}</button>
          </div>

          <input
            v-model="form.amount"
            type="number"
            placeholder="Amount (₱)"
            min="0.01"
            step="0.01"
            class="w-full bg-zinc-800 text-white placeholder-zinc-500 rounded-lg px-4 py-3 text-sm outline-none focus:ring-1 focus:ring-zinc-600"
          />

          <select
            v-model="form.category"
            class="w-full bg-zinc-800 text-white rounded-lg px-4 py-3 text-sm outline-none focus:ring-1 focus:ring-zinc-600"
          >
            <option value="" disabled>Select category</option>
            <option v-for="cat in filteredCategories" :key="cat.id" :value="cat.name">
              {{ cat.icon }} {{ cat.name }}
            </option>
          </select>

          <input
            v-model="form.notes"
            type="text"
            placeholder="Notes (optional)"
            class="w-full bg-zinc-800 text-white placeholder-zinc-500 rounded-lg px-4 py-3 text-sm outline-none focus:ring-1 focus:ring-zinc-600"
          />

          <p v-if="formError" class="text-red-400 text-xs">{{ formError }}</p>

          <button
            @click="addTransaction"
            :disabled="submitting"
            class="w-full bg-white text-black font-medium py-3 rounded-lg text-sm hover:bg-zinc-200 transition disabled:opacity-50"
          >{{ submitting ? 'Saving…' : 'Save Transaction' }}</button>
        </div>
      </div>
    </Transition>

    <!-- Transaction List -->
    <div class="px-4 pb-12">
      <h2 class="text-zinc-400 text-xs uppercase tracking-widest mb-3">Transactions</h2>

      <p v-if="deleteError" class="text-red-400 text-xs mb-2">{{ deleteError }}</p>

      <div v-if="loading" class="text-zinc-500 text-sm text-center py-12">Loading…</div>

      <div v-else-if="transactions.length === 0" class="text-zinc-600 text-sm text-center py-12">
        No transactions yet. Add one above.
      </div>

      <div v-else class="space-y-2">
        <div
          v-for="tx in transactions"
          :key="tx.id"
          class="bg-zinc-900 rounded-xl overflow-hidden"
        >
          <div class="px-4 py-3 flex items-center justify-between">
            <div class="min-w-0 mr-3">
              <p class="text-white text-sm font-medium">{{ tx.category }}</p>
              <p class="text-zinc-500 text-xs truncate">
                {{ tx.date }}{{ tx.notes ? ' · ' + tx.notes : '' }}
              </p>
            </div>
            <div class="flex items-center gap-3 shrink-0">
              <p
                class="font-medium text-sm"
                :class="tx.type === 'income' ? 'text-emerald-400' : 'text-red-400'"
              >{{ tx.type === 'income' ? '+' : '-' }}{{ formatPHP(tx.amount) }}</p>
              <button
                @click="startEdit(tx)"
                class="text-zinc-600 hover:text-white transition text-xs leading-none"
              >✎</button>
              <button
                @click="deleteTransaction(tx.id)"
                class="text-zinc-600 hover:text-red-400 transition text-xs leading-none"
              >✕</button>
            </div>
          </div>

          <!-- Inline edit form -->
          <div v-if="editingId === tx.id" class="px-4 pb-4 space-y-3 border-t border-zinc-800">
            <div class="flex gap-2 pt-3">
              <button
                v-for="t in (['expense', 'income'] as const)"
                :key="t"
                @click="editForm.type = t"
                :class="[
                  'flex-1 py-2 rounded-lg text-sm font-medium transition',
                  editForm.type === t
                    ? t === 'income' ? 'bg-emerald-500 text-white' : 'bg-red-500 text-white'
                    : 'bg-zinc-800 text-zinc-400',
                ]"
              >{{ t === 'income' ? 'Income' : 'Expense' }}</button>
            </div>

            <input
              v-model="editForm.amount"
              type="number"
              placeholder="Amount (₱)"
              min="0.01"
              step="0.01"
              class="w-full bg-zinc-800 text-white placeholder-zinc-500 rounded-lg px-4 py-3 text-sm outline-none focus:ring-1 focus:ring-zinc-600"
            />

            <select
              v-model="editForm.category"
              class="w-full bg-zinc-800 text-white rounded-lg px-4 py-3 text-sm outline-none focus:ring-1 focus:ring-zinc-600"
            >
              <option value="" disabled>Select category</option>
              <option v-for="cat in filteredEditCategories" :key="cat.id" :value="cat.name">
                {{ cat.icon }} {{ cat.name }}
              </option>
            </select>

            <input
              v-model="editForm.notes"
              type="text"
              placeholder="Notes (optional)"
              class="w-full bg-zinc-800 text-white placeholder-zinc-500 rounded-lg px-4 py-3 text-sm outline-none focus:ring-1 focus:ring-zinc-600"
            />

            <p v-if="editError" class="text-red-400 text-xs">{{ editError }}</p>

            <div class="flex gap-2">
              <button
                @click="saveEdit(tx.id)"
                :disabled="editSubmitting"
                class="flex-1 bg-white text-black font-medium py-3 rounded-lg text-sm hover:bg-zinc-200 transition disabled:opacity-50"
              >{{ editSubmitting ? 'Saving…' : 'Save' }}</button>
              <button
                @click="cancelEdit"
                class="flex-1 bg-zinc-800 text-zinc-400 font-medium py-3 rounded-lg text-sm hover:bg-zinc-700 transition"
              >Cancel</button>
            </div>
          </div>
        </div>
      </div>
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

const { user, initialized, signOut } = useAuth()
const api = useApi()

const transactions = ref<Transaction[]>([])
const categories = ref<Category[]>([])
const loading = ref(true)
const showForm = ref(false)
const submitting = ref(false)
const formError = ref('')
const deleteError = ref('')

const form = reactive({
  type: 'expense' as 'income' | 'expense',
  amount: '',
  category: '',
  notes: '',
})

const editingId = ref<string | null>(null)
const editForm = reactive({
  type: 'expense' as 'income' | 'expense',
  amount: '',
  category: '',
  notes: '',
})
const editSubmitting = ref(false)
const editError = ref('')

const balance = computed(() =>
  transactions.value.reduce(
    (sum, tx) => (tx.type === 'income' ? sum + tx.amount : sum - tx.amount),
    0,
  ),
)
const totalIncome = computed(() =>
  transactions.value
    .filter((tx) => tx.type === 'income')
    .reduce((sum, tx) => sum + tx.amount, 0),
)
const totalExpense = computed(() =>
  transactions.value
    .filter((tx) => tx.type === 'expense')
    .reduce((sum, tx) => sum + tx.amount, 0),
)
const filteredCategories = computed(() =>
  categories.value.filter((cat) => cat.type === form.type),
)
const filteredEditCategories = computed(() =>
  categories.value.filter((cat) => cat.type === editForm.type),
)

async function loadData() {
  const uid = user.value?.uid
  if (!uid) return
  loading.value = true
  try {
    const [txList, catList] = await Promise.all([
      api.get<Transaction[]>(`/api/transactions/${uid}`),
      api.get<Category[]>(`/api/categories/${uid}`),
    ])
    transactions.value = txList
    categories.value = catList
  } finally {
    loading.value = false
  }
}

async function addTransaction() {
  formError.value = ''
  if (!form.amount || !form.category) {
    formError.value = 'Amount and category are required'
    return
  }
  submitting.value = true
  try {
    const uid = user.value!.uid
    const tx = await api.post<Transaction>(`/api/transactions/${uid}`, {
      amount: parseFloat(form.amount),
      type: form.type,
      category: form.category,
      notes: form.notes || null,
    })
    transactions.value.unshift(tx)
    showForm.value = false
    form.amount = ''
    form.category = ''
    form.notes = ''
  } catch (e: unknown) {
    formError.value = (e as { data?: { detail?: string } })?.data?.detail ?? 'Failed to save'
  } finally {
    submitting.value = false
  }
}

async function deleteTransaction(id: string) {
  deleteError.value = ''
  try {
    const uid = user.value!.uid
    await api.del(`/api/transactions/${uid}/${id}`)
    transactions.value = transactions.value.filter((tx) => tx.id !== id)
  } catch {
    deleteError.value = 'Failed to delete transaction'
  }
}

function startEdit(tx: Transaction) {
  editingId.value = tx.id
  editForm.type = tx.type
  editForm.amount = String(tx.amount)
  editForm.category = tx.category
  editForm.notes = tx.notes ?? ''
  editError.value = ''
}

function cancelEdit() {
  editingId.value = null
  editError.value = ''
}

async function saveEdit(id: string) {
  editError.value = ''
  if (!editForm.amount || !editForm.category) {
    editError.value = 'Amount and category are required'
    return
  }
  editSubmitting.value = true
  try {
    const uid = user.value!.uid
    const updated = await api.put<Transaction>(`/api/transactions/${uid}/${id}`, {
      amount: parseFloat(editForm.amount),
      type: editForm.type,
      category: editForm.category,
      notes: editForm.notes || null,
    })
    const idx = transactions.value.findIndex((tx) => tx.id === id)
    if (idx !== -1) transactions.value[idx] = updated
    editingId.value = null
  } catch (e: unknown) {
    editError.value = (e as { data?: { detail?: string } })?.data?.detail ?? 'Failed to update'
  } finally {
    editSubmitting.value = false
  }
}

function onReceiptParsed({ amount, notes }: { amount: number | null; date: string | null; notes: string | null }) {
  if (amount !== null) form.amount = String(amount)
  if (notes) form.notes = notes
}

onMounted(loadData)
</script>

<style scoped>
.slide-enter-active,
.slide-leave-active {
  transition: all 0.2s ease;
}
.slide-enter-from,
.slide-leave-to {
  opacity: 0;
  transform: translateY(-8px);
}
</style>
