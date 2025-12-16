import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

/**
 * Vite Configuration
 *
 * Best Practices:
 * - Code splitting for vendor chunks
 * - Minification with terser for production
 * - Compression with gzip/brotli
 * - Source maps for debugging
 * - Optimized chunk sizes
 */
export default defineConfig({
  plugins: [react()],

  // Development server configuration
  server: {
    port: 3000,
    host: true, // Listen on all addresses
    strictPort: true,
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
        secure: false,
      }
    }
  },

  // Preview server configuration (for testing production builds)
  preview: {
    port: 4173,
    host: true,
  },

  // Build configuration
  build: {
    // Output directory
    outDir: 'dist',

    // Enable source maps for debugging (disable in production for security)
    sourcemap: process.env.NODE_ENV !== 'production',

    // Minification
    minify: 'terser',
    terserOptions: {
      compress: {
        drop_console: process.env.NODE_ENV === 'production',
        drop_debugger: true,
      },
    },

    // Chunk size warnings
    chunkSizeWarningLimit: 500,

    // Rollup options for code splitting
    rollupOptions: {
      output: {
        // Manual chunk splitting for better caching
        manualChunks: {
          // Vendor chunks - rarely change, better caching
          'vendor-react': ['react', 'react-dom'],
          'vendor-router': ['react-router-dom'],
          'vendor-state': ['zustand'],
          'vendor-ui': ['lucide-react', 'react-hot-toast'],
          'vendor-http': ['axios'],
        },
        // Asset file naming
        assetFileNames: (assetInfo) => {
          const info = assetInfo.name.split('.')
          const ext = info[info.length - 1]
          if (/png|jpe?g|svg|gif|tiff|bmp|ico/i.test(ext)) {
            return `assets/images/[name]-[hash][extname]`
          }
          if (/woff2?|eot|ttf|otf/i.test(ext)) {
            return `assets/fonts/[name]-[hash][extname]`
          }
          return `assets/[name]-[hash][extname]`
        },
        chunkFileNames: 'assets/js/[name]-[hash].js',
        entryFileNames: 'assets/js/[name]-[hash].js',
      },
    },

    // Target modern browsers
    target: 'es2020',

    // CSS code splitting
    cssCodeSplit: true,
  },

  // Optimization
  optimizeDeps: {
    include: ['react', 'react-dom', 'react-router-dom', 'zustand', 'axios'],
  },

  // Define global constants
  define: {
    __APP_VERSION__: JSON.stringify(process.env.npm_package_version || '1.0.0'),
  },
})
