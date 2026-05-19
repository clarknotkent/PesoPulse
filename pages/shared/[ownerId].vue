<template>
  <div class="min-h-[100dvh] bg-[var(--bg)] text-[var(--text)]">
    <header class="px-5 pt-10 pb-6">
      <div class="mb-6">
        <p class="label">
          PesoPulse · shared view
        </p>
        <p class="text-[var(--text-subtle)] text-xs mt-1 font-mono truncate">
          {{ ownerId }}
        </p>
      </div>

      <div class="bg-[var(--bg-surface)] border border-[var(--border)] rounded-2xl p-5">
        <p class="text-[var(--text-muted)] text-xs mb-1">
          Net balance
        </p>
        <p
          class="text-3xl font-semibold tabular-nums tracking-tightest"
          :class="balance >= 0 ? 'text-[var(--text)]' : 'text-[var(--c-expense)]'"
        >
          {{ formatPHP(balance) }}
        </p>
        <div class="flex gap-6 mt-4 border-t border-[var(--border)] pt-3">
          <div>
            <p class="text-[var(--text-subtle)] text-[11px]">
              Income
            </p>
            <p class="text-[var(--c-income)] font-semibold text-sm tabular-nums mt-1">
              {{ formatPHP(totalIncome) }}
            </p>
          </div>
          <div>
            <p class="text-[var(--text-subtle)] text-[11px]">
              Expenses
            </p>
            <p class="text-[var(--c-expense)] font-semibold text-sm tabular-nums mt-1">
              {{ formatPHP(totalExpense) }}
            </p>
          </div>
        </div>
      </div>
    </header>

    <div class="px-5 pb-12">
      <div class="flex items-center gap-2 mb-3">
        <h2 class="label">
          Transactions
        </h2>
        <span class="text-[var(--text-subtle)] text-xs">(read-only)</span>
      </div>

      <div
        v-if="loading"
        class="text-[var(--text-subtle)] text-sm text-center py-12"
      >
        Loading…
      </div>

      <div
        v-else-if="error"
        class="text-[var(--c-expense)] text-sm text-center py-12"
      >
        {{ error }}
      </div>

      <div
        v-else-if="transactions.length === 0"
        class="text-[var(--text-subtle)] text-sm text-center py-12"
      >
        No transactions.
      </div>

      <div
        v-else
        class="border-t border-[var(--border)]"
      >
        <div
          v-for="tx in transactions"
          :key="tx.id"
          class="py-3 border-b border-[var(--border)] flex items-center justify-between"
        >
          <div class="min-w-0 mr-3">
            <p class="text-[var(--text)] text-sm font-medium truncate">
              {{ tx.category }}
            </p>
            <p class="text-[var(--text-subtle)] text-xs truncate tabular-nums">
              {{ tx.date }}{{ tx.notes ? ' · ' + tx.notes : '' }}
            </p>
          </div>
          <p
            class="font-semibold text-sm shrink-0 tabular-nums"
            :class="tx.type === 'income' ? 'text-[var(--c-income)]' : 'text-[var(--c-expense)]'"
          >
            {{ tx.type === 'income' ? '+' : '-' }}{{ formatPHP(tx.amount) }}
          </p>
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
  }
  catch (e: unknown) {
    const status = (e as { status?: number })?.status
    if (status === 403) {
      error.value = 'Access denied. You do not have permission to view this ledger.'
    }
    else {
      error.value = 'Failed to load transactions.'
    }
  }
  finally {
    loading.value = false
  }
})
</script>
