export function useAddTransaction() {
  const open = useState<boolean>('add:open', () => false)
  const router = useRouter()
  const route = useRoute()

  async function show() {
    if (route.path !== '/dashboard') {
      await router.push('/dashboard')
    }
    open.value = true
  }

  function hide() {
    open.value = false
  }

  return { open, show, hide }
}
