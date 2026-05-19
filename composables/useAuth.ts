import {
  signInWithEmailAndPassword,
  createUserWithEmailAndPassword,
  signOut as firebaseSignOut,
  onAuthStateChanged,
  sendEmailVerification,
  sendPasswordResetEmail,
  reauthenticateWithCredential,
  getRedirectResult,
  EmailAuthProvider,
  GoogleAuthProvider,
  signInWithPopup,
  type Auth,
  type User,
} from 'firebase/auth'

const IDLE_TIMEOUT_MS = 15 * 60 * 1000

export function useAuth() {
  const nuxtApp = useNuxtApp()

  const user = useState<User | null>('auth:user', () => null)
  const initialized = useState<boolean>('auth:initialized', () => false)
  const emailVerified = useState<boolean>('auth:emailVerified', () => false)
  const listenerRegistered = useState<boolean>('auth:listener', () => false)
  const idleHandlersRegistered = useState<boolean>('auth:idle', () => false)

  function getFirebaseAuth(): Auth {
    return nuxtApp.$firebaseAuth as Auth
  }

  if (import.meta.client && !listenerRegistered.value) {
    listenerRegistered.value = true
    const fbAuth = getFirebaseAuth()

    getRedirectResult(fbAuth)
      .then(async (result) => {
        if (result?.user) {
          user.value = markRaw(result.user)
          emailVerified.value = result.user.emailVerified
          try {
            await registerOnApi(result.user)
          }
          catch {
            // already registered
          }
          if (typeof window !== 'undefined') {
            const path = window.location.pathname
            if (path === '/auth' || path === '/') {
              const params = new URLSearchParams(window.location.search)
              const redirectParam = params.get('redirect')
              const target = redirectParam && redirectParam.startsWith('/') && !redirectParam.startsWith('//')
                ? redirectParam
                : '/dashboard'
              window.location.replace(target)
            }
          }
        }
      })
      .catch((err: unknown) => {
        const code = (err as { code?: string })?.code
        if (code && code !== 'auth/no-auth-event') {
          if (typeof sessionStorage !== 'undefined') {
            sessionStorage.setItem('pesopulse:auth-error', (err as Error)?.message ?? 'Google sign-in failed')
          }
        }
      })

    onAuthStateChanged(fbAuth, (firebaseUser) => {
      user.value = firebaseUser ? markRaw(firebaseUser) : null
      emailVerified.value = firebaseUser?.emailVerified ?? false
      initialized.value = true
    })
  }

  function resetIdleTimer(): void {
    if (typeof window === 'undefined') return
    const w = window as Window & { __pesoIdleTimer?: ReturnType<typeof setTimeout> }
    if (w.__pesoIdleTimer) clearTimeout(w.__pesoIdleTimer)
    w.__pesoIdleTimer = setTimeout(async () => {
      if (user.value) {
        await firebaseSignOut(getFirebaseAuth())
        user.value = null
        await navigateTo('/auth?reason=idle')
      }
    }, IDLE_TIMEOUT_MS)
  }

  function initIdleWatcher(): void {
    if (!import.meta.client || idleHandlersRegistered.value) return
    idleHandlersRegistered.value = true
    const events: (keyof DocumentEventMap)[] = ['mousemove', 'keydown', 'touchstart', 'click', 'scroll']
    for (const ev of events) {
      document.addEventListener(ev, resetIdleTimer, { passive: true })
    }
    resetIdleTimer()
  }

  async function idToken(forceRefresh: boolean = false): Promise<string | null> {
    if (!user.value) return null
    return user.value.getIdToken(forceRefresh)
  }

  async function refreshVerified(): Promise<boolean> {
    if (!user.value) return false
    await user.value.reload()
    await user.value.getIdToken(true)
    emailVerified.value = user.value.emailVerified
    return emailVerified.value
  }

  async function sendVerification(): Promise<void> {
    if (!user.value) throw new Error('not_authenticated')
    await sendEmailVerification(user.value)
  }

  async function sendPasswordReset(email: string): Promise<void> {
    if (!email) throw new Error('email_required')
    await sendPasswordResetEmail(getFirebaseAuth(), email)
  }

  async function reauthenticate(password: string): Promise<void> {
    if (!user.value || !user.value.email) throw new Error('not_authenticated')
    const cred = EmailAuthProvider.credential(user.value.email, password)
    await reauthenticateWithCredential(user.value, cred)
  }

  async function registerOnApi(firebaseUser: User): Promise<void> {
    const token = await firebaseUser.getIdToken()
    try {
      await $fetch('/api/auth/register', {
        method: 'POST',
        headers: { Authorization: `Bearer ${token}` },
      })
    }
    catch (e: unknown) {
      const status = (e as { status?: number, statusCode?: number })?.status
        ?? (e as { statusCode?: number })?.statusCode
      const data = (e as { data?: { detail?: string } })?.data
      if (status === 403 && data?.detail === 'user_cap_reached') {
        await firebaseSignOut(getFirebaseAuth())
        user.value = null
        const err = new Error('PesoPulse is full (5 users max). Ask the owner for a viewer link.') as Error & { code?: string }
        err.code = 'app/user-cap-reached'
        throw err
      }
      if (status === 403 && data?.detail === 'email_not_verified') {
        // Expected pre-verification — register endpoint requires verified email.
        // Frontend gates on emailVerified separately.
        return
      }
      throw e
    }
  }

  async function signIn(email: string, password: string): Promise<void> {
    const cred = await signInWithEmailAndPassword(getFirebaseAuth(), email, password)
    user.value = markRaw(cred.user)
    emailVerified.value = cred.user.emailVerified
  }

  async function signUp(email: string, password: string): Promise<void> {
    const cred = await createUserWithEmailAndPassword(getFirebaseAuth(), email, password)
    user.value = markRaw(cred.user)
    emailVerified.value = cred.user.emailVerified
    try {
      await sendEmailVerification(cred.user)
    }
    catch {
      // verification email send is best-effort
    }
    await registerOnApi(cred.user)
  }

  async function signInWithGoogle(): Promise<void> {
    const provider = new GoogleAuthProvider()
    provider.setCustomParameters({ prompt: 'select_account' })
    const auth = getFirebaseAuth()

    const cred = await signInWithPopup(auth, provider)
    user.value = markRaw(cred.user)
    emailVerified.value = cred.user.emailVerified
    await registerOnApi(cred.user)
  }

  async function signOut(): Promise<void> {
    await firebaseSignOut(getFirebaseAuth())
    user.value = null
    emailVerified.value = false
    await navigateTo('/')
  }

  async function signOutEverywhere(): Promise<void> {
    const token = await idToken()
    if (!token) throw new Error('not_authenticated')
    await $fetch('/api/auth/revoke-tokens', {
      method: 'POST',
      headers: { Authorization: `Bearer ${token}` },
    })
    await signOut()
  }

  return {
    user: readonly(user),
    initialized: readonly(initialized),
    emailVerified: readonly(emailVerified),
    idToken,
    refreshVerified,
    sendVerification,
    sendPasswordReset,
    reauthenticate,
    signIn,
    signUp,
    signInWithGoogle,
    signOut,
    signOutEverywhere,
    registerOnApi,
    initIdleWatcher,
  }
}
