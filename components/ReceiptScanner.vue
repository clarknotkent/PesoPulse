<template>
  <div>
    <input
      ref="fileInput"
      type="file"
      accept="image/*"
      capture="environment"
      class="hidden"
      @change="onFileSelected"
    />
    <button
      type="button"
      @click="fileInput?.click()"
      :disabled="loading"
      class="w-full bg-zinc-800 text-white font-medium py-3 rounded-lg text-sm hover:bg-zinc-700 transition disabled:opacity-50 flex items-center justify-center gap-2"
    >
      <span v-if="loading" class="animate-spin">⏳</span>
      <span>{{ loading ? 'Scanning…' : '📷 Scan Receipt' }}</span>
    </button>
    <p v-if="error" class="text-red-400 text-xs mt-1">{{ error }}</p>
  </div>
</template>

<script setup lang="ts">
const emit = defineEmits<{ parsed: [{ amount: number | null; date: string | null; notes: string | null }] }>()
const { idToken } = useAuth()
const fileInput = ref<HTMLInputElement | null>(null)
const loading = ref(false)
const error = ref('')

async function onFileSelected(e: Event) {
  const file = (e.target as HTMLInputElement).files?.[0]
  if (!file) return
  loading.value = true
  error.value = ''
  try {
    const token = await idToken()
    if (!token) throw new Error('Not authenticated')
    const fd = new FormData()
    fd.append('file', file)
    const result = await $fetch<{ success: boolean; data: { merchant: string | null; total: number | null; date: string | null } }>('/api/receipts/parse', {
      method: 'POST',
      body: fd,
      headers: { Authorization: `Bearer ${token}` },
    })
    emit('parsed', { amount: result.data.total, date: result.data.date, notes: result.data.merchant })
  } catch {
    error.value = 'Could not parse receipt. Try again.'
  } finally {
    loading.value = false
    if (fileInput.value) fileInput.value.value = ''
  }
}
</script>
