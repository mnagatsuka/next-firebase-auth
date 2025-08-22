import { APIGatewayProxyHandler, APIGatewayProxyEvent, APIGatewayProxyResult } from 'aws-lambda';
import { PutCommand } from '@aws-sdk/lib-dynamodb';
import { dynamoClient } from './shared/clients';
import { createResponse, createErrorResponse, validateEnvironment, logger, createTtl } from './shared/utils';
import { ConnectionItem } from './shared/types';

export const handler: APIGatewayProxyHandler = async (
  event: APIGatewayProxyEvent
): Promise<APIGatewayProxyResult> => {
  const connectionId = event.requestContext.connectionId;

  if (!connectionId) {
    logger.error('Missing connectionId in request context');
    return createErrorResponse(400, 'Missing connection ID');
  }

  try {
    const config = validateEnvironment();
    
    const connectionItem: ConnectionItem = {
      connectionId,
      timestamp: Date.now(),
      ttl: createTtl(24), // 24 hours TTL
    };

    const command = new PutCommand({
      TableName: config.DYNAMODB_CONNECTIONS_TABLE,
      Item: connectionItem,
    });

    await dynamoClient.send(command);

    logger.info(`Connection established: ${connectionId}`);
    
    return createResponse(200, { message: 'Connected' });
  } catch (error) {
    logger.error('Connection error:', error);
    
    if (error instanceof Error && error.message.includes('environment variable')) {
      return createErrorResponse(500, 'Server configuration error');
    }
    
    return createErrorResponse(
      500,
      'Failed to connect',
      error instanceof Error ? error.message : 'Unknown error'
    );
  }
};