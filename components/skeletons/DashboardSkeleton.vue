<template>
  <div class="bg-[var(--bg-surface)] border border-[var(--border)] rounded-3xl p-6 space-y-5">
    <Skeleton :width="90" :height="10" rounded="sm" />
    <div>
      <Skeleton :width="240" :height="40" rounded="lg" />
      <div class="mt-2">
        <Skeleton :width="160" :height="12" rounded="sm" />
      </div>
    </div>

    <div class="flex gap-2">
      <Skeleton v-for="n in 3" :key="n" :width="60" :height="24" rounded="full" />
    </div>

    <div class="border-t border-[var(--border)] pt-3 grid grid-cols-3 gap-3">
      <div v-for="n in 3" :key="n" class="space-y-1.5">
        <Skeleton :width="50" :height="9" rounded="sm" />
        <Skeleton :width="70" :height="14" />
      </div>
    </div>
  </div>
</template>
