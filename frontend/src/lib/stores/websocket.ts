'use client'

import { create } from 'zustand'
import { subscribeWithSelector } from 'zustand/middleware'

export interface WebSocketMessage {
  type: string
  data: any
  timestamp: string
}

interface WebSocketState {
  // Connection state
  isConnected: boolean
  reconnectAttempts: number
  lastError: string | null
  
  // WebSocket instance (not reactive, just for internal use)
  _ws: WebSocket | null
  _reconnectTimeout: NodeJS.Timeout | null
  _subscribers: Map<string, Set<(message: WebSocketMessage) => void>>
  
  // Actions
  connect: (url: string) => void
  disconnect: () => void
  subscribe: (messageType: string, callback: (message: WebSocketMessage) => void) => () => void
  
  // Internal actions
  _setConnected: (connected: boolean) => void
  _setReconnectAttempts: (attempts: number) => void
  _setLastError: (error: string | null) => void
}

const MAX_RECONNECT_ATTEMPTS = 5
const RECONNECT_INTERVAL = 3000

export const useWebSocketStore = create<WebSocketState>()(
  subscribeWithSelector((set, get) => ({
    // Initial state
    isConnected: false,
    reconnectAttempts: 0,
    lastError: null,
    _ws: null,
    _reconnectTimeout: null,
    _subscribers: new Map(),

    connect: (url: string) => {
      const state = get()
      
      // Don't connect if already connected to the same URL
      if (state._ws && state.isConnected && state._ws.url === url) {
        return
      }

      // Close existing connection
      if (state._ws) {
        state._ws.close()
      }

      console.log('🔌 Connecting to WebSocket:', url)
      
      try {
        const ws = new WebSocket(url)
        
        ws.onopen = () => {
          console.log('✅ WebSocket connected')
          set(state => ({ 
            ...state,
            _ws: ws,
            isConnected: true,
            reconnectAttempts: 0,
            lastError: null
          }))
        }
        
        ws.onmessage = (event) => {
          try {
            const message: WebSocketMessage = JSON.parse(event.data)
            console.log('📨 WebSocket message:', message.type, message.data)
            
            const state = get()
            
            // Notify subscribers for this specific message type
            const typeSubscribers = state._subscribers.get(message.type)
            if (typeSubscribers) {
              typeSubscribers.forEach(callback => {
                try {
                  callback(message)
                } catch (error) {
                  console.error('❌ Error in WebSocket subscriber:', error)
                }
              })
            }
            
            // Notify subscribers listening to all messages
            const allSubscribers = state._subscribers.get('*')
            if (allSubscribers) {
              allSubscribers.forEach(callback => {
                try {
                  callback(message)
                } catch (error) {
                  console.error('❌ Error in WebSocket subscriber:', error)
                }
              })
            }
          } catch (error) {
            console.error('❌ Failed to parse WebSocket message:', error)
            set(state => ({ ...state, lastError: 'Failed to parse message' }))
          }
        }
        
        ws.onclose = () => {
          console.log('🔌 WebSocket disconnected')
          const state = get()
          
          set(prevState => ({ 
            ...prevState,
            isConnected: false,
            _ws: null
          }))
          
          // Attempt reconnection if under the limit
          if (state.reconnectAttempts < MAX_RECONNECT_ATTEMPTS) {
            const newAttempts = state.reconnectAttempts + 1
            console.log(`🔄 Attempting reconnection ${newAttempts}/${MAX_RECONNECT_ATTEMPTS}`)
            
            const timeout = setTimeout(() => {
              get().connect(url)
            }, RECONNECT_INTERVAL)
            
            set(prevState => ({
              ...prevState,
              reconnectAttempts: newAttempts,
              _reconnectTimeout: timeout
            }))
          } else {
            console.log('❌ Max reconnection attempts reached')
            set(state => ({ ...state, lastError: 'Max reconnection attempts reached' }))
          }
        }
        
        ws.onerror = (error) => {
          console.error('❌ WebSocket error:', error)
          set(state => ({ 
            ...state, 
            lastError: 'Connection error',
            isConnected: false 
          }))
        }
        
        // Store the WebSocket instance
        set(state => ({ ...state, _ws: ws }))
        
      } catch (error) {
        console.error('❌ Failed to create WebSocket:', error)
        set(state => ({ ...state, lastError: 'Failed to create connection' }))
      }
    },

    disconnect: () => {
      const state = get()
      
      // Clear reconnection timeout
      if (state._reconnectTimeout) {
        clearTimeout(state._reconnectTimeout)
      }
      
      // Close WebSocket
      if (state._ws) {
        state._ws.close()
      }
      
      // Clear subscribers
      state._subscribers.clear()
      
      set({
        isConnected: false,
        reconnectAttempts: 0,
        lastError: null,
        _ws: null,
        _reconnectTimeout: null,
        _subscribers: new Map()
      })
      
      console.log('🔌 WebSocket manually disconnected')
    },

    subscribe: (messageType: string, callback: (message: WebSocketMessage) => void) => {
      const state = get()
      
      // Add subscriber
      if (!state._subscribers.has(messageType)) {
        state._subscribers.set(messageType, new Set())
      }
      state._subscribers.get(messageType)!.add(callback)
      
      console.log(`📬 Subscribed to WebSocket messages of type: ${messageType}`)
      
      // Return unsubscribe function
      return () => {
        const currentState = get()
        const typeSubscribers = currentState._subscribers.get(messageType)
        if (typeSubscribers) {
          typeSubscribers.delete(callback)
          if (typeSubscribers.size === 0) {
            currentState._subscribers.delete(messageType)
          }
        }
        console.log(`📪 Unsubscribed from WebSocket messages of type: ${messageType}`)
      }
    },

    // Internal actions
    _setConnected: (connected: boolean) => set(state => ({ ...state, isConnected: connected })),
    _setReconnectAttempts: (attempts: number) => set(state => ({ ...state, reconnectAttempts: attempts })),
    _setLastError: (error: string | null) => set(state => ({ ...state, lastError: error }))
  }))
)