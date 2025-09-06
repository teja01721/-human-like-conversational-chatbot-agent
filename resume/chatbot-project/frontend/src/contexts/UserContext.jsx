import React, { createContext, useContext, useReducer, useEffect } from 'react'
import { userAPI } from '../utils/api'
import toast from 'react-hot-toast'

const UserContext = createContext()

const initialState = {
  user: null,
  userId: null,
  profile: null,
  memories: [],
  isLoading: false,
  error: null
}

function userReducer(state, action) {
  switch (action.type) {
    case 'SET_LOADING':
      return { ...state, isLoading: action.payload }
    
    case 'SET_ERROR':
      return { ...state, error: action.payload }
    
    case 'SET_USER':
      return { ...state, user: action.payload }
    
    case 'SET_USER_ID':
      return { ...state, userId: action.payload }
    
    case 'SET_PROFILE':
      return { ...state, profile: action.payload }
    
    case 'SET_MEMORIES':
      return { ...state, memories: action.payload }
    
    case 'ADD_MEMORY':
      return { ...state, memories: [...state.memories, action.payload] }
    
    case 'DELETE_MEMORY':
      return {
        ...state,
        memories: state.memories.filter(m => m.id !== action.payload)
      }
    
    default:
      return state
  }
}

export function UserProvider({ children }) {
  const [state, dispatch] = useReducer(userReducer, initialState)

  // Initialize user on app start
  useEffect(() => {
    const storedUserId = localStorage.getItem('chatbot_user_id')
    if (storedUserId) {
      dispatch({ type: 'SET_USER_ID', payload: storedUserId })
      loadUser(storedUserId)
    } else {
      // Generate new user ID
      const newUserId = `user_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`
      localStorage.setItem('chatbot_user_id', newUserId)
      dispatch({ type: 'SET_USER_ID', payload: newUserId })
      createUser(newUserId)
    }
  }, [])

  const createUser = async (userId, userData = {}) => {
    try {
      const user = await userAPI.createUser({
        user_id: userId,
        name: userData.name || null,
        email: userData.email || null,
        preferences: userData.preferences || {}
      })
      dispatch({ type: 'SET_USER', payload: user })
    } catch (error) {
      console.error('Error creating user:', error)
      // User might already exist, try to load instead
      loadUser(userId)
    }
  }

  const loadUser = async (userId) => {
    dispatch({ type: 'SET_LOADING', payload: true })
    
    try {
      const user = await userAPI.getUser(userId)
      dispatch({ type: 'SET_USER', payload: user })
    } catch (error) {
      console.error('Error loading user:', error)
      // If user doesn't exist, create them
      if (error.response?.status === 404) {
        createUser(userId)
      }
    } finally {
      dispatch({ type: 'SET_LOADING', payload: false })
    }
  }

  const updateUser = async (userData) => {
    try {
      const updatedUser = await userAPI.updateUser(state.userId, userData)
      dispatch({ type: 'SET_USER', payload: updatedUser })
      toast.success('Profile updated successfully')
    } catch (error) {
      console.error('Error updating user:', error)
      toast.error('Failed to update profile')
    }
  }

  const loadProfile = async () => {
    if (!state.userId) return
    
    try {
      const profile = await userAPI.getUserProfile(state.userId)
      dispatch({ type: 'SET_PROFILE', payload: profile })
    } catch (error) {
      console.error('Error loading profile:', error)
    }
  }

  const loadMemories = async (memoryType = null) => {
    if (!state.userId) return
    
    try {
      const response = await userAPI.getUserMemories(state.userId, memoryType)
      dispatch({ type: 'SET_MEMORIES', payload: response.memories })
    } catch (error) {
      console.error('Error loading memories:', error)
    }
  }

  const addMemory = async (memoryData) => {
    if (!state.userId) return
    
    try {
      await userAPI.addUserMemory(state.userId, memoryData)
      dispatch({ type: 'ADD_MEMORY', payload: memoryData })
      toast.success('Memory added successfully')
      loadMemories() // Refresh memories
    } catch (error) {
      console.error('Error adding memory:', error)
      toast.error('Failed to add memory')
    }
  }

  const deleteMemory = async (memoryId) => {
    if (!state.userId) return
    
    try {
      await userAPI.deleteUserMemory(state.userId, memoryId)
      dispatch({ type: 'DELETE_MEMORY', payload: memoryId })
      toast.success('Memory deleted successfully')
    } catch (error) {
      console.error('Error deleting memory:', error)
      toast.error('Failed to delete memory')
    }
  }

  const value = {
    ...state,
    updateUser,
    loadProfile,
    loadMemories,
    addMemory,
    deleteMemory
  }

  return (
    <UserContext.Provider value={value}>
      {children}
    </UserContext.Provider>
  )
}

export function useUser() {
  const context = useContext(UserContext)
  if (!context) {
    throw new Error('useUser must be used within a UserProvider')
  }
  return context
}
