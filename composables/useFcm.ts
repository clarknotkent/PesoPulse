import { getMessaging, getToken, onMessage, isSupported } from 'firebase/messaging'
import type { FirebaseApp } from 'firebase/app'

export type NotifStatus = 'unsupported' | 'denied' | 'default' | 'granted'

export function useFcm() {
  const nuxtApp = useNuxtApp()
  const { user } = useAuth()
  const api = useApi()
  const toast = useToast()
  const status = useState<NotifStatus>('fcm:status', () => 'default')

  function detectStatus() {
    if (typeof window === 'undefined' || !('Notification' in window)) {
      status.value = 'unsupported'
      return
    }
    status.value = Notification.permission as NotifStatus
  }

  async function register(): Promise<boolean> {
    if (typeof window === 'undefined') return false
    if (!(await isSupported())) {
      status.value = 'unsupported'
      return false
    }
    const { public: pub } = useRuntimeConfig()
    const vapidKey = (pub.firebaseVapidKey as string ?? '').trim()
    if (!vapidKey) {
      console.warn('FCM disabled: NUXT_PUBLIC_FIREBASE_VAPID_KEY not set')
      return false
    }
    if (!/^[A-Za-z0-9_-]{80,100}$/.test(vapidKey)) {
      console.warn(
        'FCM disabled: NUXT_PUBLIC_FIREBASE_VAPID_KEY format invalid. ' +
        'Expected ~88-char base64url Web Push certificate key from Firebase Console → ' +
        'Project Settings → Cloud Messaging → Web Push certificates.',
      )
      return false
    }

    try {
      const perm = await Notification.requestPermission()
      status.value = perm as NotifStatus
      if (perm !== 'granted') return false

      const swReg = await navigator.serviceWorker.register(
        '/firebase-messaging-sw.js',
        { scope: '/' },
      )
      const app = nuxtApp.$firebaseApp as FirebaseApp
      const messaging = getMessaging(app)
      const fcmToken = await getToken(messaging, {
        vapidKey,
        serviceWorkerRegistration: swReg,
      })

      if (!fcmToken) return false

      const uid = user.value?.uid
      if (!uid) return false
      await api.post(`/api/notifications/${uid}/register`, {
        fcmToken,
        platform: 'web',
      })

      onMessage(messaging, (msg) => {
        const title = msg.notification?.title ?? 'PesoPulse'
        const body = msg.notification?.body ?? ''
        toast.info(title, body)
      })

      return true
    } catch (e) {
      console.error('FCM registration failed', e)
      return false
    }
  }

  return { status, detectStatus, register }
}
