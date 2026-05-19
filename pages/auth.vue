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

      <p v-if="banner" class="mb-4 bg-amber-500/10 border border-amber-500/30 text-amber-200 text-xs rounded-lg px-3 py-2">{{ banner }}</p>

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
          :autocomplete="mode === 'signup' ? 'new-password' : 'current-password'"
          class="field w-full bg-[var(--bg-input)] text-[var(--text)] placeholder-[var(--text-subtle)] rounded-lg px-4 py-3 text-sm outline-none"
        />

        <div v-if="mode === 'signup' && password" class="space-y-1.5">
          <div class="h-1 bg-[var(--bg-input)] rounded-full overflow-hidden">
            <div :class="['h-full transition-all duration-300', strengthClass]" :style="{ width: strengthPct + '%' }"></div>
          </div>
          <ul class="text-[10px] space-y-0.5">
            <li v-for="r in rules" :key="r.id" :class="r.ok ? 'text-emerald-400' : 'text-[var(--text-subtle)]'">
              {{ r.ok ? '✓' : '·' }} {{ r.label }}
            </li>
          </ul>
        </div>

        <p v-if="error" class="text-[var(--c-expense)] text-xs">{{ error }}</p>

        <button
          @click="submit"
          :disabled="loading || googleLoading || (mode === 'signup' && !passwordValid)"
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
definePageMeta({ layout: false, pageTransition: false, layoutTransition: false })

const { signIn, signUp, signInWithGoogle, user } = useAuth()
const route = useRoute()

const redirectTarget = computed<string>(() => {
  const r = route.query.redirect
  if (typeof r === 'string' && r.startsWith('/') && !r.startsWith('//')) return r
  return '/dashboard'
})

const banner = computed<string>(() => {
  const reason = route.query.reason
  if (reason === 'idle') return 'Signed out after inactivity. Please sign in again.'
  if (reason === 'session_expired') return 'Your session expired. Please sign in again.'
  return ''
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

const rules = computed(() => {
  const p = password.value
  return [
    { id: 'len', label: 'At least 10 characters', ok: p.length >= 10 },
    { id: 'num', label: 'Contains a number', ok: /[0-9]/.test(p) },
    { id: 'sym', label: 'Contains a symbol (!@#$…)', ok: /[^A-Za-z0-9]/.test(p) },
    { id: 'case', label: 'Mixes upper & lower case', ok: /[a-z]/.test(p) && /[A-Z]/.test(p) },
  ]
})

const passwordValid = computed<boolean>(() => rules.value.every((r) => r.ok))
const strengthPct = computed<number>(() => (rules.value.filter((r) => r.ok).length / rules.value.length) * 100)
const strengthClass = computed<string>(() => {
  const pct = strengthPct.value
  if (pct < 50) return 'bg-red-500'
  if (pct < 100) return 'bg-amber-500'
  return 'bg-emerald-500'
})

async function submit() {
  error.value = ''
  if (mode.value === 'signup' && !passwordValid.value) {
    error.value = 'Password does not meet complexity rules.'
    return
  }
  loading.value = true
  try {
    if (mode.value === 'signin') {
      await signIn(email.value, password.value)
    } else {
      await signUp(email.value, password.value)
    }
    await nextTick()
    await navigateTo(redirectTarget.value, { replace: true })
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
      await nextTick()
      await navigateTo(redirectTarget.value, { replace: true })
    }
  } catch (e: unknown) {
    const code = (e as { code?: string })?.code
    if (code === 'auth/popup-closed-by-user' || code === 'auth/cancelled-popup-request') {
      // dismissed
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
