<template>
  <div class="picker">
    <!-- Trigger row -->
    <button
      type="button"
      @click="toggle"
      class="press field w-full bg-[var(--bg-input)] text-left rounded-lg px-4 py-3 text-sm flex items-center justify-between"
      :aria-expanded="expanded"
    >
      <span class="flex items-center gap-2 min-w-0">
        <span v-if="selected" class="flex items-center gap-2 text-[var(--text)] truncate">
          <Icon :name="resolveIcon(selected)" :size="16" class="text-[var(--c-income)]" />
          {{ selected.name }}
        </span>
        <span v-else class="text-[var(--text-subtle)]">{{ placeholder }}</span>
      </span>
      <Icon
        name="chevron-down"
        :size="16"
        class="text-[var(--text-subtle)] transition-transform"
        :class="{ 'rotate-180': expanded }"
      />
    </button>

    <!-- Inline accordion grid -->
    <Transition name="accordion">
      <div v-if="expanded" class="grid-wrap mt-2">
        <div v-if="filtered.length === 0" class="text-[var(--text-subtle)] text-xs px-1 py-3">
          No {{ type }} categories yet.
        </div>
        <div v-else class="grid grid-cols-3 gap-2">
          <button
            v-for="(c, i) in filtered"
            :key="c.id"
            type="button"
            @click="pick(c)"
            class="press chip stagger-in rounded-lg px-2 py-2.5 text-xs font-medium flex flex-col items-center gap-1 text-center"
            :class="modelValue === c.name
              ? 'bg-emerald-500/15 text-[var(--c-income)] ring-1 ring-emerald-500/60'
              : 'bg-[var(--bg-input)] text-[var(--text)]'"
            :style="{ '--i': Math.min(i, 11) }"
          >
            <Icon :name="resolveIcon(c)" :size="18" />
            <span class="truncate w-full">{{ c.name }}</span>
          </button>
        </div>
      </div>
    </Transition>
  </div>
</template>

<script setup lang="ts">
interface Category {
  id: string
  name: string
  icon: string
  type: 'income' | 'expense'
  isSystem?: boolean
}

const props = withDefaults(
  defineProps<{
    modelValue: string
    categories: Category[]
    type?: 'income' | 'expense'
    placeholder?: string
    allowAll?: boolean
  }>(),
  { type: 'expense', placeholder: 'Select category', allowAll: false },
)

const emit = defineEmits<{ 'update:modelValue': [value: string] }>()

const expanded = ref(false)

function toggle() {
  expanded.value = !expanded.value
}

const filtered = computed<Category[]>(() => {
  const list = props.categories.filter((c) => c.type === props.type)
  if (props.allowAll) {
    return [
      { id: '__all__', name: 'All', icon: 'tag', type: props.type, isSystem: true },
      ...list,
    ]
  }
  return list
})

const selected = computed<Category | null>(() => {
  if (!props.modelValue) return null
  return filtered.value.find((c) => c.name === props.modelValue) ?? null
})

function pick(c: Category) {
  const next = c.id === '__all__' ? '' : c.name
  emit('update:modelValue', next)
  expanded.value = false
}

watch(
  () => props.type,
  () => {
    if (selected.value && selected.value.type !== props.type) {
      emit('update:modelValue', '')
    }
  },
)

const ICON_KEYWORDS: Array<[RegExp, string]> = [
  [/food|meal|grocer|restaurant|drink|coffee|snack/i, 'receipt'],
  [/transport|fuel|gas|fare|commute|ride|taxi|grab/i, 'arrow-right'],
  [/util|bill|electric|water|internet|phone|rent/i, 'wallet'],
  [/health|medic|pharma|hospital/i, 'sparkles'],
  [/salary|pay|wage|allowance|bonus/i, 'trend-up'],
  [/save|fund|emergency|goal/i, 'piggy'],
  [/shop|cloth|gift/i, 'tag'],
  [/entertain|movie|fun|game|stream/i, 'sparkles'],
  [/school|tuition|book|edu/i, 'list'],
  [/travel|trip|hotel|flight/i, 'arrow-right'],
]

function resolveIcon(cat: Category): string {
  const m = ICON_KEYWORDS.find(([re]) => re.test(cat.name))
  if (m) return m[1]
  return cat.type === 'income' ? 'trend-up' : 'tag'
}
</script>

<style scoped>
.field {
  transition:
    box-shadow 160ms var(--ease-out),
    background-color 160ms var(--ease-out);
}
.field:focus,
.field:focus-visible {
  outline: none;
  box-shadow: 0 0 0 1px var(--accent), 0 0 0 4px var(--accent-soft);
}

.chip {
  transition:
    background-color 200ms var(--ease-out),
    color 200ms var(--ease-out),
    box-shadow 200ms var(--ease-out),
    transform 160ms var(--ease-out);
  will-change: transform;
}

.rotate-180 {
  transform: rotate(180deg);
}

.accordion-enter-active,
.accordion-leave-active {
  transition:
    grid-template-rows 260ms var(--ease-out),
    opacity 200ms var(--ease-out);
  display: grid;
  grid-template-rows: 1fr;
  overflow: hidden;
}
.accordion-enter-from,
.accordion-leave-to {
  grid-template-rows: 0fr;
  opacity: 0;
}
.accordion-enter-active > *,
.accordion-leave-active > * {
  overflow: hidden;
  min-height: 0;
}
</style>
