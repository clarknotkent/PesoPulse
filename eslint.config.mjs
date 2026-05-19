import withNuxt from './.nuxt/eslint.config.mjs'

export default withNuxt({
  rules: {
    // ── Bugs ─────────────────────────────────────────────────────────────
    'no-console': ['warn', { allow: ['warn', 'error'] }],
    'no-debugger': 'error',
    'no-unused-vars': 'off',
    '@typescript-eslint/no-unused-vars': ['error', {
      argsIgnorePattern: '^_',
      varsIgnorePattern: '^_',
      caughtErrorsIgnorePattern: '^_',
    }],
    '@typescript-eslint/no-explicit-any': 'warn',
    'prefer-const': 'error',
    'no-var': 'error',
    'eqeqeq': ['error', 'always', { null: 'ignore' }],

    // ── Vue ──────────────────────────────────────────────────────────────
    'vue/multi-word-component-names': 'off',
    'vue/no-multiple-template-root': 'off',
    'vue/html-self-closing': ['warn', {
      html: { void: 'always', normal: 'always', component: 'always' },
    }],
    'vue/component-name-in-template-casing': ['error', 'PascalCase', {
      registeredComponentsOnly: false,
    }],
    'vue/define-macros-order': ['warn', {
      order: ['defineOptions', 'defineProps', 'defineEmits', 'defineSlots'],
    }],
    'vue/no-unused-refs': 'warn',
    'vue/no-useless-v-bind': 'warn',
    'vue/prefer-true-attribute-shorthand': 'warn',

    // ── Stylistic ────────────────────────────────────────────────────────
    '@stylistic/indent': ['error', 2],
    '@stylistic/quotes': ['error', 'single', { avoidEscape: true, allowTemplateLiterals: 'always' }],
    '@stylistic/semi': ['error', 'never'],
    '@stylistic/comma-dangle': ['error', 'always-multiline'],
    '@stylistic/object-curly-spacing': ['error', 'always'],
    '@stylistic/arrow-parens': ['error', 'always'],
    '@stylistic/space-before-function-paren': ['error', {
      anonymous: 'always', named: 'never', asyncArrow: 'always',
    }],
    '@stylistic/no-multiple-empty-lines': ['error', { max: 1, maxBOF: 0, maxEOF: 1 }],
    '@stylistic/no-trailing-spaces': 'error',
    '@stylistic/eol-last': ['error', 'always'],

    // ── Imports ──────────────────────────────────────────────────────────
    'import/order': 'off',
    'sort-imports': 'off',
  },
  ignores: [
    'api/**',
    '.firebase/**',
    'firebase-hosting-stub/**',
    '.output/**',
    '.nuxt/**',
    'node_modules/**',
    'dist/**',
    'public/**',
  ],
})
