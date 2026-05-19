<template>
  <div class="space-y-4">
    <!-- Burndown placeholder -->
    <div class="bg-[var(--bg-surface)] rounded-2xl p-5 border border-[var(--border)] space-y-3">
      <div class="flex items-center justify-between">
        <Skeleton
          :width="130"
          :height="10"
          rounded="sm"
        />
        <Skeleton
          :width="60"
          :height="18"
          rounded="full"
        />
      </div>
      <Skeleton
        :width="180"
        :height="32"
        rounded="lg"
      />
      <Skeleton
        :width="240"
        :height="11"
        rounded="sm"
      />
      <div class="space-y-2 pt-1">
        <div class="space-y-1">
          <div class="flex justify-between">
            <Skeleton
              :width="30"
              :height="9"
              rounded="sm"
            />
            <Skeleton
              :width="30"
              :height="9"
              rounded="sm"
            />
          </div>
          <Skeleton
            :height="6"
            rounded="full"
            class="w-full"
          />
        </div>
        <div class="space-y-1">
          <div class="flex justify-between">
            <Skeleton
              :width="30"
              :height="9"
              rounded="sm"
            />
            <Skeleton
              :width="30"
              :height="9"
              rounded="sm"
            />
          </div>
          <Skeleton
            :height="6"
            rounded="full"
            class="w-full"
          />
        </div>
      </div>
    </div>

    <!-- Total card -->
    <div class="bg-[var(--bg-surface)] rounded-2xl p-5 border border-[var(--border)] space-y-3">
      <div class="flex items-center justify-between">
        <Skeleton
          :width="120"
          :height="10"
          rounded="sm"
        />
        <Skeleton
          :width="20"
          :height="14"
          rounded="sm"
        />
      </div>
      <div class="flex items-baseline justify-between">
        <Skeleton
          :width="140"
          :height="24"
        />
        <Skeleton
          :width="100"
          :height="11"
          rounded="sm"
        />
      </div>
      <Skeleton
        :height="8"
        rounded="full"
        class="w-full"
      />
    </div>

    <!-- Per-category rows -->
    <div class="space-y-2">
      <Skeleton
        :width="100"
        :height="9"
        rounded="sm"
        class="mx-1"
      />
      <div
        v-for="n in 3"
        :key="n"
        class="bg-[var(--bg-surface)] rounded-2xl p-4 border border-[var(--border)] space-y-2"
      >
        <div class="flex items-center justify-between">
          <Skeleton
            :width="100"
            :height="14"
          />
          <Skeleton
            :width="120"
            :height="11"
            rounded="sm"
          />
        </div>
        <Skeleton
          :height="8"
          rounded="full"
          class="w-full"
        />
      </div>
    </div>
  </div>
</template>
