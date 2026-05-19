<template>
  <NuxtLink to="/dashboard" class="logo press inline-flex items-center gap-2 select-none">
    <span class="logo-mark relative w-7 h-7 rounded-lg overflow-hidden flex items-center justify-center">
      <span class="absolute inset-0 bg-gradient-to-br from-emerald-400 to-emerald-700"></span>
      <svg viewBox="0 0 24 24" class="relative w-4 h-4 text-white" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
        <path d="M3 12h4l2 -6 4 12 2 -6h6" />
      </svg>
    </span>
    <span v-if="!iconOnly" class="logo-word text-[15px] font-semibold tracking-tightest">
      Peso<span class="text-[var(--c-income)]">Pulse</span>
    </span>
  </NuxtLink>
</template>

<script setup lang="ts">
withDefaults(defineProps<{ iconOnly?: boolean }>(), { iconOnly: false })
</script>

<style scoped>
.logo {
  transition: transform 160ms var(--ease-out);
}
.logo-mark {
  transition: transform 220ms var(--ease-out), box-shadow 240ms var(--ease-out);
  box-shadow: 0 0 0 1px rgb(16 185 129 / 0.25), 0 8px 16px -8px rgb(16 185 129 / 0.4);
}
@media (hover: hover) and (pointer: fine) {
  .logo:hover .logo-mark {
    transform: rotate(-3deg) scale(1.04);
  }
}
</style>
