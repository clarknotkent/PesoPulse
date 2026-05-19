<template>
  <div class="min-h-[100dvh] bg-[var(--bg)] flex items-center justify-center px-4 relative overflow-hidden">
    <div class="absolute -top-32 -left-20 w-96 h-96 rounded-full bg-emerald-500/10 blur-3xl pointer-events-none" />
    <div class="absolute -bottom-32 -right-20 w-96 h-96 rounded-full bg-emerald-500/5 blur-3xl pointer-events-none" />

    <div class="w-full max-w-sm relative space-y-6">
      <div class="space-y-3">
        <Logo />
        <p class="text-[var(--text-muted)] text-sm">
          Verify your email
        </p>
      </div>

      <div class="bg-[var(--bg-surface)] border border-[var(--border)] rounded-2xl p-5 space-y-4">
        <div class="flex items-start gap-3">
          <div class="w-10 h-10 rounded-full bg-emerald-500/15 flex items-center justify-center shrink-0">
            <Icon
              name="receipt"
              :size="18"
              class="text-emerald-400"
            />
          </div>
          <div class="space-y-1">
            <p class="text-[var(--text)] text-sm font-medium">
              Check your inbox
            </p>
            <p class="text-[var(--text-muted)] text-xs leading-relaxed">
              We sent a verification link to
              <span class="text-[var(--text)]">{{ email || 'your email' }}</span>.
              Click it, then come back here.
            </p>
          </div>
        </div>

        <p
          v-if="status"
          class="text-[10px] text-[var(--text-subtle)]"
        >
          {{ status }}
        </p>

        <div class="flex gap-2">
          <button
            :disabled="resending || cooldown > 0"
            class="press flex-1 py-2.5 rounded-lg text-sm font-medium bg-[var(--bg-input)] text-[var(--text)] disabled:opacity-50"
            @click="onResend"
          >
            <template v-if="cooldown > 0">
              Resend in {{ cooldown }}s
            </template>
            <template v-else>
              {{ resending ? 'Sending…' : 'Resend email' }}
            </template>
          </button>
          <button
            :disabled="checking"
            class="press-strong flex-1 py-2.5 rounded-lg text-sm font-medium bg-emerald-500 text-white disabled:opacity-50"
            @click="onCheck"
          >
            <Icon
              v-if="checking"
              name="loader"
              :size="14"
              class="animate-spin inline-block mr-1"
            />
            I've verified
          </button>
        </div>

        <button
          class="press w-full text-center text-[var(--text-subtle)] hover:text-[var(--text)] text-xs py-1"
          @click="onSignOut"
        >
          Sign out
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
definePageMeta({ layout: false, middleware: [] })

const { user, emailVerified, sendVerification, refreshVerified, signOut, registerOnApi } = useAuth()
const router = useRouter()

if (import.meta.client && !user.value) {
  await navigateTo('/auth')
}

if (import.meta.client && emailVerified.value) {
  await navigateTo('/dashboard')
}

const email = computed<string>(() => user.value?.email ?? '')
const status = ref<string>('')
const resending = ref(false)
const checking = ref(false)
const cooldown = ref(0)

let cooldownTimer: ReturnType<typeof setInterval> | null = null
let pollTimer: ReturnType<typeof setInterval> | null = null

function startCooldown(seconds: number): void {
  cooldown.value = seconds
  if (cooldownTimer) clearInterval(cooldownTimer)
  cooldownTimer = setInterval(() => {
    cooldown.value -= 1
    if (cooldown.value <= 0 && cooldownTimer) {
      clearInterval(cooldownTimer)
      cooldownTimer = null
    }
  }, 1000)
}

async function onResend(): Promise<void> {
  if (cooldown.value > 0) return
  resending.value = true
  status.value = ''
  try {
    await sendVerification()
    status.value = 'Verification email sent.'
    startCooldown(60)
  }
  catch (e: unknown) {
    const code = (e as { code?: string })?.code
    if (code === 'auth/too-many-requests') {
      status.value = 'Too many requests. Wait before resending.'
      startCooldown(60)
    }
    else {
      status.value = 'Could not send. Try again later.'
    }
  }
  finally {
    resending.value = false
  }
}

async function onCheck(): Promise<void> {
  checking.value = true
  status.value = ''
  try {
    const ok = await refreshVerified()
    if (ok) {
      if (user.value) {
        try {
          await registerOnApi(user.value as unknown as import('firebase/auth').User)
        }
        catch {
          // user may already be registered
        }
      }
      await router.push('/dashboard')
    }
    else {
      status.value = 'Still not verified. Check your inbox (and spam).'
    }
  }
  finally {
    checking.value = false
  }
}

async function onSignOut(): Promise<void> {
  await signOut()
}

onMounted(() => {
  pollTimer = setInterval(async () => {
    if (!user.value) return
    const ok = await refreshVerified()
    if (ok) {
      if (pollTimer) clearInterval(pollTimer)
      try {
        if (user.value) {
          await registerOnApi(user.value as unknown as import('firebase/auth').User)
        }
      }
      catch {
        // ignore
      }
      await router.push('/dashboard')
    }
  }, 8000)
})

onBeforeUnmount(() => {
  if (cooldownTimer) clearInterval(cooldownTimer)
  if (pollTimer) clearInterval(pollTimer)
})
</script>
