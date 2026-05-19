export interface TxnFilters {
  search: string
  from: string
  to: string
  type: '' | 'income' | 'expense'
  category: string
  minAmount: string
  maxAmount: string
}

export function emptyFilters(): TxnFilters {
  return {
    search: '',
    from: '',
    to: '',
    type: '',
    category: '',
    minAmount: '',
    maxAmount: '',
  }
}

export function buildQuery(f: TxnFilters): string {
  const parts: string[] = []
  if (f.search) parts.push(`search=${encodeURIComponent(f.search)}`)
  if (f.from) parts.push(`from=${f.from}`)
  if (f.to) parts.push(`to=${f.to}`)
  if (f.type) parts.push(`type=${f.type}`)
  if (f.category) parts.push(`category=${encodeURIComponent(f.category)}`)
  if (f.minAmount) parts.push(`minAmount=${f.minAmount}`)
  if (f.maxAmount) parts.push(`maxAmount=${f.maxAmount}`)
  return parts.length > 0 ? '?' + parts.join('&') : ''
}

export function hasActiveFilters(f: TxnFilters): boolean {
  return Boolean(f.from || f.to || f.type || f.category || f.minAmount || f.maxAmount)
}

export function useTxnFilters() {
  const filters = useState<TxnFilters>('txn:filters', () => emptyFilters())

  function reset() {
    filters.value = emptyFilters()
  }

  return {
    filters,
    reset,
    buildQuery: () => buildQuery(filters.value),
    hasActive: computed(() => hasActiveFilters(filters.value)),
  }
}
