// Shared AWS clients for WebSocket handlers

import { DynamoDBClient } from '@aws-sdk/client-dynamodb';
import { DynamoDBDocumentClient } from '@aws-sdk/lib-dynamodb';
import { ApiGatewayManagementApiClient } from '@aws-sdk/client-apigatewaymanagementapi';

// Initialize DynamoDB client
const ddbClient = new DynamoDBClient({
  region: process.env.AWS_REGION,
  endpoint: process.env.DYNAMODB_ENDPOINT || undefined,
});

export const dynamoClient = DynamoDBDocumentClient.from(ddbClient);

// Initialize API Gateway Management client
export const apiGatewayClient = new ApiGatewayManagementApiClient({
  endpoint: process.env.WEBSOCKET_API_ENDPOINT,
});

// Client factory for testing or custom configurations
export const createDynamoClient = (config?: { endpoint?: string; region?: string }) => {
  const client = new DynamoDBClient({
    region: config?.region || process.env.AWS_REGION,
    endpoint: config?.endpoint || process.env.DYNAMODB_ENDPOINT || undefined,
  });
  return DynamoDBDocumentClient.from(client);
};

export const createApiGatewayClient = (endpoint?: string) => {
  return new ApiGatewayManagementApiClient({
    endpoint: endpoint || process.env.WEBSOCKET_API_ENDPOINT,
  });
};