function pad(n: number): string {
  return String(n).padStart(2, '0')
}

function isoFromDate(d: Date): string {
  return `${d.getFullYear()}-${pad(d.getMonth() + 1)}-${pad(d.getDate())}`
}

export function humanizeDate(iso: string, now: Date = new Date()): string {
  if (!iso) return ''
  const today = new Date(now.getFullYear(), now.getMonth(), now.getDate())
  const todayIso = isoFromDate(today)
  const yesterday = new Date(today)
  yesterday.setDate(today.getDate() - 1)
  const yesterdayIso = isoFromDate(yesterday)

  if (iso === todayIso) return 'Today'
  if (iso === yesterdayIso) return 'Yesterday'

  const parts = iso.split('-').map(Number)
  if (parts.length !== 3 || parts.some(isNaN)) return iso
  const [y, m, d] = parts
  const target = new Date(y, m - 1, d)
  const diffDays = Math.round((today.getTime() - target.getTime()) / 86400000)

  if (diffDays > 0 && diffDays < 7) {
    return target.toLocaleDateString('en-PH', { weekday: 'short' })
  }
  if (target.getFullYear() === today.getFullYear()) {
    return target.toLocaleDateString('en-PH', { month: 'short', day: 'numeric' })
  }
  const monthDay = target.toLocaleDateString('en-PH', { month: 'short', day: 'numeric' })
  return `${monthDay} '${String(target.getFullYear()).slice(-2)}`
}

export function todayIso(now: Date = new Date()): string {
  return isoFromDate(now)
}

export function yesterdayIso(now: Date = new Date()): string {
  const y = new Date(now)
  y.setDate(now.getDate() - 1)
  return isoFromDate(y)
}
