import { APIGatewayProxyHandler, APIGatewayProxyEvent, APIGatewayProxyResult } from 'aws-lambda';
import { randomUUID } from 'crypto';
import { ScanCommand, DeleteCommand } from '@aws-sdk/lib-dynamodb'
import { createApiGatewayManagementClient, createDynamoDbDocClient } from '../utils'

// Type definitions
type BroadcastRequestBody = {
  type: string;
  version?: string;
  id?: string;
  source?: string;
  meta?: Record<string, unknown>;
  data: any;
}

interface WebSocketMessage {
  type: string;
  version: string;
  id: string;
  timestamp: string;
  source: string;
  data: any;
  meta?: Record<string, unknown>;
}

interface ConnectionItem {
  connectionId: string;
}

const dynamodb = createDynamoDbDocClient()
const apiGatewayV3 = createApiGatewayManagementClient({ timeoutMs: 2000 })

// Default WebSocket message handler
export const handler: APIGatewayProxyHandler = async (
  event: APIGatewayProxyEvent
): Promise<APIGatewayProxyResult> => {
  const connectionId = event.requestContext.connectionId;
  
  if (!connectionId) {
    console.error('Missing connectionId in request context');
    return {
      statusCode: 400,
      body: JSON.stringify({ message: 'Missing connection ID' })
    };
  }

  try {
    const message = JSON.parse(event.body || '{}');
    console.log(`Received message from ${connectionId}:`, message);
    
    // Echo back or handle specific message types
    const response: WebSocketMessage = {
      type: 'echo',
      version: '1',
      id: randomUUID(),
      timestamp: new Date().toISOString(),
      source: 'backend',
      data: { message: 'Message received' }
    };

    await apiGatewayV3.send(new (await import('@aws-sdk/client-apigatewaymanagementapi')).PostToConnectionCommand({
      ConnectionId: connectionId,
      Data: Buffer.from(JSON.stringify(response))
    }))

    return {
      statusCode: 200,
      body: JSON.stringify({ message: 'Message processed' })
    };
  } catch (error) {
    console.error('Message handling error:', error);
    return {
      statusCode: 500,
      body: JSON.stringify({ 
        message: 'Failed to process message',
        error: error instanceof Error ? error.message : 'Unknown error'
      })
    };
  }
};

// HTTP endpoint for broadcasting from FastAPI
export const broadcastToAll: APIGatewayProxyHandler = async (
  event: APIGatewayProxyEvent
): Promise<APIGatewayProxyResult> => {
  const tableName = process.env.DYNAMODB_CONNECTIONS_TABLE;
  
  if (!tableName) {
    console.error('Missing DYNAMODB_CONNECTIONS_TABLE environment variable');
    return {
      statusCode: 500,
      headers: {
        'Access-Control-Allow-Origin': process.env.CORS_ORIGIN || '*'
      },
      body: JSON.stringify({ message: 'Server configuration error' })
    };
  }

  try {
    // Parse the broadcast request from FastAPI
    if (!event.body) {
      return {
        statusCode: 400,
        headers: {
          'Access-Control-Allow-Origin': process.env.CORS_ORIGIN || '*'
        },
        body: JSON.stringify({ message: 'Missing request body' })
      };
    }

    const requestBody: BroadcastRequestBody = JSON.parse(event.body);
    const { type, data, version, id, source, meta } = requestBody;
    
    // Get all active connections
    const connections = await dynamodb.send(new ScanCommand({
      TableName: tableName,
      ProjectionExpression: 'connectionId'
    }))

    const message: WebSocketMessage = {
      type,
      version: version ?? '1',
      id: id ?? randomUUID(),
      timestamp: new Date().toISOString(),
      source: source ?? 'backend',
      data,
      ...(meta ? { meta } : {})
    };

    const messageData = JSON.stringify(message);

    // Broadcast to all connections
    const broadcastPromises = ((connections.Items as ConnectionItem[]) || []).map(async ({ connectionId }) => {
      try {
        await apiGatewayV3.send(new (await import('@aws-sdk/client-apigatewaymanagementapi')).PostToConnectionCommand({
          ConnectionId: connectionId,
          Data: Buffer.from(messageData)
        }))
        
        console.log(`Message sent to connection: ${connectionId}`);
      } catch (error: any) {
        const status = error?.$metadata?.httpStatusCode || error?.statusCode
        if (status === 410) {
          // Connection is stale, remove it
          await dynamodb.send(new DeleteCommand({
            TableName: tableName,
            Key: { connectionId }
          }))
          
          console.log(`Removed stale connection: ${connectionId}`);
        } else {
          console.error(`Failed to send to ${connectionId}:`, error);
        }
      }
    });

    await Promise.all(broadcastPromises);

    return {
      statusCode: 200,
      headers: {
        'Access-Control-Allow-Origin': process.env.CORS_ORIGIN || '*',
        'Access-Control-Allow-Headers': 'Content-Type,Authorization',
        'Access-Control-Allow-Methods': 'POST,OPTIONS'
      },
      body: JSON.stringify({
        message: 'Broadcast completed',
        connectionCount: connections.Items?.length || 0
      })
    };
  } catch (error) {
    console.error('Broadcast error:', error);
    return {
      statusCode: 500,
      headers: {
        'Access-Control-Allow-Origin': process.env.CORS_ORIGIN || '*'
      },
      body: JSON.stringify({ 
        message: 'Broadcast failed',
        error: error instanceof Error ? error.message : 'Unknown error'
      })
    };
  }
};
