export interface BudgetBreach {
  period: 'week' | 'month'
  scope: 'category' | 'total'
  category: string | null
  limit: number
  rollover: number
  spent: number
  remaining: number
}

export interface BudgetCheckResult {
  wouldOverspend: boolean
  breaches: BudgetBreach[]
}

export function useBudgetCheck() {
  const api = useApi()
  const { user } = useAuth()

  async function check(amount: number, category: string, date?: string): Promise<BudgetCheckResult | null> {
    const uid = user.value?.uid
    if (!uid) return null
    try {
      return await api.post<BudgetCheckResult>(`/api/budgets/${uid}/check`, {
        amount,
        category,
        date,
      })
    }
    catch {
      return null
    }
  }

  return { check }
}
