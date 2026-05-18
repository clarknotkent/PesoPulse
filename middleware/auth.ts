export default defineNuxtRouteMiddleware(async () => {
  if (process.server) return

  const { user, initialized } = useAuth()

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
    return navigateTo('/auth')
  }
})
