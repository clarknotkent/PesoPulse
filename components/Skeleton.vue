<template>
  <span
    class="skeleton block"
    :class="[roundedClass, $attrs.class as string]"
    :style="styleObj"
    aria-hidden="true"
  />
</template>

<script setup lang="ts">
defineOptions({ inheritAttrs: false })

const props = withDefaults(
  defineProps<{
    width?: string | number
    height?: string | number
    rounded?: 'none' | 'sm' | 'md' | 'lg' | 'xl' | '2xl' | 'full'
  }>(),
  {
    rounded: 'md',
  },
)

const roundedClass = computed(() => {
  switch (props.rounded) {
    case 'none': return ''
    case 'sm': return 'rounded-sm'
    case 'lg': return 'rounded-lg'
    case 'xl': return 'rounded-xl'
    case '2xl': return 'rounded-2xl'
    case 'full': return 'rounded-full'
    default: return 'rounded-md'
  }
})

function toCss(v: string | number | undefined): string | undefined {
  if (v === undefined) return undefined
  return typeof v === 'number' ? `${v}px` : v
}

const styleObj = computed(() => {
  const out: Record<string, string> = {}
  const w = toCss(props.width)
  const h = toCss(props.height)
  if (w) out.width = w
  if (h) out.height = h
  return out
})
</script>

<style scoped>
.skeleton {
  background: linear-gradient(
    90deg,
    var(--bg-input) 0%,
    var(--bg-surface) 50%,
    var(--bg-input) 100%
  );
  background-size: 200% 100%;
  animation: shimmer 1.5s var(--ease-in-out) infinite;
}

@keyframes shimmer {
  0% { background-position: 200% 0; }
  100% { background-position: -200% 0; }
}

@media (prefers-reduced-motion: reduce) {
  .skeleton {
    animation: none;
    background: var(--bg-input);
  }
}
</style>
