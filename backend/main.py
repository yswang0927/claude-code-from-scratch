#!/usr/bin/env python3
"""
main.py: FastAPI Backend Server

提供RESTful API和WebSocket接口
"""

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
from dataclasses import asdict, is_dataclass
import json

from agent_service import agent_service

app = FastAPI(title="AI Agent Service", version="1.0.0")

# CORS配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ==================== Pydantic Models ====================

class CreateSessionRequest(BaseModel):
    title: Optional[str] = "New Chat"


class ChatRequest(BaseModel):
    session_id: str
    message: str
    include_context: bool = True


class AddContextFileRequest(BaseModel):
    session_id: str
    file_path: str


class RemoveContextFileRequest(BaseModel):
    session_id: str
    file_path: str


def serialize_message(message):
    """序列化消息，确保旧内存对象也包含 tool_calls 字段。"""
    if is_dataclass(message):
        data = asdict(message)
    else:
        data = {
            "id": getattr(message, "id", None),
            "role": getattr(message, "role", None),
            "content": getattr(message, "content", ""),
            "timestamp": getattr(message, "timestamp", None),
        }
    data.setdefault("tool_calls", getattr(message, "tool_calls", None))
    return data


# ==================== REST API Endpoints ====================

@app.get("/")
async def root():
    """健康检查"""
    return {
        "status": "ok",
        "service": "AI Agent Service",
        "version": "1.0.0"
    }


@app.post("/api/sessions")
async def create_session(request: CreateSessionRequest):
    """创建新会话"""
    session = agent_service.create_session(request.title)
    return {
        "id": session.id,
        "title": session.title,
        "created": session.created
    }


@app.get("/api/sessions")
async def list_sessions():
    """获取会话列表"""
    sessions = agent_service.list_sessions()
    return {"sessions": sessions}


@app.get("/api/sessions/{session_id}")
async def get_session(session_id: str):
    """获取会话详情"""
    session = agent_service.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    return {
        "id": session.id,
        "title": session.title,
        "created": session.created,
        "updated": session.updated,
        "messages": [serialize_message(m) for m in session.messages],
        "context_files": session.context_files
    }


@app.delete("/api/sessions/{session_id}")
async def delete_session(session_id: str):
    """删除会话"""
    success = agent_service.delete_session(session_id)
    if not success:
        raise HTTPException(status_code=404, detail="Session not found")
    return {"success": True}


@app.post("/api/context/add")
async def add_context_file(request: AddContextFileRequest):
    """添加上下文文件"""
    result = agent_service.add_context_file(request.session_id, request.file_path)
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    return result


@app.post("/api/context/remove")
async def remove_context_file(request: RemoveContextFileRequest):
    """移除上下文文件"""
    success = agent_service.remove_context_file(request.session_id, request.file_path)
    if not success:
        raise HTTPException(status_code=404, detail="Context file not found")
    return {"success": True}


@app.get("/api/context/{session_id}")
async def get_context_files(session_id: str):
    """获取会话的上下文文件"""
    files = agent_service.get_context_files(session_id)
    return {"files": files}


# ==================== WebSocket Endpoint ====================

@app.websocket("/ws/chat")
async def websocket_chat(websocket: WebSocket):
    """WebSocket流式对话接口"""
    await websocket.accept()
    
    try:
        while True:
            # 接收消息
            data = await websocket.receive_text()
            request = json.loads(data)
            
            session_id = request.get("session_id")
            message = request.get("message")
            include_context = request.get("include_context", True)
            
            if not session_id or not message:
                await websocket.send_json({
                    "type": "error",
                    "content": "Missing session_id or message"
                })
                continue
            
            # 流式处理对话
            async for chunk in agent_service.chat_stream(
                session_id, 
                message,
                include_context
            ):
                await websocket.send_json(chunk)
    
    except WebSocketDisconnect:
        print("Client disconnected")
    except Exception as e:
        print(f"WebSocket error: {e}")
        try:
            await websocket.send_json({
                "type": "error",
                "content": str(e)
            })
        except:
            pass


# ==================== File System API ====================

@app.get("/api/filesystem/list")
async def list_directory(path: str = "."):
    """列出目录内容"""
    from pathlib import Path
    
    try:
        dir_path = Path(path)
        if not dir_path.exists():
            raise HTTPException(status_code=404, detail="Path not found")
        
        if not dir_path.is_dir():
            raise HTTPException(status_code=400, detail="Path is not a directory")
        
        items = []
        for item in sorted(dir_path.iterdir()):
            # 跳过隐藏文件和常见的排除目录
            if item.name.startswith('.') or item.name in ['node_modules', '__pycache__', 'venv']:
                continue
            
            items.append({
                "name": item.name,
                "path": str(item),
                "type": "file" if item.is_file() else "directory",
                "size": item.stat().st_size if item.is_file() else 0
            })
        
        return {
            "current_path": str(dir_path.absolute()),
            "parent_path": str(dir_path.parent.absolute()) if dir_path.parent != dir_path else None,
            "items": items
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")
