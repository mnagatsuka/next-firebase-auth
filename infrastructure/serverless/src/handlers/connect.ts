import { APIGatewayProxyHandler, APIGatewayProxyEvent, APIGatewayProxyResult } from 'aws-lambda';
import { PutCommand } from '@aws-sdk/lib-dynamodb'
import { createDynamoDbDocClient } from '../utils'

const dynamodb = createDynamoDbDocClient()

export const handler: APIGatewayProxyHandler = async (
  event: APIGatewayProxyEvent
): Promise<APIGatewayProxyResult> => {
  const connectionId = event.requestContext.connectionId;
  const tableName = process.env.DYNAMODB_CONNECTIONS_TABLE;

  if (!connectionId) {
    console.error('Missing connectionId in request context');
    return {
      statusCode: 400,
      body: JSON.stringify({ message: 'Missing connection ID' })
    };
  }

  if (!tableName) {
    console.error('Missing DYNAMODB_CONNECTIONS_TABLE environment variable');
    return {
      statusCode: 500,
      body: JSON.stringify({ message: 'Server configuration error' })
    };
  }

  try {
    await dynamodb.send(new PutCommand({
      TableName: tableName,
      Item: {
        connectionId,
        timestamp: Date.now(),
        ttl: Math.floor(Date.now() / 1000) + 86400 // 24 hours TTL
      }
    }))

    console.log(`Connection established: ${connectionId}`);
    
    return {
      statusCode: 200,
      body: JSON.stringify({ message: 'Connected' })
    };
  } catch (error) {
    console.error('Connection error:', error);
    return {
      statusCode: 500,
      body: JSON.stringify({ 
        message: 'Failed to connect',
        error: error instanceof Error ? error.message : 'Unknown error'
      })
    };
  }
};
