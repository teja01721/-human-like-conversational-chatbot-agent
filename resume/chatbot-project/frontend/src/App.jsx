import React, { useState, useEffect } from 'react'
import { Toaster } from 'react-hot-toast'
import ChatInterface from './components/ChatInterface'
import Sidebar from './components/Sidebar'
import UserProfile from './components/UserProfile'
import { ChatProvider } from './contexts/ChatContext'
import { UserProvider } from './contexts/UserContext'

function App() {
  const [sidebarOpen, setSidebarOpen] = useState(true)
  const [currentView, setCurrentView] = useState('chat')

  return (
    <UserProvider>
      <ChatProvider>
        <div className="flex h-screen bg-gray-50">
          <Toaster 
            position="top-right"
            toastOptions={{
              duration: 3000,
              style: {
                background: '#363636',
                color: '#fff',
              },
            }}
          />
          
          {/* Sidebar */}
          <Sidebar 
            isOpen={sidebarOpen}
            onToggle={() => setSidebarOpen(!sidebarOpen)}
            currentView={currentView}
            onViewChange={setCurrentView}
          />
          
          {/* Main Content */}
          <div className="flex-1 flex flex-col">
            {currentView === 'chat' && <ChatInterface />}
            {currentView === 'profile' && <UserProfile />}
          </div>
        </div>
      </ChatProvider>
    </UserProvider>
  )
}

export default App
