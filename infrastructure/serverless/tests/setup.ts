import { beforeEach, vi } from 'vitest';

// Mock environment variables
beforeEach(() => {
  vi.stubEnv('AWS_REGION', 'ap-northeast-1');
  vi.stubEnv('DYNAMODB_CONNECTIONS_TABLE', 'test-connections');
  vi.stubEnv('WEBSOCKET_API_ENDPOINT', 'http://localhost:3001');
  vi.stubEnv('CORS_ORIGIN', 'http://localhost:3000');
  vi.stubEnv('IS_OFFLINE', 'true');
});
