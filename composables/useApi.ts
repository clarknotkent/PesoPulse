export function useApi() {
  const { idToken } = useAuth()

  async function authHeaders(): Promise<Record<string, string>> {
    const token = await idToken()
    if (!token) throw new Error('Not authenticated')
    return { Authorization: `Bearer ${token}` }
  }

  async function get<T>(path: string): Promise<T> {
    return $fetch<T>(path, { headers: await authHeaders() })
  }

  async function post<T>(path: string, body: unknown): Promise<T> {
    return $fetch<T>(path, { method: 'POST', body, headers: await authHeaders() })
  }

  async function put<T>(path: string, body: unknown): Promise<T> {
    return $fetch<T>(path, { method: 'PUT', body, headers: await authHeaders() })
  }

  async function del<T>(path: string): Promise<T> {
    return $fetch<T>(path, { method: 'DELETE', headers: await authHeaders() })
  }

  return { get, post, put, del }
}
