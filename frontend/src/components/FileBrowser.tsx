import React, { useState, useEffect } from 'react'
import { Folder, File, ChevronRight, X } from 'lucide-react'
import { api } from '../api'
import './FileBrowser.css'

interface FileBrowserProps {
  onSelect: (path: string) => void
  onClose: () => void
}

interface FileItem {
  name: string
  path: string
  type: 'file' | 'directory'
  size: number
}

const FileBrowser: React.FC<FileBrowserProps> = ({ onSelect, onClose }) => {
  const [currentPath, setCurrentPath] = useState('.')
  const [parentPath, setParentPath] = useState<string | null>(null)
  const [items, setItems] = useState<FileItem[]>([])
  const [loading, setLoading] = useState(false)

  useEffect(() => {
    loadDirectory(currentPath)
  }, [currentPath])

  const loadDirectory = async (path: string) => {
    setLoading(true)
    try {
      const data = await api.listDirectory(path)
      setItems(data.items)
      setParentPath(data.parent_path)
    } catch (error) {
      console.error('Failed to load directory:', error)
      alert('Failed to load directory')
    } finally {
      setLoading(false)
    }
  }

  const handleItemClick = (item: FileItem) => {
    if (item.type === 'directory') {
      setCurrentPath(item.path)
    } else {
      onSelect(item.path)
    }
  }

  const handleGoUp = () => {
    if (parentPath) {
      setCurrentPath(parentPath)
    }
  }

  const formatSize = (bytes: number) => {
    if (bytes < 1024) return `${bytes} B`
    if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`
    return `${(bytes / (1024 * 1024)).toFixed(1)} MB`
  }

  return (
    <div className="file-browser-overlay" onClick={onClose}>
      <div className="file-browser" onClick={(e) => e.stopPropagation()}>
        <div className="file-browser-header">
          <h3>Select File or Directory</h3>
          <button className="btn-icon" onClick={onClose}>
            <X size={20} />
          </button>
        </div>

        <div className="file-browser-path">
          {parentPath && (
            <button className="path-up" onClick={handleGoUp}>
              ← Back
            </button>
          )}
          <span className="current-path">{currentPath}</span>
        </div>

        <div className="file-browser-content">
          {loading ? (
            <div className="loading">Loading...</div>
          ) : (
            <div className="file-list">
              {items.map((item) => (
                <div
                  key={item.path}
                  className="file-item"
                  onClick={() => handleItemClick(item)}
                >
                  <div className="file-icon">
                    {item.type === 'directory' ? (
                      <Folder size={18} />
                    ) : (
                      <File size={18} />
                    )}
                  </div>
                  <div className="file-info">
                    <div className="file-name">{item.name}</div>
                    {item.type === 'file' && (
                      <div className="file-size">{formatSize(item.size)}</div>
                    )}
                  </div>
                  {item.type === 'directory' && (
                    <ChevronRight size={18} className="file-arrow" />
                  )}
                </div>
              ))}
              {items.length === 0 && (
                <div className="empty-directory">Empty directory</div>
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  )
}

export default FileBrowser
