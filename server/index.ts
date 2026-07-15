import express from 'express';
import cors from 'cors';
import dotenv from 'dotenv';
import { initSentry, captureException, startTransaction, finishTransaction } from './_core/sentry';
import logger from './_core/logger';
import securityHeaders from './middleware/securityHeaders';
import { apiLimiter, authLimiter } from './middleware/rateLimiter';
import { globalErrorHandler, catchAsync } from './middleware/errorHandler';

// Load environment variables
dotenv.config();

// Initialize Sentry
initSentry();

const app = express();
const PORT = process.env.PORT || 3000;

// Middleware
app.use(cors());
app.use(express.json());
app.use(securityHeaders);

// Apply rate limiters to specific routes
app.use('/api/', apiLimiter); // General API rate limiting
app.use('/auth/', authLimiter); // Authentication specific rate limiting

// Health check endpoint
app.get('/health', (req, res) => {
  res.status(200).json({ status: 'UP', timestamp: new Date().toISOString() });
});

// Example protected route (replace with actual routes)
app.get('/api/protected', catchAsync(async (req, res) => {
  const transaction = startTransaction('protected_route_access', 'http.server');
  // Simulate some work
  await new Promise(resolve => setTimeout(resolve, 100));
  logger.info('Accessing protected route');
  if (transaction) finishTransaction(transaction);
  res.status(200).json({ message: 'Access granted to protected resource!' });
}));

// Example error route
app.get('/api/error', catchAsync(async (req, res, next) => {
  throw new Error('This is a test error!');
}));

// Global error handler
app.use(globalErrorHandler);

// Start the server
app.listen(PORT, () => {
  logger.info(`Server running on port ${PORT}`);
  logger.info(`Environment: ${process.env.NODE_ENV}`);
  logger.info(`Sentry DSN: ${process.env.SENTRY_DSN ? 'Configured' : 'Not Configured'}`);
  logger.info(`Redis URL: ${process.env.REDIS_URL ? 'Configured' : 'Not Configured'}`);
});

// Handle unhandled promise rejections
process.on('unhandledRejection', (err: Error) => {
  logger.error('UNHANDLED REJECTION! 💥 Shutting down...');
  captureException(err);
  process.exit(1);
});

// Handle uncaught exceptions
process.on('uncaughtException', (err: Error) => {
  logger.error('UNCAUGHT EXCEPTION! 💥 Shutting down...');
  captureException(err);
  process.exit(1);
});
