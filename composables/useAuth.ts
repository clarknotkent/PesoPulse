import {
  signInWithEmailAndPassword,
  createUserWithEmailAndPassword,
  signOut as firebaseSignOut,
  onAuthStateChanged,
  GoogleAuthProvider,
  signInWithPopup,
  signInWithRedirect,
  type Auth,
  type User,
} from 'firebase/auth'

export function useAuth() {
  const nuxtApp = useNuxtApp()

  const user = useState<User | null>('auth:user', () => null)
  const initialized = useState<boolean>('auth:initialized', () => false)
  const listenerRegistered = useState<boolean>('auth:listener', () => false)

  function getFirebaseAuth(): Auth {
    return nuxtApp.$firebaseAuth as Auth
  }

  if (process.client && !listenerRegistered.value) {
    listenerRegistered.value = true
    onAuthStateChanged(getFirebaseAuth(), (firebaseUser) => {
      user.value = firebaseUser
      initialized.value = true
    })
  }

  async function idToken(): Promise<string | null> {
    if (!user.value) return null
    return user.value.getIdToken()
  }

  async function registerOnApi(firebaseUser: User): Promise<void> {
    const token = await firebaseUser.getIdToken()
    try {
      await $fetch('/api/auth/register', {
        method: 'POST',
        headers: { Authorization: `Bearer ${token}` },
      })
    } catch (e: unknown) {
      const status = (e as { status?: number; statusCode?: number })?.status
        ?? (e as { statusCode?: number })?.statusCode
      if (status === 403) {
        await firebaseSignOut(getFirebaseAuth())
        user.value = null
        const err = new Error('PesoPulse is full (5 users max). Ask the owner for a viewer link.') as Error & { code?: string }
        err.code = 'app/user-cap-reached'
        throw err
      }
      throw e
    }
  }

  async function signIn(email: string, password: string): Promise<void> {
    const cred = await signInWithEmailAndPassword(getFirebaseAuth(), email, password)
    user.value = cred.user
  }

  async function signUp(email: string, password: string): Promise<void> {
    const cred = await createUserWithEmailAndPassword(getFirebaseAuth(), email, password)
    user.value = cred.user
    await registerOnApi(cred.user)
  }

  function shouldUseRedirect(): boolean {
    if (typeof window === 'undefined') return true
    const standalone = window.matchMedia?.('(display-mode: standalone)').matches
    const iosStandalone = (window.navigator as unknown as { standalone?: boolean }).standalone === true
    const mobile = /Mobile|Android|iPhone|iPad|iPod/i.test(navigator.userAgent)
    return Boolean(standalone || iosStandalone || mobile)
  }

  async function signInWithGoogle(): Promise<void> {
    const provider = new GoogleAuthProvider()
    provider.setCustomParameters({ prompt: 'select_account' })
    const auth = getFirebaseAuth()

    if (shouldUseRedirect()) {
      await signInWithRedirect(auth, provider)
      return
    }

    try {
      const cred = await signInWithPopup(auth, provider)
      user.value = cred.user
      await registerOnApi(cred.user)
    } catch (e: unknown) {
      const code = (e as { code?: string })?.code
      if (code === 'auth/popup-blocked' || code === 'auth/popup-closed-by-user' || code === 'auth/cancelled-popup-request') {
        // popup path failed — fall back to redirect
        await signInWithRedirect(auth, provider)
        return
      }
      throw e
    }
  }

  async function signOut(): Promise<void> {
    await firebaseSignOut(getFirebaseAuth())
    user.value = null
    await navigateTo('/')
  }

  return {
    user: readonly(user),
    initialized: readonly(initialized),
    idToken,
    signIn,
    signUp,
    signInWithGoogle,
    signOut,
    registerOnApi,
  }
}
