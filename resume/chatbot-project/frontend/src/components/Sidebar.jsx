import React, { useEffect } from 'react'
import { 
  MessageSquare, 
  Plus, 
  User, 
  Settings, 
  Trash2, 
  Menu, 
  X,
  Brain,
  BarChart3
} from 'lucide-react'
import { motion, AnimatePresence } from 'framer-motion'
import { useChat } from '../contexts/ChatContext'
import { useUser } from '../contexts/UserContext'
import { formatDistanceToNow } from 'date-fns'

function Sidebar({ isOpen, onToggle, currentView, onViewChange }) {
  const { 
    sessions, 
    currentSessionId, 
    loadSessions, 
    loadChatHistory, 
    createNewSession, 
    deleteSession 
  } = useChat()
  const { userId, user } = useUser()

  useEffect(() => {
    if (userId) {
      loadSessions(userId)
    }
  }, [userId])

  const handleSessionClick = (sessionId) => {
    loadChatHistory(sessionId)
  }

  const handleDeleteSession = (e, sessionId) => {
    e.stopPropagation()
    if (window.confirm('Are you sure you want to delete this conversation?')) {
      deleteSession(sessionId)
    }
  }

  const sidebarVariants = {
    open: { x: 0 },
    closed: { x: '-100%' }
  }

  return (
    <>
      {/* Mobile overlay */}
      <AnimatePresence>
        {isOpen && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 bg-black bg-opacity-50 z-40 lg:hidden"
            onClick={onToggle}
          />
        )}
      </AnimatePresence>

      {/* Sidebar */}
      <motion.div
        variants={sidebarVariants}
        animate={isOpen ? 'open' : 'closed'}
        className="fixed lg:relative inset-y-0 left-0 z-50 w-80 bg-white border-r border-gray-200 flex flex-col"
      >
        {/* Header */}
        <div className="flex items-center justify-between p-4 border-b border-gray-200">
          <div className="flex items-center space-x-3">
            <div className="w-8 h-8 bg-primary-600 rounded-lg flex items-center justify-center">
              <Brain className="w-5 h-5 text-white" />
            </div>
            <h2 className="text-lg font-semibold text-gray-900">ChatBot</h2>
          </div>
          <button
            onClick={onToggle}
            className="p-2 hover:bg-gray-100 rounded-lg lg:hidden"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* New Chat Button */}
        <div className="p-4">
          <button
            onClick={createNewSession}
            className="w-full flex items-center space-x-3 p-3 bg-primary-600 hover:bg-primary-700 text-white rounded-lg transition-colors"
          >
            <Plus className="w-5 h-5" />
            <span>New Conversation</span>
          </button>
        </div>

        {/* Navigation */}
        <div className="px-4 pb-4">
          <nav className="space-y-1">
            <button
              onClick={() => onViewChange('chat')}
              className={`sidebar-item w-full ${currentView === 'chat' ? 'active' : ''}`}
            >
              <MessageSquare className="w-5 h-5" />
              <span>Chat</span>
            </button>
            <button
              onClick={() => onViewChange('profile')}
              className={`sidebar-item w-full ${currentView === 'profile' ? 'active' : ''}`}
            >
              <User className="w-5 h-5" />
              <span>Profile</span>
            </button>
            <button
              onClick={() => onViewChange('analytics')}
              className={`sidebar-item w-full ${currentView === 'analytics' ? 'active' : ''}`}
            >
              <BarChart3 className="w-5 h-5" />
              <span>Analytics</span>
            </button>
          </nav>
        </div>

        {/* Chat Sessions */}
        <div className="flex-1 overflow-y-auto custom-scrollbar">
          <div className="px-4">
            <h3 className="text-sm font-medium text-gray-500 mb-3">Recent Conversations</h3>
            <div className="space-y-2">
              {sessions.map((session) => (
                <div
                  key={session.session_id}
                  className={`group relative p-3 rounded-lg cursor-pointer transition-colors ${
                    currentSessionId === session.session_id
                      ? 'bg-primary-50 border border-primary-200'
                      : 'hover:bg-gray-50'
                  }`}
                  onClick={() => handleSessionClick(session.session_id)}
                >
                  <div className="flex items-start justify-between">
                    <div className="flex-1 min-w-0">
                      <p className="text-sm font-medium text-gray-900 truncate">
                        {session.title || 'Untitled Conversation'}
                      </p>
                      <p className="text-xs text-gray-500 mt-1">
                        {formatDistanceToNow(new Date(session.updated_at), { addSuffix: true })}
                      </p>
                    </div>
                    <button
                      onClick={(e) => handleDeleteSession(e, session.session_id)}
                      className="opacity-0 group-hover:opacity-100 p-1 hover:bg-red-100 rounded transition-all"
                    >
                      <Trash2 className="w-4 h-4 text-red-500" />
                    </button>
                  </div>
                </div>
              ))}
              
              {sessions.length === 0 && (
                <div className="text-center py-8">
                  <MessageSquare className="w-12 h-12 text-gray-300 mx-auto mb-3" />
                  <p className="text-sm text-gray-500">No conversations yet</p>
                  <p className="text-xs text-gray-400 mt-1">Start chatting to see your history</p>
                </div>
              )}
            </div>
          </div>
        </div>

        {/* User Info */}
        <div className="p-4 border-t border-gray-200">
          <div className="flex items-center space-x-3">
            <div className="w-10 h-10 bg-gray-200 rounded-full flex items-center justify-center">
              <User className="w-5 h-5 text-gray-600" />
            </div>
            <div className="flex-1 min-w-0">
              <p className="text-sm font-medium text-gray-900 truncate">
                {user?.name || 'Anonymous User'}
              </p>
              <p className="text-xs text-gray-500 truncate">
                {userId}
              </p>
            </div>
            <button className="p-2 hover:bg-gray-100 rounded-lg">
              <Settings className="w-4 h-4 text-gray-500" />
            </button>
          </div>
        </div>
      </motion.div>

      {/* Mobile menu button */}
      <button
        onClick={onToggle}
        className="fixed top-4 left-4 z-30 p-2 bg-white border border-gray-200 rounded-lg shadow-sm lg:hidden"
      >
        <Menu className="w-5 h-5" />
      </button>
    </>
  )
}

export default Sidebar
