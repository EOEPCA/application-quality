import { fileURLToPath, URL } from 'node:url'

import { defineConfig, searchForWorkspaceRoot } from 'vite'
import vue from '@vitejs/plugin-vue'

// https://vite.dev/config/
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
    host: process.env.VITE_API_HOST || 'localhost',
    port: parseInt(process.env.VITE_API_PORT) || 3000,
    fs: {
      allow: [
        searchForWorkspaceRoot(process.cwd()),
        // Custom rules
      ],
    },
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
        target: 'http://eoepca-plus-testing:30002',
        changeOrigin: true,
        secure: false,
        ws: true,
        configure: (proxy, _options) => {
          proxy.on('error', (err, _req, _res) => {
            console.log('proxy error', err);
          });
          proxy.on('proxyReq', (proxyReq, req, _res) => {
            // Add custom headers here if needed
            proxyReq.setHeader('Access-Control-Allow-Origin', '*');
            console.log('Sending Login Request:', req.method, req.url);
          });
          proxy.on('proxyRes', (proxyRes, req, _res) => {
            console.log('Received Login Response:', proxyRes.statusCode, req.url);
          });
        }
      },
      '/oidc': {
        target: 'http://eoepca-plus-testing:30002',
        changeOrigin: true,
        secure: false,
        ws: true,
        configure: (proxy, _options) => {
          proxy.on('error', (err, _req, _res) => {
            console.log('proxy error', err);
          });
          proxy.on('proxyReq', (proxyReq, req, _res) => {
            proxyReq.setHeader('Access-Control-Allow-Origin', '*');
            console.log('Sending Login Request:', req.method, req.url);
          });
          proxy.on('proxyRes', (proxyRes, req, _res) => {
            console.log('Received Login Response:', proxyRes.statusCode, req.url);
          });
        }
      },
      '/api': {
        target: 'http://eoepca-plus-testing:30002',
        changeOrigin: true,
        secure: false,
        ws: true,
        configure: (proxy, _options) => {
          proxy.on('error', (err, _req, _res) => {
            console.log('proxy error', err);
          });
          proxy.on('proxyReq', (proxyReq, req, _res) => {
            proxyReq.setHeader('Access-Control-Allow-Origin', '*');
            console.log('Sending API Request:', req.method, req.url);
          });
          proxy.on('proxyRes', (proxyRes, req, _res) => {
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
