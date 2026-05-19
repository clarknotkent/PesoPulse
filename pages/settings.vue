<template>
  <div class="page">
    <!-- Header -->
    <header class="page-header space-y-5">
      <div class="flex items-center justify-between">
        <h1 class="text-[var(--text)] font-medium">Settings</h1>
        <button
          @click="signOut"
          class="press text-[var(--text-subtle)] hover:text-[var(--c-expense)] text-xs inline-flex items-center gap-1"
        >
          <Icon name="logout" :size="14" />
          Sign out
        </button>
      </div>

      <!-- Tab toggle -->
      <div class="flex gap-1 bg-[var(--bg-input)] rounded-xl p-1 overflow-x-auto">
        <button
          v-for="tab in (['categories', 'sharing', 'recurring', 'security', 'appearance', 'app'] as const)"
          :key="tab"
          @click="activeTab = tab"
          :class="[
            'press flex-1 py-2 rounded-lg text-sm font-medium transition capitalize whitespace-nowrap px-3',
            activeTab === tab ? 'bg-[var(--bg-surface)] text-[var(--text)] shadow-sm' : 'text-[var(--text-muted)]',
          ]"
        >{{ tabLabel(tab) }}</button>
      </div>
    </header>

    <!-- Categories tab -->
    <div v-if="activeTab === 'categories'" class="page-body">
      <!-- System pills -->
      <section class="page-section">
        <p class="label mb-3">System</p>
        <div class="flex flex-wrap gap-2">
          <span
            v-for="cat in systemCategories"
            :key="cat.id"
            class="border border-[var(--border)] text-[var(--text-muted)] text-xs px-3 py-1.5 rounded-full inline-flex items-center gap-1.5"
          >
            <Icon :name="resolveCatIcon(cat)" :size="12" />
            {{ cat.name }}
          </span>
        </div>
      </section>

      <!-- Custom — hairline rows -->
      <section class="page-section">
        <p class="label mb-3">Custom</p>
        <p v-if="customCategories.length === 0" class="text-[var(--text-subtle)] text-sm py-2">No custom categories yet.</p>
        <div v-else class="border-t border-[var(--border)]">
          <div
            v-for="cat in customCategories"
            :key="cat.id"
            class="py-3 border-b border-[var(--border)] flex items-center justify-between gap-3"
          >
            <div class="flex items-center gap-3 min-w-0">
              <span class="w-8 h-8 rounded-lg bg-[var(--bg-input)] flex items-center justify-center text-[var(--text-muted)] shrink-0">
                <Icon :name="resolveCatIcon(cat)" :size="14" />
              </span>
              <div class="min-w-0">
                <p class="text-[var(--text)] text-sm font-medium truncate">{{ cat.name }}</p>
                <span
                  :class="[
                    'text-[10px] px-1.5 py-0.5 rounded-full inline-block mt-0.5',
                    cat.type === 'income' ? 'bg-emerald-500/10 text-[var(--c-income)]' : 'bg-red-500/10 text-[var(--c-expense)]',
                  ]"
                >{{ cat.type }}</span>
              </div>
            </div>
            <button
              @click="deleteCategory(cat.id)"
              class="press text-[var(--text-subtle)] hover:text-[var(--c-expense)] w-8 h-8 flex items-center justify-center shrink-0"
              aria-label="Delete category"
            >
              <Icon name="x" :size="14" />
            </button>
          </div>
        </div>
      </section>

      <!-- Add form (earned) -->
      <section class="page-section">
        <div class="bg-[var(--bg-surface)] border border-[var(--border)] rounded-2xl p-4 space-y-4">
          <p class="label">Add category</p>

          <div class="space-y-3">
            <input
              v-model="newCat.name"
              type="text"
              placeholder="Category name"
              class="focus-ring w-full bg-[var(--bg-input)] text-[var(--text)] placeholder-[var(--text-subtle)] rounded-lg px-4 py-3 text-sm outline-none"
            />

            <div class="flex gap-2">
              <button
                v-for="t in (['expense', 'income'] as const)"
                :key="t"
                @click="newCat.type = t"
                :class="[
                  'press flex-1 py-2 rounded-lg text-sm font-medium transition',
                  newCat.type === t
                    ? t === 'income' ? 'bg-emerald-500 text-white' : 'bg-red-500 text-white'
                    : 'bg-[var(--bg-input)] text-[var(--text-muted)]',
                ]"
              >{{ t === 'income' ? 'Income' : 'Expense' }}</button>
            </div>
          </div>

          <p v-if="catError" class="text-[var(--c-expense)] text-xs">{{ catError }}</p>

          <button
            @click="addCategory"
            :disabled="catSubmitting"
            class="press w-full bg-[var(--text)] text-[var(--bg)] font-medium py-3 rounded-lg text-sm disabled:opacity-50 disabled:active:scale-100"
          >{{ catSubmitting ? 'Adding…' : 'Add category' }}</button>
        </div>
      </section>
    </div>

    <!-- Sharing tab -->
    <div v-if="activeTab === 'sharing'" class="page-body">
      <!-- Hairline list -->
      <section class="page-section">
        <p class="label mb-3">Access granted to</p>
        <p v-if="grants.length === 0" class="text-[var(--text-subtle)] text-sm py-2">No one has access.</p>
        <div v-else class="border-t border-[var(--border)]">
          <div
            v-for="grant in grants"
            :key="grant.id"
            class="py-4 border-b border-[var(--border)] flex items-center justify-between gap-3"
          >
            <div class="min-w-0">
              <p class="text-[var(--text)] text-sm font-medium truncate">{{ grant.viewerEmail }}</p>
              <p class="text-[var(--text-subtle)] text-xs tabular-nums mt-0.5">{{ formatGrantDate(grant.grantedAt) }}</p>
            </div>
            <button
              @click="revokeGrant(grant.id)"
              class="press text-[var(--text-subtle)] hover:text-[var(--c-expense)] text-xs px-2 py-1 rounded shrink-0"
            >Revoke</button>
          </div>
        </div>
      </section>

      <!-- Grant form (earned) -->
      <section class="page-section">
        <div class="bg-[var(--bg-surface)] border border-[var(--border)] rounded-2xl p-4 space-y-4">
          <p class="label">Grant access</p>

          <input
            v-model="shareEmail"
            type="email"
            placeholder="Email address"
            class="focus-ring w-full bg-[var(--bg-input)] text-[var(--text)] placeholder-[var(--text-subtle)] rounded-lg px-4 py-3 text-sm outline-none"
          />

          <p v-if="shareError" class="text-[var(--c-expense)] text-xs">{{ shareError }}</p>

          <button
            @click="grantAccess"
            :disabled="shareSubmitting"
            class="press w-full bg-[var(--text)] text-[var(--bg)] font-medium py-3 rounded-lg text-sm disabled:opacity-50 disabled:active:scale-100"
          >{{ shareSubmitting ? 'Granting…' : 'Grant access' }}</button>
        </div>
      </section>

      <!-- Share link (earned — copy CTA) -->
      <section v-if="grants.length > 0" class="page-section">
        <div class="bg-[var(--bg-surface)] border border-[var(--border)] rounded-2xl p-4 space-y-3">
          <p class="label">Your share link</p>
          <p class="font-mono text-xs text-[var(--text-muted)] break-all">{{ shareUrl }}</p>
          <button
            @click="copyLink"
            class="press w-full bg-[var(--bg-input)] text-[var(--text)] font-medium py-3 rounded-lg text-sm inline-flex items-center justify-center gap-2"
          >
            <Icon :name="copied ? 'check' : 'share'" :size="14" />
            {{ copied ? 'Copied' : 'Copy link' }}
          </button>
        </div>
      </section>
    </div>

    <!-- Recurring tab -->
    <div v-if="activeTab === 'recurring'" class="page-body">
      <section class="page-section">
        <NuxtLink
          to="/recurring"
          class="press flex items-center justify-between border-b border-t border-[var(--border)] py-4"
        >
          <div>
            <p class="text-[var(--text)] text-sm font-medium">Recurring transactions</p>
            <p class="text-[var(--text-subtle)] text-xs mt-0.5">Manage automatic income & bills.</p>
          </div>
          <Icon name="chevron-right" :size="16" class="text-[var(--text-subtle)]" />
        </NuxtLink>
      </section>
    </div>

    <!-- Security tab -->
    <div v-if="activeTab === 'security'" class="page-body">
      <section class="page-section">
        <div class="bg-[var(--bg-surface)] border border-[var(--border)] rounded-2xl p-4 space-y-3">
          <p class="label">Email</p>
          <div class="flex items-center justify-between gap-3">
            <div class="min-w-0">
              <p class="text-[var(--text)] text-sm font-medium truncate">{{ user?.email }}</p>
              <p class="text-[var(--text-subtle)] text-xs mt-0.5">
                <span v-if="emailVerified" class="text-emerald-400">✓ Verified</span>
                <span v-else class="text-amber-400">! Not verified</span>
              </p>
            </div>
            <button
              v-if="!emailVerified"
              @click="onResendVerification"
              :disabled="verifyBusy"
              class="press shrink-0 bg-[var(--bg-input)] text-[var(--text)] text-xs px-3 py-1.5 rounded-lg disabled:opacity-50"
            >{{ verifyBusy ? 'Sending…' : 'Resend' }}</button>
          </div>
        </div>
      </section>

      <section class="page-section">
        <div class="bg-[var(--bg-surface)] border border-[var(--border)] rounded-2xl p-4 space-y-3">
          <p class="label">Sessions</p>
          <p class="text-[var(--text-subtle)] text-xs leading-relaxed">
            Sign out of every browser and device using your account. Use this if you lost a device.
          </p>
          <button
            @click="onRevokeAll"
            :disabled="revokeBusy"
            class="press w-full bg-red-500/10 border border-red-500/30 text-red-300 font-medium py-3 rounded-lg text-sm disabled:opacity-50"
          >{{ revokeBusy ? 'Revoking…' : 'Sign out everywhere' }}</button>
        </div>
      </section>

      <section class="page-section">
        <p class="label mb-3">Recent activity</p>
        <p v-if="auditLoading" class="text-[var(--text-subtle)] text-sm py-2">Loading…</p>
        <p v-else-if="auditEntries.length === 0" class="text-[var(--text-subtle)] text-sm py-2">No recorded activity yet.</p>
        <div v-else class="border-t border-[var(--border)]">
          <div
            v-for="entry in auditEntries"
            :key="entry.id"
            class="py-3 border-b border-[var(--border)] flex items-start justify-between gap-3"
          >
            <div class="min-w-0">
              <p class="text-[var(--text)] text-sm font-medium">{{ formatAction(entry.action) }}</p>
              <p class="text-[var(--text-subtle)] text-[11px] mt-0.5 tabular-nums">{{ formatTs(entry.ts) }}<span v-if="entry.ip"> · {{ entry.ip }}</span></p>
            </div>
          </div>
        </div>
      </section>
    </div>

    <!-- Appearance tab -->
    <div v-if="activeTab === 'appearance'" class="page-body">
      <section class="page-section">
        <p class="label mb-3">Theme</p>
        <div class="grid grid-cols-3 gap-2">
          <button
            v-for="opt in themeOptions"
            :key="opt.value"
            @click="setTheme(opt.value)"
            :class="[
              'press py-3 rounded-lg text-sm font-medium capitalize inline-flex flex-col items-center gap-1.5 border',
              themeChoice === opt.value
                ? 'bg-[var(--text)] text-[var(--bg)] border-transparent'
                : 'bg-transparent text-[var(--text-muted)] border-[var(--border)]',
            ]"
          >
            <Icon :name="opt.icon" :size="16" />
            {{ opt.value }}
          </button>
        </div>
        <p class="text-[var(--text-subtle)] text-xs mt-3">Currently: {{ effectiveTheme }}</p>
      </section>
    </div>

    <!-- App tab — install + about -->
    <div v-if="activeTab === 'app'" class="page-body">
      <section class="page-section">
        <div class="bg-[var(--bg-surface)] border border-[var(--border)] rounded-2xl p-5">
          <div class="flex items-center justify-between gap-3">
            <div class="min-w-0">
              <p class="text-[var(--text)] text-sm font-medium">{{ installed ? 'Installed' : 'Install PesoPulse' }}</p>
              <p class="text-[var(--text-subtle)] text-xs mt-1">
                {{ installed
                  ? 'Running as an installed app.'
                  : (canInstall
                      ? 'Add to your home screen for an app-like experience.'
                      : (isIos
                        ? 'On iOS: Share → Add to Home Screen.'
                        : 'Install not available on this browser yet.')) }}
              </p>
            </div>
            <button
              v-if="canInstall && !installed"
              @click="promptInstall"
              class="press shrink-0 bg-emerald-500 text-white font-medium py-2 px-4 rounded-lg text-sm inline-flex items-center gap-1.5"
            >
              <Icon name="plus" :size="14" :stroke-width="2.5" />
              Install
            </button>
          </div>
        </div>
      </section>

      <section class="page-section">
        <p class="label mb-2">About</p>
        <p class="text-[var(--text-muted)] text-sm leading-relaxed max-w-prose">
          PesoPulse is a personal finance tracker for the Philippine Peso. Built as a Progressive Web App; works online,
          installable to your home screen, and ready for offline navigation.
        </p>
      </section>
    </div>
  </div>
</template>

<script setup lang="ts">
definePageMeta({ middleware: 'auth' })

interface Category {
  id: string
  name: string
  icon: string
  type: 'income' | 'expense'
  isSystem: boolean
}

interface Grant {
  id: string
  ownerId: string
  viewerId: string
  viewerEmail: string
  grantedAt: string
}

const { user, signOut, emailVerified, sendVerification, signOutEverywhere } = useAuth()
const { requireFresh } = useReauthGate()
const toast = useToast()
const api = useApi()

interface AuditEntry {
  id: string
  action: string
  ts: string
  ip: string | null
  targetDocId: string | null
}

const auditEntries = ref<AuditEntry[]>([])
const auditLoading = ref(false)
const verifyBusy = ref(false)
const revokeBusy = ref(false)

const ACTION_LABELS: Record<string, string> = {
  'auth.register': 'Account registered',
  'auth.revoke_tokens': 'Signed out everywhere',
  'txn.create': 'Transaction created',
  'txn.update': 'Transaction edited',
  'txn.delete': 'Transaction deleted',
  'sharing.grant': 'Granted view access',
  'sharing.revoke': 'Revoked view access',
  'receipt.scan': 'Receipt scanned',
}

function formatAction(a: string): string {
  return ACTION_LABELS[a] ?? a
}

function formatTs(iso: string): string {
  try {
    return new Date(iso).toLocaleString('en-PH', { year: 'numeric', month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit' })
  } catch {
    return iso
  }
}

async function loadAuditLog(): Promise<void> {
  const uid = user.value?.uid
  if (!uid) return
  auditLoading.value = true
  try {
    auditEntries.value = await api.get<AuditEntry[]>(`/api/audit/${uid}?limit=30`)
  } catch {
    auditEntries.value = []
  } finally {
    auditLoading.value = false
  }
}

async function onResendVerification(): Promise<void> {
  verifyBusy.value = true
  try {
    await sendVerification()
    toast.info('Sent', 'Verification email sent.')
  } catch {
    toast.error('Failed', 'Could not send verification email.')
  } finally {
    verifyBusy.value = false
  }
}

async function onRevokeAll(): Promise<void> {
  const fresh = await requireFresh('Sign out all devices')
  if (!fresh) return
  revokeBusy.value = true
  try {
    await signOutEverywhere()
  } catch {
    toast.error('Failed', 'Could not revoke sessions.')
    revokeBusy.value = false
  }
}

const { choice: themeChoice, effective: effectiveTheme, setTheme } = useTheme()
const { canInstall, installed, prompt: promptInstall, isIos } = useInstallPrompt()

type Tab = 'categories' | 'sharing' | 'recurring' | 'security' | 'appearance' | 'app'
const activeTab = ref<Tab>('categories')

watch(activeTab, (tab) => {
  if (tab === 'security') loadAuditLog()
})

function tabLabel(t: Tab): string {
  if (t === 'appearance') return 'Theme'
  if (t === 'app') return 'App'
  if (t === 'security') return 'Security'
  return t
}

const themeOptions = [
  { value: 'system' as const, icon: 'monitor' },
  { value: 'light' as const, icon: 'sun' },
  { value: 'dark' as const, icon: 'moon' },
]

const categories = ref<Category[]>([])
const catError = ref('')
const catSubmitting = ref(false)
const newCat = reactive({ name: '', type: 'expense' as 'income' | 'expense' })

const systemCategories = computed(() => categories.value.filter((c) => c.isSystem))
const customCategories = computed(() => categories.value.filter((c) => !c.isSystem))

const grants = ref<Grant[]>([])
const shareEmail = ref('')
const shareError = ref('')
const shareSubmitting = ref(false)
const copied = ref(false)

const shareUrl = computed(() => {
  if (process.client) {
    return `${window.location.origin}/shared/${user.value?.uid}`
  }
  return ''
})

const ICON_KEYWORDS: Array<[RegExp, string]> = [
  [/food|meal|grocer|restaurant|drink|coffee|snack/i, 'receipt'],
  [/transport|fuel|gas|fare|commute|ride|taxi|grab/i, 'arrow-right'],
  [/util|bill|electric|water|internet|phone|rent/i, 'wallet'],
  [/health|medic|pharma|hospital/i, 'sparkles'],
  [/salary|pay|wage|allowance|bonus/i, 'trend-up'],
  [/save|fund|emergency|goal/i, 'piggy'],
  [/shop|cloth|gift/i, 'tag'],
  [/entertain|movie|fun|game|stream/i, 'sparkles'],
  [/school|tuition|book|edu/i, 'list'],
  [/travel|trip|hotel|flight/i, 'arrow-right'],
]

function resolveCatIcon(cat: Category): string {
  const m = ICON_KEYWORDS.find(([re]) => re.test(cat.name))
  if (m) return m[1]
  return cat.type === 'income' ? 'trend-up' : 'tag'
}

function formatGrantDate(iso: string) {
  return new Date(iso).toLocaleDateString('en-PH', { year: 'numeric', month: 'short', day: 'numeric' })
}

async function loadCategories() {
  const uid = user.value?.uid
  if (!uid) return
  try {
    categories.value = await api.get<Category[]>(`/api/categories/${uid}`)
  } catch {}
}

async function loadGrants() {
  const uid = user.value?.uid
  if (!uid) return
  try {
    grants.value = await api.get<Grant[]>(`/api/sharing/${uid}`)
  } catch {}
}

async function addCategory() {
  catError.value = ''
  if (!newCat.name.trim()) {
    catError.value = 'Name is required'
    return
  }
  catSubmitting.value = true
  try {
    const uid = user.value!.uid
    const cat = await api.post<Category>(`/api/categories/${uid}`, {
      name: newCat.name.trim(),
      icon: '',
      type: newCat.type,
    })
    categories.value.push(cat)
    newCat.name = ''
  } catch (e: unknown) {
    catError.value = (e as { data?: { detail?: string } })?.data?.detail ?? 'Failed to add category'
  } finally {
    catSubmitting.value = false
  }
}

async function deleteCategory(id: string) {
  const uid = user.value!.uid
  try {
    await api.del(`/api/categories/${uid}/${id}`)
    categories.value = categories.value.filter((c) => c.id !== id)
  } catch {}
}

async function grantAccess() {
  shareError.value = ''
  if (!shareEmail.value.trim()) {
    shareError.value = 'Email is required'
    return
  }
  shareSubmitting.value = true
  try {
    const uid = user.value!.uid
    const grant = await api.post<Grant>(`/api/sharing/${uid}`, { viewerEmail: shareEmail.value.trim() })
    grants.value.push(grant)
    shareEmail.value = ''
  } catch (e: unknown) {
    const status = (e as { status?: number })?.status
    const detail = (e as { data?: { detail?: string } })?.data?.detail
    if (status === 404) {
      shareError.value = 'User not registered in PesoPulse'
    } else if (status === 409) {
      shareError.value = 'Already has access'
    } else if (status === 400) {
      shareError.value = detail ?? 'Invalid request'
    } else {
      shareError.value = detail ?? 'Failed to grant access'
    }
  } finally {
    shareSubmitting.value = false
  }
}

async function revokeGrant(id: string) {
  const fresh = await requireFresh('Revoke shared access')
  if (!fresh) return
  const uid = user.value!.uid
  try {
    await api.del(`/api/sharing/${uid}/${id}`)
    grants.value = grants.value.filter((g) => g.id !== id)
  } catch {}
}

async function copyLink() {
  await navigator.clipboard.writeText(shareUrl.value)
  copied.value = true
  setTimeout(() => { copied.value = false }, 2000)
}

onMounted(() => {
  loadCategories()
  loadGrants()
})
</script>
