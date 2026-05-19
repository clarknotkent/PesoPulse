<template>
  <nav
    v-if="visible"
    class="fixed bottom-0 left-0 right-0 z-[var(--z-nav)] border-t border-[var(--border)] bg-[var(--bg-surface)]/95 backdrop-blur"
    :style="{ paddingBottom: 'env(safe-area-inset-bottom)' }"
  >
    <div class="grid grid-cols-5 max-w-md mx-auto relative">
      <NuxtLink
        v-for="item in items"
        :key="item.key"
        :to="item.to"
        :class="[
          'nav-link flex flex-col items-center justify-center py-2.5',
          item.fab ? 'pointer-events-none' : (isActive(item) ? 'is-active text-[var(--c-income)]' : 'text-[var(--text-subtle)]'),
        ]"
      >
        <template v-if="item.fab">
          <button
            type="button"
            @click.prevent="onFabClick"
            class="fab absolute left-1/2 -translate-x-1/2 -translate-y-4 w-14 h-14 rounded-full bg-emerald-500 text-white shadow-xl shadow-emerald-500/30 flex items-center justify-center pointer-events-auto"
            aria-label="Add transaction"
          >
            <Icon name="plus" :size="24" :stroke-width="2.5" />
          </button>
          <span class="text-[10px] mt-7 opacity-0">.</span>
        </template>
        <template v-else>
          <Icon :name="item.icon!" :size="20" :stroke-width="2" class="nav-icon" />
          <span class="text-[10px] mt-1 font-medium tracking-tight">{{ item.label }}</span>
          <span class="nav-dot"></span>
        </template>
      </NuxtLink>
    </div>
  </nav>
</template>

<script setup lang="ts">
interface NavItem {
  key: string
  to: string
  label: string
  icon?: string
  fab?: boolean
}

const items: NavItem[] = [
  { key: 'home', to: '/dashboard', icon: 'home', label: 'Home' },
  { key: 'stats', to: '/stats', icon: 'stats', label: 'Stats' },
  { key: 'add', to: '/dashboard?add=1', label: 'Add', fab: true },
  { key: 'budgets', to: '/budgets', icon: 'wallet', label: 'Budgets' },
  { key: 'settings', to: '/settings', icon: 'settings', label: 'Settings' },
]

const route = useRoute()
const router = useRouter()

const hiddenRoutes = ['/', '/auth', '/login', '/offline']

const visible = computed(() => {
  const p = route.path
  if (p.startsWith('/shared/')) return false
  return !hiddenRoutes.includes(p)
})

function isActive(item: NavItem) {
  if (item.to.startsWith('/dashboard')) return route.path === '/dashboard' || route.path === '/'
  return route.path === item.to.split('?')[0]
}

const { show: showAddModal } = useAddTransaction()

function onFabClick() {
  showAddModal()
}
</script>

<style scoped>
.nav-link {
  position: relative;
  transition: color 180ms var(--ease-out);
  will-change: transform;
}
.nav-icon {
  transition: transform 220ms var(--ease-out);
  display: inline-block;
}
.nav-link:active .nav-icon {
  transform: scale(0.9);
}
.nav-link.is-active .nav-icon {
  transform: scale(1.1);
}
.nav-dot {
  position: absolute;
  bottom: 4px;
  left: 50%;
  width: 4px;
  height: 4px;
  border-radius: 9999px;
  background: rgb(16 185 129);
  transform: translateX(-50%) scale(0);
  opacity: 0;
  transition:
    transform 240ms var(--ease-out),
    opacity 200ms var(--ease-out);
}
.nav-link.is-active .nav-dot {
  transform: translateX(-50%) scale(1);
  opacity: 1;
}

@media (hover: hover) and (pointer: fine) {
  .nav-link:not(.is-active):hover {
    color: var(--text);
  }
}

.fab {
  transition:
    transform 200ms var(--ease-out),
    box-shadow 200ms var(--ease-out),
    background-color 200ms var(--ease-out);
  will-change: transform;
}
.fab:active {
  transform: translateX(-50%) translateY(-1rem) scale(0.92);
  background-color: rgb(5 150 105);
}
@media (hover: hover) and (pointer: fine) {
  .fab:hover {
    transform: translateX(-50%) translateY(-1.15rem) scale(1.02);
    box-shadow: 0 16px 28px -8px rgb(16 185 129 / 0.45);
  }
}
</style>
