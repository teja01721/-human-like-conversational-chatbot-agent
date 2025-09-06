import React, { useState, useRef, useEffect } from 'react'
import { Send, Loader2, Bot, User, Heart, Brain, Clock } from 'lucide-react'
import { motion, AnimatePresence } from 'framer-motion'
import ReactMarkdown from 'react-markdown'
import { useChat } from '../contexts/ChatContext'
import { useUser } from '../contexts/UserContext'
import TypingIndicator from './TypingIndicator'
import MessageMetadata from './MessageMetadata'

function ChatInterface() {
  const [inputMessage, setInputMessage] = useState('')
  const [showMetadata, setShowMetadata] = useState({})
  const messagesEndRef = useRef(null)
  const inputRef = useRef(null)
  
  const { messages, isTyping, sendMessage, currentSessionId } = useChat()
  const { userId } = useUser()

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  useEffect(() => {
    scrollToBottom()
  }, [messages, isTyping])

  const handleSubmit = async (e) => {
    e.preventDefault()
    if (!inputMessage.trim() || !userId) return

    await sendMessage(inputMessage, userId)
    setInputMessage('')
    inputRef.current?.focus()
  }

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSubmit(e)
    }
  }

  const toggleMetadata = (messageId) => {
    setShowMetadata(prev => ({
      ...prev,
      [messageId]: !prev[messageId]
    }))
  }

  const getEmotionColor = (emotions) => {
    if (!emotions) return 'text-gray-500'
    
    const dominant = Object.entries(emotions).reduce((a, b) => 
      emotions[a[0]] > emotions[b[0]] ? a : b
    )
    
    const emotionColors = {
      joy: 'text-yellow-500',
      sadness: 'text-blue-500',
      anger: 'text-red-500',
      fear: 'text-purple-500',
      surprise: 'text-green-500',
      disgust: 'text-gray-500'
    }
    
    return emotionColors[dominant[0]] || 'text-gray-500'
  }

  return (
    <div className="flex flex-col h-full">
      {/* Header */}
      <div className="bg-white border-b border-gray-200 px-6 py-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <div className="w-10 h-10 bg-primary-100 rounded-full flex items-center justify-center">
              <Bot className="w-6 h-6 text-primary-600" />
            </div>
            <div>
              <h1 className="text-lg font-semibold text-gray-900">AI Assistant</h1>
              <p className="text-sm text-gray-500">
                {currentSessionId ? 'Active conversation' : 'Start a new conversation'}
              </p>
            </div>
          </div>
          
          <div className="flex items-center space-x-2 text-sm text-gray-500">
            <Brain className="w-4 h-4" />
            <span>Memory-enabled</span>
          </div>
        </div>
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto custom-scrollbar">
        <div className="max-w-4xl mx-auto px-4 py-6 space-y-6">
          {messages.length === 0 && (
            <div className="text-center py-12">
              <Bot className="w-16 h-16 text-gray-300 mx-auto mb-4" />
              <h3 className="text-lg font-medium text-gray-900 mb-2">
                Welcome to your AI Assistant
              </h3>
              <p className="text-gray-500 max-w-md mx-auto">
                I'm here to have natural, meaningful conversations with you. 
                I'll remember our interactions and adapt to your communication style.
              </p>
            </div>
          )}

          <AnimatePresence>
            {messages.map((message) => (
              <motion.div
                key={message.id}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -20 }}
                className="chat-message"
              >
                <div className={`flex ${message.isUser ? 'justify-end' : 'justify-start'}`}>
                  <div className={`max-w-3xl ${message.isUser ? 'user-message' : 'bot-message'}`}>
                    <div className="flex items-start space-x-3 p-4">
                      <div className={`w-8 h-8 rounded-full flex items-center justify-center flex-shrink-0 ${
                        message.isUser 
                          ? 'bg-primary-600 text-white' 
                          : 'bg-primary-100 text-primary-600'
                      }`}>
                        {message.isUser ? <User className="w-4 h-4" /> : <Bot className="w-4 h-4" />}
                      </div>
                      
                      <div className="flex-1 min-w-0">
                        <div className="markdown-content">
                          <ReactMarkdown>
                            {message.isUser ? message.message : message.response}
                          </ReactMarkdown>
                        </div>
                        
                        {!message.isUser && (
                          <MessageMetadata
                            message={message}
                            isVisible={showMetadata[message.id]}
                            onToggle={() => toggleMetadata(message.id)}
                          />
                        )}
                      </div>
                    </div>
                  </div>
                </div>
              </motion.div>
            ))}
          </AnimatePresence>

          {isTyping && (
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              className="chat-message"
            >
              <div className="flex justify-start">
                <div className="bot-message max-w-xs">
                  <div className="flex items-start space-x-3 p-4">
                    <div className="w-8 h-8 bg-primary-100 rounded-full flex items-center justify-center">
                      <Bot className="w-4 h-4 text-primary-600" />
                    </div>
                    <TypingIndicator />
                  </div>
                </div>
              </div>
            </motion.div>
          )}
          
          <div ref={messagesEndRef} />
        </div>
      </div>

      {/* Input */}
      <div className="bg-white border-t border-gray-200 px-6 py-4">
        <form onSubmit={handleSubmit} className="max-w-4xl mx-auto">
          <div className="flex items-end space-x-4">
            <div className="flex-1">
              <textarea
                ref={inputRef}
                value={inputMessage}
                onChange={(e) => setInputMessage(e.target.value)}
                onKeyPress={handleKeyPress}
                placeholder="Type your message here..."
                className="message-input"
                rows="1"
                style={{
                  minHeight: '44px',
                  maxHeight: '120px',
                  resize: 'none'
                }}
                onInput={(e) => {
                  e.target.style.height = 'auto'
                  e.target.style.height = Math.min(e.target.scrollHeight, 120) + 'px'
                }}
              />
            </div>
            
            <button
              type="submit"
              disabled={!inputMessage.trim() || isTyping}
              className="send-button"
            >
              {isTyping ? (
                <Loader2 className="w-5 h-5 animate-spin" />
              ) : (
                <Send className="w-5 h-5" />
              )}
            </button>
          </div>
          
          <div className="flex items-center justify-between mt-2 text-xs text-gray-500">
            <span>Press Enter to send, Shift+Enter for new line</span>
            <span>{inputMessage.length}/2000</span>
          </div>
        </form>
      </div>
    </div>
  )
}

export default ChatInterface
