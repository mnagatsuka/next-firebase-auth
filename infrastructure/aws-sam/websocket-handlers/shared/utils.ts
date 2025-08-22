// Shared utilities for WebSocket handlers

import { LambdaResponse, EnvironmentConfig } from './types';

export const createResponse = (
  statusCode: number,
  body: any,
  headers: Record<string, string> = {}
): LambdaResponse => {
  return {
    statusCode,
    headers: {
      'Content-Type': 'application/json',
      ...headers,
    },
    body: JSON.stringify(body),
  };
};

export const createCorsResponse = (
  statusCode: number,
  body: any,
  corsOrigin?: string
): LambdaResponse => {
  return createResponse(statusCode, body, {
    'Access-Control-Allow-Origin': corsOrigin || '*',
    'Access-Control-Allow-Headers': 'Content-Type,Authorization',
    'Access-Control-Allow-Methods': 'GET,POST,PUT,DELETE,OPTIONS',
  });
};

export const createErrorResponse = (
  statusCode: number,
  message: string,
  error?: string,
  corsOrigin?: string
): LambdaResponse => {
  return createCorsResponse(
    statusCode,
    {
      message,
      ...(error && { error }),
    },
    corsOrigin
  );
};

export const validateEnvironment = (): EnvironmentConfig => {
  const config: EnvironmentConfig = {
    AWS_REGION: process.env.AWS_REGION || 'ap-northeast-1',
    DYNAMODB_CONNECTIONS_TABLE: process.env.DYNAMODB_CONNECTIONS_TABLE || '',
    WEBSOCKET_API_ENDPOINT: process.env.WEBSOCKET_API_ENDPOINT || '',
    DYNAMODB_ENDPOINT: process.env.DYNAMODB_ENDPOINT,
    LOG_LEVEL: process.env.LOG_LEVEL || 'INFO',
    CORS_ORIGIN: process.env.CORS_ORIGIN,
  };

  if (!config.DYNAMODB_CONNECTIONS_TABLE) {
    throw new Error('DYNAMODB_CONNECTIONS_TABLE environment variable is required');
  }

  if (!config.WEBSOCKET_API_ENDPOINT) {
    throw new Error('WEBSOCKET_API_ENDPOINT environment variable is required');
  }

  return config;
};

export const logger = {
  debug: (message: string, ...args: any[]) => {
    if (process.env.LOG_LEVEL === 'DEBUG') {
      console.log(`[DEBUG] ${message}`, ...args);
    }
  },
  info: (message: string, ...args: any[]) => {
    console.log(`[INFO] ${message}`, ...args);
  },
  warn: (message: string, ...args: any[]) => {
    console.warn(`[WARN] ${message}`, ...args);
  },
  error: (message: string, ...args: any[]) => {
    console.error(`[ERROR] ${message}`, ...args);
  },
};

export const encodeMessage = (message: any): Uint8Array => {
  return new TextEncoder().encode(JSON.stringify(message));
};

export const createTtl = (hoursFromNow: number = 24): number => {
  return Math.floor(Date.now() / 1000) + (hoursFromNow * 3600);
};
