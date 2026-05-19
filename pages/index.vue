<template>
  <div class="landing min-h-[100dvh] bg-[var(--bg)] text-[var(--text)] overflow-x-hidden">
    <!-- floating header -->
    <header class="fixed top-0 left-0 right-0 z-[var(--z-nav)] backdrop-blur bg-[var(--bg)]/80 border-b border-[var(--border)]">
      <div class="max-w-5xl mx-auto px-5 py-3 flex items-center justify-between">
        <Logo />
        <NuxtLink
          v-if="user"
          to="/dashboard"
          class="press inline-flex items-center gap-1 text-sm text-[var(--text-muted)] hover:text-[var(--text)]"
        >
          Open app <Icon
            name="arrow-right"
            :size="14"
          />
        </NuxtLink>
        <NuxtLink
          v-else
          to="/auth"
          class="press text-sm font-medium text-[var(--text)]"
        >Log in</NuxtLink>
      </div>
    </header>

    <!-- HERO -->
    <section class="px-5 pt-32 pb-20 max-w-5xl mx-auto">
      <p class="label-quiet">
        Personal peso tracker
      </p>
      <h1
        class="mt-6 font-semibold tracking-[-0.04em] leading-[0.95]"
        style="font-size: clamp(2.75rem, 9vw, 5.5rem);"
      >
        Money you<br />actually <span class="text-[var(--c-income)]">see</span>.
      </h1>
      <p class="mt-8 text-[var(--text-muted)] text-lg max-w-xl leading-relaxed">
        A private finance tracker for one. Add transactions, backdate weeks,
        watch the pesos move. No banks. No ads. No fifty dashboards you'll never open.
      </p>
      <div class="mt-10 flex items-center gap-2">
        <NuxtLink
          :to="user ? '/dashboard' : '/auth'"
          class="press inline-flex items-center gap-1.5 bg-[var(--text)] text-[var(--bg)] px-6 py-3 rounded-full font-medium text-sm"
        >
          {{ user ? 'Open dashboard' : 'Start tracking' }}
          <Icon
            name="arrow-right"
            :size="14"
          />
        </NuxtLink>
        <a
          href="#how"
          class="press text-sm text-[var(--text-muted)] hover:text-[var(--text)] px-4 py-3"
        >How it works</a>
      </div>
    </section>

    <!-- PRODUCT MOCK -->
    <section class="px-5 pb-24">
      <div class="relative mx-auto max-w-[360px]">
        <!-- ambient glow -->
        <div class="absolute -inset-10 bg-emerald-500/10 blur-3xl rounded-full pointer-events-none" />
        <div class="relative aspect-[9/17] rounded-[2.25rem] overflow-hidden border border-[var(--border)] shadow-[0_40px_80px_-30px_rgba(16,185,129,0.35)]">
          <DashboardMock />
        </div>
      </div>
    </section>

    <!-- THREE TRAITS -->
    <section
      id="how"
      class="px-5 pb-28 max-w-3xl mx-auto space-y-16"
    >
      <div class="grid grid-cols-[auto_1fr] gap-5 items-baseline">
        <span class="label tabular-nums">01</span>
        <div>
          <h3 class="text-2xl font-medium tracking-tight">
            Strict privacy.
          </h3>
          <p class="mt-2 text-[var(--text-muted)] leading-relaxed">
            Five-user cap. No public sharing. Your viewer (dad, partner) opens a private read-only link, nothing else.
          </p>
        </div>
      </div>
      <div class="grid grid-cols-[auto_1fr] gap-5 items-baseline">
        <span class="label tabular-nums">02</span>
        <div>
          <h3 class="text-2xl font-medium tracking-tight">
            Receipt scan, zero storage.
          </h3>
          <p class="mt-2 text-[var(--text-muted)] leading-relaxed">
            Snap a receipt. Gemini parses the amount and merchant. The image leaves immediately, nothing kept.
          </p>
        </div>
      </div>
      <div class="grid grid-cols-[auto_1fr] gap-5 items-baseline">
        <span class="label tabular-nums">03</span>
        <div>
          <h3 class="text-2xl font-medium tracking-tight">
            Install it.
          </h3>
          <p class="mt-2 text-[var(--text-muted)] leading-relaxed">
            A real PWA. Add to home screen on iOS or Android. Offline-ready. Push alerts when you overspend.
          </p>
        </div>
      </div>
    </section>

    <!-- closing CTA -->
    <section class="px-5 pb-24 max-w-5xl mx-auto">
      <div class="border-t border-[var(--border)] pt-16 flex flex-col sm:flex-row sm:items-end sm:justify-between gap-6">
        <div>
          <p class="label-quiet">
            Ready?
          </p>
          <p class="mt-3 text-3xl font-semibold tracking-[-0.03em] max-w-md leading-tight">
            One sign-in. Then peso clarity.
          </p>
        </div>
        <NuxtLink
          :to="user ? '/dashboard' : '/auth'"
          class="press shrink-0 inline-flex items-center gap-1.5 bg-emerald-500 text-white px-6 py-3 rounded-full font-medium text-sm"
        >
          {{ user ? 'Open dashboard' : 'Start tracking' }}
          <Icon
            name="arrow-right"
            :size="14"
          />
        </NuxtLink>
      </div>
    </section>

    <!-- FOOTER -->
    <footer class="px-5 py-10 border-t border-[var(--border)]">
      <div class="max-w-5xl mx-auto flex items-baseline justify-between">
        <Logo />
        <p class="text-[var(--text-subtle)] text-xs tabular-nums">
          Built in Manila · {{ year }}
        </p>
      </div>
    </footer>
  </div>
</template>

<script setup lang="ts">
definePageMeta({ layout: false })

const { user } = useAuth()
const year = new Date().getFullYear()
</script>

<style scoped>
.landing {
  scroll-behavior: smooth;
}
</style>
