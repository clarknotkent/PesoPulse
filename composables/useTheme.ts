export type ThemeChoice = 'system' | 'light' | 'dark'

const STORAGE_KEY = 'pesopulse:theme'

function resolveEffective(choice: ThemeChoice): 'light' | 'dark' {
  if (choice === 'light' || choice === 'dark') return choice
  if (typeof window === 'undefined') return 'dark'
  return window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light'
}

function applyClass(effective: 'light' | 'dark') {
  if (typeof document === 'undefined') return
  const root = document.documentElement
  root.classList.toggle('dark', effective === 'dark')
  root.classList.toggle('light', effective === 'light')
}

export function useTheme() {
  const choice = useState<ThemeChoice>('theme:choice', () => 'system')
  const effective = useState<'light' | 'dark'>('theme:effective', () => 'dark')

  function setTheme(next: ThemeChoice) {
    choice.value = next
    const eff = resolveEffective(next)
    effective.value = eff
    applyClass(eff)
    if (typeof localStorage !== 'undefined') {
      localStorage.setItem(STORAGE_KEY, next)
    }
  }

  function initTheme() {
    if (typeof window === 'undefined') return
    const stored = (localStorage.getItem(STORAGE_KEY) as ThemeChoice | null) ?? 'system'
    setTheme(stored)
    const mq = window.matchMedia('(prefers-color-scheme: dark)')
    mq.addEventListener('change', () => {
      if (choice.value === 'system') setTheme('system')
    })
  }

  return {
    choice: readonly(choice),
    effective: readonly(effective),
    setTheme,
    initTheme,
  }
}
