import { APIGatewayProxyHandler, APIGatewayProxyEvent, APIGatewayProxyResult } from 'aws-lambda';
import { DeleteCommand } from '@aws-sdk/lib-dynamodb';
import { dynamoClient } from './shared/clients';
import { createResponse, createErrorResponse, validateEnvironment, logger } from './shared/utils';

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

    const command = new DeleteCommand({
      TableName: config.DYNAMODB_CONNECTIONS_TABLE,
      Key: { connectionId },
    });

    await dynamoClient.send(command);

    logger.info(`Connection removed: ${connectionId}`);
    
    return createResponse(200, { message: 'Disconnected' });
  } catch (error) {
    logger.error('Disconnection error:', error);
    
    if (error instanceof Error && error.message.includes('environment variable')) {
      return createErrorResponse(500, 'Server configuration error');
    }
    
    return createErrorResponse(
      500,
      'Failed to disconnect',
      error instanceof Error ? error.message : 'Unknown error'
    );
  }
};