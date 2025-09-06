import React, { createContext, useContext, useReducer, useEffect } from 'react'
import { v4 as uuidv4 } from 'uuid'
import { chatAPI } from '../utils/api'
import toast from 'react-hot-toast'

const ChatContext = createContext()

const initialState = {
  messages: [],
  sessions: [],
  currentSessionId: null,
  isLoading: false,
  isTyping: false,
  error: null,
  analytics: null
}

function chatReducer(state, action) {
  switch (action.type) {
    case 'SET_LOADING':
      return { ...state, isLoading: action.payload }
    
    case 'SET_TYPING':
      return { ...state, isTyping: action.payload }
    
    case 'SET_ERROR':
      return { ...state, error: action.payload }
    
    case 'ADD_MESSAGE':
      return {
        ...state,
        messages: [...state.messages, action.payload]
      }
    
    case 'SET_MESSAGES':
      return { ...state, messages: action.payload }
    
    case 'SET_SESSIONS':
      return { ...state, sessions: action.payload }
    
    case 'SET_CURRENT_SESSION':
      return { ...state, currentSessionId: action.payload }
    
    case 'ADD_SESSION':
      return {
        ...state,
        sessions: [action.payload, ...state.sessions]
      }
    
    case 'DELETE_SESSION':
      return {
        ...state,
        sessions: state.sessions.filter(s => s.session_id !== action.payload),
        currentSessionId: state.currentSessionId === action.payload ? null : state.currentSessionId,
        messages: state.currentSessionId === action.payload ? [] : state.messages
      }
    
    case 'SET_ANALYTICS':
      return { ...state, analytics: action.payload }
    
    case 'CLEAR_MESSAGES':
      return { ...state, messages: [] }
    
    default:
      return state
  }
}

export function ChatProvider({ children }) {
  const [state, dispatch] = useReducer(chatReducer, initialState)

  const sendMessage = async (message, userId) => {
    if (!message.trim()) return

    const userMessage = {
      id: uuidv4(),
      message: message,
      response: null,
      timestamp: new Date().toISOString(),
      isUser: true
    }

    dispatch({ type: 'ADD_MESSAGE', payload: userMessage })
    dispatch({ type: 'SET_TYPING', payload: true })

    try {
      const response = await chatAPI.sendMessage({
        user_id: userId,
        message: message,
        session_id: state.currentSessionId,
        context: {
          recent_context: state.messages.slice(-3).map(m => m.message).join(' ')
        }
      })

      const botMessage = {
        id: uuidv4(),
        message: message,
        response: response.response,
        timestamp: new Date().toISOString(),
        isUser: false,
        tone_used: response.tone_used,
        emotion_detected: response.emotion_detected,
        memory_recalled: response.memory_recalled,
        tokens_used: response.tokens_used,
        response_time: response.response_time
      }

      dispatch({ type: 'ADD_MESSAGE', payload: botMessage })
      
      // Update current session if new one was created
      if (response.session_id !== state.currentSessionId) {
        dispatch({ type: 'SET_CURRENT_SESSION', payload: response.session_id })
        await loadSessions(userId) // Refresh sessions list
      }

    } catch (error) {
      console.error('Error sending message:', error)
      toast.error('Failed to send message. Please try again.')
      dispatch({ type: 'SET_ERROR', payload: error.message })
    } finally {
      dispatch({ type: 'SET_TYPING', payload: false })
    }
  }

  const loadSessions = async (userId) => {
    try {
      const sessions = await chatAPI.getSessions(userId)
      dispatch({ type: 'SET_SESSIONS', payload: sessions })
    } catch (error) {
      console.error('Error loading sessions:', error)
      toast.error('Failed to load chat sessions')
    }
  }

  const loadChatHistory = async (sessionId) => {
    dispatch({ type: 'SET_LOADING', payload: true })
    
    try {
      const history = await chatAPI.getChatHistory(sessionId)
      const formattedMessages = history.flatMap(msg => [
        {
          id: `${msg.id}-user`,
          message: msg.message,
          response: null,
          timestamp: msg.timestamp,
          isUser: true
        },
        {
          id: `${msg.id}-bot`,
          message: msg.message,
          response: msg.response,
          timestamp: msg.timestamp,
          isUser: false,
          tone_used: msg.tone_detected,
          emotion_detected: msg.emotion_score
        }
      ])
      
      dispatch({ type: 'SET_MESSAGES', payload: formattedMessages })
      dispatch({ type: 'SET_CURRENT_SESSION', payload: sessionId })
    } catch (error) {
      console.error('Error loading chat history:', error)
      toast.error('Failed to load chat history')
    } finally {
      dispatch({ type: 'SET_LOADING', payload: false })
    }
  }

  const createNewSession = () => {
    dispatch({ type: 'CLEAR_MESSAGES' })
    dispatch({ type: 'SET_CURRENT_SESSION', payload: null })
  }

  const deleteSession = async (sessionId) => {
    try {
      await chatAPI.deleteSession(sessionId)
      dispatch({ type: 'DELETE_SESSION', payload: sessionId })
      toast.success('Session deleted successfully')
    } catch (error) {
      console.error('Error deleting session:', error)
      toast.error('Failed to delete session')
    }
  }

  const loadAnalytics = async (userId) => {
    try {
      const analytics = await chatAPI.getAnalytics(userId)
      dispatch({ type: 'SET_ANALYTICS', payload: analytics })
    } catch (error) {
      console.error('Error loading analytics:', error)
    }
  }

  const value = {
    ...state,
    sendMessage,
    loadSessions,
    loadChatHistory,
    createNewSession,
    deleteSession,
    loadAnalytics
  }

  return (
    <ChatContext.Provider value={value}>
      {children}
    </ChatContext.Provider>
  )
}

export function useChat() {
  const context = useContext(ChatContext)
  if (!context) {
    throw new Error('useChat must be used within a ChatProvider')
  }
  return context
}
