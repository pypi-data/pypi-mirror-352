# 小红书自动化工具 - 部署和发布指南

## 🏗️ 环境设置

### 方法一：使用 uv（推荐）

```bash
# 1. 安装 uv
# Windows PowerShell:
curl -LsSf https://astral.sh/uv/install.ps1 | powershell

# macOS/Linux:
curl -LsSf https://astral.sh/uv/install.sh | sh

# 2. 创建虚拟环境
uv venv

# 3. 激活虚拟环境
# Windows:
.venv\Scripts\activate
# macOS/Linux:
source .venv/bin/activate

# 4. 安装依赖
uv sync
```

### 方法二：使用便捷脚本（Windows）

```bash
# 一键设置开发环境
scripts\setup_dev.bat
```

### 方法三：传统方式

```bash
# 创建虚拟环境
python -m venv venv

# 激活虚拟环境
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt
```

## 📦 打包构建

### 使用 uv 构建

```bash
# 激活虚拟环境后
uv build

# 构建结果在 dist/ 目录：
# - xiaohongshu_automation-1.0.0-py3-none-any.whl
# - xiaohongshu_automation-1.0.0.tar.gz
```

### 检查构建结果

```bash
# 查看打包内容
tar -tzf dist/xiaohongshu_automation-1.0.0.tar.gz

# 或使用 Python
python -m zipfile -l dist/xiaohongshu_automation-1.0.0-py3-none-any.whl
```

## 🚀 发布到 PyPI

### 准备工作

1. **注册 PyPI 账号**
   - 正式环境：https://pypi.org/account/register/
   - 测试环境：https://test.pypi.org/account/register/

2. **配置 API Token**

创建 `~/.pypirc` 文件：

```ini
[distutils]
index-servers = 
    pypi
    testpypi

[pypi]
repository = https://upload.pypi.org/legacy/
username = __token__
password = pypi-your-api-token-here

[testpypi]
repository = https://test.pypi.org/legacy/
username = __token__
password = pypi-your-test-api-token-here
```

### 发布方法

#### 方法一：使用便捷脚本（推荐）

```bash
# Windows:
scripts\publish.bat

# 或使用 Python 脚本:
python scripts\publish.py
```

#### 方法二：手动发布

```bash
# 1. 安装 twine
uv pip install twine

# 2. 先上传到测试环境
twine upload --repository testpypi dist/*

# 3. 测试安装
pip install --index-url https://test.pypi.org/simple/ xiaohongshu-automation

# 4. 测试通过后上传到正式环境
twine upload dist/*
```

## 🧪 测试安装

### 测试本地构建

```bash
# 安装本地构建的包
pip install dist/xiaohongshu_automation-1.0.0-py3-none-any.whl

# 或从源码安装
pip install -e .
```

### 测试 PyPI 安装

```bash
# 从测试环境安装
pip install --index-url https://test.pypi.org/simple/ xiaohongshu-automation

# 从正式环境安装
pip install xiaohongshu-automation
```

## 🔧 版本管理

### 更新版本号

1. **更新 pyproject.toml**

```toml
[project]
version = "1.0.1"  # 更新版本号
```

2. **创建 Git 标签**

```bash
git tag v1.0.1
git push origin v1.0.1
```

### 版本命名规范

- **主版本号** (1.x.x): 不兼容的API修改
- **次版本号** (x.1.x): 向后兼容的功能性新增
- **修订号** (x.x.1): 向后兼容的问题修正

## 📁 项目结构说明

```
xiaohongshu-automation/
├── pyproject.toml          # 项目配置和依赖
├── README.md               # 项目说明
├── LICENSE                 # 许可证
├── MANIFEST.in             # 打包文件控制
├── .gitignore              # Git 忽略文件
├── main.py                 # FastAPI 主服务
├── mcp_server.py          # MCP 服务器
├── config.py              # 配置管理
├── xiaohongshu_tools.py   # 核心功能模块
├── unti.py                # 工具函数
├── requirements.txt       # 依赖清单（兼容性）
├── scripts/               # 自动化脚本
│   ├── setup_dev.bat     # 开发环境设置
│   ├── publish.bat       # 发布脚本（Windows）
│   └── publish.py        # 发布脚本（Python）
├── adapters/              # 服务适配器
├── tools/                 # MCP 工具
├── docs/                  # 文档
└── dist/                  # 构建输出（自动生成）
```

## 🚨 常见问题

### 构建问题

**问题**: `No solution found when resolving dependencies`
**解决**: 检查 Python 版本是否 >= 3.10

```bash
python --version
# 如果版本过低，安装 Python 3.10+
```

### 编码问题

**问题**: Windows 下 Unicode 编码错误
**解决**: 设置环境变量

```bash
set PYTHONIOENCODING=utf-8
chcp 65001
```

### 上传问题

**问题**: `403 Forbidden` 错误
**解决**: 
1. 检查 API token 是否正确
2. 确保包名未被占用
3. 先上传到 TestPyPI 测试

**问题**: 包名冲突
**解决**: 修改 `pyproject.toml` 中的包名

```toml
[project]
name = "xiaohongshu-automation-yourname"
```

## 📋 发布检查清单

- [ ] 代码测试通过
- [ ] 版本号已更新
- [ ] README 文档已更新
- [ ] 依赖版本已确认
- [ ] 构建成功无错误
- [ ] 在 TestPyPI 测试成功
- [ ] Git 标签已创建
- [ ] 正式发布到 PyPI

## 🔗 相关链接

- [uv 官方文档](https://docs.astral.sh/uv/)
- [PyPI 官网](https://pypi.org/)
- [TestPyPI](https://test.pypi.org/)
- [Python 打包指南](https://packaging.python.org/)
- [Twine 文档](https://twine.readthedocs.io/) 