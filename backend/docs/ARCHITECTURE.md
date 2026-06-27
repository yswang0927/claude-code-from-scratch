# 🏗️ 系统架构文档

## 整体架构

```
┌─────────────────────────────────────────────────────────┐
│                    Browser (React)                      │
│  ┌──────────────┐  ┌─────────────┐  ┌──────────────┐  │
│  │ ChatInterface│  │   Sidebar   │  │ FileBrowser  │  │
│  └──────────────┘  └─────────────┘  └──────────────┘  │
└────────────────┬─────────────────────────────┬──────────┘
                 │ HTTP/WebSocket              │
                 ▼                             ▼
┌─────────────────────────────────────────────────────────┐
│              FastAPI Backend (Python)                   │
│  ┌─────────────────────────────────────────────────┐   │
│  │           AgentService (agent_service.py)       │   │
│  │  • Session Management                            │   │
│  │  • Context File Management                       │   │
│  │  • Chat Stream Handler                           │   │
│  │  • Tool Execution                                │   │
│  └────────────────┬────────────────────────────────┘   │
│                   │                                     │
│  ┌────────────────▼────────────────────────────────┐   │
│  │            Core Module (core.py)                │   │
│  │  • Tool Schemas (EXTENDED_TOOLS)                │   │
│  │  • Tool Dispatch (EXTENDED_DISPATCH)            │   │
│  │  • Tool Implementations (bash, read, write...)  │   │
│  └─────────────────────────────────────────────────┘   │
└────────────────┬────────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────────┐
│              Anthropic API (Claude)                     │
│  • Claude 3.5 Sonnet                                    │
│  • Streaming Response                                   │
│  • Tool Use (Function Calling)                          │
└─────────────────────────────────────────────────────────┘
```

## 数据流

### 1. 用户发送消息流程

```
User Input → ChatInterface → WebSocket → AgentService
                                              ↓
                                    Build Message History
                                              ↓
                                       Anthropic API
                                              ↓
                                    Stream Response ← Tool Calls?
                                              │            ↓ Yes
                                              │      Execute Tools
                                              │            ↓
                                              │    Return Results
                                              │            ↓
                                              └────────────┘
                                              ↓ No (Done)
                                    Update Session
                                              ↓
                                        Save to Disk
```

### 2. 工具调用流程

```
Claude Request Tool → AgentService._execute_tool()
                              ↓
                   Lookup in EXTENDED_DISPATCH
                              ↓
                   Execute Handler (bash/read/write...)
                              ↓
                      Return Result String
                              ↓
                   Append to Message History
                              ↓
                   Send Back to Claude
```

## 核心组件说明

### Frontend (React + TypeScript)

#### 1. App.tsx
- 根组件
- 管理全局状态（会话列表、当前会话）
- 协调 Sidebar 和 ChatInterface

#### 2. ChatInterface.tsx
- 核心对话界面
- WebSocket 连接管理
- 流式消息渲染
- 上下文文件管理

#### 3. Sidebar.tsx
- 会话列表展示
- 新建/删除会话
- 会话切换

#### 4. FileBrowser.tsx
- 文件系统浏览
- 文件/目录选择
- 添加到上下文

### Backend (FastAPI + Python)

#### 1. main.py - API Server
**REST Endpoints:**
- `POST /api/sessions` - 创建会话
- `GET /api/sessions` - 获取会话列表
- `GET /api/sessions/{id}` - 获取会话详情
- `DELETE /api/sessions/{id}` - 删除会话
- `POST /api/context/add` - 添加上下文文件
- `POST /api/context/remove` - 移除上下文文件
- `GET /api/filesystem/list` - 浏览文件系统

**WebSocket Endpoint:**
- `WS /ws/chat` - 流式对话

#### 2. agent_service.py - Agent核心
**AgentService类:**

```python
class AgentService:
    # 会话管理
    def create_session() -> Session
    def get_session(session_id) -> Session
    def list_sessions() -> List[Session]
    def delete_session(session_id) -> bool
    
    # 上下文管理
    def add_context_file(session_id, file_path) -> ContextFile
    def remove_context_file(session_id, file_path) -> bool
    def get_context_files(session_id) -> List[ContextFile]
    
    # 对话处理
    async def chat_stream(session_id, message) -> AsyncGenerator[StreamChunk]
    
    # 内部方法
    def _build_message_history() -> List[Dict]
    def _build_context_content() -> str
    async def _stream_llm_response() -> AsyncGenerator
    async def _execute_tool(tool_name, tool_input) -> str
```

#### 3. core.py - 工具系统
继承自原始的 s01-s23 系列，提供：

```python
# Anthropic客户端
client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

# 模型配置
MODEL = "claude-3-5-sonnet-20241022"

# 工具定义
EXTENDED_TOOLS = [
    {
        "name": "bash",
        "description": "Execute a shell command",
        "input_schema": {...}
    },
    {
        "name": "read",
        "description": "Read file contents",
        "input_schema": {...}
    },
    # ... 更多工具
]

# 工具分发
EXTENDED_DISPATCH = {
    "bash": run_bash,
    "read": run_read,
    "write": run_write,
    "grep": run_grep,
    "glob": run_glob,
    "revert": run_revert
}
```

## 关键设计决策

### 1. 为什么使用WebSocket而不是SSE？

**选择WebSocket的原因：**
- 双向通信（可以实时中断）
- 更好的浏览器支持
- 更低的延迟
- 便于未来扩展（如协作功能）

### 2. 会话持久化策略

**JSON文件存储：**
- ✅ 简单可靠
- ✅ 易于调试和检查
- ✅ 无需额外数据库
- ❌ 不适合高并发（可升级到SQLite/PostgreSQL）

### 3. 上下文文件处理

**策略：**
- 只在发送消息时读取文件内容
- 不在会话中缓存文件内容
- 自动检测文件类型（文件 vs 目录）

**原因：**
- 保持会话文件小巧
- 始终使用最新的文件内容
- 避免内存溢出

### 4. 工具执行安全

**当前实现：**
- 工具在后端执行
- 使用当前工作目录
- 无沙箱隔离

**生产环境建议：**
- 添加权限系统（参考 s15_permissions.py）
- Docker容器隔离
- 命令白名单
- 文件访问范围限制

## 性能优化

### 1. 前端优化
- React.memo 避免不必要的重渲染
- WebSocket连接复用
- 虚拟滚动（大量消息时）
- 代码分割和懒加载

### 2. 后端优化
- 异步I/O（asyncio）
- 工具并行执行
- 会话缓存（内存）
- 流式响应（降低TTFB）

### 3. API优化
- Prompt缓存（参考 s20）
- 连接池
- 请求去重

## 扩展点

### 1. 添加新工具
```python
# 在 core.py 中添加

def run_custom_tool(input_dict):
    # 实现你的工具逻辑
    return "result"

EXTENDED_TOOLS.append({
    "name": "custom_tool",
    "description": "Description",
    "input_schema": {...}
})

EXTENDED_DISPATCH["custom_tool"] = run_custom_tool
```

### 2. 多模型支持
```python
# 在 agent_service.py 中修改

async def chat_stream(self, session_id, message, model="claude-3-5-sonnet"):
    response = client.messages.stream(
        model=model,  # 动态选择模型
        ...
    )
```

### 3. 用户认证
```python
# 添加到 main.py

from fastapi.security import HTTPBearer
security = HTTPBearer()

@app.get("/api/sessions")
async def list_sessions(token: str = Depends(security)):
    # 验证token
    # 返回用户的会话
```

### 4. 团队协作
- 实现会话共享
- WebSocket广播
- 实时协作编辑

## 从s01-s23的映射

| 原始模块 | 整合位置 | 功能 |
|---------|---------|------|
| s01 | agent_service.py | 基础循环 |
| s02 | core.py | 工具分发 |
| s06 | agent_service.py | 上下文管理 |
| s13 | agent_service.py | 流式响应 |
| s14 | core.py | 扩展工具 |
| s15 | (可选) | 权限控制 |
| s17 | agent_service.py | 会话持久化 |
| s18-s20 | agent_service.py | 异步优化 |

## 部署建议

### 开发环境
- 使用提供的 `start.sh` / `start.bat`
- 热重载开启

### 生产环境
```bash
# 后端 (使用Gunicorn + Uvicorn workers)
gunicorn main:app \
  --workers 4 \
  --worker-class uvicorn.workers.UvicornWorker \
  --bind 0.0.0.0:8000

# 前端 (构建静态文件)
cd frontend
npm run build
# 使用 Nginx 托管 dist/ 目录
```

### Docker部署
```dockerfile
# Dockerfile示例
FROM python:3.10
WORKDIR /app
COPY backend/requirements.txt .
RUN pip install -r requirements.txt
COPY backend/ .
CMD ["python", "main.py"]
```

## 监控和日志

### 建议添加
- 请求日志（FastAPI middleware）
- 错误追踪（Sentry）
- 性能监控（Prometheus）
- 用量统计（API调用次数、Token使用）

## 总结

这个系统整合了s01-s23的精华，提供了：
1. ✅ 简洁的用户界面
2. ✅ 强大的Agent能力
3. ✅ 可扩展的架构
4. ✅ 生产就绪的基础

可以作为：
- 个人AI助手
- 团队协作工具
- AI应用的起点
- 学习Agent开发的参考

继续探索和定制，打造属于你的AI Agent系统！
