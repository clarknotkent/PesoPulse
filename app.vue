<template>
  <div>
    <NuxtPage />
    <BottomNav />
    <ToastHost />
    <ReauthModal />
  </div>
</template>

<script setup lang="ts">
const { initTheme } = useTheme()

onMounted(() => {
  initTheme()
})
</script>
