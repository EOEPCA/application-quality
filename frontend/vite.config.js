import { fileURLToPath, URL } from 'node:url'
import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

// Doc: https://vite.dev/config/
export default defineConfig({
  plugins: [
    vue(),
  ],
  resolve: {
    alias: {
      '@': fileURLToPath(new URL('./src', import.meta.url)),
    }
  },
  server: {
    host: 'localhost',
    port: 3000,
    cors: {
      origin: '*', // Be careful with this in production
      methods: ['GET', 'POST', 'PUT', 'DELETE', 'PATCH', 'OPTIONS'],
      allowedHeaders: ['Content-Type', 'Authorization', 'X-Requested-With'],
      exposedHeaders: ['Content-Range', 'X-Content-Range'],
      credentials: true,
      maxAge: 3600
    },
    proxy: {
      '/login': {
        //target: 'http://eoepca-plus-testing:30002',
        target: 'http://application-quality-2.eoepca-plus-testing',
        changeOrigin: true,
        secure: false,
        ws: true,
        configure: (proxy) => {
          proxy.on('error', (err) => {
            console.log('proxy error', err);
          });
          proxy.on('proxyReq', (proxyReq, req) => {
            proxyReq.setHeader('Access-Control-Allow-Origin', '*');
            console.log('Sending Login Request:', req.method, req.url);
          });
          proxy.on('proxyRes', (proxyRes, req) => {
            console.log('Received Login Response:', proxyRes.statusCode, req.url);
          });
        }
      },
      '/oidc': {
        //target: 'http://eoepca-plus-testing:30002',
        target: 'http://application-quality-2.eoepca-plus-testing',
        changeOrigin: true,
        secure: false,
        ws: true,
        configure: (proxy) => {
          proxy.on('error', (err) => {
            console.log('proxy error', err);
          });
          proxy.on('proxyReq', (proxyReq, req) => {
            proxyReq.setHeader('Access-Control-Allow-Origin', '*');
            console.log('Sending Login Request:', req.method, req.url);
          });
          proxy.on('proxyRes', (proxyRes, req) => {
            console.log('Received OIDC Response:', proxyRes.statusCode, req.url);
          });
        }
      },
      '/api': {
        //target: 'http://eoepca-plus-testing:30002',
        target: 'http://application-quality-2.eoepca-plus-testing',
        changeOrigin: true,
        secure: false,
        ws: true,
        configure: (proxy) => {
          proxy.on('error', (err) => {
            console.log('proxy error', err);
          });
          proxy.on('proxyReq', (proxyReq, req) => {
            proxyReq.setHeader('Access-Control-Allow-Origin', '*');
            console.log('Sending API Request:', req.method, req.url);
          });
          proxy.on('proxyRes', (proxyRes, req) => {
            console.log('Received API Response:', proxyRes.statusCode, req.url);
          });
        }
      }
    },
    headers: {
      'Access-Control-Allow-Origin': '*',
      'Access-Control-Allow-Methods': 'GET,HEAD,PUT,PATCH,POST,DELETE',
      'Access-Control-Allow-Headers': 'Origin, X-Requested-With, Content-Type, Accept, Authorization',
      'Access-Control-Allow-Credentials': 'true'
    }
  }
})
