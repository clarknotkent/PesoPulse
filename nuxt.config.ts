export default defineNuxtConfig({
  compatibilityDate: '2026-05-17',
  ssr: false,
  devtools: { enabled: true },
  modules: ['@nuxtjs/tailwindcss', '@vite-pwa/nuxt'],
  css: ['~/assets/css/main.css'],
  components: [{ path: '~/components', pathPrefix: false }],

  app: {
    pageTransition: false,
    layoutTransition: false,
    head: {
      meta: [
        { name: 'apple-mobile-web-app-capable', content: 'yes' },
        { name: 'apple-mobile-web-app-status-bar-style', content: 'black-translucent' },
        { name: 'apple-mobile-web-app-title', content: 'PesoPulse' },
        { name: 'mobile-web-app-capable', content: 'yes' },
        { name: 'theme-color', content: '#08090b', media: '(prefers-color-scheme: dark)' },
        { name: 'theme-color', content: '#f6f7f9', media: '(prefers-color-scheme: light)' },
      ],
      link: [
        { rel: 'preconnect', href: 'https://fonts.googleapis.com' },
        { rel: 'preconnect', href: 'https://fonts.gstatic.com', crossorigin: '' },
        {
          rel: 'stylesheet',
          href: 'https://fonts.googleapis.com/css2?family=Geist:wght@400;500;600;700&family=Geist+Mono:wght@500&display=swap',
        },
        { rel: 'apple-touch-icon', href: '/icons/icon-192x192.png' },
        { rel: 'apple-touch-icon', sizes: '512x512', href: '/icons/icon-512x512.png' },
      ],
    },
  },

  router: {
    options: {
      scrollBehaviorType: 'smooth',
    },
  },

  runtimeConfig: {
    public: {
      firebaseApiKey: '',
      firebaseAuthDomain: '',
      firebaseProjectId: '',
      firebaseAppId: '',
      firebaseMessagingSenderId: '',
      firebaseVapidKey: '',
      apiBaseUrl: '/api',
    },
  },

  nitro: {
    devProxy: {
      '/api': {
        target: 'http://127.0.0.1:8000/api',
        changeOrigin: true
      }
    }
  },

  routeRules: {
    '/**': {
      headers: {
        'Content-Security-Policy': [
          "default-src 'self'",
          "script-src 'self' 'unsafe-inline' https://www.gstatic.com https://www.googleapis.com https://apis.google.com",
          "connect-src 'self' https://*.googleapis.com https://*.firebaseio.com https://identitytoolkit.googleapis.com https://securetoken.googleapis.com https://www.googleapis.com https://fcmregistrations.googleapis.com https://apis.google.com https://accounts.google.com https://www.google.com wss://*.firebaseio.com",
          "img-src 'self' data: blob: https://*.googleusercontent.com",
          "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com",
          "font-src 'self' https://fonts.gstatic.com",
          "frame-src https://*.firebaseapp.com https://accounts.google.com https://apis.google.com",
          "worker-src 'self'",
          "manifest-src 'self'",
          "frame-ancestors 'none'",
          "base-uri 'self'",
          "form-action 'self'",
        ].join('; '),
        'X-Content-Type-Options': 'nosniff',
        'X-Frame-Options': 'DENY',
        'Referrer-Policy': 'strict-origin-when-cross-origin',
        'Permissions-Policy': 'camera=(), microphone=(), geolocation=()',
        'Strict-Transport-Security': 'max-age=63072000; includeSubDomains; preload',
      },
    },
  },

  pwa: {
    registerType: 'autoUpdate',
    manifest: {
      name: 'PesoPulse Personal Tracker',
      short_name: 'PesoPulse',
      description: 'A tightly coupled modern micro-finance application',
      theme_color: '#08090b',
      background_color: '#08090b',
      display: 'standalone',
      orientation: 'portrait',
      lang: 'en-PH',
      categories: ['finance', 'productivity'],
      icons: [
        {
          src: 'icons/icon-192x192.png',
          sizes: '192x192',
          type: 'image/png',
          purpose: 'any',
        },
        {
          src: 'icons/icon-512x512.png',
          sizes: '512x512',
          type: 'image/png',
          purpose: 'any',
        },
        {
          src: 'icons/icon-512x512.png',
          sizes: '512x512',
          type: 'image/png',
          purpose: 'maskable',
        },
      ],
      shortcuts: [
        {
          name: 'Add transaction',
          short_name: 'Add',
          url: '/dashboard?add=1',
          icons: [{ src: 'icons/icon-192x192.png', sizes: '192x192' }],
        },
        {
          name: 'Stats',
          short_name: 'Stats',
          url: '/stats',
        },
      ],
    },
    workbox: {
      navigateFallback: '/offline',
      navigateFallbackDenylist: [/^\/firebase-messaging-sw\.js$/, /^\/api\//],
      globPatterns: ['**/*.{js,css,html,png,svg,ico,woff2}'],
      runtimeCaching: [
        {
          urlPattern: ({ url }: { url: URL }) =>
            url.origin === self.location.origin && url.pathname.startsWith('/api/'),
          handler: 'NetworkFirst',
          options: {
            cacheName: 'pp-api',
            networkTimeoutSeconds: 5,
            expiration: { maxEntries: 60, maxAgeSeconds: 60 * 60 * 24 },
            cacheableResponse: { statuses: [0, 200] },
          },
        },
        {
          urlPattern: ({ request }: { request: Request }) => request.destination === 'image',
          handler: 'CacheFirst',
          options: {
            cacheName: 'pp-images',
            expiration: { maxEntries: 60, maxAgeSeconds: 60 * 60 * 24 * 30 },
          },
        },
        {
          urlPattern: /^https:\/\/fonts\.(googleapis|gstatic)\.com\//,
          handler: 'StaleWhileRevalidate',
          options: { cacheName: 'pp-fonts' },
        },
      ],
    },
    client: {
      installPrompt: true,
    },
    devOptions: {
      enabled: false,
      type: 'module',
    },
  },
})
