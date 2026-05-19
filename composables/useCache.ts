import type { Ref, ComputedRef } from 'vue'

const MIN_SKELETON_MS = 150

function storageKey(key: string): string {
  return `cache:${key}`
}

function readStorage<T>(key: string): T | null {
  if (typeof sessionStorage === 'undefined') return null
  try {
    const raw = sessionStorage.getItem(storageKey(key))
    if (!raw) return null
    return JSON.parse(raw) as T
  }
  catch {
    return null
  }
}

function writeStorage<T>(key: string, value: T): void {
  if (typeof sessionStorage === 'undefined') return
  try {
    sessionStorage.setItem(storageKey(key), JSON.stringify(value))
  }
  catch {}
}

export interface UseCacheResult<T> {
  data: Ref<T | null>
  isLoading: Ref<boolean>
  isStale: Ref<boolean>
  error: Ref<unknown>
  refresh: () => Promise<void>
}

type KeyArg = string | Ref<string> | ComputedRef<string> | (() => string)

function unwrapKey(k: KeyArg): string {
  if (typeof k === 'string') return k
  if (typeof k === 'function') return (k as () => string)()
  return (k as Ref<string>).value
}

const inMemoryCache = new Map<string, unknown>()

export function useCache<T>(
  keyArg: KeyArg,
  fetcher: () => Promise<T>,
): UseCacheResult<T> {
  const data = ref<T | null>(null) as Ref<T | null>
  const isLoading = ref(false)
  const isStale = ref(false)
  const error = ref<unknown>(null)
  let activeKey = unwrapKey(keyArg)

  function hydrate(key: string): T | null {
    if (inMemoryCache.has(key)) {
      return inMemoryCache.get(key) as T
    }
    const fromStorage = readStorage<T>(key)
    if (fromStorage !== null) {
      inMemoryCache.set(key, fromStorage)
      return fromStorage
    }
    return null
  }

  async function doFetch(key: string, showSkeleton: boolean): Promise<void> {
    error.value = null
    if (showSkeleton) {
      isLoading.value = true
      const start = Date.now()
      try {
        const result = await fetcher()
        if (key !== activeKey) return
        data.value = result
        inMemoryCache.set(key, result)
        writeStorage(key, result)
        isStale.value = false
      }
      catch (e) {
        if (key === activeKey) error.value = e
      }
      finally {
        const elapsed = Date.now() - start
        const remain = MIN_SKELETON_MS - elapsed
        if (remain > 0) {
          await new Promise((r) => setTimeout(r, remain))
        }
        if (key === activeKey) isLoading.value = false
      }
    }
    else {
      isStale.value = true
      try {
        const result = await fetcher()
        if (key !== activeKey) return
        data.value = result
        inMemoryCache.set(key, result)
        writeStorage(key, result)
      }
      catch (e) {
        if (key === activeKey) error.value = e
      }
      finally {
        if (key === activeKey) isStale.value = false
      }
    }
  }

  function load() {
    const key = unwrapKey(keyArg)
    activeKey = key
    const cached = hydrate(key)
    if (cached !== null) {
      data.value = cached
      isLoading.value = false
      doFetch(key, false)
    }
    else {
      data.value = null
      doFetch(key, true)
    }
  }

  async function refresh() {
    await doFetch(unwrapKey(keyArg), false)
  }

  if (import.meta.client) {
    load()
    if (typeof keyArg !== 'string') {
      const keyRef = typeof keyArg === 'function' ? computed(keyArg as () => string) : (keyArg as Ref<string>)
      watch(() => keyRef.value, () => load())
    }
  }

  return { data, isLoading, isStale, error, refresh }
}
