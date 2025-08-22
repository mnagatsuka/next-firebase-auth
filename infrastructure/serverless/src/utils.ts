import { ApiGatewayManagementApiClient } from '@aws-sdk/client-apigatewaymanagementapi'
import { DynamoDBClient } from '@aws-sdk/client-dynamodb'
import { DynamoDBDocumentClient } from '@aws-sdk/lib-dynamodb'
import { NodeHttpHandler } from '@smithy/node-http-handler'

export function normalizeManagementEndpoint(raw: string): string {
  if (raw.startsWith('wss://')) return raw.replace('wss://', 'https://')
  if (raw.startsWith('ws://')) return raw.replace('ws://', 'http://')
  return raw
}

export function createApiGatewayManagementClient(options?: { timeoutMs?: number }) {
  const timeoutMs = options?.timeoutMs ?? 2000
  const raw = process.env.WEBSOCKET_API_ENDPOINT || 'http://localhost:3001'
  const endpoint = normalizeManagementEndpoint(raw)

  const requestHandler = new NodeHttpHandler({
    connectionTimeout: timeoutMs,
    requestTimeout: timeoutMs,
  })

  const client = new ApiGatewayManagementApiClient({
    endpoint,
    region: process.env.AWS_REGION || 'ap-northeast-1',
    requestHandler,
    ...(process.env.IS_OFFLINE && {
      credentials: {
        accessKeyId: 'test',
        secretAccessKey: 'test',
      },
    }),
  })

  return client
}

export function createDynamoDbDocClient(options?: { timeoutMs?: number }) {
  const timeoutMs = options?.timeoutMs ?? 2000
  const requestHandler = new NodeHttpHandler({
    connectionTimeout: timeoutMs,
    requestTimeout: timeoutMs,
  })

  const client = new DynamoDBClient({
    region: process.env.AWS_REGION || 'ap-northeast-1',
    requestHandler,
    ...(process.env.IS_OFFLINE && {
      endpoint: process.env.AWS_ENDPOINT_URL || 'http://localhost:4566',
      credentials: {
        accessKeyId: 'test',
        secretAccessKey: 'test',
      },
    }),
  })

  return DynamoDBDocumentClient.from(client)
}
