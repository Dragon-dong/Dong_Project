# 跨模态内容生成系统 - 文件功能说明

## 项目结构

```
📁 gradual project/
├── 📁 database/              # 数据库相关代码
│   ├── db_connection.py      # 数据库连接和初始化
│   └── db_operations.py      # 数据库操作封装
├── 📁 models/                # AI模型封装
│   ├── sd_model.py           # Stable Diffusion模型（文生图）
│   ├── llava_model.py        # LLaVA模型（图生文）
│   ├── llm_model.py          # LLM模型（文本生成）
│   ├── multilingual_model.py # 多语言文化适配模型
│   └── rag_model.py          # RAG模型（风格知识检索）
├── 📁 img/                   # 生成的图像存储
├── 📁 unused_code/           # 测试和用不上的代码
├── main.py                   # 后端服务主文件
├── index.html                # 前端界面
├── requirements.txt          # 项目依赖
├── .env                      # 环境配置
├── TODO.md                   # 待完成任务
├── xiangmu.md                # 项目需求文档
└── 项目说明文档.md           # 项目详细说明
```

## 文件功能说明

### 核心文件

| 文件 | 图标 | 功能说明 |
|------|------|----------|
| `main.py` | 🚀 | 后端服务主文件，实现API路由和业务逻辑，集成所有功能模块 |
| `index.html` | 🖥️ | 前端界面，提供用户交互界面 |
| `requirements.txt` | 📦 | 项目依赖配置，管理Python包依赖 |
| `.env` | ⚙️ | 环境配置文件，存储数据库连接信息和其他配置 |

### 数据库模块

| 文件 | 图标 | 功能说明 |
|------|------|----------|
| `database/db_connection.py` | 🗄️ | 数据库连接管理，负责MySQL和Redis的连接和初始化 |
| `database/db_operations.py` | 📊 | 数据库操作封装，提供CRUD操作和缓存功能 |

### 模型模块

| 文件 | 图标 | 功能说明 |
|------|------|----------|
| `models/sd_model.py` | 🖼️ | Stable Diffusion模型封装，用于文生图功能 |
| `models/llava_model.py` | 👁️ | LLaVA模型封装，用于图生文功能 |
| `models/llm_model.py` | 📝 | LLM模型封装，用于文本生成和动态叙事 |
| `models/multilingual_model.py` | 🌍 | 多语言文化适配模型，支持多语言翻译和文化背景分析 |
| `models/rag_model.py` | 📚 | RAG模型封装，用于风格知识检索和提示词增强 |

### 资源目录

| 目录 | 图标 | 功能说明 |
|------|------|----------|
| `img/` | 📷 | 生成的图像存储目录 |
| `unused_code/` | 📁 | 测试文件和用不上的代码 |

## API端点说明

| API端点 | 方法 | 功能说明 |
|---------|------|----------|
| `/` | GET | 根路径，返回前端页面 |
| `/api/text-to-image` | POST | 文本生成图像接口 |
| `/api/image-to-text` | POST | 图像生成文本接口 |
| `/api/generate-story` | POST | 动态叙事生成接口 |
| `/api/style-transfer` | POST | 风格迁移接口 |
| `/api/multilingual-adaptation` | POST | 多语言文化适配接口 |
| `/api/history` | GET | 获取生成历史记录 |
| `/api/config` | GET/POST | 获取/设置系统配置 |
| `/api/cache/clear` | POST | 清除缓存 |

## 技术栈

| 技术 | 图标 | 用途 |
|------|------|------|
| FastAPI | ⚡ | 后端API框架 |
| MySQL | 🗄️ | 数据持久化 |
| Redis | 🚀 | 缓存系统 |
| SiliconFlow API | 🖼️ | 图像生成 |
| 阿里云百炼API | 👁️ | 图像理解和文本生成 |
| ONNX Runtime | 🔄 | 模型推理优化 |
| Diffusers | 🎨 | 扩散模型集成 |

## 运行说明

1. 安装依赖：`pip install -r requirements.txt`
2. 配置环境变量：编辑 `.env` 文件
3. 启动服务：`python main.py`
4. 访问前端：浏览器打开 `http://localhost:8000`
5. API文档：`http://localhost:8000/docs`

## 功能特性

- ✅ 文本描述生成对应图像
- ✅ 图像内容自动生成描述文案
- ✅ 动态叙事生成（包含图像和文案）
- ✅ 风格迁移控制
- ✅ 多语言文化适配
- ✅ 数据库集成和历史记录
- ✅ 缓存机制
- ✅ 错误处理和日志记录

## 系统架构

```
┌─────────────────────────────────────────────────────────┐
│                       前端层                            │
│   index.html (HTML/CSS/JavaScript)                    │
└──────────────────┬────────────────────────────────────┘
                   │
┌──────────────────▼────────────────────────────────────┐
│                       后端层                            │
│   main.py (FastAPI)                                   │
└──────────────────┬────────────────────────────────────┘
                   │
┌──────────────────▼────────────────────────────────────┐
│                       模型层                            │
│   sd_model.py   llava_model.py   llm_model.py         │
│   multilingual_model.py   rag_model.py               │
└──────────────────┬────────────────────────────────────┘
                   │
┌──────────────────▼────────────────────────────────────┐
│                       存储层                            │
│   database/ (MySQL + Redis)   img/ (生成图像)         │
└─────────────────────────────────────────────────────────┘
```