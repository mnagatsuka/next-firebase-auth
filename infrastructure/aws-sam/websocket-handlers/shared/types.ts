// Common types for WebSocket handlers

export interface WebSocketMessage {
  type: string;
  data: any;
  timestamp: string;
}

export interface ConnectionItem {
  connectionId: string;
  timestamp?: number;
  ttl?: number;
}

export interface BroadcastRequestBody {
  type: string;
  data: {
    post_id: string;
    comments: Array<{
      id: string;
      content: string;
      user_id: string;
      created_at: string;
      post_id: string;
    }>;
    count: number;
  };
}

export interface LambdaResponse {
  statusCode: number;
  headers?: Record<string, string>;
  body: string;
}

export interface EnvironmentConfig {
  AWS_REGION: string;
  DYNAMODB_CONNECTIONS_TABLE: string;
  WEBSOCKET_API_ENDPOINT: string;
  DYNAMODB_ENDPOINT?: string;
  LOG_LEVEL?: string;
  CORS_ORIGIN?: string;
}