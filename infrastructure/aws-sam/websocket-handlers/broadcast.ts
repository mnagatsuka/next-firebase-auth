import { APIGatewayProxyHandler, APIGatewayProxyEvent, APIGatewayProxyResult } from 'aws-lambda';
import { BroadcastService } from './shared/broadcast-service';
import { createCorsResponse, createErrorResponse, validateEnvironment, logger } from './shared/utils';
import { BroadcastRequestBody, WebSocketMessage } from './shared/types';

export const handler: APIGatewayProxyHandler = async (
  event: APIGatewayProxyEvent
): Promise<APIGatewayProxyResult> => {
  try {
    const config = validateEnvironment();
    const corsOrigin = config.CORS_ORIGIN;

    // Validate request body
    if (!event.body) {
      return createErrorResponse(400, 'Missing request body', undefined, corsOrigin);
    }

    let requestBody: BroadcastRequestBody;
    try {
      requestBody = JSON.parse(event.body);
    } catch (parseError) {
      return createErrorResponse(400, 'Invalid JSON in request body', undefined, corsOrigin);
    }

    // Validate request structure
    if (!requestBody.type || !requestBody.data) {
      return createErrorResponse(400, 'Missing required fields: type, data', undefined, corsOrigin);
    }

    const { type, data } = requestBody;
    
    logger.info(`Broadcasting message of type: ${type}`);

    // Create broadcast message
    const message: WebSocketMessage = {
      type,
      data,
      timestamp: new Date().toISOString()
    };

    // Initialize broadcast service and send to all connections
    const broadcastService = new BroadcastService(config.DYNAMODB_CONNECTIONS_TABLE);
    const results = await broadcastService.broadcastToAll(message);

    return createCorsResponse(
      200,
      {
        message: 'Broadcast completed',
        results: {
          totalConnections: results.sent + results.failed + results.stale,
          sent: results.sent,
          failed: results.failed,
          staleRemoved: results.stale
        }
      },
      corsOrigin
    );
  } catch (error) {
    logger.error('Broadcast error:', error);
    
    if (error instanceof Error && error.message.includes('environment variable')) {
      return createErrorResponse(500, 'Server configuration error', undefined, process.env.CORS_ORIGIN);
    }
    
    return createErrorResponse(
      500,
      'Broadcast failed',
      error instanceof Error ? error.message : 'Unknown error',
      process.env.CORS_ORIGIN
    );
  }
};