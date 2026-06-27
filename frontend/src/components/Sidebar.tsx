import React from 'react'
import { MessageSquare, Plus, Trash2, Menu } from 'lucide-react'
import { Session } from '../types'
import './Sidebar.css'

interface SidebarProps {
  sessions: Session[]
  currentSessionId: string | null
  onNewChat: () => void
  onSelectSession: (sessionId: string) => void
  onDeleteSession: (sessionId: string) => void
  isOpen: boolean
  onToggle: () => void
}

const Sidebar: React.FC<SidebarProps> = ({
  sessions,
  currentSessionId,
  onNewChat,
  onSelectSession,
  onDeleteSession,
  isOpen
}) => {
  const formatDate = (dateStr: string) => {
    const date = new Date(dateStr)
    const now = new Date()
    const diff = now.getTime() - date.getTime()
    const days = Math.floor(diff / (1000 * 60 * 60 * 24))
    
    if (days === 0) return 'Today'
    if (days === 1) return 'Yesterday'
    if (days < 7) return `${days} days ago`
    return date.toLocaleDateString()
  }

  if (!isOpen) return null

  return (
    <div className="sidebar">
      <div className="sidebar-header">
        <h1>AI Agent</h1>
        <button 
          className="btn-icon"
          onClick={onNewChat}
          title="New Chat"
        >
          <Plus size={20} />
        </button>
      </div>

      <div className="session-list">
        {sessions.map(session => (
          <div
            key={session.id}
            className={`session-item ${currentSessionId === session.id ? 'active' : ''}`}
            onClick={() => onSelectSession(session.id)}
          >
            <div className="session-icon">
              <MessageSquare size={16} />
            </div>
            <div className="session-info">
              <div className="session-title">{session.title}</div>
              <div className="session-meta">
                {formatDate(session.created)} • {session.message_count || 0} messages
              </div>
            </div>
            <button
              className="btn-icon-small"
              onClick={(e) => {
                e.stopPropagation()
                if (window.confirm('Delete this conversation?')) {
                  onDeleteSession(session.id)
                }
              }}
              title="Delete"
            >
              <Trash2 size={14} />
            </button>
          </div>
        ))}
      </div>

      <div className="sidebar-footer">
        <div className="sidebar-info">
          Simple Claude • Powered by Anthropic
        </div>
      </div>
    </div>
  )
}

export default Sidebar
