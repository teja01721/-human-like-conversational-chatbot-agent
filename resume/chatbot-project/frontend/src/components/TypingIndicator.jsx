import React from 'react'

function TypingIndicator() {
  return (
    <div className="typing-indicator">
      <div 
        className="typing-dot" 
        style={{ '--delay': '0ms' }}
      />
      <div 
        className="typing-dot" 
        style={{ '--delay': '150ms' }}
      />
      <div 
        className="typing-dot" 
        style={{ '--delay': '300ms' }}
      />
    </div>
  )
}

export default TypingIndicator
