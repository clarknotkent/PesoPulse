<template>
  <div class="w-full bg-[var(--bg-surface)] rounded-xl px-4 py-3 flex items-center justify-between">
    <div class="min-w-0 mr-3 flex-1 space-y-1.5">
      <Skeleton :width="120" :height="14" />
      <Skeleton :width="180" :height="11" rounded="sm" />
    </div>
    <Skeleton :width="70" :height="14" />
  </div>
</template>
