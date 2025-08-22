import { APIGatewayProxyHandler, APIGatewayProxyEvent, APIGatewayProxyResult } from 'aws-lambda';
import { PostToConnectionCommand } from '@aws-sdk/client-apigatewaymanagementapi';
import { apiGatewayClient } from './shared/clients';
import { createResponse, createErrorResponse, validateEnvironment, logger, encodeMessage } from './shared/utils';
import { WebSocketMessage } from './shared/types';

export const handler: APIGatewayProxyHandler = async (
  event: APIGatewayProxyEvent
): Promise<APIGatewayProxyResult> => {
  const connectionId = event.requestContext.connectionId;
  
  if (!connectionId) {
    logger.error('Missing connectionId in request context');
    return createErrorResponse(400, 'Missing connection ID');
  }

  try {
    validateEnvironment();
    
    const message = JSON.parse(event.body || '{}');
    logger.info(`Received message from ${connectionId}:`, message);
    
    // Create response message
    const response: WebSocketMessage = {
      type: 'echo',
      data: { 
        message: 'Message received', 
        original: message,
        connectionId 
      },
      timestamp: new Date().toISOString()
    };

    const command = new PostToConnectionCommand({
      ConnectionId: connectionId,
      Data: encodeMessage(response)
    });

    await apiGatewayClient.send(command);

    logger.debug(`Message echoed back to connection: ${connectionId}`);
    
    return createResponse(200, { message: 'Message processed' });
  } catch (error) {
    logger.error('Message handling error:', error);
    
    if (error instanceof Error && error.message.includes('environment variable')) {
      return createErrorResponse(500, 'Server configuration error');
    }
    
    return createErrorResponse(
      500,
      'Failed to process message',
      error instanceof Error ? error.message : 'Unknown error'
    );
  }
};