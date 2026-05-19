<template>
  <component
    :is="resolved"
    v-if="resolved"
    :size="size"
    :stroke-width="strokeWidth"
    :class="['shrink-0', $attrs.class as string]"
    :aria-hidden="ariaHidden"
  />
</template>

<script setup lang="ts">
import {
  Home,
  BarChart3,
  Plus,
  Target,
  Settings,
  Search,
  SlidersHorizontal,
  Pencil,
  X,
  Check,
  ChevronLeft,
  ChevronRight,
  ChevronDown,
  Calendar,
  List,
  Trash2,
  Bell,
  RotateCcw,
  Wallet,
  TrendingUp,
  TrendingDown,
  Plus as PlusIcon,
  Minus,
  LogOut,
  ArrowRight,
  ArrowLeft,
  AlertTriangle,
  Sparkles,
  PiggyBank,
  Receipt,
  ScanLine,
  Sun,
  Moon,
  Monitor,
  Tag,
  Share2,
  Eye,
  EyeOff,
  Loader,
  CircleDot,
  Mail,
  Lock,
} from 'lucide-vue-next'

defineOptions({ inheritAttrs: false })

const props = withDefaults(
  defineProps<{
    name: string
    size?: number | string
    strokeWidth?: number
    ariaHidden?: boolean
  }>(),
  {
    size: 18,
    strokeWidth: 2,
    ariaHidden: true,
  },
)

const map: Record<string, any> = {
  'home': Home,
  'stats': BarChart3,
  'plus': Plus,
  'target': Target,
  'settings': Settings,
  'search': Search,
  'sliders': SlidersHorizontal,
  'pencil': Pencil,
  'edit': Pencil,
  'close': X,
  'x': X,
  'check': Check,
  'chevron-left': ChevronLeft,
  'chevron-right': ChevronRight,
  'chevron-down': ChevronDown,
  'calendar': Calendar,
  'list': List,
  'trash': Trash2,
  'bell': Bell,
  'recurring': RotateCcw,
  'wallet': Wallet,
  'trend-up': TrendingUp,
  'trend-down': TrendingDown,
  'plus-icon': PlusIcon,
  'minus': Minus,
  'logout': LogOut,
  'arrow-right': ArrowRight,
  'arrow-left': ArrowLeft,
  'warning': AlertTriangle,
  'sparkles': Sparkles,
  'piggy': PiggyBank,
  'receipt': Receipt,
  'scan': ScanLine,
  'sun': Sun,
  'moon': Moon,
  'monitor': Monitor,
  'tag': Tag,
  'share': Share2,
  'eye': Eye,
  'eye-off': EyeOff,
  'loader': Loader,
  'dot': CircleDot,
  'mail': Mail,
  'lock': Lock,
}

const resolved = computed(() => map[props.name] ?? null)
</script>
