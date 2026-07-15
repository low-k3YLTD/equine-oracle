import * as Sentry from '@sentry/node';
import { nodeProfilingIntegration } from '@sentry/profiling-node';

export function initSentry() {
  if (process.env.SENTRY_DSN) {
    Sentry.init({
      dsn: process.env.SENTRY_DSN,
      integrations: [
        // Add TracingIntegration for performance monitoring
        new Sentry.Integrations.Tracing({}),
        nodeProfilingIntegration(),
      ],
      // Performance Monitoring
      tracesSampleRate: 1.0, // Capture 100% of the transactions
      // Set sampling rate for profiling
      profilesSampleRate: 1.0,
      environment: process.env.NODE_ENV || 'development',
    });
    console.log('Sentry initialized successfully.');
  } else {
    console.warn('SENTRY_DSN not found. Sentry will not be initialized.');
  }
}

export function captureException(error: any, context?: Record<string, any>) {
  if (process.env.SENTRY_DSN) {
    Sentry.captureException(error, context);
  } else {
    console.error('Error captured (Sentry not initialized):', error, context);
  }
}

export function startTransaction(name: string, op?: string) {
  if (process.env.SENTRY_DSN) {
    return Sentry.startTransaction({ name, op });
  } else {
    return null;
  }
}

export function finishTransaction(transaction: any) {
  if (transaction) {
    transaction.finish();
  }
}
