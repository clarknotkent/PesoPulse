export function useApi() {
  const { idToken, signOut } = useAuth()

  async function authHeaders(forceRefresh: boolean = false): Promise<Record<string, string>> {
    const token = await idToken(forceRefresh)
    if (!token) throw new Error('Not authenticated')
    return { Authorization: `Bearer ${token}` }
  }

  type FetchOpts = { method?: string; body?: unknown }

  async function request<T>(path: string, opts: FetchOpts = {}): Promise<T> {
    const method = opts.method ?? 'GET'
    try {
      return await $fetch<T>(path, { method, body: opts.body, headers: await authHeaders() })
    } catch (e: unknown) {
      const status = (e as { status?: number; statusCode?: number })?.status
        ?? (e as { statusCode?: number })?.statusCode
      const detail = (e as { data?: { detail?: string } })?.data?.detail

      if (status === 401) {
        try {
          return await $fetch<T>(path, { method, body: opts.body, headers: await authHeaders(true) })
        } catch (retry: unknown) {
          const retryStatus = (retry as { status?: number; statusCode?: number })?.status
            ?? (retry as { statusCode?: number })?.statusCode
          if (retryStatus === 401) {
            await signOut()
            await navigateTo('/auth?reason=session_expired')
          }
          throw retry
        }
      }

      if (status === 403 && detail === 'email_not_verified') {
        await navigateTo('/auth/verify')
      }

      throw e
    }
  }

  return {
    get: <T>(path: string) => request<T>(path),
    post: <T>(path: string, body?: unknown) => request<T>(path, { method: 'POST', body }),
    put: <T>(path: string, body?: unknown) => request<T>(path, { method: 'PUT', body }),
    del: <T>(path: string) => request<T>(path, { method: 'DELETE' }),
  }
}
