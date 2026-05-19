<template>
  <div>
    <!-- Month nav -->
    <div class="flex items-center justify-between mb-3">
      <Skeleton
        :width="40"
        :height="40"
        rounded="lg"
      />
      <Skeleton
        :width="140"
        :height="20"
        rounded="md"
      />
      <Skeleton
        :width="40"
        :height="40"
        rounded="lg"
      />
    </div>

    <!-- Weekday header -->
    <div class="grid grid-cols-7 gap-1 mb-1">
      <Skeleton
        v-for="n in 7"
        :key="n"
        :height="12"
        rounded="sm"
        class="mx-auto w-8"
      />
    </div>

    <!-- 6×7 grid -->
    <div class="grid grid-cols-7 gap-1">
      <Skeleton
        v-for="n in 42"
        :key="n"
        rounded="xl"
        class="aspect-square w-full"
      />
    </div>
  </div>
</template>
