<template>
  <div class="mock w-full h-full bg-[var(--bg)] text-[var(--text)] flex flex-col overflow-hidden">
    <!-- top header -->
    <div class="px-5 pt-8 pb-5 flex items-center justify-between">
      <Logo />
      <span class="w-9 h-9 rounded-xl border border-[var(--border)] flex items-center justify-center text-[var(--text-muted)]">
        <Icon
          name="settings"
          :size="16"
        />
      </span>
    </div>

    <!-- hero card -->
    <div class="px-5">
      <div class="bg-[var(--bg-surface)] border border-[var(--border)] rounded-3xl p-5">
        <p class="label">
          Net balance
        </p>
        <p class="text-4xl font-semibold tabular-nums tracking-[-0.04em] mt-2">
          ₱47,231.18
        </p>
        <p class="text-[var(--text-muted)] text-xs tabular-nums mt-1.5">
          Week of Nov 11 – Nov 17
        </p>

        <div class="flex gap-2 mt-4">
          <span class="rounded-full px-3 py-1 text-[11px] font-medium bg-transparent text-[var(--text-muted)] border border-[var(--border)]">Day</span>
          <span class="rounded-full px-3 py-1 text-[11px] font-medium bg-emerald-500 text-white">Week</span>
          <span class="rounded-full px-3 py-1 text-[11px] font-medium bg-transparent text-[var(--text-muted)] border border-[var(--border)]">Month</span>
        </div>

        <div class="mt-4 grid grid-cols-3 divide-x divide-[var(--border)] border-t border-[var(--border)]">
          <div class="py-3 pr-3">
            <p class="text-[var(--text-subtle)] text-[10px]">
              Income
            </p>
            <p class="text-[var(--c-income)] font-semibold text-xs tabular-nums mt-1">
              ₱12,400.00
            </p>
          </div>
          <div class="py-3 px-3">
            <p class="text-[var(--text-subtle)] text-[10px]">
              Expenses
            </p>
            <p class="text-[var(--c-expense)] font-semibold text-xs tabular-nums mt-1">
              ₱3,847.62
            </p>
          </div>
          <div class="py-3 pl-3">
            <p class="text-[var(--text-subtle)] text-[10px]">
              Txns
            </p>
            <p class="text-[var(--text)] font-semibold text-xs tabular-nums mt-1">
              23
            </p>
          </div>
        </div>
      </div>
    </div>

    <!-- recent rows -->
    <div class="px-5 mt-7">
      <p class="label mb-3">
        Recent transactions
      </p>
      <div class="space-y-2">
        <div
          v-for="row in rows"
          :key="row.id"
          class="bg-[var(--bg-surface)] rounded-xl px-4 py-3 flex items-center justify-between"
        >
          <div class="min-w-0 mr-3">
            <p class="text-[var(--text)] text-xs font-medium truncate">
              {{ row.category }}
            </p>
            <p class="text-[var(--text-subtle)] text-[10px] truncate tabular-nums">
              {{ row.meta }}
            </p>
          </div>
          <p
            class="font-semibold text-xs shrink-0 tabular-nums"
            :class="row.type === 'income' ? 'text-[var(--c-income)]' : 'text-[var(--c-expense)]'"
          >
            {{ row.type === 'income' ? '+' : '-' }}{{ row.amount }}
          </p>
        </div>
      </div>
    </div>

    <!-- spacer -->
    <div class="flex-1" />

    <!-- bottom nav -->
    <div class="relative border-t border-[var(--border)] bg-[var(--bg-surface)]/90 backdrop-blur">
      <div class="grid grid-cols-5 max-w-md mx-auto relative h-14">
        <div class="flex flex-col items-center justify-center text-[var(--c-income)]">
          <Icon
            name="home"
            :size="18"
          />
          <span class="text-[9px] mt-1 font-medium">Home</span>
        </div>
        <div class="flex flex-col items-center justify-center text-[var(--text-subtle)]">
          <Icon
            name="stats"
            :size="18"
          />
          <span class="text-[9px] mt-1">Stats</span>
        </div>
        <div class="relative">
          <span class="absolute left-1/2 -translate-x-1/2 -top-5 w-12 h-12 rounded-full bg-emerald-500 text-white flex items-center justify-center shadow-xl shadow-emerald-500/30">
            <Icon
              name="plus"
              :size="20"
              :stroke-width="2.5"
            />
          </span>
        </div>
        <div class="flex flex-col items-center justify-center text-[var(--text-subtle)]">
          <Icon
            name="wallet"
            :size="18"
          />
          <span class="text-[9px] mt-1">Budgets</span>
        </div>
        <div class="flex flex-col items-center justify-center text-[var(--text-subtle)]">
          <Icon
            name="settings"
            :size="18"
          />
          <span class="text-[9px] mt-1">Settings</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
const rows = [
  { id: 1, category: 'Groceries', meta: 'Today · Pure Gold', type: 'expense', amount: '₱847.20' },
  { id: 2, category: 'Allowance', meta: 'Yesterday', type: 'income', amount: '₱12,400.00' },
  { id: 3, category: 'Transport', meta: 'Wed · Grab', type: 'expense', amount: '₱180.00' },
  { id: 4, category: 'Coffee', meta: 'Wed · Tim Hortons', type: 'expense', amount: '₱245.00' },
]
</script>
