interface BeforeInstallPromptEvent extends Event {
  prompt: () => Promise<void>
  userChoice: Promise<{ outcome: 'accepted' | 'dismissed', platform: string }>
}

const deferred = ref<BeforeInstallPromptEvent | null>(null)
const installed = ref(false)
const standalone = ref(false)
const isIos = ref(false)
let bound = false

function detectStandalone(): boolean {
  if (typeof window === 'undefined') return false
  const matched = window.matchMedia?.('(display-mode: standalone)').matches
  const iosStandalone = (window.navigator as unknown as { standalone?: boolean }).standalone === true
  return Boolean(matched || iosStandalone)
}

function detectIos(): boolean {
  if (typeof navigator === 'undefined') return false
  const ua = navigator.userAgent
  return /iPhone|iPad|iPod/i.test(ua) && !/CriOS|FxiOS/.test(ua)
}

function bind() {
  if (bound || typeof window === 'undefined') return
  bound = true
  standalone.value = detectStandalone()
  isIos.value = detectIos()
  installed.value = standalone.value

  window.addEventListener('beforeinstallprompt', (e) => {
    e.preventDefault()
    deferred.value = e as BeforeInstallPromptEvent
  })

  window.addEventListener('appinstalled', () => {
    installed.value = true
    deferred.value = null
  })
}

export function useInstallPrompt() {
  if (import.meta.client) bind()

  const canInstall = computed(() => Boolean(deferred.value) && !installed.value)

  async function prompt() {
    const ev = deferred.value
    if (!ev) return null
    await ev.prompt()
    const choice = await ev.userChoice
    deferred.value = null
    if (choice.outcome === 'accepted') {
      installed.value = true
    }
    return choice.outcome
  }

  return {
    canInstall,
    installed,
    standalone,
    isIos,
    prompt,
  }
}
