import { mergeConfig } from 'vite'
import { defineConfig } from 'vitest/config'
import { fileURLToPath, URL } from 'node:url'
import vue from '@vitejs/plugin-vue'

export default mergeConfig(
  defineConfig({
    plugins: [
        vue(),
    ],
    resolve: {
      alias: {
        '@': fileURLToPath(new URL('./src', import.meta.url)),
      }
    },
    test: {
      globals: true,
      environment: "jsdom",
      root: fileURLToPath(new URL('./test', import.meta.url)),
      server: {
        deps: {
          inline: ['vuetify']
        }
      },
        plugins: [
      vue({
      template: {
        compilerOptions: {
          isCustomElement: (tag) => {
            return tag.startsWith('v-') 
          }
        }
      }
    })
	],
  }
 })
)