export interface Message {
  id: string
  role: 'user' | 'assistant' | 'system'
  content: string
  timestamp: string
  tool_calls?: ToolCall[]
}

export interface ToolCall {
  name: string
  input: any
  result?: string
}

export interface Session {
  id: string
  title: string
  created: string
  updated?: string
  message_count?: number
}

export interface SessionDetail extends Session {
  messages: Message[]
  context_files: string[]
}

export interface ContextFile {
  path: string
  type: 'file' | 'directory'
  size: number
  preview?: string
}

export interface StreamChunk {
  type: 'thinking' | 'text' | 'tool_call' | 'tool_result' | 'done' | 'error'
  content: string
  metadata?: any
}
