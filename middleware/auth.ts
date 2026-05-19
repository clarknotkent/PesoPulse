export default defineNuxtRouteMiddleware(async (to) => {
  if (import.meta.server) return

  const { user, initialized, initIdleWatcher } = useAuth()

  if (!initialized.value) {
    await new Promise<void>((resolve) => {
      const stop = watch(initialized, (val) => {
        if (val) {
          stop()
          resolve()
        }
      })
    })
  }

  if (!user.value) {
    const target = to.fullPath && to.fullPath !== '/' ? to.fullPath : '/dashboard'
    return navigateTo(`/auth?redirect=${encodeURIComponent(target)}`)
  }

  initIdleWatcher()
})
