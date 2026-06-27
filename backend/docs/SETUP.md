# 🚀 快速安装指南

## 最快5分钟开始使用！

### 第一步：准备环境

确保你已安装：
- Python 3.10 或更高版本
- Node.js 18 或更高版本  
- 一个 Anthropic API Key ([获取地址](https://console.anthropic.com/))

### 第二步：配置API Key

1. 复制环境变量模板：
```bash
cd backend
cp .env.example .env
```

2. 编辑 `.env` 文件，填入你的API Key：
```bash
ANTHROPIC_API_KEY=sk-ant-xxxxx
```

### 第三步：启动服务

**Linux/Mac用户:**
```bash
./start.sh
```

**Windows用户:**
```cmd
start.bat
```

或者手动启动：

**后端:**
```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
python main.py
```

**前端 (新终端):**
```bash
cd frontend
npm install
npm run dev
```

### 第四步：开始使用

打开浏览器访问：http://localhost:3000

🎉 完成！现在你可以：
- 创建新对话
- 添加文件到上下文
- 让AI帮你编程

## 常见问题

### Q: 后端启动失败 "Module not found"
```bash
cd backend
source venv/bin/activate
pip install -r requirements.txt
```

### Q: 前端报错 "Cannot find module"
```bash
cd frontend
rm -rf node_modules
npm install
```

### Q: API Key 错误
检查 `backend/.env` 文件：
- 确认文件名是 `.env` 不是 `.env.example`
- 确认Key格式正确 `sk-ant-...`
- 确认没有多余的空格或引号

### Q: 端口被占用
修改端口：
- 后端: 编辑 `backend/main.py` 的 `port=8000`
- 前端: 编辑 `frontend/vite.config.ts` 的 `port: 3000`

## 下一步

- 阅读 [README.md](README.md) 了解完整功能
- 查看 [API文档](http://localhost:8000/docs) (后端启动后)
- 探索源码学习Agent实现原理

## 需要帮助？

遇到问题？创建 GitHub Issue 或查看项目文档。
