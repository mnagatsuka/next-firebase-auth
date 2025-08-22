// Broadcast service for WebSocket connections

import { ScanCommand, DeleteCommand } from '@aws-sdk/lib-dynamodb';
import { PostToConnectionCommand } from '@aws-sdk/client-apigatewaymanagementapi';
import { dynamoClient, apiGatewayClient } from './clients';
import { ConnectionItem, WebSocketMessage } from './types';
import { logger, encodeMessage } from './utils';

export class BroadcastService {
  private readonly tableName: string;
  private readonly chunkSize: number = 50;

  constructor(tableName: string) {
    this.tableName = tableName;
  }

  /**
   * Get all active connections with pagination
   */
  async getAllConnections(): Promise<ConnectionItem[]> {
    let lastEvaluatedKey: Record<string, any> | undefined = undefined;
    let allConnections: ConnectionItem[] = [];

    do {
      const scanCommand: ScanCommand = new ScanCommand({
        TableName: this.tableName,
        ProjectionExpression: 'connectionId',
        ExclusiveStartKey: lastEvaluatedKey,
      });

      const result = await dynamoClient.send(scanCommand);
      if (result.Items) {
        allConnections = allConnections.concat(result.Items as ConnectionItem[]);
      }
      lastEvaluatedKey = result.LastEvaluatedKey;
    } while (lastEvaluatedKey);

    logger.info(`Found ${allConnections.length} active connections`);
    return allConnections;
  }

  /**
   * Send message to a single connection and handle stale connections
   */
  async sendToConnection(connectionId: string, message: WebSocketMessage): Promise<boolean> {
    try {
      const command = new PostToConnectionCommand({
        ConnectionId: connectionId,
        Data: encodeMessage(message),
      });

      await apiGatewayClient.send(command);
      logger.debug(`Message sent to connection: ${connectionId}`);
      return true;
    } catch (error: any) {
      if (error.$metadata?.httpStatusCode === 410 || error.statusCode === 410) {
        // Connection is stale, remove it
        await this.removeStaleConnection(connectionId);
        return false;
      } else {
        logger.error(`Failed to send to ${connectionId}:`, error);
        return false;
      }
    }
  }

  /**
   * Remove a stale connection from DynamoDB
   */
  private async removeStaleConnection(connectionId: string): Promise<void> {
    try {
      const deleteCommand = new DeleteCommand({
        TableName: this.tableName,
        Key: { connectionId },
      });

      await dynamoClient.send(deleteCommand);
      logger.info(`Removed stale connection: ${connectionId}`);
    } catch (error) {
      logger.error(`Failed to remove stale connection ${connectionId}:`, error);
    }
  }

  /**
   * Broadcast message to all connections with chunked processing
   */
  async broadcastToAll(message: WebSocketMessage): Promise<{ sent: number; failed: number; stale: number }> {
    const connections = await this.getAllConnections();
    
    let sent = 0;
    let failed = 0;
    let stale = 0;

    // Process connections in chunks to avoid overwhelming the system
    for (let i = 0; i < connections.length; i += this.chunkSize) {
      const chunk = connections.slice(i, i + this.chunkSize);
      
      const results = await Promise.allSettled(
        chunk.map(({ connectionId }) => this.sendToConnection(connectionId, message))
      );

      // Count results
      results.forEach((result, index) => {
        if (result.status === 'fulfilled') {
          if (result.value) {
            sent++;
          } else {
            stale++; // Connection was stale and removed
          }
        } else {
          failed++;
          logger.error(`Failed to process connection ${chunk[index].connectionId}:`, result.reason);
        }
      });

      // Add small delay between chunks to prevent throttling
      if (i + this.chunkSize < connections.length) {
        await new Promise(resolve => setTimeout(resolve, 10));
      }
    }

    logger.info(`Broadcast completed: ${sent} sent, ${failed} failed, ${stale} stale`);
    return { sent, failed, stale };
  }
}