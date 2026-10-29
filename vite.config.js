import { defineConfig } from 'vite';
import { resolve } from 'path';
import { ordersApiMiddleware } from './server/orders.js';

export default defineConfig({
  plugins: [
    {
      name: 'orders-api',
      configureServer(server) {
        server.middlewares.use(ordersApiMiddleware);
      },
      configurePreviewServer(server) {
        server.middlewares.use(ordersApiMiddleware);
      }
    }
  ],
  server: {
    port: 3000,
    host: '0.0.0.0',
    strictPort: false,
    allowedHosts: true
  },
  preview: {
    port: 3000,
    host: true
  },
  appType: 'mpa',
  build: {
    rollupOptions: {
      input: {
        main: resolve(import.meta.dirname, 'index.html'),
        vipNumberClub: resolve(import.meta.dirname, 'vip-number-club.html'),
        checkout: resolve(import.meta.dirname, 'checkout.html'),
      }
    }
  }
});
