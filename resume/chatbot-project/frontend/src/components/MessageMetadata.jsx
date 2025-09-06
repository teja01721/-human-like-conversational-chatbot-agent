import React from 'react'
import { ChevronDown, ChevronUp, Clock, Brain, Heart, Zap } from 'lucide-react'
import { motion, AnimatePresence } from 'framer-motion'

function MessageMetadata({ message, isVisible, onToggle }) {
  const formatTime = (ms) => {
    if (ms < 1000) return `${Math.round(ms)}ms`
    return `${(ms / 1000).toFixed(1)}s`
  }

  const getEmotionIcon = (emotion) => {
    const icons = {
      joy: '😊',
      sadness: '😢',
      anger: '😠',
      fear: '😨',
      surprise: '😲',
      disgust: '🤢'
    }
    return icons[emotion] || '😐'
  }

  const getDominantEmotion = (emotions) => {
    if (!emotions || Object.keys(emotions).length === 0) return null
    return Object.entries(emotions).reduce((a, b) => 
      emotions[a[0]] > emotions[b[0]] ? a : b
    )
  }

  const dominantEmotion = getDominantEmotion(message.emotion_detected)

  return (
    <div className="mt-3">
      <button
        onClick={onToggle}
        className="flex items-center space-x-2 text-xs text-gray-500 hover:text-gray-700 transition-colors"
      >
        <span>Message details</span>
        {isVisible ? <ChevronUp className="w-3 h-3" /> : <ChevronDown className="w-3 h-3" />}
      </button>

      <AnimatePresence>
        {isVisible && (
          <motion.div
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: 'auto' }}
            exit={{ opacity: 0, height: 0 }}
            className="mt-2 p-3 bg-gray-50 rounded-lg text-xs space-y-2"
          >
            {/* Response Time & Tokens */}
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-2">
                <Clock className="w-3 h-3 text-gray-400" />
                <span className="text-gray-600">
                  Response time: {formatTime(message.response_time * 1000)}
                </span>
              </div>
              <div className="flex items-center space-x-2">
                <Zap className="w-3 h-3 text-gray-400" />
                <span className="text-gray-600">
                  {message.tokens_used} tokens
                </span>
              </div>
            </div>

            {/* Tone Used */}
            {message.tone_used && (
              <div className="flex items-center space-x-2">
                <Heart className="w-3 h-3 text-gray-400" />
                <span className="text-gray-600">
                  Tone: <span className="font-medium text-primary-600">{message.tone_used}</span>
                </span>
              </div>
            )}

            {/* Dominant Emotion */}
            {dominantEmotion && (
              <div className="flex items-center space-x-2">
                <span className="text-sm">{getEmotionIcon(dominantEmotion[0])}</span>
                <span className="text-gray-600">
                  Detected emotion: <span className="font-medium">{dominantEmotion[0]}</span>
                  <span className="text-gray-500 ml-1">
                    ({Math.round(dominantEmotion[1] * 100)}%)
                  </span>
                </span>
              </div>
            )}

            {/* Memory Recalled */}
            {message.memory_recalled && message.memory_recalled.length > 0 && (
              <div className="space-y-1">
                <div className="flex items-center space-x-2">
                  <Brain className="w-3 h-3 text-gray-400" />
                  <span className="text-gray-600 font-medium">Memories recalled:</span>
                </div>
                <div className="ml-5 space-y-1">
                  {message.memory_recalled.map((memory, index) => (
                    <div key={index} className="text-gray-500 text-xs">
                      • {memory}
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* All Emotions */}
            {message.emotion_detected && Object.keys(message.emotion_detected).length > 0 && (
              <div className="space-y-1">
                <span className="text-gray-600 font-medium">Emotion breakdown:</span>
                <div className="grid grid-cols-2 gap-1 ml-2">
                  {Object.entries(message.emotion_detected).map(([emotion, score]) => (
                    <div key={emotion} className="flex items-center justify-between">
                      <span className="text-gray-500 capitalize">{emotion}:</span>
                      <div className="flex items-center space-x-1">
                        <div className="w-12 h-1 bg-gray-200 rounded-full overflow-hidden">
                          <div 
                            className="h-full bg-primary-400 transition-all duration-300"
                            style={{ width: `${score * 100}%` }}
                          />
                        </div>
                        <span className="text-gray-400 text-xs w-8 text-right">
                          {Math.round(score * 100)}%
                        </span>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  )
}

export default MessageMetadata
