<template>
  <Teleport to="body">
    <Transition name="drawer">
      <div v-if="open" class="drawer-root fixed inset-0 z-[var(--z-modal)] flex items-end">
        <div class="drawer-backdrop absolute inset-0 bg-black/60" @click="$emit('close')"></div>
        <div class="drawer-panel relative w-full bg-[var(--bg-surface)] rounded-t-3xl p-5 pb-safe space-y-5 max-h-[85dvh] overflow-y-auto">
          <div class="mx-auto -mt-2 mb-1 h-1 w-10 rounded-full bg-[var(--border)]"></div>
          <div class="flex items-center justify-between">
            <p class="text-[var(--text)] font-medium">Filters</p>
            <button @click="$emit('close')" class="press text-[var(--text-subtle)] hover:text-[var(--text)] w-8 h-8 flex items-center justify-center -mr-2" aria-label="Close">
              <Icon name="x" :size="16" />
            </button>
          </div>

          <!-- Date range -->
          <div>
            <p class="text-[var(--text-subtle)] text-[10px] uppercase mb-1">Date Range</p>
            <div class="grid grid-cols-2 gap-2">
              <input
                v-model="draft.from"
                type="date"
                class="field w-full bg-[var(--bg-input)] text-[var(--text)] rounded-lg px-3 py-2 text-sm"
              />
              <input
                v-model="draft.to"
                type="date"
                class="field w-full bg-[var(--bg-input)] text-[var(--text)] rounded-lg px-3 py-2 text-sm"
              />
            </div>
          </div>

          <!-- Type -->
          <div>
            <p class="text-[var(--text-subtle)] text-[10px] uppercase mb-1">Type</p>
            <div class="flex gap-2">
              <button
                v-for="t in (['', 'income', 'expense'] as const)"
                :key="t"
                @click="draft.type = t"
                :class="[
                  'press toggle flex-1 py-2 rounded-lg text-sm font-medium capitalize',
                  draft.type === t ? 'bg-[var(--text)] text-[var(--bg)]' : 'bg-[var(--bg-input)] text-[var(--text-muted)]',
                ]"
              >{{ t || 'All' }}</button>
            </div>
          </div>

          <!-- Category -->
          <div>
            <p class="text-[var(--text-subtle)] text-[10px] uppercase mb-1">Category</p>
            <CategoryPicker
              v-model="draft.category"
              :categories="filteredCategoriesForType"
              :type="pickerType"
              placeholder="All"
              allow-all
            />
          </div>

          <!-- Amount -->
          <div>
            <p class="text-[var(--text-subtle)] text-[10px] uppercase mb-1">Amount (₱)</p>
            <div class="grid grid-cols-2 gap-2">
              <input
                v-model="draft.minAmount"
                type="number" min="0" step="0.01" placeholder="Min"
                class="field w-full bg-[var(--bg-input)] text-[var(--text)] rounded-lg px-3 py-2 text-sm"
              />
              <input
                v-model="draft.maxAmount"
                type="number" min="0" step="0.01" placeholder="Max"
                class="field w-full bg-[var(--bg-input)] text-[var(--text)] rounded-lg px-3 py-2 text-sm"
              />
            </div>
          </div>

          <div class="flex gap-2 pt-2">
            <button
              @click="applyAndClose"
              class="press flex-1 bg-[var(--text)] text-[var(--bg)] font-medium py-3 rounded-lg text-sm"
            >Apply</button>
            <button
              @click="resetAndClose"
              class="press flex-1 bg-[var(--bg-input)] text-[var(--text)] font-medium py-3 rounded-lg text-sm"
            >Reset</button>
          </div>
        </div>
      </div>
    </Transition>
  </Teleport>
</template>

<script setup lang="ts">
import type { TxnFilters } from '~/composables/useTxnFilters'

interface Category { id: string; name: string; icon: string; type: 'income' | 'expense'; isSystem: boolean }

const props = defineProps<{
  open: boolean
  filters: TxnFilters
  categories: Category[]
}>()

const emit = defineEmits<{
  close: []
  apply: [filters: TxnFilters]
  reset: []
}>()

const draft = reactive<TxnFilters>({ ...props.filters })

watch(() => props.open, (val) => {
  if (val) Object.assign(draft, props.filters)
})

// CategoryPicker needs a type — when filter type is 'all' show union (default expense list + income list).
const pickerType = computed<'income' | 'expense'>(() => (draft.type === 'income' ? 'income' : 'expense'))
const filteredCategoriesForType = computed(() => {
  if (draft.type === '') {
    // Show all categories as one list — re-type the unmatched side to satisfy CategoryPicker filter.
    return props.categories.map((c) => ({ ...c, type: pickerType.value }))
  }
  return props.categories
})

function applyAndClose() {
  emit('apply', { ...draft })
  emit('close')
}

function resetAndClose() {
  emit('reset')
  emit('close')
}
</script>

<style scoped>
.drawer-enter-active .drawer-backdrop,
.drawer-leave-active .drawer-backdrop {
  transition: opacity 240ms var(--ease-out);
}
.drawer-enter-from .drawer-backdrop,
.drawer-leave-to .drawer-backdrop {
  opacity: 0;
}

.drawer-panel {
  will-change: transform;
}
.drawer-enter-active .drawer-panel {
  transition: transform 360ms var(--ease-drawer);
}
.drawer-leave-active .drawer-panel {
  transition: transform 240ms var(--ease-out);
}
.drawer-enter-from .drawer-panel,
.drawer-leave-to .drawer-panel {
  transform: translateY(100%);
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
