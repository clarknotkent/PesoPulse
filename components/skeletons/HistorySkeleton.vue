<template>
  <div v-if="view === 'calendar'" class="space-y-4">
    <CalendarSkeleton />

    <!-- Day detail card -->
    <div class="bg-[var(--bg-surface)] rounded-2xl p-4 border border-[var(--border)] space-y-3">
      <div class="flex items-center justify-between">
        <Skeleton :width="140" :height="14" />
        <Skeleton :width="100" :height="11" rounded="sm" />
      </div>
      <div class="space-y-2">
        <TransactionRowSkeleton v-for="n in 2" :key="n" />
      </div>
    </div>
  </div>

  <div v-else class="space-y-5">
    <div v-for="g in 3" :key="g" class="space-y-2">
      <div class="flex items-center justify-between px-1">
        <Skeleton :width="80" :height="10" rounded="sm" />
        <Skeleton :width="120" :height="10" rounded="sm" />
      </div>
      <TransactionRowSkeleton v-for="n in 3" :key="n" />
    </div>
  </div>
</template>

<script setup lang="ts">
withDefaults(defineProps<{ view?: 'calendar' | 'list' }>(), { view: 'calendar' })
</script>
