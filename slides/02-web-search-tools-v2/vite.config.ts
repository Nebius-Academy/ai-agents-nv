import { defineConfig } from 'vite'

// Local file: theme lives under node_modules, which Vite ignores by default —
// without this, edits to slidev-theme-nebius-agents never hot-reload.
export default defineConfig({
  server: {
    watch: {
      ignored: [
        '**/node_modules/**',
        '!**/node_modules/slidev-theme-nebius-agents/**',
        '!**/node_modules/.pnpm/slidev-theme-nebius-agents@*/**',
      ],
    },
  },
})
