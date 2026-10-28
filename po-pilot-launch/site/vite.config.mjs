import { defineConfig } from 'vite'
import { fileURLToPath, URL } from 'node:url'

export default defineConfig({
  build: {
    rollupOptions: {
      input: {
        main: fileURLToPath(new URL('./index.html', import.meta.url)),
        alternative: fileURLToPath(new URL('./stocky-alternative/index.html', import.meta.url)),
        guide: fileURLToPath(new URL('./stocky-export-guide/index.html', import.meta.url)),
      },
    },
  },
})
