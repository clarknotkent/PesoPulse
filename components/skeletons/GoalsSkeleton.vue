<template>
  <div class="space-y-4">
    <div
      v-for="n in 2"
      :key="n"
      class="bg-[var(--bg-surface)] rounded-2xl p-5 border border-[var(--border)] space-y-3"
    >
      <div class="flex items-center justify-between">
        <div class="space-y-1.5 min-w-0">
          <Skeleton
            :width="140"
            :height="14"
          />
          <Skeleton
            :width="100"
            :height="11"
            rounded="sm"
          />
        </div>
        <Skeleton
          :width="16"
          :height="16"
          rounded="sm"
        />
      </div>
      <div class="flex items-center gap-4">
        <Skeleton
          :width="80"
          :height="80"
          rounded="full"
        />
        <div class="min-w-0 flex-1 space-y-1.5">
          <Skeleton
            :width="120"
            :height="22"
          />
          <Skeleton
            :width="90"
            :height="11"
            rounded="sm"
          />
          <Skeleton
            :width="60"
            :height="10"
            rounded="sm"
          />
        </div>
      </div>
    </div>
  </div>
</template>
