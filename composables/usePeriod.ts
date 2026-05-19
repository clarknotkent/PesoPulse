export type Period = 'week' | 'month' | 'year'

function todayISO(): string {
  const now = new Date()
  const y = now.getFullYear()
  const m = String(now.getMonth() + 1).padStart(2, '0')
  const d = String(now.getDate()).padStart(2, '0')
  return `${y}-${m}-${d}`
}

function parseISO(iso: string): Date {
  const [y, m, d] = iso.split('-').map(Number)
  return new Date(y, m - 1, d)
}

function toISO(date: Date): string {
  const y = date.getFullYear()
  const m = String(date.getMonth() + 1).padStart(2, '0')
  const d = String(date.getDate()).padStart(2, '0')
  return `${y}-${m}-${d}`
}

function startOfWeek(date: Date): Date {
  const day = date.getDay()
  const diff = day === 0 ? -6 : 1 - day
  const d = new Date(date)
  d.setDate(date.getDate() + diff)
  return d
}

function endOfWeek(date: Date): Date {
  const s = startOfWeek(date)
  const e = new Date(s)
  e.setDate(s.getDate() + 6)
  return e
}

function startOfMonth(date: Date): Date {
  return new Date(date.getFullYear(), date.getMonth(), 1)
}

function endOfMonth(date: Date): Date {
  return new Date(date.getFullYear(), date.getMonth() + 1, 0)
}

function startOfYear(date: Date): Date {
  return new Date(date.getFullYear(), 0, 1)
}

function endOfYear(date: Date): Date {
  return new Date(date.getFullYear(), 11, 31)
}

function formatLabel(period: Period, anchor: string): string {
  const d = parseISO(anchor)
  if (period === 'week') {
    const s = startOfWeek(d)
    const e = endOfWeek(d)
    const sameMonth = s.getMonth() === e.getMonth()
    const month = s.toLocaleDateString('en-PH', { month: 'short' })
    const monthEnd = e.toLocaleDateString('en-PH', { month: 'short' })
    if (sameMonth) {
      return `${month} ${s.getDate()}–${e.getDate()}, ${e.getFullYear()}`
    }
    return `${month} ${s.getDate()} – ${monthEnd} ${e.getDate()}, ${e.getFullYear()}`
  }
  if (period === 'month') {
    return d.toLocaleDateString('en-PH', { month: 'long', year: 'numeric' })
  }
  return String(d.getFullYear())
}

export function usePeriod() {
  const period = useState<Period>('period:period', () => 'week')
  const anchor = useState<string>('period:anchor', () => todayISO())

  const label = computed(() => formatLabel(period.value, anchor.value))

  const range = computed(() => {
    const d = parseISO(anchor.value)
    let from: Date
    let to: Date
    if (period.value === 'week') {
      from = startOfWeek(d)
      to = endOfWeek(d)
    } else if (period.value === 'month') {
      from = startOfMonth(d)
      to = endOfMonth(d)
    } else {
      from = startOfYear(d)
      to = endOfYear(d)
    }
    return { from: toISO(from), to: toISO(to) }
  })

  function setPeriod(next: Period) {
    period.value = next
  }

  function prev() {
    const d = parseISO(anchor.value)
    if (period.value === 'week') d.setDate(d.getDate() - 7)
    else if (period.value === 'month') d.setMonth(d.getMonth() - 1)
    else d.setFullYear(d.getFullYear() - 1)
    anchor.value = toISO(d)
  }

  function next() {
    const d = parseISO(anchor.value)
    if (period.value === 'week') d.setDate(d.getDate() + 7)
    else if (period.value === 'month') d.setMonth(d.getMonth() + 1)
    else d.setFullYear(d.getFullYear() + 1)
    anchor.value = toISO(d)
  }

  function today() {
    anchor.value = todayISO()
  }

  return {
    period: readonly(period),
    anchor: readonly(anchor),
    label,
    range,
    setPeriod,
    prev,
    next,
    today,
  }
}
