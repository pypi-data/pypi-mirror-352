@echo off
chcp 65001 >nul
echo 🚀 开始发布小红书自动化工具包...

cd /d "%~dp0\.."

echo 🔄 激活虚拟环境...
if exist ".venv\Scripts\activate.bat" (
    call .venv\Scripts\activate.bat
) else if exist "venv\Scripts\activate.bat" (
    call venv\Scripts\activate.bat
) else (
    echo ❌ 未找到虚拟环境，请先运行 uv venv
    pause
    exit /b 1
)

echo 🧹 清理旧的构建文件...
if exist "dist" rmdir /s /q "dist"
if exist "build" rmdir /s /q "build"

echo 📦 构建包...
uv build
if %errorlevel% neq 0 (
    echo ❌ 构建失败
    pause
    exit /b 1
)

echo ✅ 构建成功! 
echo 📂 查看构建的文件:
dir dist

echo.
set /p upload="🔽 是否上传到 PyPI? (y/N): "
if /i "%upload%"=="y" (
    echo 📥 安装 twine...
    uv pip install twine
    
    echo 🌐 上传到 PyPI...
    echo 📝 请确保已设置 PyPI 凭据
    twine upload dist/*
    
    if %errorlevel% equ 0 (
        echo 🎉 成功发布到 PyPI!
        echo 📖 用户现在可以使用以下命令安装:
        echo    pip install xiaohongshu-automation
    ) else (
        echo ❌ 上传失败，请检查凭据和网络连接
    )
) else (
    echo 📦 本地构建完成，文件位于 dist/ 目录
    echo 💡 如需手动上传，使用: twine upload dist/*
)

echo.
echo ✨ 发布流程完成!
pause 