import { Session, SessionDetail, ContextFile } from './types'

const API_BASE = '/api'

export const api = {
  // 会话管理
  async getSessions(): Promise<{ sessions: Session[] }> {
    const res = await fetch(`${API_BASE}/sessions`)
    return res.json()
  },

  async getSession(sessionId: string): Promise<SessionDetail> {
    const res = await fetch(`${API_BASE}/sessions/${sessionId}`)
    return res.json()
  },

  async createSession(title: string = 'New Chat'): Promise<Session> {
    const res = await fetch(`${API_BASE}/sessions`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ title })
    })
    return res.json()
  },

  async deleteSession(sessionId: string): Promise<void> {
    await fetch(`${API_BASE}/sessions/${sessionId}`, {
      method: 'DELETE'
    })
  },

  // 上下文文件管理
  async getContextFiles(sessionId: string): Promise<{ files: ContextFile[] }> {
    const res = await fetch(`${API_BASE}/context/${sessionId}`)
    return res.json()
  },

  async addContextFile(sessionId: string, filePath: string): Promise<ContextFile> {
    const res = await fetch(`${API_BASE}/context/add`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ session_id: sessionId, file_path: filePath })
    })
    return res.json()
  },

  async removeContextFile(sessionId: string, filePath: string): Promise<void> {
    await fetch(`${API_BASE}/context/remove`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ session_id: sessionId, file_path: filePath })
    })
  },

  // 文件系统浏览
  async listDirectory(path: string = '.'): Promise<{
    current_path: string
    parent_path: string | null
    items: Array<{ name: string; path: string; type: string; size: number }>
  }> {
    const res = await fetch(`${API_BASE}/filesystem/list?path=${encodeURIComponent(path)}`)
    return res.json()
  }
}
