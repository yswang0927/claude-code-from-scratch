import React, { useState, useEffect, useRef } from 'react'
import { Menu, File, FolderOpen, X, Send, Loader } from 'lucide-react'
import ReactMarkdown from 'react-markdown'
import remarkGfm from 'remark-gfm'
import { SessionDetail, Message, ContextFile, StreamChunk, ToolCall } from '../types'
import { api } from '../api'
import FileBrowser from './FileBrowser'
import './ChatInterface.css'

interface ChatInterfaceProps {
  sessionId: string
  onToggleSidebar: () => void
}

const ChatInterface: React.FC<ChatInterfaceProps> = ({ sessionId, onToggleSidebar }) => {
  const [session, setSession] = useState<SessionDetail | null>(null)
  const [messages, setMessages] = useState<Message[]>([])
  const [input, setInput] = useState('')
  const [isStreaming, setIsStreaming] = useState(false)
  const [streamingContent, setStreamingContent] = useState('')
  const [contextFiles, setContextFiles] = useState<ContextFile[]>([])
  const [showFileBrowser, setShowFileBrowser] = useState(false)
  
  const messagesEndRef = useRef<HTMLDivElement>(null)
  const wsRef = useRef<WebSocket | null>(null)
  const markdownPlugins = [remarkGfm]

  const formatJson = (value: any) => {
    if (value === undefined || value === null || value === '') return ''
    try {
      return JSON.stringify(value, null, 2)
    } catch {
      return String(value)
    }
  }

  const appendToolCall = (chunk: StreamChunk) => {
    const toolName = chunk.metadata?.name || chunk.content.replace(/^🔧\s*/, '')
    const input = formatJson(chunk.metadata?.input)
    const inputBlock = input ? `\n\nInput:\n\`\`\`json\n${input}\n\`\`\`` : ''
    setStreamingContent(prev => `${prev}\n\n🔧 **Tool:** \`${toolName}\`${inputBlock}\n`)
  }

  const appendToolResult = (chunk: StreamChunk) => {
    const toolName = chunk.metadata?.tool ? ` \`${chunk.metadata.tool}\`` : ''
    setStreamingContent(prev => `${prev}\n**Result${toolName}:**\n\`\`\`text\n${chunk.content}\n\`\`\`\n`)
  }

  const renderToolCalls = (toolCalls?: ToolCall[]) => {
    if (!toolCalls?.length) return null;

    return (
      <div className="tool-calls">
        {toolCalls.map((toolCall, index) => (
          <details className="tool-call-card" key={`${toolCall.name}-${index}`}>
            <summary>🔧 {toolCall.name}</summary>
            {toolCall.input !== undefined && (
              <>
                <div className="tool-section-label">Input</div>
                <pre>{formatJson(toolCall.input)}</pre>
              </>
            )}
            {toolCall.result && (
              <>
                <div className="tool-section-label">Result</div>
                <pre>{toolCall.result}</pre>
              </>
            )}
          </details>
        ))}
      </div>
    )
  }

  // 加载会话详情
  useEffect(() => {
    loadSession()
    loadContextFiles()
  }, [sessionId])

  // 自动滚动到底部
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages, streamingContent])

  const loadSession = async () => {
    try {
      const data = await api.getSession(sessionId)
      setSession(data)
      setMessages(data.messages)
    } catch (error) {
      console.error('Failed to load session:', error)
    }
  }

  const loadContextFiles = async () => {
    try {
      const data = await api.getContextFiles(sessionId)
      setContextFiles(data.files)
    } catch (error) {
      console.error('Failed to load context files:', error)
    }
  }

  const connectWebSocket = () => {
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:'
    const ws = new WebSocket(`${protocol}//${window.location.host}/ws/chat`)
    
    ws.onopen = () => {
      console.log('WebSocket connected')
    }
    
    ws.onmessage = async (event) => {
      const chunk: StreamChunk = JSON.parse(event.data)
      console.log(event.data);

      switch (chunk.type) {
        case 'thinking':
          // 后端每一轮模型思考前都会发送 thinking；不要清空已收到的工具日志。
          break
        
        case 'text':
          setStreamingContent(prev => prev + chunk.content)
          break
        
        case 'tool_call':
          appendToolCall(chunk)
          break
        
        case 'tool_result':
          appendToolResult(chunk)
          break
        
        case 'done':
          // 流式完成后先加载持久化消息，再清掉临时流内容，避免工具信息闪一下消失。
          await loadSession()
          setIsStreaming(false)
          setStreamingContent('')
          break
        
        case 'error':
          console.error('Stream error:', chunk.content)
          setStreamingContent(prev => prev + `\n\n❌ Error: ${chunk.content}`)
          setIsStreaming(false)
          break
      }
    }
    
    ws.onerror = (error) => {
      console.error('WebSocket error:', error)
      setIsStreaming(false)
    }
    
    ws.onclose = () => {
      console.log('WebSocket closed')
      wsRef.current = null
    }
    
    wsRef.current = ws
    return ws
  }

  const handleSendMessage = async () => {
    if (!input.trim() || isStreaming) return

    const userMessage = input.trim()
    setInput('')
    setIsStreaming(true)
    setStreamingContent('')

    // 添加用户消息到界面
    const tempMessage: Message = {
      id: Date.now().toString(),
      role: 'user',
      content: userMessage,
      timestamp: new Date().toISOString()
    }
    setMessages(prev => [...prev, tempMessage])

    // 连接WebSocket并发送消息
    const ws = wsRef.current || connectWebSocket()
    
    // 等待连接打开
    if (ws.readyState === WebSocket.CONNECTING) {
      ws.addEventListener('open', () => {
        ws.send(JSON.stringify({
          session_id: sessionId,
          message: userMessage,
          include_context: contextFiles.length > 0
        }))
      }, { once: true })
    } else if (ws.readyState === WebSocket.OPEN) {
      ws.send(JSON.stringify({
        session_id: sessionId,
        message: userMessage,
        include_context: contextFiles.length > 0
      }))
    }
  }

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSendMessage()
    }
  }

  const handleAddFile = async (filePath: string) => {
    try {
      const file = await api.addContextFile(sessionId, filePath)
      setContextFiles(prev => [...prev, file])
      setShowFileBrowser(false)
    } catch (error) {
      console.error('Failed to add context file:', error)
      alert('Failed to add file to context')
    }
  }

  const handleRemoveFile = async (filePath: string) => {
    try {
      await api.removeContextFile(sessionId, filePath)
      setContextFiles(prev => prev.filter(f => f.path !== filePath))
    } catch (error) {
      console.error('Failed to remove context file:', error)
    }
  }

  return (
    <div className="chat-interface">
      {/* Header */}
      <div className="chat-header">
        <button className="btn-icon" onClick={onToggleSidebar}>
          <Menu size={20} />
        </button>
        <h2>{session?.title || 'Chat'}</h2>
        <button 
          className="btn-icon"
          onClick={() => setShowFileBrowser(!showFileBrowser)}
          title="Add files to context"
        >
          <FolderOpen size={20} />
        </button>
      </div>

      {/* Context Files Bar */}
      {contextFiles.length > 0 && (
        <div className="context-bar">
          <div className="context-label">Context:</div>
          {contextFiles.map(file => (
            <div key={file.path} className="context-chip">
              <File size={14} />
              <span>{file.path.split('/').pop()}</span>
              <button onClick={() => handleRemoveFile(file.path)}>
                <X size={12} />
              </button>
            </div>
          ))}
        </div>
      )}

      {/* Messages */}
      <div className="messages-container">
        {messages.map(message => (
          <div key={message.id} className={`message ${message.role}`}>
            <div className="message-avatar">
              {message.role === 'user' ? '👤' : '🤖'}
            </div>
            <div className="message-content">
              {renderToolCalls(message.tool_calls)}
              <ReactMarkdown remarkPlugins={markdownPlugins}>{message.content}</ReactMarkdown>
            </div>
          </div>
        ))}

        {/* Streaming message */}
        {isStreaming && streamingContent && (
          <div className="message assistant streaming">
            <div className="message-avatar">🤖</div>
            <div className="message-content">
              <ReactMarkdown remarkPlugins={markdownPlugins}>{streamingContent}</ReactMarkdown>
            </div>
          </div>
        )}

        {/* Thinking indicator */}
        {isStreaming && !streamingContent && (
          <div className="message assistant">
            <div className="message-avatar">🤖</div>
            <div className="message-content">
              <div className="thinking">
                <Loader className="spinner" size={16} />
                <span>Thinking...</span>
              </div>
            </div>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      {/* Input Area */}
      <div className="input-container">
        <textarea
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyPress={handleKeyPress}
          placeholder="Type your message... (Shift+Enter for new line)"
          rows={1}
          disabled={isStreaming}
        />
        <button
          onClick={handleSendMessage}
          disabled={!input.trim() || isStreaming}
          className="send-button"
        >
          <Send size={20} />
        </button>
      </div>

      {/* File Browser Modal */}
      {showFileBrowser && (
        <FileBrowser
          onSelect={handleAddFile}
          onClose={() => setShowFileBrowser(false)}
        />
      )}
    </div>
  )
}

export default ChatInterface
