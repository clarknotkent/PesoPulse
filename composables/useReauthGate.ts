const FRESHNESS_MS = 5 * 60 * 1000

type Resolver = (ok: boolean) => void

export function useReauthGate() {
  const open = useState<boolean>('reauth:open', () => false)
  const error = useState<string | null>('reauth:error', () => null)
  const busy = useState<boolean>('reauth:busy', () => false)
  const lastVerifiedAt = useState<number>('reauth:lastVerifiedAt', () => 0)
  const pending = useState<Resolver | null>('reauth:pending', () => null)
  const reason = useState<string>('reauth:reason', () => 'Confirm it is you')

  const { reauthenticate } = useAuth()

  function isFresh(): boolean {
    return Date.now() - lastVerifiedAt.value < FRESHNESS_MS
  }

  function requireFresh(label?: string): Promise<boolean> {
    if (isFresh()) return Promise.resolve(true)
    reason.value = label || 'Confirm it is you'
    error.value = null
    open.value = true
    return new Promise<boolean>((resolve) => {
      pending.value = resolve
    })
  }

  async function submit(password: string): Promise<void> {
    busy.value = true
    error.value = null
    try {
      await reauthenticate(password)
      lastVerifiedAt.value = Date.now()
      open.value = false
      const res = pending.value
      pending.value = null
      res?.(true)
    }
    catch (e: unknown) {
      const code = (e as { code?: string })?.code
      if (code === 'auth/wrong-password' || code === 'auth/invalid-credential') {
        error.value = 'Wrong password.'
      }
      else if (code === 'auth/too-many-requests') {
        error.value = 'Too many attempts. Try again later.'
      }
      else {
        error.value = 'Verification failed. Try again.'
      }
    }
    finally {
      busy.value = false
    }
  }

  function cancel(): void {
    open.value = false
    const res = pending.value
    pending.value = null
    res?.(false)
  }

  function invalidate(): void {
    lastVerifiedAt.value = 0
  }

  return { open, busy, error, reason, requireFresh, submit, cancel, invalidate, isFresh }
}
