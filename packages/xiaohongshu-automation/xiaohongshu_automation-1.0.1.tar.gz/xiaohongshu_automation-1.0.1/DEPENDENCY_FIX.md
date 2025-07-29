# 依赖修复指南 - webdriver_manager 问题

## 🐛 问题描述

使用 `uvx --from xiaohongshu-automation xhs-server` 时出现错误：

```
ModuleNotFoundError: No module named 'webdriver_manager'
```

## ✅ 解决方案

已在以下文件中添加了缺失的依赖：

### 1. pyproject.toml
已添加 `webdriver_manager` 到依赖列表：

```toml
dependencies = [
    "fastapi>=0.104.0",
    "uvicorn>=0.24.0",
    "pydantic>=2.0.0",
    "httpx>=0.25.0",
    "mcp>=1.0.0",
    "selenium",
    "webdriver_manager",  # ✅ 新添加
    "requests",
]
```

### 2. requirements.txt
已添加浏览器自动化相关依赖：

```txt
# 浏览器自动化依赖
selenium
webdriver_manager  # ✅ 新添加
requests
```

### 3. 版本更新
- 版本从 1.0.0 更新为 1.0.1

## 🔧 修复步骤

### 方法一：重新构建本地包

```bash
# 1. 重新构建包
uv build

# 2. 测试新包
uvx --from ./dist/xiaohongshu_automation-1.0.1-py3-none-any.whl xhs-server
```

### 方法二：从源码直接运行

```bash
# 1. 确保依赖已安装
uv sync

# 2. 直接运行
python main.py
```

### 方法三：等待新版本发布

一旦 v1.0.1 发布到 PyPI，可以直接使用：

```bash
uvx --from xiaohongshu-automation==1.0.1 xhs-server
```

## 🧪 验证修复

运行以下命令验证依赖是否正确安装：

```bash
# 检查包依赖
uv pip show xiaohongshu-automation

# 验证 webdriver_manager 可用
python -c "from webdriver_manager.chrome import ChromeDriverManager; print('✅ webdriver_manager 可用')"
```

## 📦 新版本信息

**版本**: 1.0.1  
**修复内容**: 
- ✅ 添加 webdriver_manager 依赖
- ✅ 添加 selenium 依赖到 requirements.txt
- ✅ 保持依赖配置同步

## 🔍 依赖说明

`webdriver_manager` 用于：
- 自动下载和管理 Chrome WebDriver
- 简化 Selenium 的设置过程
- 确保浏览器自动化功能正常工作

这是 `xiaohongshu_tools.py` 中必需的依赖：

```python
from webdriver_manager.chrome import ChromeDriverManager
```

---

*修复时间: 2025-06-01* 