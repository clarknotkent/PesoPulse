<template>
  <div>
    <!-- Month nav -->
    <div class="flex items-center justify-between mb-3">
      <button @click="shiftMonth(-1)" class="press w-10 h-10 rounded-lg bg-[var(--bg-surface)] text-[var(--text-muted)] flex items-center justify-center" aria-label="Prev month">
        <Icon name="chevron-left" :size="18" />
      </button>
      <button @click="jumpToday" class="press text-sm font-medium text-[var(--text)] px-3 py-1.5 rounded-lg tabular-nums" :title="`Jump to ${todayLabel}`">{{ monthLabel }}</button>
      <button @click="shiftMonth(1)" class="press w-10 h-10 rounded-lg bg-[var(--bg-surface)] text-[var(--text-muted)] flex items-center justify-center" aria-label="Next month">
        <Icon name="chevron-right" :size="18" />
      </button>
    </div>

    <!-- Weekday header -->
    <div class="grid grid-cols-7 gap-1 mb-1">
      <p
        v-for="d in weekdayLabels"
        :key="d"
        class="text-[10px] uppercase tracking-wider text-[var(--text-subtle)] text-center py-1"
      >{{ d }}</p>
    </div>

    <!-- Grid -->
    <div class="grid grid-cols-7 gap-1">
      <button
        v-for="(cell, idx) in cells"
        :key="idx"
        @click="selectCell(cell)"
        :disabled="!cell.inMonth"
        :class="[
          'day-cell press relative aspect-square rounded-xl flex flex-col items-center justify-start pt-1.5 transition-colors',
          cell.inMonth
            ? (isSelected(cell) ? 'bg-[var(--text)] text-[var(--bg)]' : 'bg-[var(--bg-surface)] text-[var(--text)]')
            : 'bg-transparent text-[var(--text-subtle)] opacity-40 cursor-default',
          cell.inMonth && isToday(cell) && !isSelected(cell) ? 'ring-1 ring-emerald-500' : '',
        ]"
      >
        <span
          class="text-xs tabular-nums leading-none"
          :class="cell.inMonth && isToday(cell) && !isSelected(cell) ? 'text-[var(--c-income)] font-semibold' : ''"
        >{{ cell.day }}</span>

        <span
          v-if="cell.inMonth && cell.net !== 0"
          class="dot mt-1.5 rounded-full"
          :class="[dotColor(cell, isSelected(cell)), { ready: animateReady }]"
          :style="{ width: `${dotSize(cell)}px`, height: `${dotSize(cell)}px` }"
        ></span>
        <span
          v-else-if="cell.inMonth && cell.txnCount > 0"
          class="dot mt-1.5 w-1.5 h-1.5 rounded-full bg-[var(--text-subtle)]"
          :class="{ ready: animateReady }"
        ></span>
      </button>
    </div>

    <!-- Legend / hint -->
    <div class="flex items-center justify-center gap-3 mt-3 text-[10px] text-[var(--text-subtle)]">
      <span class="flex items-center gap-1"><span class="w-2 h-2 rounded-full bg-emerald-500"></span> income net</span>
      <span class="flex items-center gap-1"><span class="w-2 h-2 rounded-full bg-red-500"></span> expense net</span>
      <span class="flex items-center gap-1"><span class="w-2 h-2 rounded-full bg-[var(--text-subtle)]"></span> flat</span>
    </div>
  </div>
</template>

<script setup lang="ts">
interface DayData {
  date: string
  income: number
  expense: number
  net: number
  txnCount: number
}

interface Cell {
  day: number
  date: string
  inMonth: boolean
  income: number
  expense: number
  net: number
  txnCount: number
}

const props = defineProps<{
  anchor: string
  dayData: DayData[]
  selectedDate: string | null
}>()

const emit = defineEmits<{
  'update:anchor': [iso: string]
  'select-date': [iso: string]
}>()

const weekdayLabels = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']

function pad(n: number): string {
  return String(n).padStart(2, '0')
}

function isoFromDate(d: Date): string {
  return `${d.getFullYear()}-${pad(d.getMonth() + 1)}-${pad(d.getDate())}`
}

function todayIso(): string {
  return isoFromDate(new Date())
}

const today = todayIso()

const todayLabel = computed(() => {
  return new Date().toLocaleDateString('en-PH', { month: 'long', day: 'numeric', year: 'numeric' })
})

const monthLabel = computed(() => {
  const [y, m] = props.anchor.split('-').map(Number)
  const d = new Date(y, m - 1, 1)
  return d.toLocaleDateString('en-PH', { month: 'long', year: 'numeric' })
})

const dayMap = computed(() => {
  const m = new Map<string, DayData>()
  for (const d of props.dayData) m.set(d.date, d)
  return m
})

const cells = computed<Cell[]>(() => {
  const [y, m] = props.anchor.split('-').map(Number)
  const firstOfMonth = new Date(y, m - 1, 1)
  const offset = firstOfMonth.getDay() === 0 ? 6 : firstOfMonth.getDay() - 1
  const start = new Date(firstOfMonth)
  start.setDate(firstOfMonth.getDate() - offset)

  const out: Cell[] = []
  const cur = new Date(start)
  for (let i = 0; i < 42; i++) {
    const iso = isoFromDate(cur)
    const inMonth = cur.getMonth() === m - 1
    const d = dayMap.value.get(iso)
    out.push({
      day: cur.getDate(),
      date: iso,
      inMonth,
      income: d?.income ?? 0,
      expense: d?.expense ?? 0,
      net: d?.net ?? 0,
      txnCount: d?.txnCount ?? 0,
    })
    cur.setDate(cur.getDate() + 1)
  }
  return out
})

const maxAbsNet = computed(() => {
  let max = 0
  for (const c of cells.value) {
    if (!c.inMonth) continue
    const a = Math.abs(c.net)
    if (a > max) max = a
  }
  return max
})

function dotSize(cell: Cell): number {
  if (maxAbsNet.value <= 0) return 6
  const ratio = Math.abs(cell.net) / maxAbsNet.value
  const min = 6
  const max = 16
  return Math.round(min + (max - min) * Math.min(1, Math.max(0.15, ratio)))
}

function dotColor(cell: Cell, selected: boolean): string {
  if (selected) return cell.net >= 0 ? 'bg-emerald-700' : 'bg-red-700'
  if (cell.net > 0) return 'bg-emerald-500'
  if (cell.net < 0) return 'bg-red-500'
  return 'bg-[var(--text-subtle)]'
}

function isToday(cell: Cell): boolean {
  return cell.date === today
}

function isSelected(cell: Cell): boolean {
  return props.selectedDate === cell.date
}

function selectCell(cell: Cell) {
  if (!cell.inMonth) return
  emit('select-date', cell.date)
}

function shiftMonth(delta: number) {
  const [y, m] = props.anchor.split('-').map(Number)
  const d = new Date(y, m - 1 + delta, 1)
  emit('update:anchor', `${d.getFullYear()}-${pad(d.getMonth() + 1)}-01`)
}

function jumpToday() {
  const d = new Date()
  emit('update:anchor', `${d.getFullYear()}-${pad(d.getMonth() + 1)}-01`)
  emit('select-date', isoFromDate(d))
}

const animateReady = ref(false)
let resetTimer: ReturnType<typeof setTimeout> | null = null

function armAnimate() {
  animateReady.value = false
  if (resetTimer) clearTimeout(resetTimer)
  resetTimer = setTimeout(() => {
    requestAnimationFrame(() => {
      animateReady.value = true
    })
  }, 20)
}

watch(() => props.anchor, armAnimate, { immediate: true })
</script>

<style scoped>
.day-cell {
  transition:
    background-color 200ms var(--ease-out),
    color 180ms var(--ease-out),
    transform 160ms var(--ease-out);
}
.dot {
  transition: none;
}
.dot.ready {
  transition:
    background-color 240ms var(--ease-out),
    width 240ms var(--ease-out),
    height 240ms var(--ease-out);
}
</style>
