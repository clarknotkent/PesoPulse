<template>
  <div class="min-h-[100dvh] bg-[var(--bg)] flex items-center justify-center px-4 relative overflow-hidden">
    <div class="absolute -top-32 -left-20 w-96 h-96 rounded-full bg-emerald-500/10 blur-3xl pointer-events-none"></div>
    <div class="absolute -bottom-32 -right-20 w-96 h-96 rounded-full bg-emerald-500/5 blur-3xl pointer-events-none"></div>

    <div class="w-full max-w-sm relative">
      <NuxtLink to="/" class="press inline-flex items-center gap-1 text-[var(--text-subtle)] hover:text-[var(--text)] text-xs mb-8">
        <Icon name="chevron-left" :size="14" />
        Back
      </NuxtLink>

      <div class="mb-8 space-y-3">
        <Logo />
        <p class="text-[var(--text-muted)] text-sm">Track every peso. Plan every week.</p>
      </div>

      <div class="bg-[var(--bg-surface)] border border-[var(--border)] rounded-2xl p-5 space-y-4">
        <div class="flex rounded-lg bg-[var(--bg-input)] p-1">
          <button
            v-for="tab in tabs"
            :key="tab.value"
            @click="mode = tab.value"
            :class="[
              'press flex-1 py-2 text-sm rounded-md auth-tab font-medium',
              mode === tab.value ? 'bg-[var(--bg-surface)] text-[var(--text)] shadow-sm' : 'text-[var(--text-muted)]',
            ]"
          >{{ tab.label }}</button>
        </div>

        <!-- Google primary -->
        <button
          @click="onGoogle"
          :disabled="googleLoading || loading"
          class="press w-full flex items-center justify-center gap-2.5 bg-[var(--bg-input)] text-[var(--text)] border border-[var(--border)] py-3 rounded-lg text-sm font-medium disabled:opacity-50 disabled:active:scale-100"
        >
          <Icon v-if="googleLoading" name="loader" :size="16" class="animate-spin" />
          <svg v-else width="18" height="18" viewBox="0 0 18 18" aria-hidden="true">
            <path fill="#4285F4" d="M17.64 9.2c0-.637-.057-1.251-.164-1.84H9v3.481h4.844a4.14 4.14 0 0 1-1.796 2.716v2.259h2.908c1.702-1.567 2.684-3.875 2.684-6.615z"/>
            <path fill="#34A853" d="M9 18c2.43 0 4.467-.806 5.956-2.184l-2.908-2.259c-.806.54-1.837.86-3.048.86-2.344 0-4.328-1.584-5.036-3.711H.957v2.332A8.997 8.997 0 0 0 9 18z"/>
            <path fill="#FBBC05" d="M3.964 10.71A5.41 5.41 0 0 1 3.682 9c0-.593.102-1.17.282-1.71V4.958H.957A8.996 8.996 0 0 0 0 9c0 1.452.348 2.827.957 4.042l3.007-2.332z"/>
            <path fill="#EA4335" d="M9 3.58c1.321 0 2.508.454 3.44 1.345l2.582-2.58C13.463.891 11.426 0 9 0A8.997 8.997 0 0 0 .957 4.958L3.964 7.29C4.672 5.163 6.656 3.58 9 3.58z"/>
          </svg>
          <span>{{ googleLoading ? 'Redirecting…' : 'Continue with Google' }}</span>
        </button>

        <!-- divider -->
        <div class="flex items-center gap-3 py-1">
          <span class="flex-1 h-px bg-[var(--border)]"></span>
          <span class="text-[var(--text-subtle)] text-[10px] uppercase tracking-[0.16em]">or email</span>
          <span class="flex-1 h-px bg-[var(--border)]"></span>
        </div>

        <input
          v-model="email"
          type="email"
          placeholder="Email"
          autocomplete="email"
          class="field w-full bg-[var(--bg-input)] text-[var(--text)] placeholder-[var(--text-subtle)] rounded-lg px-4 py-3 text-sm outline-none"
        />
        <input
          v-model="password"
          type="password"
          placeholder="Password"
          autocomplete="current-password"
          class="field w-full bg-[var(--bg-input)] text-[var(--text)] placeholder-[var(--text-subtle)] rounded-lg px-4 py-3 text-sm outline-none"
        />

        <p v-if="error" class="text-[var(--c-expense)] text-xs">{{ error }}</p>

        <button
          @click="submit"
          :disabled="loading || googleLoading"
          class="press w-full bg-emerald-500 text-white font-semibold py-3 rounded-lg text-sm disabled:opacity-50 disabled:active:scale-100 flex items-center justify-center gap-2"
        >
          <Icon v-if="loading" name="loader" :size="16" class="animate-spin" />
          {{ loading ? 'Loading…' : mode === 'signin' ? 'Sign in' : 'Create account' }}
        </button>
      </div>

      <p class="text-[var(--text-subtle)] text-[10px] text-center mt-6 leading-relaxed">
        Private personal tracker. Five-user cap. Philippine Peso only.
      </p>
    </div>
  </div>
</template>

<script setup lang="ts">
definePageMeta({ layout: false })

const { signIn, signUp, signInWithGoogle, user } = useAuth()
const route = useRoute()

const redirectTarget = computed<string>(() => {
  const r = route.query.redirect
  if (typeof r === 'string' && r.startsWith('/') && !r.startsWith('//')) return r
  return '/dashboard'
})

if (process.client && user.value) {
  await navigateTo(redirectTarget.value)
}

if (process.client && typeof sessionStorage !== 'undefined') {
  const stored = sessionStorage.getItem('pesopulse:auth-error')
  if (stored) {
    sessionStorage.removeItem('pesopulse:auth-error')
  }
}

const tabs = [
  { label: 'Sign in', value: 'signin' as const },
  { label: 'Sign up', value: 'signup' as const },
]

const mode = ref<'signin' | 'signup'>('signin')
const email = ref('')
const password = ref('')
const error = ref(
  process.client && typeof sessionStorage !== 'undefined'
    ? sessionStorage.getItem('pesopulse:auth-error') ?? ''
    : '',
)
const loading = ref(false)
const googleLoading = ref(false)

async function submit() {
  error.value = ''
  loading.value = true
  try {
    if (mode.value === 'signin') {
      await signIn(email.value, password.value)
    } else {
      await signUp(email.value, password.value)
    }
    await navigateTo(redirectTarget.value)
  } catch (e: unknown) {
    error.value = (e as { message?: string })?.message ?? 'Authentication failed'
  } finally {
    loading.value = false
  }
}

async function onGoogle() {
  error.value = ''
  googleLoading.value = true
  try {
    await signInWithGoogle()
    if (user.value) {
      await navigateTo(redirectTarget.value)
    }
  } catch (e: unknown) {
    const code = (e as { code?: string })?.code
    if (code === 'auth/popup-closed-by-user' || code === 'auth/cancelled-popup-request') {
      // user dismissed — silent
    } else {
      error.value = (e as { message?: string })?.message ?? 'Google sign-in failed'
    }
  } finally {
    googleLoading.value = false
  }
}
</script>

<style scoped>
.auth-tab {
  transition: background-color 220ms var(--ease-out), color 180ms var(--ease-out), transform 160ms var(--ease-out), box-shadow 220ms var(--ease-out);
}
.field {
  transition: box-shadow 160ms var(--ease-out), background-color 160ms var(--ease-out);
}
.field:focus {
  box-shadow: 0 0 0 1px var(--accent), 0 0 0 4px var(--accent-soft);
}
</style>
