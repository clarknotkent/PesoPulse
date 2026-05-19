import { initializeApp, getApps } from 'firebase/app'
import { getAuth } from 'firebase/auth'

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

  return {
    provide: {
      firebaseAuth: auth,
      firebaseApp: app,
    },
  }
})
