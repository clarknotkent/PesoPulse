<template>
  <Teleport to="body">
    <Transition name="modal">
      <div
        v-if="open && tx"
        class="modal-root fixed inset-0 z-[var(--z-modal)] flex items-end sm:items-center sm:justify-center"
      >
        <div
          class="modal-backdrop absolute inset-0 bg-black/60"
          @click="$emit('close')"
        />
        <div class="modal-panel relative w-full sm:max-w-md bg-[var(--bg-surface)] rounded-t-3xl sm:rounded-3xl p-5 pb-safe space-y-5 max-h-[90dvh] overflow-y-auto">
          <div class="flex items-center justify-between">
            <p class="text-[var(--text)] font-medium">
              Edit Transaction
            </p>
            <button
              class="press text-[var(--text-subtle)] hover:text-[var(--text)] w-8 h-8 flex items-center justify-center -mr-2"
              aria-label="Close"
              @click="$emit('close')"
            >
              <Icon
                name="x"
                :size="16"
              />
            </button>
          </div>

          <div class="flex gap-2">
            <button
              v-for="t in (['expense', 'income'] as const)"
              :key="t"
              :class="[
                'press flex-1 py-2 rounded-lg text-sm font-medium toggle',
                draft.type === t
                  ? t === 'income' ? 'bg-emerald-500 text-white' : 'bg-red-500 text-white'
                  : 'bg-[var(--bg-input)] text-[var(--text-muted)]',
              ]"
              @click="draft.type = t"
            >
              {{ t }}
            </button>
          </div>

          <input
            v-model="draft.amount"
            type="number"
            min="0.01"
            step="0.01"
            placeholder="Amount (₱)"
            class="field w-full bg-[var(--bg-input)] text-[var(--text)] rounded-lg px-4 py-3 text-sm"
          />

          <div class="space-y-2">
            <p class="text-[var(--text-subtle)] text-[11px]">
              Date
            </p>
            <input
              v-model="draft.date"
              type="date"
              class="field w-full bg-[var(--bg-input)] text-[var(--text)] rounded-lg px-4 py-3 text-sm tabular-nums"
            />
          </div>

          <CategoryPicker
            v-model="draft.category"
            :categories="categories"
            :type="draft.type"
          />

          <input
            v-model="draft.notes"
            type="text"
            placeholder="Notes (optional)"
            class="field w-full bg-[var(--bg-input)] text-[var(--text)] rounded-lg px-4 py-3 text-sm"
          />

          <p
            v-if="error"
            class="text-[var(--c-expense)] text-xs"
          >
            {{ error }}
          </p>

          <div class="flex gap-2 pt-1">
            <button
              :disabled="saving"
              class="press flex-1 bg-[var(--text)] text-[var(--bg)] font-medium py-3 rounded-lg text-sm disabled:opacity-50 disabled:active:scale-100"
              @click="onSave"
            >
              {{ saving ? 'Saving…' : 'Save' }}
            </button>
            <button
              class="press flex-1 bg-red-900/40 text-[var(--c-expense)] font-medium py-3 rounded-lg text-sm"
              @click="onDelete"
            >
              Delete
            </button>
          </div>
        </div>
      </div>
    </Transition>
  </Teleport>
</template>

<script setup lang="ts">
interface Transaction {
  id: string
  amount: number
  type: 'income' | 'expense'
  date: string
  category: string
  notes?: string | null
}

interface Category { id: string, name: string, icon: string, type: 'income' | 'expense', isSystem: boolean }

const props = defineProps<{
  open: boolean
  tx: Transaction | null
  categories: Category[]
}>()

const emit = defineEmits<{
  close: []
  save: [payload: { id: string, amount: number, type: 'income' | 'expense', category: string, notes: string | null, date: string }]
  delete: [id: string]
}>()

const draft = reactive({
  type: 'expense' as 'income' | 'expense',
  amount: '',
  category: '',
  notes: '',
  date: '',
})

const error = ref('')
const saving = ref(false)

watch(() => props.tx, (tx) => {
  if (tx) {
    draft.type = tx.type
    draft.amount = String(tx.amount)
    draft.category = tx.category
    draft.notes = tx.notes ?? ''
    draft.date = tx.date ?? ''
    error.value = ''
  }
}, { immediate: true })

async function onSave() {
  if (!props.tx) return
  if (!draft.amount || !draft.category) {
    error.value = 'Amount and category required'
    return
  }
  if (!draft.date) {
    error.value = 'Date required'
    return
  }
  saving.value = true
  try {
    emit('save', {
      id: props.tx.id,
      amount: parseFloat(draft.amount),
      type: draft.type,
      category: draft.category,
      notes: draft.notes || null,
      date: draft.date,
    })
  }
  finally {
    saving.value = false
  }
}

function onDelete() {
  if (!props.tx) return
  if (confirm('Delete this transaction?')) {
    emit('delete', props.tx.id)
  }
}
</script>

<style scoped>
.modal-enter-active .modal-backdrop,
.modal-leave-active .modal-backdrop {
  transition: opacity 220ms var(--ease-out);
}
.modal-enter-from .modal-backdrop,
.modal-leave-to .modal-backdrop {
  opacity: 0;
}

.modal-panel {
  transform-origin: center bottom;
  will-change: transform, opacity;
}
.modal-enter-active .modal-panel {
  transition: transform 320ms var(--ease-drawer), opacity 260ms var(--ease-out);
}
.modal-leave-active .modal-panel {
  transition: transform 200ms var(--ease-out), opacity 180ms var(--ease-out);
}
.modal-enter-from .modal-panel {
  opacity: 0;
  transform: translateY(24px) scale(0.97);
}
.modal-leave-to .modal-panel {
  opacity: 0;
  transform: translateY(12px) scale(0.97);
}

@media (min-width: 640px) {
  .modal-panel { transform-origin: center; }
  .modal-enter-from .modal-panel,
  .modal-leave-to .modal-panel {
    transform: scale(0.96);
  }
}

.field {
  transition: box-shadow 160ms var(--ease-out), background-color 160ms var(--ease-out);
}
.field:focus {
  outline: none;
  box-shadow: 0 0 0 1px var(--accent), 0 0 0 4px var(--accent-soft);
}

.toggle {
  transition: background-color 180ms var(--ease-out), color 180ms var(--ease-out), transform 160ms var(--ease-out);
}

.pb-safe {
  padding-bottom: calc(1.25rem + env(safe-area-inset-bottom));
}
</style>
