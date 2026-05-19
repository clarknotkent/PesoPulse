export type ToastTone = 'info' | 'success' | 'error' | 'warning'

export interface Toast {
  id: number
  title: string
  message?: string
  tone: ToastTone
  duration: number
}

let counter = 0

export function useToast() {
  const toasts = useState<Toast[]>('toast:list', () => [])

  function push(toast: Omit<Toast, 'id' | 'duration'> & { duration?: number }) {
    const id = ++counter
    const duration = toast.duration ?? 4000
    toasts.value.push({ id, duration, ...toast })
    if (duration > 0) {
      setTimeout(() => dismiss(id), duration)
    }
    return id
  }

  function dismiss(id: number) {
    toasts.value = toasts.value.filter((t) => t.id !== id)
  }

  function clear() {
    toasts.value = []
  }

  return {
    toasts: readonly(toasts),
    push,
    dismiss,
    clear,
    info: (title: string, message?: string) => push({ title, message, tone: 'info' }),
    success: (title: string, message?: string) => push({ title, message, tone: 'success' }),
    error: (title: string, message?: string) => push({ title, message, tone: 'error' }),
    warning: (title: string, message?: string) => push({ title, message, tone: 'warning' }),
  }
}
