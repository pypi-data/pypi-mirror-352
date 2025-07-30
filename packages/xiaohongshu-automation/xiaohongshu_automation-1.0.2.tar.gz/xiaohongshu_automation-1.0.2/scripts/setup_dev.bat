@echo off
chcp 65001 >nul
echo 🛠️ 设置小红书自动化工具开发环境...

cd /d "%~dp0\.."

echo 🔍 检查 uv 是否已安装...
uv --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ uv 未安装，请先安装 uv
    echo 📖 安装方法: https://github.com/astral-sh/uv
    pause
    exit /b 1
)

echo ✅ uv 已安装

echo 🐍 创建虚拟环境...
if exist ".venv" rmdir /s /q ".venv"
uv venv

echo 🔄 激活虚拟环境并安装依赖...
call .venv\Scripts\activate.bat
uv sync

echo 📦 安装开发依赖...
uv pip install --dev

echo 🧪 运行基础测试...
if exist "test_basic.py" (
    python test_basic.py
    if %errorlevel% equ 0 (
        echo ✅ 测试通过
    ) else (
        echo ⚠️ 测试失败，但环境设置完成
    )
)

echo.
echo ✨ 开发环境设置完成!
echo 🚀 现在你可以:
echo   - 运行服务: python main.py
echo   - 运行 MCP 服务器: python mcp_server.py
echo   - 构建包: uv build
echo   - 发布包: scripts\publish.bat
echo.
pause 