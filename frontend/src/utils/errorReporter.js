/**
 * Error Reporting Utility
 *
 * PRODUCTION-READY: Centralized error handling and reporting
 * - Development: Logs to console
 * - Production: Integrates with Sentry, LogRocket, or custom backend
 *
 * SETUP:
 * 1. Install Sentry: npm install @sentry/react
 * 2. Set REACT_APP_SENTRY_DSN in .env.production
 * 3. Optional: Set REACT_APP_LOGROCKET_ID for LogRocket
 */

const isDevelopment = process.env.NODE_ENV === 'development';

// Sentry integration check
const hasSentry = typeof window !== 'undefined' && window.Sentry;

// LogRocket integration check
const hasLogRocket = typeof window !== 'undefined' && window.LogRocket;

/**
 * Report an error to the appropriate service
 *
 * @param {Error|string} error - Error object or message
 * @param {Object} context - Additional context (component name, user action, etc.)
 */
export const reportError = (error, context = {}) => {
  const errorInfo = {
    message: error?.message || error,
    stack: error?.stack,
    timestamp: new Date().toISOString(),
    userAgent: navigator.userAgent,
    url: window.location.href,
    ...context
  };

  if (isDevelopment) {
    // Development: Log to console with full details
    console.error('🔴 Error:', errorInfo);
  } else {
    // Production: Send to error reporting service(s)

    // 1. Sentry integration
    if (hasSentry) {
      try {
        window.Sentry.captureException(error, {
          extra: context,
          tags: {
            component: context.component,
            action: context.action
          },
          level: 'error'
        });
      } catch (e) {
        // Fail silently if Sentry fails
      }
    }

    // 2. LogRocket integration
    if (hasLogRocket) {
      try {
        window.LogRocket.captureException(error, {
          extra: context
        });
      } catch (e) {
        // Fail silently if LogRocket fails
      }
    }

    // 3. Custom backend logging (fallback)
    if (!hasSentry && !hasLogRocket) {
      try {
        fetch('/api/v1/logs/frontend-error', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(errorInfo)
        }).catch(() => {
          // Silently fail if logging endpoint is unavailable
        });
      } catch (e) {
        // Prevent error reporting from breaking the app
      }
    }
  }
};

/**
 * Report a warning (non-critical issue)
 *
 * @param {string} message - Warning message
 * @param {Object} context - Additional context
 */
export const reportWarning = (message, context = {}) => {
  const warningInfo = {
    level: 'warning',
    message,
    timestamp: new Date().toISOString(),
    ...context
  };

  if (isDevelopment) {
    console.warn('⚠️ Warning:', warningInfo);
  } else {
    // Production: Could send warnings to analytics or monitoring
    // For now, we only log errors in production to reduce noise
  }
};

/**
 * Report an info message (for debugging)
 *
 * @param {string} message - Info message
 * @param {Object} data - Additional data
 */
export const reportInfo = (message, data = {}) => {
  if (isDevelopment) {
    console.info('ℹ️ Info:', message, data);
  }
  // Production: Don't log info messages
};

/**
 * Wrapper for async operations with error handling
 *
 * @param {Function} asyncFn - Async function to execute
 * @param {Object} context - Context for error reporting
 * @returns {Promise} Result or error
 */
export const withErrorHandling = async (asyncFn, context = {}) => {
  try {
    return await asyncFn();
  } catch (error) {
    reportError(error, context);
    throw error; // Re-throw to allow caller to handle
  }
};

/**
 * Initialize error reporting services
 *
 * Call this in index.js/main.js before rendering the app
 *
 * @param {Object} config - Configuration object
 * @param {string} config.sentryDsn - Sentry DSN
 * @param {string} config.logRocketId - LogRocket App ID
 * @param {string} config.environment - Environment (production, staging, etc.)
 * @param {string} config.release - App version/release
 */
export const initErrorReporting = (config = {}) => {
  if (isDevelopment) {
    console.info('📊 Error reporting: Development mode (console only)');
    return;
  }

  // Initialize Sentry
  if (config.sentryDsn && typeof window !== 'undefined') {
    try {
      // Note: Sentry must be initialized in index.js with @sentry/react
      // This is just a configuration helper
      console.info('📊 Sentry error reporting enabled');
    } catch (error) {
      console.warn('Failed to configure Sentry:', error);
    }
  }

  // Initialize LogRocket
  if (config.logRocketId && typeof window !== 'undefined') {
    try {
      // Note: LogRocket must be initialized separately
      console.info('📊 LogRocket session recording enabled');
    } catch (error) {
      console.warn('Failed to configure LogRocket:', error);
    }
  }

  // Integrate LogRocket with Sentry
  if (hasSentry && hasLogRocket) {
    try {
      window.LogRocket.getSessionURL((sessionURL) => {
        window.Sentry.configureScope((scope) => {
          scope.setExtra('sessionURL', sessionURL);
        });
      });
      console.info('📊 LogRocket + Sentry integration enabled');
    } catch (error) {
      console.warn('Failed to integrate LogRocket with Sentry:', error);
    }
  }
};

export default {
  reportError,
  reportWarning,
  reportInfo,
  withErrorHandling,
  initErrorReporting
};
