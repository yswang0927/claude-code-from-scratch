import React, { useState, useEffect } from 'react'
import './App.css'
import ChatInterface from './components/ChatInterface'
import Sidebar from './components/Sidebar'
import { Session } from './types'
import { api } from './api'

function App() {
  const [sessions, setSessions] = useState<Session[]>([])
  const [currentSessionId, setCurrentSessionId] = useState<string | null>(null)
  const [sidebarOpen, setSidebarOpen] = useState(true)

  // 加载会话列表
  useEffect(() => {
    loadSessions()
  }, [])

  const loadSessions = async () => {
    try {
      const data = await api.getSessions()
      setSessions(data.sessions)
      
      // 如果没有当前会话且有会话列表，选择第一个
      if (!currentSessionId && data.sessions.length > 0) {
        setCurrentSessionId(data.sessions[0].id)
      }
    } catch (error) {
      console.error('Failed to load sessions:', error)
    }
  }

  const handleNewChat = async () => {
    try {
      const session = await api.createSession('New Chat')
      setSessions([session, ...sessions])
      setCurrentSessionId(session.id)
    } catch (error) {
      console.error('Failed to create session:', error)
    }
  }

  const handleSelectSession = (sessionId: string) => {
    setCurrentSessionId(sessionId)
  }

  const handleDeleteSession = async (sessionId: string) => {
    try {
      await api.deleteSession(sessionId)
      setSessions(sessions.filter(s => s.id !== sessionId))
      
      // 如果删除的是当前会话，切换到第一个
      if (currentSessionId === sessionId) {
        const remaining = sessions.filter(s => s.id !== sessionId)
        setCurrentSessionId(remaining.length > 0 ? remaining[0].id : null)
      }
    } catch (error) {
      console.error('Failed to delete session:', error)
    }
  }

  return (
    <div className="app">
      <Sidebar
        sessions={sessions}
        currentSessionId={currentSessionId}
        onNewChat={handleNewChat}
        onSelectSession={handleSelectSession}
        onDeleteSession={handleDeleteSession}
        isOpen={sidebarOpen}
        onToggle={() => setSidebarOpen(!sidebarOpen)}
      />
      
      <div className={`main-content ${sidebarOpen ? 'sidebar-open' : ''}`}>
        {currentSessionId ? (
          <ChatInterface 
            sessionId={currentSessionId}
            onToggleSidebar={() => setSidebarOpen(!sidebarOpen)}
          />
        ) : (
          <div className="empty-state">
            <h2>Welcome to AI Agent</h2>
            <p>Start a new conversation to begin</p>
            <button onClick={handleNewChat} className="btn-primary">
              New Chat
            </button>
          </div>
        )}
      </div>
    </div>
  )
}

export default App
