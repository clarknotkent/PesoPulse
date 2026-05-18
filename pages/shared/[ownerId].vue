<template>
  <div class="min-h-screen bg-[#0a0a0a] text-white">
    <header class="px-4 pt-10 pb-4">
      <div class="mb-6">
        <p class="text-zinc-400 text-xs uppercase tracking-widest">PesoPulse · Shared View</p>
        <p class="text-zinc-500 text-xs mt-1 font-mono truncate">{{ ownerId }}</p>
      </div>

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

    <div class="px-4 pb-12">
      <div class="flex items-center gap-2 mb-3">
        <h2 class="text-zinc-400 text-xs uppercase tracking-widest">Transactions</h2>
        <span class="text-zinc-600 text-xs">(read-only)</span>
      </div>

      <div v-if="loading" class="text-zinc-500 text-sm text-center py-12">Loading…</div>

      <div v-else-if="error" class="text-red-400 text-sm text-center py-12">{{ error }}</div>

      <div v-else-if="transactions.length === 0" class="text-zinc-600 text-sm text-center py-12">
        No transactions.
      </div>

      <div v-else class="space-y-2">
        <div
          v-for="tx in transactions"
          :key="tx.id"
          class="bg-zinc-900 rounded-xl px-4 py-3 flex items-center justify-between"
        >
          <div class="min-w-0 mr-3">
            <p class="text-white text-sm font-medium">{{ tx.category }}</p>
            <p class="text-zinc-500 text-xs truncate">
              {{ tx.date }}{{ tx.notes ? ' · ' + tx.notes : '' }}
            </p>
          </div>
          <p
            class="font-medium text-sm shrink-0"
            :class="tx.type === 'income' ? 'text-emerald-400' : 'text-red-400'"
          >{{ tx.type === 'income' ? '+' : '-' }}{{ formatPHP(tx.amount) }}</p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
definePageMeta({ middleware: 'auth' })

interface Transaction {
  id: string
  amount: number
  type: 'income' | 'expense'
  date: string
  category: string
  notes?: string | null
}

const route = useRoute()
const ownerId = route.params.ownerId as string
const api = useApi()

const transactions = ref<Transaction[]>([])
const loading = ref(true)
const error = ref('')

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

onMounted(async () => {
  try {
    transactions.value = await api.get<Transaction[]>(`/api/transactions/${ownerId}`)
  } catch (e: unknown) {
    const status = (e as { status?: number })?.status
    if (status === 403) {
      error.value = 'Access denied. You do not have permission to view this ledger.'
    } else {
      error.value = 'Failed to load transactions.'
    }
  } finally {
    loading.value = false
  }
})
</script>
