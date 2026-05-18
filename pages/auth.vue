<template>
  <div class="min-h-screen bg-[#0a0a0a] flex items-center justify-center px-4">
    <div class="w-full max-w-sm">
      <h1 class="text-white text-2xl font-bold mb-1">PesoPulse</h1>
      <p class="text-zinc-400 text-sm mb-8">Personal Finance Tracker</p>

      <div class="bg-zinc-900 rounded-2xl p-6 space-y-4">
        <div class="flex rounded-lg bg-zinc-800 p-1">
          <button
            v-for="tab in tabs"
            :key="tab.value"
            @click="mode = tab.value"
            :class="[
              'flex-1 py-1.5 text-sm rounded-md transition-all',
              mode === tab.value ? 'bg-white text-black font-medium' : 'text-zinc-400',
            ]"
          >{{ tab.label }}</button>
        </div>

        <input
          v-model="email"
          type="email"
          placeholder="Email"
          autocomplete="email"
          class="w-full bg-zinc-800 text-white placeholder-zinc-500 rounded-lg px-4 py-3 text-sm outline-none focus:ring-1 focus:ring-zinc-600"
        />
        <input
          v-model="password"
          type="password"
          placeholder="Password"
          autocomplete="current-password"
          class="w-full bg-zinc-800 text-white placeholder-zinc-500 rounded-lg px-4 py-3 text-sm outline-none focus:ring-1 focus:ring-zinc-600"
        />

        <p v-if="error" class="text-red-400 text-xs">{{ error }}</p>

        <button
          @click="submit"
          :disabled="loading"
          class="w-full bg-white text-black font-medium py-3 rounded-lg text-sm hover:bg-zinc-200 transition disabled:opacity-50"
        >
          {{ loading ? 'Loading…' : mode === 'signin' ? 'Sign In' : 'Create Account' }}
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
definePageMeta({ layout: false })

const { signIn, signUp, user } = useAuth()

if (process.client && user.value) {
  await navigateTo('/dashboard')
}

const tabs = [
  { label: 'Sign In', value: 'signin' as const },
  { label: 'Sign Up', value: 'signup' as const },
]

const mode = ref<'signin' | 'signup'>('signin')
const email = ref('')
const password = ref('')
const error = ref('')
const loading = ref(false)

async function submit() {
  error.value = ''
  loading.value = true
  try {
    if (mode.value === 'signin') {
      await signIn(email.value, password.value)
    } else {
      await signUp(email.value, password.value)
    }
    await navigateTo('/dashboard')
  } catch (e: unknown) {
    error.value = (e as { message?: string })?.message ?? 'Authentication failed'
  } finally {
    loading.value = false
  }
}
</script>
