/**
 * Error Reporting Utility
 *
 * PRODUCTION-READY: Centralized error handling and reporting
 * - Development: Logs to console
 * - Production: Can be integrated with Sentry, LogRocket, or other services
 */

const isDevelopment = process.env.NODE_ENV === 'development';

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
    // Production: Send to error reporting service
    // TODO: Integrate with Sentry, LogRocket, or custom backend endpoint

    // Example Sentry integration (uncomment when configured):
    // if (window.Sentry) {
    //   window.Sentry.captureException(error, { extra: context });
    // }

    // Example custom backend logging:
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

export default {
  reportError,
  reportWarning,
  reportInfo,
  withErrorHandling
};
