export default defineEventHandler((event) => {
  const { public: pub } = useRuntimeConfig()
  const config = {
    apiKey: pub.firebaseApiKey,
    authDomain: pub.firebaseAuthDomain,
    projectId: pub.firebaseProjectId,
    appId: pub.firebaseAppId,
    messagingSenderId: pub.firebaseMessagingSenderId,
  }

  setHeader(event, 'Content-Type', 'application/javascript; charset=utf-8')
  setHeader(event, 'Service-Worker-Allowed', '/')
  setHeader(event, 'Cache-Control', 'no-cache')

  return `importScripts('https://www.gstatic.com/firebasejs/10.7.1/firebase-app-compat.js')
importScripts('https://www.gstatic.com/firebasejs/10.7.1/firebase-messaging-compat.js')

const config = ${JSON.stringify(config)}

if (config.apiKey && config.projectId) {
  firebase.initializeApp(config)
  const messaging = firebase.messaging()

  messaging.onBackgroundMessage(function (payload) {
    const title = (payload.notification && payload.notification.title) || 'PesoPulse'
    const body = (payload.notification && payload.notification.body) || ''
    self.registration.showNotification(title, {
      body: body,
      icon: '/icons/icon-192x192.png',
      badge: '/icons/icon-192x192.png',
    })
  })
}

self.addEventListener('install', function (event) {
  event.waitUntil(self.skipWaiting())
})

self.addEventListener('activate', function (event) {
  event.waitUntil(self.clients.claim())
})
`
})
