# 🚀 快速参考卡片

## ⚡ 一分钟启动

```bash
# 1. 配置
cd backend && cp .env.example .env
# 编辑 .env 添加 ANTHROPIC_API_KEY

# 2. 启动
cd .. && ./start.sh  # 或 start.bat

# 3. 访问
# http://localhost:3000
```

## 📁 项目结构速查

```
项目根目录/
├── backend/          # Python后端
│   ├── main.py      # FastAPI服务器
│   ├── agent_service.py  # Agent核心
│   └── core.py      # 工具系统
├── frontend/        # React前端
│   └── src/
│       ├── App.tsx           # 主应用
│       ├── components/       # UI组件
│       ├── api.ts           # API客户端
│       └── types.ts         # 类型定义
└── 文档/
    ├── README.md            # 主文档
    ├── SETUP.md            # 安装指南
    ├── ARCHITECTURE.md     # 架构文档
    └── DEMO_GUIDE.md       # 演示指南
```

## 🔧 常用命令

### 后端
```bash
cd backend
source venv/bin/activate       # 激活虚拟环境
python main.py                 # 启动服务
python test_api.py             # 运行测试
```

### 前端
```bash
cd frontend
npm install                    # 安装依赖
npm run dev                    # 开发服务器
npm run build                  # 生产构建
```

## 🌐 API端点速查

### REST API
```
GET    /                       # 健康检查
POST   /api/sessions          # 创建会话
GET    /api/sessions          # 获取列表
GET    /api/sessions/{id}     # 获取详情
DELETE /api/sessions/{id}     # 删除会话
POST   /api/context/add       # 添加文件
POST   /api/context/remove    # 移除文件
GET    /api/context/{id}      # 获取上下文
GET    /api/filesystem/list   # 浏览文件
```

### WebSocket
```
WS /ws/chat                   # 流式对话
```

## 🛠️ 可用工具

| 工具 | 功能 | 示例 |
|-----|------|------|
| bash | 执行命令 | `列出文件` |
| read | 读取文件 | `读取README.md` |
| write | 写入文件 | `创建hello.py` |
| grep | 搜索内容 | `搜索所有TODO` |
| glob | 匹配路径 | `找到所有py文件` |
| revert | 回滚修改 | `撤销修改` |

## 🎯 核心功能速查

### 创建会话
```typescript
// 前端
POST /api/sessions
{ "title": "新对话" }

// 响应
{ "id": "abc123", "title": "新对话", ... }
```

### 发送消息
```typescript
// WebSocket
{
  "session_id": "abc123",
  "message": "你好",
  "include_context": true
}

// 流式响应
{ "type": "text", "content": "你" }
{ "type": "text", "content": "好" }
{ "type": "done", "content": "" }
```

### 添加文件
```typescript
POST /api/context/add
{
  "session_id": "abc123",
  "file_path": "README.md"
}
```

## 🐛 快速故障排查

### 后端无法启动
```bash
# 检查Python版本
python --version  # 需要 >= 3.10

# 检查依赖
pip list | grep fastapi

# 检查.env
cat backend/.env
```

### 前端无法连接
```bash
# 检查后端状态
curl http://localhost:8000

# 检查端口占用
lsof -i :8000
lsof -i :3000

# 重启服务
pkill -f "python main.py"
pkill -f "vite"
```

### WebSocket连接失败
```javascript
// 浏览器控制台
// 应该看到: "WebSocket connected"

// 如果失败，检查：
1. 后端是否运行在8000端口
2. 浏览器控制台错误信息
3. 防火墙设置
```

## 📊 性能基准

| 指标 | 数值 |
|-----|------|
| 首Token延迟 | ~300-500ms |
| 流式频率 | ~50ms/token |
| 会话加载 | <100ms |
| 内存占用 | ~150MB |
| 并发用户 | ~100 |

## 🔒 安全检查清单

- [ ] API Key已配置在.env
- [ ] .env未提交到Git
- [ ] 生产环境添加认证
- [ ] 限制工具执行权限
- [ ] 限制文件访问范围
- [ ] 启用HTTPS
- [ ] 配置防火墙规则

## 📝 配置速查

### .env配置
```bash
ANTHROPIC_API_KEY=sk-ant-xxxxx
MODEL=claude-3-5-sonnet-20241022
```

### Vite配置
```typescript
// frontend/vite.config.ts
server: {
  port: 3000,
  proxy: {
    '/api': 'http://localhost:8000'
  }
}
```

### CORS配置
```python
# backend/main.py
allow_origins=["http://localhost:3000"]
```

## 🎨 主题色彩

```css
--primary-color: #7c3aed     /* 紫色 */
--bg-primary: #ffffff        /* 白色 */
--bg-secondary: #f9fafb      /* 浅灰 */
--text-primary: #111827      /* 深灰 */
--border-color: #e5e7eb      /* 边框 */
```

## 📚 文档导航

| 文档 | 用途 | 时长 |
|-----|------|------|
| SETUP.md | 快速安装 | 5分钟 |
| README.md | 完整指南 | 15分钟 |
| ARCHITECTURE.md | 架构理解 | 30分钟 |
| DEMO_GUIDE.md | 演示准备 | 10分钟 |

## 🔗 有用链接

- [Anthropic Console](https://console.anthropic.com/)
- [Claude API文档](https://docs.anthropic.com/)
- [FastAPI文档](https://fastapi.tiangolo.com/)
- [React文档](https://react.dev/)
- [Vite文档](https://vitejs.dev/)

## 💡 提示技巧

### 提高响应速度
- 使用提示词缓存 (s20)
- 减少历史消息数量
- 精简上下文文件

### 提高准确性
- 添加相关文件到上下文
- 提供清晰的指令
- 分步骤执行复杂任务

### 调试技巧
- 查看浏览器控制台
- 查看后端日志输出
- 使用test_api.py测试
- 检查.sessions/文件

## 🆘 紧急救援

### 完全重置
```bash
# 停止所有服务
pkill -f "python main.py"
pkill -f "vite"

# 清理数据
rm -rf .sessions/
rm -rf backend/venv/
rm -rf frontend/node_modules/

# 重新安装
./start.sh
```

### 数据恢复
```bash
# 会话文件位置
ls .sessions/*.json

# 手动查看会话
cat .sessions/abc123.json | jq .
```

## ⌨️ 快捷键

| 快捷键 | 功能 |
|-------|------|
| Enter | 发送消息 |
| Shift+Enter | 换行 |
| Ctrl+C | 中断（终端） |
| F12 | 开发者工具 |

## 📞 获取帮助

1. 查看文档
2. 运行测试脚本
3. 检查日志
4. 提交Issue

---

**快速参考 v1.0** | 更新于: 2024-01-15
