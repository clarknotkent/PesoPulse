import {
  signInWithEmailAndPassword,
  createUserWithEmailAndPassword,
  signOut as firebaseSignOut,
  onAuthStateChanged,
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

  async function signIn(email: string, password: string): Promise<void> {
    const cred = await signInWithEmailAndPassword(getFirebaseAuth(), email, password)
    user.value = cred.user
  }

  async function signUp(email: string, password: string): Promise<void> {
    const cred = await createUserWithEmailAndPassword(getFirebaseAuth(), email, password)
    user.value = cred.user
    const token = await cred.user.getIdToken()
    await $fetch('/api/auth/register', {
      method: 'POST',
      headers: { Authorization: `Bearer ${token}` },
    })
  }

  async function signOut(): Promise<void> {
    await firebaseSignOut(getFirebaseAuth())
    user.value = null
    await navigateTo('/login')
  }

  return {
    user: readonly(user),
    initialized: readonly(initialized),
    idToken,
    signIn,
    signUp,
    signOut,
  }
}
