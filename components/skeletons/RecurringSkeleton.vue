<template>
  <div class="space-y-2">
    <div v-for="n in 3" :key="n" class="bg-[var(--bg-surface)] rounded-2xl p-4 border border-[var(--border)] space-y-2">
      <div class="flex items-center justify-between">
        <div class="min-w-0 space-y-1.5 flex-1">
          <Skeleton :width="140" :height="14" />
          <Skeleton :width="220" :height="11" rounded="sm" />
        </div>
        <div class="flex items-center gap-2 shrink-0">
          <Skeleton :width="56" :height="20" rounded="md" />
          <Skeleton :width="16" :height="16" rounded="sm" />
        </div>
      </div>
    </div>
  </div>
</template>
