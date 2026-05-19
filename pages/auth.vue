<template>
  <div class="auth-shell">
    <div class="auth-glow" aria-hidden="true"></div>

    <NuxtLink to="/" class="press back-link" aria-label="Back">
      <Icon name="chevron-left" :size="13" />
      Back
    </NuxtLink>

    <div class="auth-card stagger-root">
      <div class="hero stagger-1">
        <Logo />
      </div>

      <Transition name="heading" mode="out-in">
        <div :key="mode" class="hero-text stagger-2">
          <h1 class="heading">
            {{ mode === 'signin' ? 'Welcome back' : 'Get started' }}
          </h1>
          <p class="subhead">
            {{ mode === 'signin'
              ? 'Log in to track every peso.'
              : 'Create your tracker. Five seats only.' }}
          </p>
        </div>
      </Transition>

      <Transition name="banner">
        <p v-if="banner" class="banner">{{ banner }}</p>
      </Transition>

      <div class="fields stagger-3">
        <label class="field">
          <span class="field-icon"><Icon name="mail" :size="15" /></span>
          <input
            v-model="email"
            type="email"
            placeholder="Email"
            autocomplete="email"
            class="field-input"
          />
        </label>

        <label class="field">
          <span class="field-icon"><Icon name="lock" :size="15" /></span>
          <input
            v-model="password"
            :type="showPassword ? 'text' : 'password'"
            placeholder="Password"
            :autocomplete="mode === 'signup' ? 'new-password' : 'current-password'"
            class="field-input has-action"
          />
          <button
            type="button"
            class="press field-action"
            @click="showPassword = !showPassword"
            :aria-label="showPassword ? 'Hide password' : 'Show password'"
            tabindex="-1"
          >
            <Icon :name="showPassword ? 'eye-off' : 'eye'" :size="15" />
          </button>
        </label>
      </div>

      <div class="slot stagger-3">
        <Transition name="slot" mode="out-in">
          <button
            v-if="mode === 'signin'"
            key="forgot"
            type="button"
            class="press forgot-btn"
            :disabled="resetSending"
            @click="onForgotPassword"
          >
            {{ resetSending ? 'Sending…' : 'Forgot password?' }}
          </button>

          <div v-else-if="password" key="strength" class="strength">
            <div class="strength-pips">
              <span
                v-for="(r, i) in rules"
                :key="r.id"
                :class="['pip', r.ok ? 'is-on' : '']"
                :style="{ transitionDelay: r.ok ? `${i * 40}ms` : '0ms' }"
              ></span>
            </div>
            <p class="strength-meta">
              <template v-if="passwordValid">Looks strong.</template>
              <template v-else>{{ firstUnmetLabel }}</template>
            </p>
          </div>

          <div v-else key="placeholder" class="slot-placeholder"></div>
        </Transition>
      </div>

      <p v-if="error" class="error stagger-4">{{ error }}</p>

      <button
        @click="submit"
        :disabled="loading || googleLoading || (mode === 'signup' && !passwordValid)"
        class="press submit-btn stagger-4"
        type="button"
      >
        <Icon v-if="loading" name="loader" :size="15" class="spin" />
        <span :class="['submit-label', loading ? 'is-loading' : '']">
          {{ mode === 'signin' ? 'Log in' : 'Create account' }}
        </span>
      </button>

      <div class="divider stagger-5">
        <span></span>
        <span class="divider-text">or</span>
        <span></span>
      </div>

      <button
        @click="onGoogle"
        :disabled="googleLoading || loading"
        class="press google-btn stagger-5"
        type="button"
      >
        <Icon v-if="googleLoading" name="loader" :size="15" class="spin" />
        <svg v-else width="16" height="16" viewBox="0 0 18 18" aria-hidden="true">
          <path fill="#4285F4" d="M17.64 9.2c0-.637-.057-1.251-.164-1.84H9v3.481h4.844a4.14 4.14 0 0 1-1.796 2.716v2.259h2.908c1.702-1.567 2.684-3.875 2.684-6.615z"/>
          <path fill="#34A853" d="M9 18c2.43 0 4.467-.806 5.956-2.184l-2.908-2.259c-.806.54-1.837.86-3.048.86-2.344 0-4.328-1.584-5.036-3.711H.957v2.332A8.997 8.997 0 0 0 9 18z"/>
          <path fill="#FBBC05" d="M3.964 10.71A5.41 5.41 0 0 1 3.682 9c0-.593.102-1.17.282-1.71V4.958H.957A8.996 8.996 0 0 0 0 9c0 1.452.348 2.827.957 4.042l3.007-2.332z"/>
          <path fill="#EA4335" d="M9 3.58c1.321 0 2.508.454 3.44 1.345l2.582-2.58C13.463.891 11.426 0 9 0A8.997 8.997 0 0 0 .957 4.958L3.964 7.29C4.672 5.163 6.656 3.58 9 3.58z"/>
        </svg>
        <span>{{ googleLoading ? 'Opening Google…' : 'Continue with Google' }}</span>
      </button>

      <p class="mode-toggle stagger-6">
        {{ mode === 'signin' ? "Don't have an account?" : "Have an account?" }}
        <button
          type="button"
          class="press mode-toggle-btn"
          @click="mode = mode === 'signin' ? 'signup' : 'signin'"
        >{{ mode === 'signin' ? 'Sign up' : 'Log in' }}</button>
      </p>
    </div>

    <footer class="footer stagger-6">
      <p>Private · 5-user cap · ₱ only</p>
      <p>Secured by Firebase Auth</p>
    </footer>
  </div>
</template>

<script setup lang="ts">
definePageMeta({ layout: false, pageTransition: false, layoutTransition: false })

const { signIn, signUp, signInWithGoogle, sendPasswordReset, user } = useAuth()
const toast = useToast()
const route = useRoute()

const redirectTarget = computed<string>(() => {
  const r = route.query.redirect
  if (typeof r === 'string' && r.startsWith('/') && !r.startsWith('//')) return r
  return '/dashboard'
})

const banner = computed<string>(() => {
  const reason = route.query.reason
  if (reason === 'idle') return 'Signed out after inactivity. Log in to continue.'
  if (reason === 'session_expired') return 'Session expired. Log in to continue.'
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

const mode = ref<'signin' | 'signup'>('signin')
const email = ref('')
const password = ref('')
const showPassword = ref(false)
const error = ref(
  process.client && typeof sessionStorage !== 'undefined'
    ? sessionStorage.getItem('pesopulse:auth-error') ?? ''
    : '',
)
const loading = ref(false)
const googleLoading = ref(false)
const resetSending = ref(false)

const rules = computed(() => {
  const p = password.value
  return [
    { id: 'len', label: 'Add a few more characters (min 10).', ok: p.length >= 10 },
    { id: 'case', label: 'Mix upper and lower case.', ok: /[a-z]/.test(p) && /[A-Z]/.test(p) },
    { id: 'num', label: 'Include a number.', ok: /[0-9]/.test(p) },
    { id: 'sym', label: 'Include a symbol like ! @ # $.', ok: /[^A-Za-z0-9]/.test(p) },
  ]
})

const passwordValid = computed<boolean>(() => rules.value.every((r) => r.ok))
const firstUnmetLabel = computed<string>(() => rules.value.find((r) => !r.ok)?.label ?? '')

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
      // dismissed silently
    } else {
      error.value = (e as { message?: string })?.message ?? 'Google sign-in failed'
    }
  } finally {
    googleLoading.value = false
  }
}

async function onForgotPassword() {
  error.value = ''
  if (!email.value.trim()) {
    error.value = 'Enter your email first.'
    return
  }
  resetSending.value = true
  try {
    await sendPasswordReset(email.value.trim())
    toast.success('Sent', `Reset link sent to ${email.value.trim()}.`)
  } catch (e: unknown) {
    const code = (e as { code?: string })?.code
    if (code === 'auth/user-not-found') {
      error.value = 'No account with that email.'
    } else if (code === 'auth/invalid-email') {
      error.value = 'That email looks invalid.'
    } else {
      error.value = (e as { message?: string })?.message ?? 'Could not send reset link.'
    }
  } finally {
    resetSending.value = false
  }
}
</script>

<style scoped>
.auth-shell {
  min-height: 100dvh;
  background: var(--bg);
  position: relative;
  overflow: hidden;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 32px 20px 28px;
}

.auth-glow {
  position: absolute;
  top: -120px;
  left: 50%;
  transform: translateX(-50%);
  width: 520px;
  height: 320px;
  background: rgba(16, 185, 129, 0.10);
  filter: blur(90px);
  pointer-events: none;
  border-radius: 50%;
}

.back-link {
  position: absolute;
  top: 28px;
  left: 24px;
  display: inline-flex;
  align-items: center;
  gap: 2px;
  color: var(--text-subtle);
  font-size: 12px;
  font-weight: 500;
  letter-spacing: -0.005em;
}
.back-link:hover {
  color: var(--text);
}

.auth-card {
  position: relative;
  width: 100%;
  max-width: 360px;
  padding: 8px 0 0;
}

.hero {
  display: flex;
  justify-content: center;
  margin-bottom: 22px;
}

.hero-text {
  text-align: center;
  margin-bottom: 26px;
}
.heading {
  font-size: 22px;
  font-weight: 600;
  line-height: 1.18;
  letter-spacing: -0.022em;
  color: var(--text);
  margin: 0 0 6px;
}
.subhead {
  font-size: 13px;
  line-height: 1.5;
  color: var(--text-muted);
  margin: 0;
}

.banner {
  font-size: 12px;
  color: var(--c-warn);
  background: color-mix(in oklab, var(--c-warn) 12%, transparent);
  border: 1px solid color-mix(in oklab, var(--c-warn) 28%, transparent);
  padding: 10px 12px;
  border-radius: 10px;
  margin: 0 0 18px;
  line-height: 1.4;
  text-align: center;
}

.fields {
  display: flex;
  flex-direction: column;
  gap: 10px;
}
.field {
  position: relative;
  display: flex;
  align-items: center;
  background: var(--bg-input);
  border-radius: 10px;
  height: 46px;
  transition: box-shadow 160ms var(--ease-out), background-color 160ms var(--ease-out);
}
.field-icon {
  position: absolute;
  left: 14px;
  color: var(--text-subtle);
  pointer-events: none;
  display: inline-flex;
  transition: color 160ms var(--ease-out);
}
.field-input {
  flex: 1;
  width: 100%;
  background: transparent;
  border: 0;
  outline: 0;
  padding: 0 16px 0 40px;
  font-size: 14px;
  color: var(--text);
  font-family: inherit;
}
.field-input.has-action {
  padding-right: 44px;
}
.field-input::placeholder {
  color: var(--text-subtle);
}
.field:focus-within {
  box-shadow: inset 0 0 0 1px var(--accent), 0 0 0 3px var(--accent-soft);
}
.field:focus-within .field-icon {
  color: var(--accent);
}
.field-action {
  position: absolute;
  right: 6px;
  top: 50%;
  transform: translateY(-50%);
  width: 36px;
  height: 36px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  background: transparent;
  border: 0;
  border-radius: 8px;
  color: var(--text-subtle);
  cursor: pointer;
  transition: color 160ms var(--ease-out), background-color 160ms var(--ease-out);
}
.field-action:hover {
  color: var(--text);
}

.slot {
  margin-top: 10px;
  min-height: 28px;
  display: flex;
  flex-direction: column;
  justify-content: flex-start;
}
.slot-placeholder {
  height: 28px;
}
.forgot-btn {
  align-self: flex-start;
  background: transparent;
  border: 0;
  padding: 4px 2px;
  font-size: 12px;
  font-weight: 500;
  color: var(--accent);
  cursor: pointer;
  font-family: inherit;
}
.forgot-btn:hover {
  text-decoration: underline;
  text-underline-offset: 3px;
}
.forgot-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.strength {
  padding-top: 2px;
}
.strength-pips {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 6px;
}
.pip {
  height: 3px;
  background: var(--bg-input);
  border-radius: 999px;
  transition: background-color 240ms var(--ease-out);
}
.pip.is-on {
  background: var(--accent);
}
.strength-meta {
  margin: 8px 0 0;
  font-size: 11px;
  color: var(--text-muted);
  line-height: 1.4;
}

.error {
  margin: 12px 0 0;
  color: var(--c-expense);
  font-size: 12px;
  line-height: 1.4;
  text-align: center;
}

.submit-btn {
  margin-top: 16px;
  width: 100%;
  height: 48px;
  background: var(--accent);
  color: white;
  border: 0;
  border-radius: 10px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 10px;
  box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.14), 0 10px 24px -14px color-mix(in oklab, var(--accent) 80%, transparent);
  transition: box-shadow 180ms var(--ease-out), opacity 160ms var(--ease-out);
}
.submit-btn:disabled {
  opacity: 0.4;
  cursor: not-allowed;
  box-shadow: none;
}
.submit-label {
  transition: filter 180ms var(--ease-out), opacity 180ms var(--ease-out);
}
.submit-label.is-loading {
  filter: blur(2px);
  opacity: 0.7;
}

.divider {
  display: grid;
  grid-template-columns: 1fr auto 1fr;
  align-items: center;
  gap: 12px;
  margin: 22px 0 16px;
}
.divider > span:not(.divider-text) {
  height: 1px;
  background: var(--border);
}
.divider-text {
  color: var(--text-subtle);
  font-size: 11px;
  letter-spacing: 0.01em;
}

.google-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 10px;
  width: 100%;
  height: 44px;
  background: var(--bg-surface);
  color: var(--text);
  border: 1px solid var(--border);
  border-radius: 10px;
  font-size: 13.5px;
  font-weight: 500;
  cursor: pointer;
  transition: background-color 180ms var(--ease-out), border-color 180ms var(--ease-out);
}
.google-btn:disabled {
  opacity: 0.55;
  cursor: not-allowed;
}
@media (hover: hover) and (pointer: fine) {
  .google-btn:hover:not(:disabled) {
    background: var(--bg-input);
  }
}

.mode-toggle {
  margin: 22px 0 0;
  text-align: center;
  font-size: 13px;
  color: var(--text-muted);
  line-height: 1.4;
}
.mode-toggle-btn {
  background: transparent;
  border: 0;
  padding: 0 0 0 4px;
  font: inherit;
  font-weight: 500;
  color: var(--accent);
  cursor: pointer;
}
.mode-toggle-btn:hover {
  text-decoration: underline;
  text-underline-offset: 3px;
}

.footer {
  margin-top: 24px;
  text-align: center;
  color: var(--text-subtle);
  font-size: 10.5px;
  line-height: 1.55;
  letter-spacing: 0.01em;
}
.footer p {
  margin: 0;
}
.footer p + p {
  margin-top: 2px;
}

.spin {
  animation: auth-spin 700ms linear infinite;
}
@keyframes auth-spin {
  to { transform: rotate(360deg); }
}

/* ---------- Stagger entrance ---------- */
[class*="stagger-"] {
  opacity: 0;
  transform: translateY(8px);
  animation: auth-rise 280ms var(--ease-out) forwards;
}
.stagger-1 { animation-delay: 0ms; }
.stagger-2 { animation-delay: 40ms; }
.stagger-3 { animation-delay: 80ms; }
.stagger-4 { animation-delay: 120ms; }
.stagger-5 { animation-delay: 160ms; }
.stagger-6 { animation-delay: 200ms; }

@keyframes auth-rise {
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

/* ---------- Transitions ---------- */
.heading-enter-active,
.heading-leave-active {
  transition: opacity 180ms var(--ease-out);
}
.heading-enter-from,
.heading-leave-to {
  opacity: 0;
}

.banner-enter-active,
.banner-leave-active {
  transition: opacity 220ms var(--ease-out), transform 220ms var(--ease-out);
  overflow: hidden;
}
.banner-enter-from,
.banner-leave-to {
  opacity: 0;
  transform: translateY(-6px);
}

.slot-enter-active,
.slot-leave-active {
  transition: opacity 200ms var(--ease-out), transform 200ms var(--ease-out);
}
.slot-enter-from,
.slot-leave-to {
  opacity: 0;
  transform: translateY(-4px);
}

/* ---------- Reduced motion ---------- */
@media (prefers-reduced-motion: reduce) {
  [class*="stagger-"] {
    animation-duration: 120ms;
    animation-delay: 0ms !important;
    transform: none !important;
  }
  .heading-enter-active,
  .heading-leave-active,
  .banner-enter-active,
  .banner-leave-active,
  .slot-enter-active,
  .slot-leave-active,
  .pip,
  .submit-label,
  .field {
    transition-duration: 120ms !important;
  }
  .heading-enter-from,
  .heading-leave-to,
  .banner-enter-from,
  .banner-leave-to,
  .slot-enter-from,
  .slot-leave-to {
    transform: none !important;
  }
  .spin {
    animation-duration: 1400ms;
  }
}
</style>
