# Sentry Integration Setup

This guide explains how to integrate Sentry error reporting into the frontend application.

## 📦 Installation

```bash
npm install @sentry/react
```

## 🔧 Configuration

### 1. Environment Variables

Create `.env.production` file:

```env
REACT_APP_SENTRY_DSN=https://your-sentry-dsn@sentry.io/project-id
REACT_APP_SENTRY_ENVIRONMENT=production
REACT_APP_VERSION=1.0.0
```

### 2. Initialize Sentry

Update `src/index.js` (or `src/main.jsx`):

```javascript
import React from 'react';
import ReactDOM from 'react-dom/client';
import * as Sentry from "@sentry/react";
import App from './App';
import { initErrorReporting } from './utils/errorReporter';

// Initialize Sentry
if (process.env.NODE_ENV === 'production' && process.env.REACT_APP_SENTRY_DSN) {
  Sentry.init({
    dsn: process.env.REACT_APP_SENTRY_DSN,
    environment: process.env.REACT_APP_SENTRY_ENVIRONMENT || 'production',
    release: process.env.REACT_APP_VERSION || '1.0.0',

    // Performance Monitoring
    tracesSampleRate: 0.1, // 10% of transactions

    // Session Replay
    replaysSessionSampleRate: 0.1, // 10% of sessions
    replaysOnErrorSampleRate: 1.0, // 100% of errors

    // Integrations
    integrations: [
      new Sentry.BrowserTracing(),
      new Sentry.Replay({
        maskAllText: true,
        blockAllMedia: true,
      }),
    ],

    // Filtering
    beforeSend(event, hint) {
      // Don't send errors in development
      if (process.env.NODE_ENV === 'development') {
        return null;
      }

      // Filter out specific errors
      if (event.exception) {
        const message = event.exception.values?.[0]?.value;
        if (message && message.includes('ResizeObserver loop')) {
          return null; // Ignore benign errors
        }
      }

      return event;
    },
  });

  // Initialize our custom error reporter
  initErrorReporting({
    sentryDsn: process.env.REACT_APP_SENTRY_DSN,
    environment: process.env.REACT_APP_SENTRY_ENVIRONMENT,
    release: process.env.REACT_APP_VERSION
  });
}

const root = ReactDOM.createRoot(document.getElementById('root'));
root.render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);
```

### 3. Wrap App with ErrorBoundary

Update `src/App.jsx`:

```javascript
import * as Sentry from "@sentry/react";
import ErrorBoundary from './components/common/ErrorBoundary';

function App() {
  return (
    <Sentry.ErrorBoundary fallback={ErrorBoundary} showDialog>
      {/* Your app content */}
    </Sentry.ErrorBoundary>
  );
}

export default App;
```

## 📊 Usage

The error reporter is already integrated! All errors are automatically captured via:

1. **ErrorBoundary**: Catches React rendering errors
2. **reportError()**: Manual error reporting in catch blocks
3. **Sentry.captureException()**: Direct Sentry calls

### Example

```javascript
import { reportError } from './utils/errorReporter';

try {
  // Your code
} catch (error) {
  reportError(error, {
    component: 'MyComponent',
    action: 'fetchData',
    userId: user?.id
  });
}
```

## 🎯 Features

### Automatic Error Tracking
- React component errors
- Network errors
- Unhandled promise rejections
- Global errors

### Context & Tags
- Component name
- Action performed
- User information
- Browser/Device info

### Performance Monitoring
- Page load times
- API response times
- React component render times

### Session Replay
- Watch user sessions leading to errors
- See exactly what users experienced
- Privacy-focused (text/media masked)

## 🔐 Security

- Sensitive data is automatically masked
- Personally identifiable information (PII) filtered
- Source maps uploaded securely
- Team-based access control

## 📈 Monitoring

Access your Sentry dashboard at: https://sentry.io

- Real-time error tracking
- Error frequency trends
- User impact metrics
- Release health monitoring

## 🚀 Deploy Checklist

- [ ] Create Sentry project
- [ ] Copy DSN to `.env.production`
- [ ] Upload source maps (optional)
- [ ] Test in staging environment
- [ ] Monitor first 24 hours after deploy
- [ ] Set up alerts for critical errors

## 💡 Tips

1. **Source Maps**: Upload them for readable stack traces
   ```bash
   npm install @sentry/cli
   npx sentry-cli upload-sourcemaps build
   ```

2. **Alerts**: Configure email/Slack notifications in Sentry dashboard

3. **Releases**: Tag deployments to track which version introduced bugs
   ```bash
   npx sentry-cli releases new $REACT_APP_VERSION
   ```

4. **User Feedback**: Enable user feedback widget for better bug reports

## 🔗 Resources

- [Sentry React Docs](https://docs.sentry.io/platforms/javascript/guides/react/)
- [Performance Monitoring](https://docs.sentry.io/platforms/javascript/performance/)
- [Session Replay](https://docs.sentry.io/platforms/javascript/session-replay/)
