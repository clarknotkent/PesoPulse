const TAB_ROUTES = new Set(['/dashboard', '/stats', '/budgets', '/settings'])

function isTabRoute(path: string): boolean {
  return TAB_ROUTES.has(path)
}

function isHiddenRoute(path: string): boolean {
  return path === '/auth' || path === '/login' || path.startsWith('/shared/')
}

let listenerRegistered = false

export function useNavStack() {
  const router = useRouter()
  const transitionName = useState<string>('nav:transition', () => 'fade')
  const isPop = useState<boolean>('nav:isPop', () => false)

  if (import.meta.client && !listenerRegistered) {
    listenerRegistered = true

    window.addEventListener('popstate', () => {
      isPop.value = true
    })

    router.beforeEach((to, from) => {
      const toPath = to.path
      const fromPath = from.path

      if (isHiddenRoute(toPath) || isHiddenRoute(fromPath)) {
        transitionName.value = 'fade'
        isPop.value = false
        return
      }

      const toTab = isTabRoute(toPath)
      const fromTab = isTabRoute(fromPath)

      if (toTab && fromTab) {
        transitionName.value = 'fade'
      }
      else if (isPop.value) {
        transitionName.value = 'slide-pop'
      }
      else if (toTab && !fromTab) {
        transitionName.value = 'slide-pop'
      }
      else {
        transitionName.value = 'slide-push'
      }

      isPop.value = false
    })
  }

  return { transitionName }
}
