# 小红书自动化工具

基于 Model Context Protocol (MCP) 的小红书自动化解决方案，为 AI 助手提供内容发布、评论管理和系统监控能力。

## 🚀 快速开始

### 1. 环境准备

**推荐使用 uv 进行环境管理**（更快更现代的Python包管理器）

```bash
# 安装 uv（如果还没安装）
# Windows: 
curl -LsSf https://astral.sh/uv/install.ps1 | powershell
# macOS/Linux:
curl -LsSf https://astral.sh/uv/install.sh | sh

# 克隆项目
git clone <repository-url>
cd xiaohongshu-automation

# 方式一：使用 uv（推荐）
uv venv                    # 创建虚拟环境
uv sync                    # 安装所有依赖

# 方式二：传统方式
python -m venv venv
venv\Scripts\activate      # Windows
# source venv/bin/activate  # macOS/Linux
pip install -r requirements.txt
```

### 🛠️ 开发环境一键设置

对于 Windows 用户，可以使用便捷脚本：

```bash
# 一键设置开发环境
scripts\setup_dev.bat
```

### 📦 打包和发布

```bash
# 构建包
uv build

# 发布到 PyPI（使用便捷脚本）
scripts\publish.bat

# 或手动发布
uv pip install twine
twine upload dist/*
```

### 2. 启动服务

**重要**: 必须按顺序启动两个服务

```bash
# 第一步：启动 FastAPI 后端服务并且扫码登录小红书
python main.py

# 第二步：启动 MCP 服务器
python mcp_server.py
```

### 2. 配置 AI 客户端

在支持 MCP 的 AI 客户端中配置连接到本地 MCP 服务器。

## 📦 安装发布版本

如果项目已发布到 PyPI，用户可以直接安装：

```bash
pip install xiaohongshu-automation
```

## 🛠️ 故障排除

### 常见问题：MCP调用成功但AI显示失败

**症状**: MCP服务调用成功，但AI执行结果显示失败
**原因**: FastAPI后端服务未运行
**解决**: 运行 `python main.py` 启动后端服务

详细故障排除指南请参考：[TIMEOUT_TROUBLESHOOTING.md](TIMEOUT_TROUBLESHOOTING.md)

### 快速诊断

```bash
# 运行诊断工具
python test_timeout_improvements.py

# 或在MCP中调用
xiaohongshu_timeout_diagnostic
```

## ⚙️ 功能特性

### 🎯 核心工具

1. **xiaohongshu_publish** - 发布内容到小红书
   - 支持多张图片（1-18张）
   - 内容质量分析和优化建议
   - 智能话题标签和@用户检测

2. **xiaohongshu_get_comments** - 获取评论分析
   - 情感分析和关键词提取
   - 评论统计和互动分析

3. **xiaohongshu_reply_comments** - 批量回复评论
   - 智能回复建议和内容优化
   - 批量处理和语调调整

4. **xiaohongshu_monitor** - 系统监控
   - 健康状态评分
   - 服务状态检查
   - 历史记录分析

5. **xiaohongshu_timeout_diagnostic** - 超时诊断 🆕
   - 网络连接测试
   - 性能分析
   - 配置建议

### 📚 资源

- **xiaohongshu://monitor/status** - 实时监控状态
- **xiaohongshu://posts/history** - 发布历史记录
- **xiaohongshu://tools/info** - 工具信息总览

### 🎨 提示模板

- **xiaohongshu_content_template** - 内容创作模板
- **xiaohongshu_reply_template** - 评论回复模板
- **xiaohongshu_optimization_tips** - 优化建议模板

## 📋 API 接口

### 发布内容
```http
POST /publish
Content-Type: application/json

{
  "pic_urls": ["https://example.com/image1.jpg"],
  "title": "标题",
  "content": "内容文本"
}
```

### 获取评论(暂未完善)
```http
GET /get_comments?url=https://www.xiaohongshu.com/explore/xxxxx
```

### 回复评论(暂未完善)
```http
POST /post_comments?url=https://www.xiaohongshu.com/explore/xxxxx
Content-Type: application/json

{
  "comment_id_1": ["回复内容1", "回复内容2"],
  "comment_id_2": ["回复内容3"]
}
```

## ⚙️ 配置选项

### 超时配置

```bash
# 基本超时设置
export FASTAPI_TIMEOUT=30          # 默认超时
export PUBLISH_TIMEOUT=60          # 发布操作超时
export COMMENTS_TIMEOUT=30         # 评论操作超时
export MONITOR_TIMEOUT=15          # 监控操作超时
export HEALTH_CHECK_TIMEOUT=5      # 健康检查超时

# 重试机制
export ENABLE_AUTO_RETRY=true      # 启用自动重试
export MAX_RETRIES=3               # 最大重试次数
export RETRY_DELAY=2               # 重试间隔（秒）

# 日志配置
export LOG_LEVEL=INFO              # 日志级别
export DETAILED_ERROR_MSG=true     # 详细错误信息
```

### 环境配置示例

#### 本地开发
```bash
export FASTAPI_TIMEOUT=30
export PUBLISH_TIMEOUT=60
export ENABLE_AUTO_RETRY=true
export MAX_RETRIES=3
```

#### 生产环境
```bash
export FASTAPI_TIMEOUT=60
export PUBLISH_TIMEOUT=120
export ENABLE_AUTO_RETRY=true
export MAX_RETRIES=5
export RETRY_DELAY=3
```

## 🧪 测试

### 运行测试套件

```bash
# 基础功能测试
python test_mcp_server.py

# 超时和诊断测试
python test_timeout_improvements.py

# 发布功能专项测试
python test_publish_fix.py
```

### 性能监控

```bash
# 启用详细日志
export LOG_LEVEL=DEBUG
python mcp_server.py

# 监控系统状态
xiaohongshu_monitor
```

## 🏗️ 项目结构

```
xiaohongshu-automation/
├── main.py                     # FastAPI 主服务
├── mcp_server.py              # MCP 服务器
├── config.py                  # 配置管理
├── adapters/
│   └── xiaohongshu_adapter.py # 服务适配器
├── tools/                     # MCP 工具
│   ├── base_tool.py          # 基础工具类
│   ├── publish_tool.py       # 发布工具
│   ├── comments_tool.py      # 评论工具
│   ├── monitor_tool.py       # 监控工具
│   ├── timeout_diagnostic_tool.py # 诊断工具 🆕
│   └── tool_manager.py       # 工具管理器
├── xiaohongshu_tools.py       # 核心功能模块
├── unti.py                    # 工具函数
├── requirements.txt           # Python 依赖
├── TIMEOUT_TROUBLESHOOTING.md # 故障排除指南 🆕
└── README.md                  # 项目文档
```

## 🔒 依赖

- Python 3.8+
- FastAPI - Web 框架
- MCP (Model Context Protocol) - AI 集成协议
- httpx - HTTP 客户端
- pydantic - 数据验证
- selenium - 浏览器自动化
- requests - HTTP 请求

## 📈 版本历史

### v1.0.0 (2025-06-01)
- ✅ 基础 MCP 服务器实现
- ✅ 核心工具集（发布、评论、监控）
- ✅ 智能重试和超时配置
- ✅ 超时诊断工具
- ✅ 详细的故障排除指南

## 🤝 贡献

欢迎提交 Issue 和 Pull Request 来改进项目。

## 📄 许可证

MIT License

---

## 🆘 获取帮助

如果遇到问题：

1. **查看故障排除指南**: [TIMEOUT_TROUBLESHOOTING.md](TIMEOUT_TROUBLESHOOTING.md)
2. **运行诊断工具**: `python test_timeout_improvements.py`
3. **检查服务状态**: 确保 `python main.py` 正在运行
4. **查看日志**: 启用 `LOG_LEVEL=DEBUG` 获取详细信息

**快速检查清单**:
- [ ] FastAPI 服务已启动 (`python main.py`)
- [ ] MCP 服务器已启动 (`python mcp_server.py`)
- [ ] 可以访问 http://localhost:8000/docs
- [ ] AI 客户端正确配置了 MCP 连接

---

*最后更新: 2025-06-01* 