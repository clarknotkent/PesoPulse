<template>
  <div class="flex gap-2">
    <div class="flex-1 relative">
      <input
        :value="modelValue"
        @input="onInput"
        type="text"
        placeholder="Search notes or category…"
        class="search-input w-full bg-[var(--bg-surface)] text-[var(--text)] placeholder-[var(--text-subtle)] rounded-xl pl-10 pr-4 py-2.5 text-sm outline-none"
      />
      <span class="absolute left-3 top-1/2 -translate-y-1/2 text-[var(--text-subtle)] pointer-events-none">
        <Icon name="search" :size="16" />
      </span>
    </div>
    <button
      @click="$emit('open-filters')"
      class="press relative w-11 h-11 bg-[var(--bg-surface)] rounded-xl text-[var(--text-muted)] flex items-center justify-center filter-btn"
      aria-label="Open filters"
    >
      <Icon name="sliders" :size="18" />
      <Transition name="badge">
        <span
          v-if="activeCount > 0"
          class="absolute -top-1 -right-1 bg-emerald-500 text-white text-[10px] rounded-full w-4 h-4 flex items-center justify-center font-medium"
        >{{ activeCount }}</span>
      </Transition>
    </button>
  </div>
</template>

<script setup lang="ts">
const props = defineProps<{
  modelValue: string
  activeCount: number
}>()

const emit = defineEmits<{
  'update:modelValue': [value: string]
  'open-filters': []
}>()

let timer: ReturnType<typeof setTimeout> | null = null
function onInput(e: Event) {
  const val = (e.target as HTMLInputElement).value
  if (timer) clearTimeout(timer)
  timer = setTimeout(() => emit('update:modelValue', val), 250)
}
</script>

<style scoped>
.search-input {
  transition:
    box-shadow 200ms var(--ease-out),
    background-color 200ms var(--ease-out);
}
.search-input:focus {
  background-color: var(--bg-input);
  box-shadow: 0 0 0 1px var(--accent), 0 0 0 4px var(--accent-soft);
}

.filter-btn {
  transition:
    color 180ms var(--ease-out),
    background-color 180ms var(--ease-out),
    transform 160ms var(--ease-out);
}
@media (hover: hover) and (pointer: fine) {
  .filter-btn:hover { color: var(--text); }
}

.badge-enter-active,
.badge-leave-active {
  transition: transform 220ms var(--ease-out), opacity 180ms var(--ease-out);
}
.badge-enter-from,
.badge-leave-to {
  opacity: 0;
  transform: scale(0.5);
}
</style>
