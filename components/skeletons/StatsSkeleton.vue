<template>
  <div class="space-y-4">
    <!-- All-time strip -->
    <div class="bg-[var(--bg-surface)] rounded-2xl p-4 flex items-center justify-between border border-[var(--border)]">
      <div class="space-y-2">
        <Skeleton
          :width="80"
          :height="9"
          rounded="sm"
        />
        <Skeleton
          :width="140"
          :height="22"
        />
      </div>
      <div class="space-y-1.5 items-end flex flex-col">
        <Skeleton
          :width="80"
          :height="11"
          rounded="sm"
        />
        <Skeleton
          :width="80"
          :height="11"
          rounded="sm"
        />
      </div>
    </div>

    <!-- PeriodSwitcher -->
    <div class="space-y-3">
      <div class="flex gap-1 bg-[var(--bg-surface)] rounded-xl p-1 border border-[var(--border)]">
        <Skeleton
          v-for="n in 3"
          :key="n"
          :height="36"
          class="flex-1"
          rounded="lg"
        />
      </div>
      <div class="flex items-center justify-between">
        <Skeleton
          :width="40"
          :height="40"
          rounded="lg"
        />
        <Skeleton
          :width="160"
          :height="16"
          rounded="md"
        />
        <Skeleton
          :width="40"
          :height="40"
          rounded="lg"
        />
      </div>
    </div>

    <!-- Summary cards -->
    <div class="grid grid-cols-2 gap-3">
      <div
        v-for="n in 4"
        :key="n"
        class="bg-[var(--bg-surface)] rounded-2xl p-4 space-y-2 border border-[var(--border)]"
      >
        <Skeleton
          :width="60"
          :height="9"
          rounded="sm"
        />
        <Skeleton
          :width="90"
          :height="22"
        />
        <Skeleton
          :width="100"
          :height="11"
          rounded="sm"
        />
      </div>
    </div>

    <!-- Donut -->
    <div class="bg-[var(--bg-surface)] rounded-2xl p-5 border border-[var(--border)]">
      <div class="flex items-center justify-between mb-4">
        <Skeleton
          :width="80"
          :height="10"
          rounded="sm"
        />
        <Skeleton
          :width="120"
          :height="28"
          rounded="lg"
        />
      </div>
      <div class="flex flex-col items-center">
        <Skeleton
          :width="192"
          :height="192"
          rounded="full"
        />
        <ul class="w-full mt-4 space-y-2">
          <li
            v-for="n in 4"
            :key="n"
            class="flex items-center justify-between"
          >
            <div class="flex items-center gap-2">
              <Skeleton
                :width="10"
                :height="10"
                rounded="full"
              />
              <Skeleton
                :width="80"
                :height="11"
                rounded="sm"
              />
            </div>
            <Skeleton
              :width="80"
              :height="11"
              rounded="sm"
            />
          </li>
        </ul>
      </div>
    </div>

    <!-- Trend bars -->
    <div class="bg-[var(--bg-surface)] rounded-2xl p-5 border border-[var(--border)]">
      <Skeleton
        :width="60"
        :height="10"
        rounded="sm"
        class="mb-4"
      />
      <div class="h-56 flex items-end justify-between gap-2">
        <div
          v-for="(h, i) in barHeights"
          :key="i"
          class="flex-1 flex flex-col items-center gap-1"
        >
          <Skeleton
            :height="h"
            rounded="sm"
            class="w-full"
          />
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
const barHeights = [120, 80, 160, 100, 140, 90, 130]
</script>
