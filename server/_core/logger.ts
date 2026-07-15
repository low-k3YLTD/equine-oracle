import pino from 'pino';

const logger = pino({
  level: process.env.LOG_LEVEL || 'info',
  transport: {
    target: process.env.NODE_ENV === 'production' ? 'pino/file' : 'pino-pretty',
    options: {
      destination: process.env.NODE_ENV === 'production' ? '/var/log/equine-oracle.log' : undefined,
      colorize: process.env.NODE_ENV !== 'production',
    },
  },
  formatters: {
    level: (label) => ({ level: label.toUpperCase() }),
  },
  timestamp: pino.stdTimeFunctions.isoTime,
});

export default logger;
