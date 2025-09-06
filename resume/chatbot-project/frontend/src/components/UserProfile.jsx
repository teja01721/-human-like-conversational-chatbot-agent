import React, { useEffect, useState } from 'react'
import { 
  User, 
  Brain, 
  Heart, 
  MessageSquare, 
  Clock, 
  Trash2, 
  Plus,
  Edit3,
  Save,
  X
} from 'lucide-react'
import { motion } from 'framer-motion'
import { useUser } from '../contexts/UserContext'
import { useChat } from '../contexts/ChatContext'

function UserProfile() {
  const { 
    user, 
    userId, 
    profile, 
    memories, 
    loadProfile, 
    loadMemories, 
    updateUser, 
    addMemory, 
    deleteMemory 
  } = useUser()
  const { loadAnalytics, analytics } = useChat()
  
  const [isEditing, setIsEditing] = useState(false)
  const [editForm, setEditForm] = useState({
    name: '',
    email: '',
    preferences: {}
  })
  const [newMemory, setNewMemory] = useState({
    content: '',
    memory_type: 'preference',
    importance_score: 5
  })
  const [showAddMemory, setShowAddMemory] = useState(false)

  useEffect(() => {
    if (userId) {
      loadProfile()
      loadMemories()
      loadAnalytics(userId)
    }
  }, [userId])

  useEffect(() => {
    if (user) {
      setEditForm({
        name: user.name || '',
        email: user.email || '',
        preferences: user.preferences || {}
      })
    }
  }, [user])

  const handleSaveProfile = async () => {
    await updateUser(editForm)
    setIsEditing(false)
  }

  const handleAddMemory = async (e) => {
    e.preventDefault()
    if (!newMemory.content.trim()) return
    
    await addMemory(newMemory)
    setNewMemory({
      content: '',
      memory_type: 'preference',
      importance_score: 5
    })
    setShowAddMemory(false)
  }

  const getMemoryTypeColor = (type) => {
    const colors = {
      preference: 'bg-blue-100 text-blue-800',
      fact: 'bg-green-100 text-green-800',
      emotion: 'bg-pink-100 text-pink-800',
      context: 'bg-gray-100 text-gray-800',
      goal: 'bg-purple-100 text-purple-800',
      interest: 'bg-yellow-100 text-yellow-800'
    }
    return colors[type] || colors.fact
  }

  const personalityProfile = profile?.personality_profile || {}
  const memoryStats = profile?.memory_stats || {}
  const conversationStats = analytics?.conversation_stats || {}

  return (
    <div className="flex-1 overflow-y-auto custom-scrollbar">
      <div className="max-w-4xl mx-auto px-6 py-8 space-y-8">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-bold text-gray-900">User Profile</h1>
            <p className="text-gray-500 mt-1">Manage your personal information and memories</p>
          </div>
        </div>

        {/* Basic Information */}
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
          <div className="flex items-center justify-between mb-6">
            <h2 className="text-lg font-semibold text-gray-900 flex items-center">
              <User className="w-5 h-5 mr-2" />
              Basic Information
            </h2>
            {!isEditing ? (
              <button
                onClick={() => setIsEditing(true)}
                className="flex items-center space-x-2 px-3 py-2 text-sm bg-primary-50 text-primary-600 rounded-lg hover:bg-primary-100 transition-colors"
              >
                <Edit3 className="w-4 h-4" />
                <span>Edit</span>
              </button>
            ) : (
              <div className="flex space-x-2">
                <button
                  onClick={handleSaveProfile}
                  className="flex items-center space-x-2 px-3 py-2 text-sm bg-green-50 text-green-600 rounded-lg hover:bg-green-100 transition-colors"
                >
                  <Save className="w-4 h-4" />
                  <span>Save</span>
                </button>
                <button
                  onClick={() => setIsEditing(false)}
                  className="flex items-center space-x-2 px-3 py-2 text-sm bg-gray-50 text-gray-600 rounded-lg hover:bg-gray-100 transition-colors"
                >
                  <X className="w-4 h-4" />
                  <span>Cancel</span>
                </button>
              </div>
            )}
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Name</label>
              {isEditing ? (
                <input
                  type="text"
                  value={editForm.name}
                  onChange={(e) => setEditForm({...editForm, name: e.target.value})}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                  placeholder="Enter your name"
                />
              ) : (
                <p className="text-gray-900">{user?.name || 'Not set'}</p>
              )}
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Email</label>
              {isEditing ? (
                <input
                  type="email"
                  value={editForm.email}
                  onChange={(e) => setEditForm({...editForm, email: e.target.value})}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                  placeholder="Enter your email"
                />
              ) : (
                <p className="text-gray-900">{user?.email || 'Not set'}</p>
              )}
            </div>

            <div className="md:col-span-2">
              <label className="block text-sm font-medium text-gray-700 mb-2">User ID</label>
              <p className="text-gray-500 font-mono text-sm">{userId}</p>
            </div>
          </div>
        </div>

        {/* Personality Profile */}
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
          <h2 className="text-lg font-semibold text-gray-900 flex items-center mb-6">
            <Heart className="w-5 h-5 mr-2" />
            Personality Profile
          </h2>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            <div>
              <h3 className="text-sm font-medium text-gray-700 mb-2">Communication Style</h3>
              <p className="text-gray-900 capitalize">
                {personalityProfile.communication_style || 'Not analyzed yet'}
              </p>
            </div>

            <div>
              <h3 className="text-sm font-medium text-gray-700 mb-2">Formality Preference</h3>
              <p className="text-gray-900 capitalize">
                {personalityProfile.formality_preference || 'Not analyzed yet'}
              </p>
            </div>

            <div>
              <h3 className="text-sm font-medium text-gray-700 mb-2">Emotional Sensitivity</h3>
              <div className="flex items-center space-x-2">
                <div className="flex-1 bg-gray-200 rounded-full h-2">
                  <div 
                    className="bg-primary-500 h-2 rounded-full transition-all duration-300"
                    style={{ 
                      width: `${(personalityProfile.emotional_sensitivity || 0) * 100}%` 
                    }}
                  />
                </div>
                <span className="text-sm text-gray-600">
                  {Math.round((personalityProfile.emotional_sensitivity || 0) * 100)}%
                </span>
              </div>
            </div>

            {personalityProfile.traits && personalityProfile.traits.length > 0 && (
              <div className="md:col-span-2 lg:col-span-3">
                <h3 className="text-sm font-medium text-gray-700 mb-2">Personality Traits</h3>
                <div className="flex flex-wrap gap-2">
                  {personalityProfile.traits.map((trait, index) => (
                    <span
                      key={index}
                      className="px-3 py-1 bg-primary-100 text-primary-800 rounded-full text-sm"
                    >
                      {trait}
                    </span>
                  ))}
                </div>
              </div>
            )}
          </div>
        </div>

        {/* Statistics */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
            <div className="flex items-center">
              <MessageSquare className="w-8 h-8 text-primary-600" />
              <div className="ml-4">
                <p className="text-2xl font-bold text-gray-900">
                  {conversationStats.total_messages || 0}
                </p>
                <p className="text-sm text-gray-500">Total Messages</p>
              </div>
            </div>
          </div>

          <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
            <div className="flex items-center">
              <Brain className="w-8 h-8 text-green-600" />
              <div className="ml-4">
                <p className="text-2xl font-bold text-gray-900">
                  {memoryStats.total_memories || 0}
                </p>
                <p className="text-sm text-gray-500">Stored Memories</p>
              </div>
            </div>
          </div>

          <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
            <div className="flex items-center">
              <Clock className="w-8 h-8 text-blue-600" />
              <div className="ml-4">
                <p className="text-2xl font-bold text-gray-900">
                  {Math.round(conversationStats.average_tokens_per_response || 0)}
                </p>
                <p className="text-sm text-gray-500">Avg Tokens/Response</p>
              </div>
            </div>
          </div>
        </div>

        {/* Memories */}
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
          <div className="flex items-center justify-between mb-6">
            <h2 className="text-lg font-semibold text-gray-900 flex items-center">
              <Brain className="w-5 h-5 mr-2" />
              Personal Memories
            </h2>
            <button
              onClick={() => setShowAddMemory(true)}
              className="flex items-center space-x-2 px-3 py-2 text-sm bg-primary-50 text-primary-600 rounded-lg hover:bg-primary-100 transition-colors"
            >
              <Plus className="w-4 h-4" />
              <span>Add Memory</span>
            </button>
          </div>

          {showAddMemory && (
            <motion.form
              initial={{ opacity: 0, height: 0 }}
              animate={{ opacity: 1, height: 'auto' }}
              exit={{ opacity: 0, height: 0 }}
              onSubmit={handleAddMemory}
              className="mb-6 p-4 bg-gray-50 rounded-lg space-y-4"
            >
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Memory Content
                </label>
                <textarea
                  value={newMemory.content}
                  onChange={(e) => setNewMemory({...newMemory, content: e.target.value})}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                  rows="3"
                  placeholder="What would you like me to remember?"
                  required
                />
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Memory Type
                  </label>
                  <select
                    value={newMemory.memory_type}
                    onChange={(e) => setNewMemory({...newMemory, memory_type: e.target.value})}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                  >
                    <option value="preference">Preference</option>
                    <option value="fact">Fact</option>
                    <option value="emotion">Emotion</option>
                    <option value="goal">Goal</option>
                    <option value="interest">Interest</option>
                  </select>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Importance (1-10)
                  </label>
                  <input
                    type="number"
                    min="1"
                    max="10"
                    value={newMemory.importance_score}
                    onChange={(e) => setNewMemory({...newMemory, importance_score: parseInt(e.target.value)})}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                  />
                </div>
              </div>

              <div className="flex space-x-2">
                <button
                  type="submit"
                  className="px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition-colors"
                >
                  Add Memory
                </button>
                <button
                  type="button"
                  onClick={() => setShowAddMemory(false)}
                  className="px-4 py-2 bg-gray-200 text-gray-800 rounded-lg hover:bg-gray-300 transition-colors"
                >
                  Cancel
                </button>
              </div>
            </motion.form>
          )}

          <div className="space-y-3">
            {memories.length > 0 ? (
              memories.map((memory, index) => (
                <div
                  key={memory.id || index}
                  className="flex items-start justify-between p-4 bg-gray-50 rounded-lg"
                >
                  <div className="flex-1">
                    <div className="flex items-center space-x-2 mb-2">
                      <span className={`px-2 py-1 rounded-full text-xs font-medium ${getMemoryTypeColor(memory.metadata?.memory_type || 'fact')}`}>
                        {memory.metadata?.memory_type || 'fact'}
                      </span>
                      <span className="text-xs text-gray-500">
                        Importance: {memory.metadata?.importance_score || 1}/10
                      </span>
                    </div>
                    <p className="text-gray-900">{memory.content}</p>
                  </div>
                  <button
                    onClick={() => deleteMemory(memory.id)}
                    className="p-2 text-red-500 hover:bg-red-50 rounded-lg transition-colors"
                  >
                    <Trash2 className="w-4 h-4" />
                  </button>
                </div>
              ))
            ) : (
              <div className="text-center py-8">
                <Brain className="w-12 h-12 text-gray-300 mx-auto mb-3" />
                <p className="text-gray-500">No memories stored yet</p>
                <p className="text-sm text-gray-400 mt-1">
                  Memories will be automatically created as you chat, or you can add them manually
                </p>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  )
}

export default UserProfile
