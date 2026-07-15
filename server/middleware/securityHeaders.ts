import { Request, Response, NextFunction } from 'express';
import helmet from 'helmet';

const securityHeaders = helmet({
  contentSecurityPolicy: {
    directives: {
      defaultSrc: ["'self'"],
      scriptSrc: ["'self'", "'unsafe-inline'", "'unsafe-eval'"],
      styleSrc: ["'self'", "'unsafe-inline'"],
      imgSrc: ["'self'", "data:", "https://*.githubusercontent.com"],
      connectSrc: ["'self'", "https://*.sentry.io"],
      frameSrc: ["'self'"],
    },
  },
  crossOriginEmbedderPolicy: { policy: 'require-corp' },
  crossOriginOpenerPolicy: { policy: 'same-origin' },
  crossOriginResourcePolicy: { policy: 'same-origin' },
  originAgentCluster: true,
  referrerPolicy: { policy: 'no-referrer' },
  strictTransportSecurity: {
    maxAge: 31536000,
    includeSubDomains: true,
    preload: true,
  },
  xContentTypeOptions: true,
  xDnsPrefetchControl: { allow: false },
  xDownloadOptions: true,
  xFrameOptions: { action: 'deny' },
  xPermittedCrossDomainPolicies: { permittedPolicies: 'none' },
  xPoweredBy: false,
  xXssProtection: true,
});

export default securityHeaders;
