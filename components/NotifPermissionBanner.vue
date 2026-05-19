<template>
  <div
    v-if="show"
    class="bg-emerald-500/10 border border-emerald-500/30 rounded-2xl p-4 flex items-start gap-3"
  >
    <div class="flex-1 min-w-0">
      <p class="text-[var(--c-income)] dark:text-[var(--c-income)] text-sm font-medium">Enable notifications</p>
      <p class="text-[var(--c-income)]/80 dark:text-[var(--c-income)]/70 text-xs mt-0.5">Get budget alerts and weekly digests.</p>
    </div>
    <div class="flex gap-2 shrink-0">
      <button
        @click="enable"
        :disabled="working"
        class="press bg-emerald-500 text-white text-xs font-medium px-3 py-1.5 rounded-lg disabled:opacity-50"
      >{{ working ? '…' : 'Enable' }}</button>
      <button
        @click="skip"
        class="press text-[var(--c-income)]/80 dark:text-[var(--c-income)]/70 text-xs px-2"
      >Skip</button>
    </div>
  </div>
</template>

<script setup lang="ts">
const { status, detectStatus, register } = useFcm()
const skipped = useState<boolean>('fcm:skipped', () => {
  if (typeof localStorage === 'undefined') return false
  return localStorage.getItem('pesopulse:fcm-skipped') === '1'
})
const working = ref(false)

const show = computed(() => status.value === 'default' && !skipped.value)

async function enable() {
  working.value = true
  await register()
  working.value = false
}

function skip() {
  skipped.value = true
  if (typeof localStorage !== 'undefined') {
    localStorage.setItem('pesopulse:fcm-skipped', '1')
  }
}

onMounted(detectStatus)
</script>
