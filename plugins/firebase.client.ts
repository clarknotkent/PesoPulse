import { initializeApp, getApps } from 'firebase/app'
import { getAuth, getRedirectResult } from 'firebase/auth'

export default defineNuxtPlugin(() => {
  const { public: pub } = useRuntimeConfig()

  const app = getApps().length
    ? getApps()[0]
    : initializeApp({
        apiKey: pub.firebaseApiKey as string,
        authDomain: pub.firebaseAuthDomain as string,
        projectId: pub.firebaseProjectId as string,
        appId: pub.firebaseAppId as string,
        messagingSenderId: pub.firebaseMessagingSenderId as string,
      })

  const auth = getAuth(app)

  if (process.client) {
    getRedirectResult(auth)
      .then(async (cred) => {
        if (!cred?.user) return
        const token = await cred.user.getIdToken()
        try {
          await $fetch('/api/auth/register', {
            method: 'POST',
            headers: { Authorization: `Bearer ${token}` },
          })
        } catch (e: unknown) {
          const status = (e as { status?: number; statusCode?: number })?.status
            ?? (e as { statusCode?: number })?.statusCode
          if (status === 403) {
            await auth.signOut()
            if (typeof sessionStorage !== 'undefined') {
              sessionStorage.setItem('pesopulse:auth-error', 'PesoPulse is full (5 users max). Ask the owner for a viewer link.')
            }
            await navigateTo('/auth', { replace: true })
          }
        }
      })
      .catch(() => { /* no redirect in flight — ignore */ })
  }

  return {
    provide: {
      firebaseAuth: auth,
      firebaseApp: app,
    },
  }
})
