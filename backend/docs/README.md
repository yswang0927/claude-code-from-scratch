# 🤖 AI Agent - Simple Claude Web Interface

一个功能完备的AI Agent系统，整合了s01-s23的核心能力，提供简洁的网页界面，类似Claude的使用体验。

## ✨ 功能特性

### 核心功能
- ✅ **流式对话** - 实时显示AI响应，类似打字机效果
- ✅ **会话管理** - 创建、保存、删除多个对话会话
- ✅ **上下文文件** - 添加文件/目录到对话上下文
- ✅ **工具调用** - 支持bash、文件读写、搜索等工具
- ✅ **Markdown渲染** - 美观的代码高亮和格式化

### 整合的Agent能力
从s01-s23提取并整合的核心能力：
- 🔄 感知-行动循环 (s01)
- 🛠️ 可扩展工具系统 (s02, s14)
- 📝 上下文管理 (s06)
- 🔌 实时流式响应 (s13)
- 💾 会话持久化 (s17)
- 🔒 安全权限控制 (s15)
- ⚡ 异步执行 (s18-s20)

## 🚀 快速开始

### 前置要求

- Python 3.10+
- Node.js 18+
- Anthropic API Key

### 1. 后端设置

```bash
cd backend

# 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 安装依赖
pip install -r requirements.txt

# 配置环境变量
cp .env.example .env
# 编辑 .env 文件，填入你的 ANTHROPIC_API_KEY

# 启动后端服务
python main.py
```

后端将在 http://localhost:8000 启动

### 2. 前端设置

```bash
cd frontend

# 安装依赖
npm install

# 启动开发服务器
npm run dev
```

前端将在 http://localhost:3000 启动

### 3. 访问应用

打开浏览器访问 http://localhost:3000

## 📁 项目结构

```
.
├── backend/                 # Python FastAPI后端
│   ├── main.py             # FastAPI应用入口
│   ├── agent_service.py    # 统一Agent服务
│   ├── core.py             # 核心工具和dispatch逻辑
│   ├── requirements.txt    # Python依赖
│   └── .env.example        # 环境变量模板
│
├── frontend/               # React前端
│   ├── src/
│   │   ├── components/    # React组件
│   │   │   ├── ChatInterface.tsx   # 主对话界面
│   │   │   ├── Sidebar.tsx         # 会话列表侧边栏
│   │   │   └── FileBrowser.tsx     # 文件浏览器
│   │   ├── App.tsx        # 主应用组件
│   │   ├── api.ts         # API客户端
│   │   └── types.ts       # TypeScript类型定义
│   ├── package.json       # npm依赖
│   └── vite.config.ts     # Vite配置
│
└── README.md              # 本文件
```

## 🎯 使用指南

### 基本对话

1. 点击左上角 `+` 按钮创建新会话
2. 在底部输入框输入消息
3. 按 Enter 发送（Shift+Enter 换行）
4. AI会实时流式返回响应

### 添加上下文文件

1. 点击右上角的文件夹图标 📁
2. 在文件浏览器中选择文件或目录
3. 文件会显示在对话框上方的上下文栏
4. 发送消息时会自动包含这些文件内容

### 工具调用

Agent可以自动调用以下工具：
- `bash` - 执行Shell命令
- `read` - 读取文件内容
- `write` - 写入文件
- `grep` - 搜索文件内容
- `glob` - 文件路径匹配
- `revert` - 回滚文件修改

工具调用会在对话中显示 🔧 图标和执行结果。

## 🔧 高级配置

### 修改模型

编辑 `backend/.env`:
```
MODEL=claude-3-5-sonnet-20241022
```

### 添加自定义工具

在 `backend/core.py` 中：

1. 添加工具Schema到 `EXTENDED_TOOLS`
2. 实现工具handler
3. 添加到 `EXTENDED_DISPATCH` 映射

### CORS配置

如果部署到不同域名，修改 `backend/main.py`:
```python
allow_origins=["https://your-frontend-domain.com"]
```

## 🛠️ 开发说明

### 后端API文档

启动后端后访问：
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

### 主要API端点

**REST API:**
- `GET /api/sessions` - 获取会话列表
- `POST /api/sessions` - 创建新会话
- `GET /api/sessions/{id}` - 获取会话详情
- `DELETE /api/sessions/{id}` - 删除会话
- `POST /api/context/add` - 添加上下文文件
- `GET /api/filesystem/list` - 浏览文件系统

**WebSocket:**
- `WS /ws/chat` - 流式对话接口

### 前端开发

```bash
cd frontend
npm run dev      # 开发服务器
npm run build    # 生产构建
npm run preview  # 预览生产构建
```

## 📝 技术栈

### 后端
- **FastAPI** - 现代Python Web框架
- **Anthropic SDK** - Claude API客户端
- **Uvicorn** - ASGI服务器
- **WebSockets** - 实时通信

### 前端
- **React 18** - UI框架
- **TypeScript** - 类型安全
- **Vite** - 构建工具
- **React Markdown** - Markdown渲染
- **Lucide React** - 图标库

## 🐛 故障排查

### 后端启动失败

```bash
# 检查Python版本
python --version  # 应该 >= 3.10

# 检查依赖安装
pip list

# 检查环境变量
cat .env
```

### 前端连接失败

1. 确认后端已启动在 8000 端口
2. 检查浏览器控制台错误
3. 检查 Vite proxy 配置

### WebSocket连接问题

```javascript
// 检查浏览器控制台
// 应该看到 "WebSocket connected"

// 如果失败，检查防火墙和代理设置
```

## 🔐 安全注意事项

- ⚠️ 不要在生产环境暴露 8000 端口
- ⚠️ 保护好 `.env` 文件中的 API Key
- ⚠️ 考虑添加用户认证
- ⚠️ 限制文件系统访问范围
- ⚠️ 对bash工具添加命令白名单

## 📄 许可证

MIT License

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

## 📧 联系方式

如有问题，请创建 GitHub Issue。

---

**Enjoy coding with AI! 🚀**
