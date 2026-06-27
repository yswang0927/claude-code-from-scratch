#!/usr/bin/env python3
"""
agent_service.py: Unified AI Agent Service Backend

整合s01-s23的核心能力，提供统一的Agent服务接口
"""

import asyncio
import json
import os
import uuid
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional, AsyncGenerator
from dataclasses import dataclass, asdict

# 导入核心能力
from core import (
    client,
    MODEL,
    EXTENDED_TOOLS,
    EXTENDED_DISPATCH,
    dispatch_tools
)


@dataclass
class Message:
    """消息数据结构"""
    id: str
    role: str  # 'user' | 'assistant' | 'system'
    content: str
    timestamp: str
    tool_calls: Optional[List[Dict[str, Any]]] = None


@dataclass
class Session:
    """会话数据结构"""
    id: str
    title: str
    created: str
    updated: str
    messages: List[Message]
    context_files: List[str]  # 添加到上下文的文件路径
    
    
@dataclass
class ContextFile:
    """上下文文件信息"""
    path: str
    content: str
    size: int
    last_modified: str


class AgentService:
    """
    统一的Agent服务类
    整合了流式响应、工具调用、上下文管理等核心能力
    """
    
    def __init__(self, sessions_dir: str = ".sessions"):
        self.sessions_dir = Path(sessions_dir)
        self.sessions_dir.mkdir(exist_ok=True)
        
        # 活跃会话缓存 {session_id: Session}
        self.active_sessions: Dict[str, Session] = {}
        
        # 系统提示词
        self.system_prompt = self._build_system_prompt()
        
    def _build_system_prompt(self) -> str:
        """构建系统提示词"""
        return (
            f"You are an AI coding assistant with access to file operations. "
            f"Current working directory: {os.getcwd()}. "
            f"You can read, write, search files and execute shell commands. "
            f"Always be helpful, accurate, and concise."
        )
    
    # ==================== 会话管理 ====================
    
    def create_session(self, title: str = "New Chat") -> Session:
        """创建新会话"""
        session = Session(
            id=uuid.uuid4().hex[:12],
            title=title,
            created=datetime.now().isoformat(),
            updated=datetime.now().isoformat(),
            messages=[],
            context_files=[]
        )
        self.active_sessions[session.id] = session
        self._save_session(session)
        return session
    
    def get_session(self, session_id: str) -> Optional[Session]:
        """获取会话"""
        if session_id in self.active_sessions:
            return self.active_sessions[session_id]
        
        # 从磁盘加载
        session_file = self.sessions_dir / f"{session_id}.json"
        if session_file.exists():
            data = json.loads(session_file.read_text(encoding="utf-8"))
            session = Session(
                id=data["id"],
                title=data["title"],
                created=data["created"],
                updated=data["updated"],
                messages=[Message(**m) for m in data["messages"]],
                context_files=data.get("context_files", [])
            )
            self.active_sessions[session_id] = session
            return session
        return None
    
    def list_sessions(self) -> List[Dict[str, Any]]:
        """列出所有会话"""
        sessions = []
        for file in sorted(self.sessions_dir.glob("*.json"), 
                          key=lambda p: p.stat().st_mtime, 
                          reverse=True):
            try:
                data = json.loads(file.read_text(encoding="utf-8"))
                sessions.append({
                    "id": data["id"],
                    "title": data["title"],
                    "created": data["created"],
                    "updated": data["updated"],
                    "message_count": len(data["messages"])
                })
            except Exception:
                continue
        return sessions
    
    def delete_session(self, session_id: str) -> bool:
        """删除会话"""
        session_file = self.sessions_dir / f"{session_id}.json"
        if session_file.exists():
            session_file.unlink()
            if session_id in self.active_sessions:
                del self.active_sessions[session_id]
            return True
        return False
    
    def _save_session(self, session: Session):
        """保存会话到磁盘"""
        session.updated = datetime.now().isoformat()
        session_file = self.sessions_dir / f"{session.id}.json"
        
        data = {
            "id": session.id,
            "title": session.title,
            "created": session.created,
            "updated": session.updated,
            "messages": [asdict(m) for m in session.messages],
            "context_files": session.context_files
        }
        session_file.write_text(json.dumps(data, indent=2, ensure_ascii=False), 
                               encoding="utf-8")
    
    # ==================== 上下文文件管理 ====================
    
    def add_context_file(self, session_id: str, file_path: str) -> Dict[str, Any]:
        """添加文件到上下文"""
        session = self.get_session(session_id)
        if not session:
            return {"error": "Session not found"}
        
        path = Path(file_path)
        if not path.exists():
            return {"error": "File not found"}
        
        # 读取文件内容
        try:
            if path.is_file():
                content = path.read_text(encoding="utf-8")
                size = len(content)
            else:
                # 目录：列出文件结构
                content = self._get_directory_structure(path)
                size = len(content)
            
            # 添加到会话上下文
            if file_path not in session.context_files:
                session.context_files.append(file_path)
                self._save_session(session)
            
            return {
                "path": file_path,
                "type": "file" if path.is_file() else "directory",
                "size": size,
                "preview": content[:500] + ("..." if size > 500 else "")
            }
        except Exception as e:
            return {"error": str(e)}
    
    def remove_context_file(self, session_id: str, file_path: str) -> bool:
        """从上下文移除文件"""
        session = self.get_session(session_id)
        if session and file_path in session.context_files:
            session.context_files.remove(file_path)
            self._save_session(session)
            return True
        return False
    
    def get_context_files(self, session_id: str) -> List[Dict[str, Any]]:
        """获取会话的上下文文件列表"""
        session = self.get_session(session_id)
        if not session:
            return []
        
        files = []
        for file_path in session.context_files:
            path = Path(file_path)
            if path.exists():
                files.append({
                    "path": file_path,
                    "type": "file" if path.is_file() else "directory",
                    "size": path.stat().st_size if path.is_file() else 0
                })
        return files
    
    def _get_directory_structure(self, path: Path, max_depth: int = 3, 
                                 current_depth: int = 0) -> str:
        """获取目录结构"""
        if current_depth >= max_depth:
            return ""
        
        lines = []
        try:
            for item in sorted(path.iterdir()):
                indent = "  " * current_depth
                if item.is_file():
                    lines.append(f"{indent}📄 {item.name}")
                elif item.is_dir():
                    lines.append(f"{indent}📁 {item.name}/")
                    if current_depth < max_depth - 1:
                        lines.append(self._get_directory_structure(
                            item, max_depth, current_depth + 1
                        ))
        except PermissionError:
            lines.append(f"{'  ' * current_depth}(Permission denied)")
        
        return "\n".join(filter(None, lines))
    
    # ==================== 对话处理 ====================
    
    async def chat_stream(
        self, 
        session_id: str, 
        user_message: str,
        include_context: bool = True
    ) -> AsyncGenerator[Dict[str, Any], None]:
        """
        流式对话处理
        
        Yields:
            Dict with keys:
            - type: 'thinking' | 'text' | 'tool_call' | 'tool_result' | 'done' | 'error'
            - content: str
            - metadata: Optional[Dict]
        """
        session = self.get_session(session_id)
        if not session:
            yield {"type": "error", "content": "Session not found"}
            return
        
        # 构建消息历史
        messages = self._build_message_history(session, user_message, include_context)
        
        # 添加用户消息到会话
        user_msg = Message(
            id=uuid.uuid4().hex[:8],
            role="user",
            content=user_message,
            timestamp=datetime.now().isoformat()
        )
        session.messages.append(user_msg)
        
        # 开始Agent循环
        assistant_content_parts = []
        
        try:
            while True:
                yield {"type": "thinking", "content": ""}
                
                # 调用LLM (流式)
                async for chunk in self._stream_llm_response(messages):
                    if chunk["type"] == "text":
                        assistant_content_parts.append(chunk["content"])
                        yield chunk
                    elif chunk["type"] == "response":
                        response = chunk["response"]
                        break
                
                # 记录助手响应
                messages.append({"role": "assistant", "content": response.content})
                
                # 检查是否需要调用工具
                if response.stop_reason != "tool_use":
                    # 对话结束
                    break
                
                # 执行工具调用
                tool_results = []
                for block in response.content:
                    if block.type == "tool_use":
                        yield {
                            "type": "tool_call",
                            "content": f"🔧 {block.name}",
                            "metadata": {"name": block.name, "input": block.input}
                        }
                        
                        # 执行工具
                        result = await self._execute_tool(block.name, block.input)
                        
                        yield {
                            "type": "tool_result",
                            "content": result[:200] + ("..." if len(result) > 200 else ""),
                            "metadata": {"tool": block.name}
                        }
                        
                        tool_results.append({
                            "type": "tool_result",
                            "tool_use_id": block.id,
                            "content": result
                        })
                
                # 将工具结果添加到消息历史
                messages.append({"role": "user", "content": tool_results})
            
            # 保存助手消息
            assistant_msg = Message(
                id=uuid.uuid4().hex[:8],
                role="assistant",
                content="".join(assistant_content_parts),
                timestamp=datetime.now().isoformat()
            )
            session.messages.append(assistant_msg)
            self._save_session(session)
            
            yield {"type": "done", "content": ""}
            
        except Exception as e:
            yield {"type": "error", "content": str(e)}
    
    def _build_message_history(
        self, 
        session: Session, 
        current_message: str,
        include_context: bool
    ) -> List[Dict[str, Any]]:
        """构建完整的消息历史（包括上下文文件）"""
        messages = []
        
        # 添加上下文文件（如果有）
        if include_context and session.context_files:
            context_content = self._build_context_content(session.context_files)
            messages.append({
                "role": "user",
                "content": f"[Context Files]\n\n{context_content}"
            })
            messages.append({
                "role": "assistant",
                "content": "I've reviewed the context files. How can I help you?"
            })
        
        # 添加历史消息（保留最近20条）
        for msg in session.messages[-20:]:
            messages.append({
                "role": msg.role,
                "content": msg.content
            })
        
        # 添加当前用户消息
        messages.append({
            "role": "user",
            "content": current_message
        })
        
        return messages
    
    def _build_context_content(self, file_paths: List[str]) -> str:
        """构建上下文文件内容"""
        parts = []
        for file_path in file_paths:
            path = Path(file_path)
            if not path.exists():
                continue
            
            try:
                if path.is_file():
                    content = path.read_text(encoding="utf-8")
                    parts.append(f"=== {file_path} ===\n{content}\n")
                else:
                    structure = self._get_directory_structure(path)
                    parts.append(f"=== {file_path}/ ===\n{structure}\n")
            except Exception as e:
                parts.append(f"=== {file_path} ===\nError: {e}\n")
        
        return "\n".join(parts)
    
    async def _stream_llm_response(
        self, 
        messages: List[Dict[str, Any]]
    ) -> AsyncGenerator[Dict[str, Any], None]:
        """流式调用LLM"""
        loop = asyncio.get_event_loop()
        
        def _blocking_stream():
            with client.messages.stream(
                model=MODEL,
                system=self.system_prompt,
                messages=messages,
                tools=EXTENDED_TOOLS,
                max_tokens=8000,
            ) as stream:
                for text in stream.text_stream:
                    yield {"type": "text", "content": text}
                yield {"type": "response", "response": stream.get_final_message()}
        
        # 在线程池中执行同步流式调用
        for chunk in await loop.run_in_executor(None, lambda: list(_blocking_stream())):
            yield chunk
    
    async def _execute_tool(self, tool_name: str, tool_input: Dict[str, Any]) -> str:
        """执行工具调用"""
        handler = EXTENDED_DISPATCH.get(tool_name)
        if not handler:
            return f"Error: Unknown tool '{tool_name}'"
        
        try:
            # 如果handler是async函数
            if asyncio.iscoroutinefunction(handler):
                result = await handler(tool_input)
            else:
                # 在线程池中执行同步handler
                loop = asyncio.get_event_loop()
                result = await loop.run_in_executor(None, handler, tool_input)
            
            return str(result)
        except Exception as e:
            return f"Tool execution error: {e}"


# 创建全局服务实例
agent_service = AgentService()
