import { defineConfig } from 'vite';

export default defineConfig({
  root: './client',
  publicDir: 'public',
  server: {
    port: 5173,
    // Use localhost (not 127.0.0.1) to match the origin in the browser
    host: 'localhost',
    proxy: {
      '/api': {
        target: 'http://127.0.0.1:5001',
        changeOrigin: true,
        secure: false,
        configure: (proxy, _options) => {
          proxy.on('error', (err, _req, _res) => {
            console.log('proxy error', err);
          });
          proxy.on('proxyReq', (proxyReq, req, _res) => {
            console.log('Sending Request to:', req.method, req.url);
          });
          proxy.on('proxyRes', (proxyRes, req, _res) => {
            console.log('Received Response from:', req.method, req.url, proxyRes.statusCode);
          });
        }
      }
    }
  }
});
