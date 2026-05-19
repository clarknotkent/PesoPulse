<template>
  <div>
    <NuxtPage :transition="{ name: transitionName, mode: 'out-in' }" />
    <BottomNav />
    <ToastHost />
  </div>
</template>

<script setup lang="ts">
const { initTheme } = useTheme()
const { transitionName } = useNavStack()

onMounted(() => {
  initTheme()
})
</script>
