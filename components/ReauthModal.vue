<template>
  <Teleport to="body">
    <Transition name="modal">
      <div
        v-if="open"
        class="modal-root fixed inset-0 z-[var(--z-modal)] flex items-end sm:items-center sm:justify-center"
      >
        <div
          class="modal-backdrop absolute inset-0 bg-black/60"
          @click="onCancel"
        />
        <div class="modal-panel relative w-full sm:max-w-sm bg-[var(--bg-surface)] rounded-t-3xl sm:rounded-3xl p-5 pb-safe space-y-4 max-h-[90dvh] overflow-y-auto">
          <div class="flex items-center justify-between">
            <p class="text-[var(--text)] font-medium">
              {{ reason }}
            </p>
            <button
              class="press text-[var(--text-subtle)] hover:text-[var(--text)] w-8 h-8 flex items-center justify-center -mr-2"
              aria-label="Cancel"
              @click="onCancel"
            >
              <Icon
                name="x"
                :size="16"
              />
            </button>
          </div>
          <p class="text-[var(--text-subtle)] text-xs">
            Re-enter your password to continue.
          </p>
          <input
            ref="passwordInput"
            v-model="password"
            type="password"
            autocomplete="current-password"
            placeholder="Password"
            class="field w-full bg-[var(--bg-input)] text-[var(--text)] rounded-lg px-4 py-3 text-sm"
            @keydown.enter="onSubmit"
          />
          <p
            v-if="error"
            class="text-[var(--c-expense)] text-xs"
          >
            {{ error }}
          </p>
          <div class="flex gap-2 pt-1">
            <button
              :disabled="busy"
              class="press flex-1 py-3 rounded-lg text-sm font-medium bg-[var(--bg-input)] text-[var(--text)]"
              @click="onCancel"
            >
              Cancel
            </button>
            <button
              :disabled="busy || !password"
              class="press-strong flex-1 py-3 rounded-lg text-sm font-medium bg-[var(--accent)] text-white disabled:opacity-50"
              @click="onSubmit"
            >
              {{ busy ? 'Checking...' : 'Confirm' }}
            </button>
          </div>
        </div>
      </div>
    </Transition>
  </Teleport>
</template>

<script setup lang="ts">
const { open, busy, error, reason, submit, cancel } = useReauthGate()

const password = ref('')
const passwordInput = ref<HTMLInputElement | null>(null)

watch(open, (val) => {
  if (val) {
    password.value = ''
    nextTick(() => passwordInput.value?.focus())
  }
})

async function onSubmit(): Promise<void> {
  if (!password.value || busy.value) return
  await submit(password.value)
  if (!error.value) password.value = ''
}

function onCancel(): void {
  password.value = ''
  cancel()
}
</script>
