<template>
  <div class="min-h-screen bg-[#0a0a0a] text-white">
    <!-- Header -->
    <header class="px-4 pt-10 pb-4">
      <div class="flex items-center gap-3 mb-6">
        <NuxtLink to="/" class="text-zinc-500 hover:text-white transition text-lg leading-none">←</NuxtLink>
        <h1 class="text-white font-medium">Settings</h1>
      </div>

      <!-- Tab toggle -->
      <div class="flex gap-1 bg-zinc-900 rounded-xl p-1">
        <button
          v-for="tab in (['categories', 'sharing'] as const)"
          :key="tab"
          @click="activeTab = tab"
          :class="[
            'flex-1 py-2 rounded-lg text-sm font-medium transition capitalize',
            activeTab === tab ? 'bg-white text-black' : 'text-zinc-400 hover:text-white',
          ]"
        >{{ tab === 'categories' ? 'Categories' : 'Sharing' }}</button>
      </div>
    </header>

    <!-- Categories tab -->
    <div v-if="activeTab === 'categories'" class="px-4 pb-12 space-y-6">
      <!-- System defaults -->
      <div>
        <p class="text-zinc-500 text-xs uppercase tracking-widest mb-2">System</p>
        <div class="flex flex-wrap gap-2">
          <span
            v-for="cat in systemCategories"
            :key="cat.id"
            class="bg-zinc-900 text-zinc-400 text-xs px-3 py-1.5 rounded-full"
          >{{ cat.icon }} {{ cat.name }}</span>
        </div>
      </div>

      <!-- Custom categories -->
      <div>
        <p class="text-zinc-500 text-xs uppercase tracking-widest mb-2">Custom</p>
        <div v-if="customCategories.length === 0" class="text-zinc-600 text-sm py-4">No custom categories yet.</div>
        <div v-else class="space-y-2">
          <div
            v-for="cat in customCategories"
            :key="cat.id"
            class="bg-zinc-900 rounded-xl px-4 py-3 flex items-center justify-between"
          >
            <div class="flex items-center gap-3">
              <span class="text-lg">{{ cat.icon }}</span>
              <div>
                <p class="text-white text-sm font-medium">{{ cat.name }}</p>
                <span
                  :class="[
                    'text-xs px-2 py-0.5 rounded-full',
                    cat.type === 'income' ? 'bg-emerald-900 text-emerald-400' : 'bg-red-900 text-red-400',
                  ]"
                >{{ cat.type }}</span>
              </div>
            </div>
            <button
              @click="deleteCategory(cat.id)"
              class="text-zinc-600 hover:text-red-400 transition text-sm"
            >✕</button>
          </div>
        </div>
      </div>

      <!-- Add category form -->
      <div class="bg-zinc-900 rounded-2xl p-5 space-y-3">
        <p class="text-zinc-400 text-xs uppercase tracking-widest">Add Category</p>

        <input
          v-model="newCat.name"
          type="text"
          placeholder="Category name"
          class="w-full bg-zinc-800 text-white placeholder-zinc-500 rounded-lg px-4 py-3 text-sm outline-none focus:ring-1 focus:ring-zinc-600"
        />

        <input
          v-model="newCat.icon"
          type="text"
          placeholder="Icon (e.g. 🏠)"
          class="w-full bg-zinc-800 text-white placeholder-zinc-500 rounded-lg px-4 py-3 text-sm outline-none focus:ring-1 focus:ring-zinc-600"
        />

        <div class="flex gap-2">
          <button
            v-for="t in (['expense', 'income'] as const)"
            :key="t"
            @click="newCat.type = t"
            :class="[
              'flex-1 py-2 rounded-lg text-sm font-medium transition',
              newCat.type === t
                ? t === 'income' ? 'bg-emerald-500 text-white' : 'bg-red-500 text-white'
                : 'bg-zinc-800 text-zinc-400',
            ]"
          >{{ t === 'income' ? 'Income' : 'Expense' }}</button>
        </div>

        <p v-if="catError" class="text-red-400 text-xs">{{ catError }}</p>

        <button
          @click="addCategory"
          :disabled="catSubmitting"
          class="w-full bg-white text-black font-medium py-3 rounded-lg text-sm hover:bg-zinc-200 transition disabled:opacity-50"
        >{{ catSubmitting ? 'Adding…' : 'Add Category' }}</button>
      </div>
    </div>

    <!-- Sharing tab -->
    <div v-if="activeTab === 'sharing'" class="px-4 pb-12 space-y-6">
      <!-- Grants list -->
      <div>
        <p class="text-zinc-500 text-xs uppercase tracking-widest mb-2">Access Granted To</p>
        <div v-if="grants.length === 0" class="text-zinc-600 text-sm py-4">No one has access.</div>
        <div v-else class="space-y-2">
          <div
            v-for="grant in grants"
            :key="grant.id"
            class="bg-zinc-900 rounded-xl px-4 py-3 flex items-center justify-between"
          >
            <div>
              <p class="text-white text-sm font-medium">{{ grant.viewerEmail }}</p>
              <p class="text-zinc-500 text-xs">{{ formatGrantDate(grant.grantedAt) }}</p>
            </div>
            <button
              @click="revokeGrant(grant.id)"
              class="text-zinc-600 hover:text-red-400 transition text-sm"
            >Revoke</button>
          </div>
        </div>
      </div>

      <!-- Add grant form -->
      <div class="bg-zinc-900 rounded-2xl p-5 space-y-3">
        <p class="text-zinc-400 text-xs uppercase tracking-widest">Grant Access</p>

        <input
          v-model="shareEmail"
          type="email"
          placeholder="Email address"
          class="w-full bg-zinc-800 text-white placeholder-zinc-500 rounded-lg px-4 py-3 text-sm outline-none focus:ring-1 focus:ring-zinc-600"
        />

        <p v-if="shareError" class="text-red-400 text-xs">{{ shareError }}</p>

        <button
          @click="grantAccess"
          :disabled="shareSubmitting"
          class="w-full bg-white text-black font-medium py-3 rounded-lg text-sm hover:bg-zinc-200 transition disabled:opacity-50"
        >{{ shareSubmitting ? 'Granting…' : 'Grant Access' }}</button>
      </div>

      <!-- Share link -->
      <div v-if="grants.length > 0" class="bg-zinc-900 rounded-2xl p-5">
        <p class="text-zinc-400 text-xs mb-1">Your Share Link</p>
        <p class="font-mono text-xs text-zinc-300 break-all mb-3">{{ shareUrl }}</p>
        <button
          @click="copyLink"
          class="w-full bg-zinc-800 text-white font-medium py-3 rounded-lg text-sm hover:bg-zinc-700 transition"
        >{{ copied ? 'Copied!' : '📋 Copy Link' }}</button>
      </div>
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

const { user } = useAuth()
const api = useApi()
const activeTab = ref<'categories' | 'sharing'>('categories')

const categories = ref<Category[]>([])
const catError = ref('')
const catSubmitting = ref(false)
const newCat = reactive({ name: '', icon: '', type: 'expense' as 'income' | 'expense' })

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
  if (!newCat.name.trim() || !newCat.icon.trim()) {
    catError.value = 'Name and icon are required'
    return
  }
  catSubmitting.value = true
  try {
    const uid = user.value!.uid
    const cat = await api.post<Category>(`/api/categories/${uid}`, {
      name: newCat.name.trim(),
      icon: newCat.icon.trim(),
      type: newCat.type,
    })
    categories.value.push(cat)
    newCat.name = ''
    newCat.icon = ''
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
